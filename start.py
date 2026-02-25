#!/usr/bin/env python3

import subprocess
import sys

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

BASE_COLOR = "#D4A574"
ACCENT_COLOR = "#FFD700"
WARN_COLOR = "#FF8C00"


def print_banner():
    banner = f"""
[{ACCENT_COLOR}]╔═══════════════════════════════════════════════════════════════════╗
║                 SOLANA VANITY WALLET GENERATOR                    ║
║                                                                   ║
║            Interactive setup + real-time dashboard                ║
╚═══════════════════════════════════════════════════════════════════╝[/]
    """
    console.print(banner)


def check_wifi():
    console.print(f"\n[{WARN_COLOR}]Security Check[/]\n")

    wifi_off = Confirm.ask(
        f"[{BASE_COLOR}]Have you turned OFF your WiFi?[/]", default=False
    )

    if not wifi_off:
        console.print(
            f"\n[{WARN_COLOR}]Please turn off WiFi first for security.[/]"
        )
        console.print(f"[dim {BASE_COLOR}]Then run this script again.[/]\n")
        sys.exit(0)

    console.print(f"[{ACCENT_COLOR}]Security check passed[/]\n")


def get_search_params():
    console.print(f"[{ACCENT_COLOR}]=== SEARCH PARAMETERS ===[/]\n")

    console.print(f"[{BASE_COLOR}]Enter prefix (what your address should start with)[/]")
    console.print(
        "[dim]Examples: SOL, ABC, DEV - separate multiple with commas: SOL, DEV[/]"
    )
    prefix_raw = Prompt.ask(f"[{WARN_COLOR}]Prefix[/]", default="")
    prefixes = [p.strip() for p in prefix_raw.split(",") if p.strip()] if prefix_raw else []

    console.print(f"\n[{BASE_COLOR}]Enter suffix (what your address should end with)[/]")
    console.print(f"[dim]Examples: XYZ, 420, or press Enter to skip[/]")
    suffix = Prompt.ask(f"[{WARN_COLOR}]Suffix[/]", default="")

    if not prefixes and not suffix:
        console.print(
            f"\n[{WARN_COLOR}]You must provide at least a prefix OR suffix.[/]\n"
        )
        return get_search_params()

    console.print(f"\n[{BASE_COLOR}]How many wallets do you want to find?[/]")
    count = Prompt.ask(f"[{WARN_COLOR}]Count[/]", default="1")

    try:
        count = int(count)
        if count < 1:
            raise ValueError
    except ValueError:
        console.print(f"[{WARN_COLOR}]Invalid number, using 1[/]")
        count = 1

    console.print(f"\n[{BASE_COLOR}]Case-sensitive search?[/]")
    console.print(f"[dim]No = faster (abc = ABC = aBc)[/]")
    console.print(f"[dim]Yes = exact match only[/]")
    case_sensitive = Confirm.ask(f"[{WARN_COLOR}]Case-sensitive[/]", default=False)

    return {
        "prefixes": prefixes,
        "suffix": suffix,
        "count": count,
        "case_sensitive": case_sensitive,
    }


def show_summary(params):
    console.print(f"\n[{ACCENT_COLOR}]=== SEARCH SUMMARY ===[/]\n")

    if params["prefixes"]:
        prefix_display = ", ".join(params["prefixes"])
        console.print(f"[{BASE_COLOR}]Prefix(es):[/] [{ACCENT_COLOR}]{prefix_display}[/]")
    if params["suffix"]:
        console.print(f"[{BASE_COLOR}]Suffix:[/] [{ACCENT_COLOR}]{params['suffix']}[/]")

    console.print(f"[{BASE_COLOR}]Wallets to find:[/] [{ACCENT_COLOR}]{params['count']}[/]")
    console.print(
        f"[{BASE_COLOR}]Case-sensitive:[/] [{ACCENT_COLOR}]{'Yes' if params['case_sensitive'] else 'No'}[/]"
    )

    shortest_prefix = min((len(p) for p in params["prefixes"]), default=0)
    difficulty = shortest_prefix + len(params["suffix"])

    if difficulty <= 3:
        estimate = "~seconds to minutes"
        indicator = "easy"
    elif difficulty == 4:
        estimate = "~minutes"
        indicator = "medium"
    elif difficulty == 5:
        estimate = "~hours"
        indicator = "hard"
    else:
        if params["case_sensitive"]:
            estimate = "~days to weeks"
            indicator = "very hard"
        else:
            estimate = "~hours to days"
            indicator = "hard"

    console.print(
        f"\n[{BASE_COLOR}]Difficulty:[/] [{WARN_COLOR}]{difficulty} characters ({indicator})[/]"
    )
    console.print(f"[{BASE_COLOR}]Estimated time:[/] [{WARN_COLOR}]{estimate}[/]")


def launch_dashboard(params):
    console.print(f"\n[{ACCENT_COLOR}]Launching dashboard...[/]\n")

    cmd = [
        "python3",
        "dashboard.py",
        "--count",
        str(params["count"]),
        "--is-case-sensitive",
        str(params["case_sensitive"]),
    ]

    for prefix in params["prefixes"]:
        cmd.extend(["--starts-with", prefix])
    if params["suffix"]:
        cmd.extend(["--ends-with", params["suffix"]])

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        console.print(f"\n[{BASE_COLOR}]Operation cancelled.[/]\n")
    except Exception as exc:
        console.print(f"\n[{WARN_COLOR}]Error: {exc}[/]\n")


def main():
    console.clear()
    print_banner()

    check_wifi()

    params = get_search_params()

    show_summary(params)

    console.print(f"\n[{ACCENT_COLOR}]=====================================[/]\n")

    ready = Confirm.ask(
        f"[{BASE_COLOR}]Ready to start searching?[/]", default=True
    )

    if not ready:
        console.print(f"\n[{BASE_COLOR}]Operation aborted.[/]\n")
        sys.exit(0)

    launch_dashboard(params)


if __name__ == "__main__":
    main()
