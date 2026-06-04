import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from rich import box
from rich.console import Console
from rich.rule import Rule
from rich.table import Table

console = Console()


def load_results(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        return json.load(f)


def calc_z_score(current_mean, base_mean, base_stddev):
    """
    Z-Score indicates how many standard deviations
    away current run is from baseline
    """
    if base_stddev == 0:
        return 0 if current_mean == base_mean else 100.0
    return (current_mean - base_mean) / base_stddev


def compare_benchmarks(
    baseline: Dict[str, Any], current: Dict[str, Any], threshold_pct: float = 10.0
) -> bool:
    """
    Uses Mean for % change and Z-score for noise detection.
    Returns True if regressions were detected.
    """
    baseline_map = {b["name"]: b for b in baseline["benchmarks"]}
    current_map = {b["name"]: b for b in current["benchmarks"]}

    table = Table(
        title="[bold]Benchmark Comparison[/bold]",
        box=box.SIMPLE_HEAD,
        show_edge=False,
        padding=(0, 1),
    )
    table.add_column("Benchmark", style="cyan", no_wrap=False, max_width=60)
    table.add_column("Change %", justify="right")
    table.add_column("Sigma (Z)", justify="right")
    table.add_column("Status")

    regressions: List[str] = []

    for name, curr in current_map.items():
        base = baseline_map.get(name)
        if not base:
            table.add_row(name, "—", "—", "[dim]NEW[/dim]")
            continue

        m1 = base["stats"]["mean"]
        s1 = base["stats"]["stddev"]
        m2 = curr["stats"]["mean"]

        delta_pct = 0.0 if m1 == 0 else ((m2 - m1) / m1) * 100
        z_score = calc_z_score(m2, m1, s1)

        if delta_pct > threshold_pct and abs(z_score) > 2.0:
            status = "[bold red]REGRESSION[/bold red]"
            regressions.append(name)
        elif delta_pct > threshold_pct:
            status = "[yellow]NOISE[/yellow]"
        elif delta_pct < -threshold_pct and abs(z_score) > 2.0:
            status = "[bold green]IMPROVED[/bold green]"
        else:
            status = "[green]OK[/green]"

        change_str = f"{delta_pct:+.2f}%"
        z_str = f"{z_score:.2f}"
        table.add_row(name, change_str, z_str, status)

    console.print(table)

    if regressions:
        console.print(Rule(style="red"))
        console.print(
            f"[bold red]FAILURE:[/bold red] Performance regression detected "
            f"in [cyan]{len(regressions)}[/cyan] test(s)."
        )
        return True

    console.print(Rule(style="green"))
    console.print("[bold green]SUCCESS:[/bold green] No significant regressions.")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", help="Gold standard JSON")
    parser.add_argument("current", help="New run JSON")
    parser.add_argument(
        "--threshold", type=float, default=10.0, help="FAIL if slower by %%"
    )
    args = parser.parse_args()

    try:
        failed = compare_benchmarks(
            load_results(args.baseline), load_results(args.current), args.threshold
        )
        sys.exit(1 if failed else 0)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] loading files: {e}")
        sys.exit(0)
