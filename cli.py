"""
Interactive Command Line Interface for Indian Telecom Forensics Tool.
Features rich tables, panels, batch parsing, and forensic reporting.
"""

import sys
import json
import csv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

from engine import (
    analyze_single_number,
    parse_cdr_records,
    INDIAN_CIRCLES,
    SPECIAL_NUMBERS,
    STD_CODES
)

console = Console()


def display_banner():
    banner_text = """
 [bold cyan]╔════════════════════════════════════════════════════════════════╗[/bold cyan]
 [bold cyan]║[/bold cyan]   [bold white]INDIAN TELECOM FORENSIC ANALYSIS & TRIAGE TOOLKIT (ITF-KIT)[/bold white]   [bold cyan]║[/bold cyan]
 [bold cyan]║[/bold cyan]   [dim]DoT National Numbering Plan | Telecom Circles | CDR Parser[/dim]   [bold cyan]║[/bold cyan]
 [bold cyan]╚════════════════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner_text)


def print_single_number_report(info: dict):
    """Renders a beautiful forensic report for a single number."""
    if not info.get("is_valid") and not info.get("is_special_service"):
        console.print(Panel(
            f"[bold red]❌ INVALID OR UNALLOCATED NUMBER[/bold red]\n"
            f"[yellow]Input:[/yellow] {info.get('query_input')}\n"
            f"[yellow]Error / Detail:[/yellow] {info.get('investigative_guidance', ['Number does not match Indian telecom allocations'])[0]}",
            title="[bold red]Triage Assessment[/bold red]",
            border_style="red"
        ))
        return

    # Basic Info Table
    t1 = Table(title="Telecom & Identity Metadata", box=box.ROUNDED, expand=True)
    t1.add_column("Property", style="bold cyan", width=25)
    t1.add_column("Forensic Determination", style="bold white")

    t1.add_row("Standard E.164 Format", info.get("e164") or "N/A")
    t1.add_row("National Format", info.get("national") or "N/A")
    t1.add_row("International Format", info.get("international") or "N/A")
    t1.add_row("Line Classification", f"[green]{info.get('line_type')}[/green]")
    t1.add_row("Original Telecom Circle", f"[yellow]{info.get('original_circle')}[/yellow]")
    
    circle_meta = info.get("circle_details", {})
    if circle_meta.get("circle_code") != "UNKNOWN":
        t1.add_row("LSA Code & Category", f"{circle_meta.get('circle_code')} (Category {circle_meta.get('circle_category')})")
        t1.add_row("Circle Regional HQ", str(circle_meta.get("circle_hq")))
        t1.add_row("Circle Region", str(circle_meta.get("circle_region")))

    t1.add_row("Original Operator Series", info.get("original_carrier") or "Unspecified")

    if info.get("std_code_info"):
        std = info["std_code_info"]
        t1.add_row("Landline STD Area Code", f"0{std['std_code']} ({std['location']})")

    t1.add_row("Standard Timezone", ", ".join(info.get("timezones", [])))
    console.print(t1)

    # Investigative Notes Panel
    notes = "\n".join([f"• {n}" for n in info.get("investigative_guidance", [])])
    console.print(Panel(
        f"[bold white]{notes}[/bold white]\n\n"
        f"[dim yellow]Notice on MNP & Privacy:[/dim yellow] [dim]{info.get('carrier_risk_note')}\n"
        f"Subscriber Name (SDR/CAF) and Cell Site Logs (CDR) are protected under the DPDP Act and require a lawful requisition under Section 91 CrPC / Section 94 BNSS to the Telecom Service Provider (TSP).[/dim]",
        title="[bold yellow]Investigative Guidance & Legal Directives[/bold yellow]",
        border_style="yellow"
    ))


def run_single_lookup():
    console.print("\n[bold]Enter Indian Phone Number (e.g. 9810012345, +919810012345, 01123344556, 112):[/bold]")
    num = Prompt.ask("Phone Number")
    if not num.strip():
        return
    with console.status("[bold green]Analyzing Indian Telecom Allocations...[/bold green]"):
        res = analyze_single_number(num)
    print_single_number_report(res)


def run_batch_lookup():
    console.print("\n[bold cyan]Batch Processing Mode[/bold cyan]")
    console.print("Enter phone numbers separated by commas or spaces:")
    raw = Prompt.ask("Numbers")
    if not raw.strip():
        return
    
    # Split by comma or space
    items = [x.strip() for x in raw.replace(",", " ").split() if x.strip()]
    console.print(f"[green]Processing {len(items)} numbers...[/green]\n")

    t = Table(title="Batch Forensic Triage Results", box=box.ROUNDED, expand=True)
    t.add_column("#", style="dim", width=4)
    t.add_column("Input Number", style="bold white")
    t.add_column("E.164 Format", style="cyan")
    t.add_column("Type", style="green")
    t.add_column("Telecom Circle", style="yellow")
    t.add_column("Original Operator", style="magenta")
    t.add_column("Validity", style="bold")

    results = []
    for idx, num in enumerate(items, start=1):
        info = analyze_single_number(num)
        results.append(info)
        is_val = "[green]VALID[/green]" if info.get("is_valid") else "[red]INVALID[/red]"
        t.add_row(
            str(idx),
            num,
            info.get("e164") or "N/A",
            info.get("line_type", "Unknown"),
            info.get("original_circle", "N/A"),
            info.get("original_carrier", "N/A"),
            is_val
        )

    console.print(t)
    
    # Option to export
    save = Prompt.ask("\nExport this batch report to JSON? (y/N)", default="n")
    if save.lower() == "y":
        out_file = "batch_forensic_report.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        console.print(f"[bold green]✔ Report successfully saved to {out_file}[/bold green]")


def run_cdr_sample_analysis():
    console.print("\n[bold cyan]Call Detail Record (CDR) Forensic Module[/bold cyan]")
    console.print("Demonstrating analysis of Call Detail Records (CDR) with Cell Site identifiers.")
    
    # Sample CDR dataset representing typical Indian CDR format
    sample_cdrs = [
        {"timestamp": "2026-10-19 10:15:22", "caller": "9810012345", "callee": "9820098765", "call_type": "OUTGOING", "duration": 182, "lac": "40410", "cell_id": "14201"},
        {"timestamp": "2026-10-19 10:25:40", "caller": "9810012345", "callee": "9820098765", "call_type": "OUTGOING", "duration": 45, "lac": "40410", "cell_id": "14201"},
        {"timestamp": "2026-10-19 11:02:11", "caller": "9871122334", "callee": "9810012345", "call_type": "INCOMING", "duration": 340, "lac": "40410", "cell_id": "14202"},
        {"timestamp": "2026-10-19 12:45:00", "caller": "9810012345", "callee": "9830055443", "call_type": "SMS", "duration": 0, "lac": "40410", "cell_id": "14305"},
        {"timestamp": "2026-10-19 14:10:18", "caller": "9810012345", "callee": "9820098765", "call_type": "OUTGOING", "duration": 520, "lac": "40410", "cell_id": "14550"},
        {"timestamp": "2026-10-19 15:30:25", "caller": "9999887766", "callee": "9810012345", "call_type": "INCOMING", "duration": 60, "lac": "40410", "cell_id": "14550"},
    ]

    summary = parse_cdr_records(sample_cdrs)
    
    t1 = Table(title="CDR Volume & Duration Summary", box=box.ROUNDED)
    t1.add_column("Metric", style="bold cyan")
    t1.add_column("Value", style="bold white")
    t1.add_row("Total CDR Records Parsed", str(summary["total_records"]))
    t1.add_row("Total Call Duration", f"{summary['total_duration_seconds']} sec ({summary['total_duration_minutes']} mins)")
    t1.add_row("Outgoing Calls", str(summary["call_type_breakdown"]["OUTGOING"]))
    t1.add_row("Incoming Calls", str(summary["call_type_breakdown"]["INCOMING"]))
    t1.add_row("SMS / Data Records", str(summary["call_type_breakdown"]["SMS"]))
    console.print(t1)

    # Top Entities
    t2 = Table(title="Top Cell Tower Sites Visited", box=box.ROUNDED)
    t2.add_column("Cell Site / Tower ID", style="yellow")
    t2.add_column("Hit Frequency", style="bold green")
    for tower, count in summary["top_towers"]:
        t2.add_row(tower, str(count))
    console.print(t2)

    console.print(Panel(
        "[bold green]✔ CDR parsing complete.[/bold green]\n"
        "To correlate Cell IDs with physical GPS coordinates, request the official 'Cell Site Master Sheet' from the respective telecom operator.",
        title="Forensic Findings"
    ))


def display_reference_directory():
    """Displays official 22 Telecom Circles and Emergency shortcodes."""
    console.print("\n[bold cyan]Official 22 Indian Telecom Circles (LSAs)[/bold cyan]")
    t = Table(box=box.SIMPLE_HEAVY)
    t.add_column("Code", style="bold yellow", width=6)
    t.add_column("Service Area / Circle", style="bold white")
    t.add_column("Category", style="cyan", width=10)
    t.add_column("Region", style="magenta", width=12)
    t.add_column("Circle HQ", style="green")

    for code, d in sorted(INDIAN_CIRCLES.items()):
        t.add_row(code, d["name"], d["category"], d["region"], d["hq"])
    console.print(t)

    console.print("\n[bold cyan]Indian Emergency & Statutory Helplines[/bold cyan]")
    t2 = Table(box=box.SIMPLE_HEAVY)
    t2.add_column("Shortcode", style="bold yellow", width=12)
    t2.add_column("Agency / Designated Service", style="bold white")
    for code, name in sorted(SPECIAL_NUMBERS.items()):
        t2.add_row(code, name)
    console.print(t2)


def main():
    while True:
        display_banner()
        console.print("[bold]Forensic Investigation Options:[/bold]")
        console.print("  [1] Single Number Deep Triage (Circle, Operator Series, STD)")
        console.print("  [2] Batch Numbers Processing (Multiple numbers)")
        console.print("  [3] Call Detail Record (CDR) & Cell Tower Analyzer")
        console.print("  [4] View Official 22 Telecom Circles & Statutory Shortcodes")
        console.print("  [5] Launch Interactive Local Web GUI")
        console.print("  [0] Exit")

        choice = Prompt.ask("\nSelect Option", choices=["1", "2", "3", "4", "5", "0"], default="1")

        if choice == "1":
            run_single_lookup()
        elif choice == "2":
            run_batch_lookup()
        elif choice == "3":
            run_cdr_sample_analysis()
        elif choice == "4":
            display_reference_directory()
        elif choice == "5":
            console.print("[bold green]Starting Web GUI on http://127.0.0.1:8899 ...[/bold green]")
            import subprocess
            subprocess.Popen([sys.executable, "web_app.py"], cwd=sys.path[0])
            console.print("[cyan]Web GUI launched in background. Opening browser...[/cyan]")
            import webbrowser
            webbrowser.open("http://127.0.0.1:8899")
        elif choice == "0":
            console.print("[dim]Exiting ITF-KIT. Goodbye.[/dim]")
            break

        console.print("\n" + "─" * 60 + "\n")


if __name__ == "__main__":
    main()
