#!/usr/bin/env python3

import os
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

SAND = "#D4A574"
SPICE_GOLD = "#FFD700"
DESERT_ORANGE = "#FF8C00"


def print_banner():
    banner = f"""
[{SPICE_GOLD}]╔═══════════════════════════════════════════════════════════════════╗
║                    ⚡ WATER WALLET FORGE ⚡                       ║
║                                                                   ║
║        [dim]"He who controls the keys, controls the universe"[/dim]        ║
╚═══════════════════════════════════════════════════════════════════╝[/]
    """
    console.print(banner)


def check_wifi():
    console.print(f"\n[{DESERT_ORANGE}]⚠️  SECURITY CHECK[/]\n")

    wifi_off = Confirm.ask(f"[{SAND}]Have you turned OFF your WiFi?[/]", default=False)

    if not wifi_off:
        console.print(
            f"\n[{DESERT_ORANGE}]⚠️  Please turn off WiFi first for security![/]"
        )
        console.print(f"[dim {SAND}]Then run this script again.[/]\n")
        sys.exit(0)

    console.print(f"[{SPICE_GOLD}]✓ Security check passed[/]\n")


def get_search_params():
    console.print(f"[{SPICE_GOLD}]═══ SEARCH PARAMETERS ═══[/]\n")

    console.print(f"[{SAND}]Enter prefix (what your address should start with)[/]")
    console.print(
        f"[dim]Examples: WATER, Sol, DUNE — separate multiple with commas: Water, Dune, Sol[/]"
    )
    prefix_raw = Prompt.ask(f"[{DESERT_ORANGE}]Prefix[/]", default="")
    prefixes = [p.strip() for p in prefix_raw.split(",") if p.strip()] if prefix_raw else []

    console.print(f"\n[{SAND}]Enter suffix (what your address should end with)[/]")
    console.print(f"[dim]Examples: RICH, 420, or just press Enter to skip[/]")
    suffix = Prompt.ask(f"[{DESERT_ORANGE}]Suffix[/]", default="")

    if not prefixes and not suffix:
        console.print(
            f"\n[{DESERT_ORANGE}]⚠️  You must provide at least a prefix OR suffix![/]\n"
        )
        return get_search_params()

    console.print(f"\n[{SAND}]How many wallets do you want to find?[/]")
    count = Prompt.ask(f"[{DESERT_ORANGE}]Count[/]", default="1")

    try:
        count = int(count)
        if count < 1:
            raise ValueError
    except:
        console.print(f"[{DESERT_ORANGE}]Invalid number, using 1[/]")
        count = 1

    console.print(f"\n[{SAND}]Case-sensitive search?[/]")
    console.print(f"[dim]No = Much faster (water = WATER = WaTeR)[/]")
    console.print(f"[dim]Yes = Exact match only[/]")
    case_sensitive = Confirm.ask(f"[{DESERT_ORANGE}]Case-sensitive[/]", default=False)

    return {
        "prefixes": prefixes,
        "suffix": suffix,
        "count": count,
        "case_sensitive": case_sensitive,
    }


def show_summary(params):
    console.print(f"\n[{SPICE_GOLD}]═══ MISSION SUMMARY ═══[/]\n")

    if params["prefixes"]:
        prefix_display = ", ".join(params["prefixes"])
        console.print(f"[{SAND}]Prefix(es):[/] [{SPICE_GOLD}]{prefix_display}[/]")
    if params["suffix"]:
        console.print(f"[{SAND}]Suffix:[/] [{SPICE_GOLD}]{params['suffix']}[/]")

    console.print(f"[{SAND}]Wallets to find:[/] [{SPICE_GOLD}]{params['count']}[/]")
    console.print(
        f"[{SAND}]Case-sensitive:[/] [{SPICE_GOLD}]{'Yes' if params['case_sensitive'] else 'No'}[/]"
    )

    shortest_prefix = min((len(p) for p in params["prefixes"]), default=0)
    difficulty = shortest_prefix + len(params["suffix"])

    if difficulty <= 3:
        estimate = "~seconds to minutes"
        emoji = "🟢"
    elif difficulty == 4:
        estimate = "~minutes"
        emoji = "🟡"
    elif difficulty == 5:
        estimate = "~hours"
        emoji = "🟠"
    else:
        if params["case_sensitive"]:
            estimate = "~days to weeks"
            emoji = "🔴"
        else:
            estimate = "~hours to days"
            emoji = "🟠"

    console.print(
        f"\n[{SAND}]Difficulty:[/] [{DESERT_ORANGE}]{difficulty} characters {emoji}[/]"
    )
    console.print(f"[{SAND}]Estimated time:[/] [{DESERT_ORANGE}]{estimate}[/]")


def launch_dashboard(params):
    console.print(f"\n[{SPICE_GOLD}]🚀 Launching dashboard...[/]\n")

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
        console.print(f"\n[{SAND}]Operation cancelled.[/]\n")
    except Exception as e:
        console.print(f"\n[{DESERT_ORANGE}]Error: {e}[/]\n")


def main():
    console.clear()
    print_banner()

    check_wifi()

    params = get_search_params()

    show_summary(params)

    console.print(f"\n[{SPICE_GOLD}]═══════════════════════════════════════[/]\n")

    ready = Confirm.ask(f"[{SAND}]Ready to start the spice harvest?[/]", default=True)

    if not ready:
        console.print(f"\n[{SAND}]Mission aborted. The desert awaits.[/]\n")
        sys.exit(0)

    launch_dashboard(params)


if __name__ == "__main__":
    main()
