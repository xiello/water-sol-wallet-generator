#!/usr/bin/env python3

import json
import multiprocessing
import select
import sys
import termios
import threading
import time
import tty
from ctypes import c_double, c_int
from datetime import timedelta
from pathlib import Path

import click
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.config import DEFAULT_ITERATION_BITS, HostSetting
from core.opencl.manager import get_all_gpu_devices
from core.utils.helpers import check_character, load_kernel_source

SAND = "#D4A574"
LIGHT_SAND = "#F4E7D7"
BROWN = "#8B7355"
ACCENT_GOLD = "#FFD700"
PRIMARY_ORANGE = "#FF8C00"

console = Console()


def format_number(num: int) -> str:
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}b"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}m"
    elif num >= 1_000:
        return f"{num / 1_000:.0f}k"
    return str(num)


def get_gpu_names() -> list[str]:
    try:
        devices = get_all_gpu_devices()
        return [d.name.strip() for d in devices]
    except Exception:
        return []


def gpu_worker(
    index: int,
    kernel_source: str,
    iteration_bits: int,
    gpu_counts: int,
    speed_array,
    result_queue,
    stop_flag,
):
    try:
        from core.config import HostSetting
        from core.searcher import Searcher

        setting = HostSetting(kernel_source, iteration_bits)
        searcher = Searcher(
            kernel_source=kernel_source,
            index=index,
            setting=setting,
        )

        while not stop_flag.value:
            start_time = time.time()
            result = searcher.find(log_stats=False)
            elapsed = time.time() - start_time

            global_work_size = setting.global_work_size // gpu_counts
            speed_mhs = global_work_size / (elapsed * 1e6) if elapsed > 0 else 0.0
            speed_array[index] = speed_mhs

            if result[0]:
                result_queue.put(bytes(result[1:]))
                setting = HostSetting(kernel_source, iteration_bits)
                searcher = Searcher(
                    kernel_source=kernel_source,
                    index=index,
                    setting=setting,
                )

    except Exception:
        speed_array[index] = 0.0


def result_monitor_thread(
    result_queue,
    output_dir: str,
    stats: "SearchStats",
    stop_flag,
    target_count: int,
):
    from core.utils.crypto import save_keypair

    while not stop_flag.value or not result_queue.empty():
        try:
            pv_bytes = result_queue.get(timeout=0.25)
        except Exception:
            continue

        try:
            pubkey = save_keypair(pv_bytes, output_dir)
            stats.add_wallet_found(pubkey)

            if stats.wallets_found >= target_count:
                stop_flag.value = 1
        except Exception:
            pass


def keyboard_thread(
    stats: "SearchStats", stop_event: threading.Event, export_flag: threading.Event
):
    if not sys.stdin.isatty():
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while not stop_event.is_set():
            if select.select([sys.stdin], [], [], 0.15)[0]:
                key = sys.stdin.read(1).lower()
                if key == "s":
                    stats.paused = True
                elif key == "c":
                    stats.paused = False
                elif key == "e":
                    export_flag.set()
                    stop_event.set()
                    break
                elif key == "x":
                    stop_event.set()
                    break
    except Exception:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class SearchStats:
    def __init__(self, gpu_count: int, target_count: int):
        self.gpu_count = gpu_count
        self.target_count = target_count
        self.wallets_generated: int = 0
        self.wallets_found: int = 0
        self.gpu_speeds: dict[int, float] = {i: 0.0 for i in range(gpu_count)}
        self.found_addresses: list[str] = []
        self.start_time: float = time.time()
        self.paused: bool = False
        self.lock = threading.Lock()
        self.animation_frame: int = 0
        self._last_sync: float = time.time()

    def sync_from_shared(self, speed_array) -> None:
        with self.lock:
            now = time.time()
            dt = now - self._last_sync
            self._last_sync = now

            for i in range(self.gpu_count):
                speed = speed_array[i]
                self.gpu_speeds[i] = speed
                if speed > 0:
                    self.wallets_generated += int(speed * 1e6 * dt)

    def add_wallet_found(self, address: str) -> None:
        with self.lock:
            self.wallets_found += 1
            self.found_addresses.append(address)

    def get_total_speed(self) -> float:
        with self.lock:
            return sum(self.gpu_speeds.values())

    def get_elapsed_time(self) -> str:
        elapsed = int(time.time() - self.start_time)
        return str(timedelta(seconds=elapsed))


def create_header() -> Panel:
    header_art = f"""[{ACCENT_GOLD}]\
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551               \u26a1 SOLANA VANITY ADDRESS SEARCH \u26a1                 \u2551
\u2551                                                                   \u2551
\u2551               [dim]GPU-accelerated keypair generation[/dim]                \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d[/]"""
    return Panel(
        Align.center(Text.from_markup(header_art)),
        style=f"bold {SAND}",
        border_style=PRIMARY_ORANGE,
    )


def create_gpu_panel(stats: SearchStats, gpu_names: list[str]) -> Panel:
    table = Table(
        show_header=True,
        header_style=f"bold {ACCENT_GOLD}",
        border_style=BROWN,
        expand=True,
    )
    table.add_column("GPU", style=SAND, width=6)
    table.add_column("Device", style=LIGHT_SAND, ratio=2)
    table.add_column("Speed", style=PRIMARY_ORANGE, justify="right", width=14)
    table.add_column("Status", style=ACCENT_GOLD, width=16)

    spinner_frames = [
        "\u280b",
        "\u2819",
        "\u2839",
        "\u2838",
        "\u283c",
        "\u2834",
        "\u2826",
        "\u2827",
        "\u2807",
        "\u280f",
    ]
    frame = spinner_frames[stats.animation_frame % len(spinner_frames)]

    for gpu_id in range(stats.gpu_count):
        speed = stats.gpu_speeds.get(gpu_id, 0.0)
        name = gpu_names[gpu_id] if gpu_id < len(gpu_names) else f"GPU {gpu_id}"

        if speed > 0:
            status = f"[green]{frame} GENERATING[/green]"
            speed_str = f"{speed:.2f} MH/s"
        elif stats.animation_frame > 8:
            status = f"[yellow]{frame} WARMING UP[/yellow]"
            speed_str = "---"
        else:
            status = f"[dim]\u23f8 INITIALIZING[/dim]"
            speed_str = "---"

        table.add_row(f"#{gpu_id}", name, speed_str, status)

    return Panel(
        table,
        title=f"[{ACCENT_GOLD}]GPU PROCESSORS[/]",
        border_style=PRIMARY_ORANGE,
    )


def create_stats_panel(stats: SearchStats, search_params: dict) -> Panel:
    total_speed = stats.get_total_speed()
    elapsed = stats.get_elapsed_time()

    if stats.wallets_found < stats.target_count and total_speed > 0:
        prefix_len = search_params.get("prefix_len", 0)
        suffix = search_params.get("ends_with", "")
        difficulty = prefix_len + len(suffix)
        est_total = (
            int((58**difficulty) / (total_speed * 1e6)) if total_speed > 0 else 0
        )
        eta = str(timedelta(seconds=est_total))
    else:
        eta = "N/A"

    lines = [
        "",
        f"  [{LIGHT_SAND}]Wallets Generated:[/]  [{PRIMARY_ORANGE}]{format_number(stats.wallets_generated)}[/]",
        f"  [{LIGHT_SAND}]Wallets Found:[/]      [{ACCENT_GOLD}]{stats.wallets_found}/{stats.target_count}[/]",
        f"  [{LIGHT_SAND}]Total Speed:[/]        [{PRIMARY_ORANGE}]{total_speed:.2f} MH/s[/]",
        f"  [{LIGHT_SAND}]Time Elapsed:[/]       [{SAND}]{elapsed}[/]",
        f"  [{LIGHT_SAND}]Est. Completion:[/]    [{SAND}]{eta}[/]",
        "",
    ]

    if search_params.get("starts_with"):
        prefix_label = "Prefix(es)" if "," in search_params["starts_with"] else "Prefix"
        lines.append(
            f"  [{LIGHT_SAND}]\U0001f3af {prefix_label}:[/] [{ACCENT_GOLD}]{search_params['starts_with']}[/]"
        )
    if search_params.get("ends_with"):
        lines.append(
            f"  [{LIGHT_SAND}]\U0001f3af Suffix:[/] [{ACCENT_GOLD}]{search_params['ends_with']}[/]"
        )

    stats_text = "\n".join(lines)

    return Panel(
        Text.from_markup(stats_text),
        title=f"[{ACCENT_GOLD}]SEARCH STATISTICS[/]",
        border_style=BROWN,
    )


def create_found_panel(stats: SearchStats) -> Panel:
    if stats.wallets_found == 0:
        content = f"[dim {SAND}]Searching for matching addresses...[/]"
    else:
        content = f"[{ACCENT_GOLD}]{stats.wallets_found} WALLET(S) DISCOVERED[/]\n\n"
        for addr in stats.found_addresses[-5:]:
            content += f"[{PRIMARY_ORANGE}]\u25b8[/] [{LIGHT_SAND}]{addr}[/]\n"

    return Panel(
        Align.center(Text.from_markup(content)),
        title=f"[{ACCENT_GOLD}]MATCHED WALLETS[/]",
        border_style=ACCENT_GOLD,
    )


def create_controls_panel(paused: bool) -> Panel:
    if paused:
        controls = f"[{ACCENT_GOLD}]\u23f8  PAUSED[/] \u2502 [{SAND}][C]ontinue  [E]xport & Exit  [X]Abort[/]"
    else:
        controls = f"[{PRIMARY_ORANGE}]\u26a1 SEARCHING[/] \u2502 [{SAND}][S]top  [E]xport & Exit  [X]Abort[/]"

    return Panel(
        Align.center(Text.from_markup(controls)),
        style=f"dim {BROWN}",
        border_style=SAND,
    )


def create_layout(
    stats: SearchStats, search_params: dict, gpu_names: list[str]
) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=7),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )

    layout["header"].update(create_header())
    layout["footer"].update(create_controls_panel(stats.paused))

    layout["body"].split_row(
        Layout(name="left", ratio=3),
        Layout(name="right", ratio=2),
    )

    gpu_panel_height = 5 + stats.gpu_count * 2
    layout["left"].split_column(
        Layout(name="gpu", size=gpu_panel_height),
        Layout(name="stats", ratio=1),
    )

    layout["gpu"].update(create_gpu_panel(stats, gpu_names))
    layout["stats"].update(create_stats_panel(stats, search_params))
    layout["right"].update(create_found_panel(stats))

    return layout


def export_wallets(output_dir: str):
    import base58

    keys_path = Path(output_dir)
    wallet_files = list(keys_path.glob("*.json"))

    if not wallet_files:
        console.print(f"\n[{SAND}]No wallets found to export.[/]\n")
        return

    console.print(
        f"\n[{ACCENT_GOLD}]\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550[/]"
    )
    console.print(f"[{ACCENT_GOLD}]             SEARCH COMPLETE             [/]")
    console.print(
        f"[{ACCENT_GOLD}]\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550[/]\n"
    )

    for wallet_file in wallet_files:
        pubkey = wallet_file.stem
        keypair = json.load(open(wallet_file))
        private_key_b58 = base58.b58encode(bytes(keypair[:64])).decode()

        console.print(f"[{PRIMARY_ORANGE}]Public Address:[/] [{LIGHT_SAND}]{pubkey}[/]")
        console.print(f"[{SAND}]Private Key:[/] [{BROWN}]{private_key_b58}[/]")
        console.print(f"[dim {SAND}]JSON File: {wallet_file}[/]\n")

    console.print(
        f"[{ACCENT_GOLD}]\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550[/]\n"
    )


@click.command()
@click.option(
    "--starts-with",
    type=str,
    default=[],
    multiple=True,
    help="Public key prefix (can be specified multiple times)",
)
@click.option("--ends-with", type=str, default="", help="Public key suffix")
@click.option("--count", type=int, default=1, help="Number of wallets to find")
@click.option(
    "--output-dir", type=click.Path(), default="./keys", help="Output directory"
)
@click.option(
    "--iteration-bits", type=int, default=DEFAULT_ITERATION_BITS, help="Iteration bits"
)
@click.option(
    "--is-case-sensitive", type=bool, default=True, help="Case sensitive search"
)
def main(starts_with, ends_with, count, output_dir, iteration_bits, is_case_sensitive):
    if not starts_with and not ends_with:
        console.print(
            f"[{PRIMARY_ORANGE}]Error:[/] Provide at least --starts-with or --ends-with"
        )
        sys.exit(1)

    for prefix in starts_with:
        check_character("starts_with", prefix)
    if ends_with:
        check_character("ends_with", ends_with)

    multiprocessing.set_start_method("spawn", force=True)

    gpu_names = get_gpu_names()
    gpu_counts = len(gpu_names) if gpu_names else len(get_all_gpu_devices())
    if gpu_counts == 0:
        console.print(f"[{PRIMARY_ORANGE}]Error:[/] No GPU devices found.")
        sys.exit(1)

    kernel_source = load_kernel_source(starts_with, ends_with, is_case_sensitive)

    speed_array = multiprocessing.Array(c_double, gpu_counts)
    result_queue = multiprocessing.Queue()
    stop_flag = multiprocessing.Value(c_int, 0)

    stats = SearchStats(gpu_count=gpu_counts, target_count=count)
    starts_with_display = ", ".join(starts_with) if starts_with else ""
    shortest_prefix_len = min((len(p) for p in starts_with), default=0)
    search_params = {
        "starts_with": starts_with_display,
        "ends_with": ends_with,
        "prefix_len": shortest_prefix_len,
    }

    stop_event = threading.Event()
    export_flag = threading.Event()
    export_flag.set()

    processes: list[multiprocessing.Process] = []
    for i in range(gpu_counts):
        p = multiprocessing.Process(
            target=gpu_worker,
            args=(
                i,
                kernel_source,
                iteration_bits,
                gpu_counts,
                speed_array,
                result_queue,
                stop_flag,
            ),
            daemon=True,
        )
        p.start()
        processes.append(p)

    result_t = threading.Thread(
        target=result_monitor_thread,
        args=(result_queue, output_dir, stats, stop_flag, count),
        daemon=True,
    )
    result_t.start()

    kb_t = threading.Thread(
        target=keyboard_thread,
        args=(stats, stop_event, export_flag),
        daemon=True,
    )
    kb_t.start()

    should_export = True
    try:
        with Live(
            create_layout(stats, search_params, gpu_names),
            console=console,
            refresh_per_second=4,
        ) as live:
            while True:
                stats.animation_frame += 1
                stats.sync_from_shared(speed_array)
                live.update(create_layout(stats, search_params, gpu_names))

                if stats.wallets_found >= count:
                    time.sleep(0.5)
                    break

                if stop_event.is_set():
                    should_export = export_flag.is_set()
                    break

                time.sleep(0.25)
    except KeyboardInterrupt:
        pass

    stop_flag.value = 1
    stop_event.set()

    for p in processes:
        p.join(timeout=3)
        if p.is_alive():
            p.terminate()

    console.clear()

    if should_export:
        export_wallets(output_dir)
    else:
        console.print(f"\n[{SAND}]Aborted. No export.[/]\n")


if __name__ == "__main__":
    main()
