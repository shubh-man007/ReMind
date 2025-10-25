#    ___      __  ____         __
#   / _ \___ /  |/  (_)__  ___/ /
#  / , _/ -_) /|_/ / / _ \/ _  / 
# /_/|_|\__/_/  /_/_/_//_/\_,_/  


from .state_machine.state_machine import StateMachine
from .llm.llm import get_client
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.syntax import Syntax
from pyfiglet import Figlet
from datetime import datetime
import os
import time
import sys
from io import StringIO
from contextlib import contextmanager


console = Console()

def render_banner(title: str = "ReMind", subtitle: str = "Tiny Research Agent"):
    figlet = Figlet(font="slant", width=200)
    ascii_art = figlet.renderText(title)
    
    panel = Panel.fit(
        f"[bold cyan]{ascii_art}[/bold cyan]\n[bright_magenta]{subtitle}[/bright_magenta]",
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold yellow]WELCOME[/bold yellow]",
        subtitle=f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M')}[/dim]"
    )
    console.print(panel)

def display_query_info(query: str, model_name: str):
    table = Table(title="Research Configuration", 
                  show_header=True, 
                  header_style="bold cyan",
                  border_style="blue")
    
    table.add_column("Parameter", style="bold yellow", width=20)
    table.add_column("Value", style="green", width=80)
    
    table.add_row("Research Query", query)
    table.add_row("Model", model_name)
    table.add_row("Started At", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    console.print(Panel(table, border_style="cyan", padding=(1, 2)))
    console.print()

def display_node_transition(node_name: str, description: str):
    node_styles = {
        "PLANNER": "magenta",
        "RESEARCH_TEAM": "blue",
        "RESEARCH": "cyan",
        "CODE": "yellow",
        "REPORTER": "green",
    }
    
    style = node_styles.get(node_name, "white")
    console.print(Panel(
        f"[{style}]{description}[/{style}]",
        title=f"[bold {style}]>> {node_name}[/bold {style}]",
        border_style=style,
        padding=(0, 2)
    ))

def display_agent_output(output: str, agent_type: str = "AGENT"):
    agent_styles = {
        "PLANNER": ("magenta", "Planning research strategy"),
        "RESEARCHER": ("cyan", "Conducting research"),
        "CODER": ("yellow", "Processing data"),
        "REPORTER": ("green", "Generating report"),
    }
    
    style, description = agent_styles.get(agent_type, ("white", "Processing"))
    
    wrapped_output = Text(output, style="white")
    
    console.print(Panel(
        wrapped_output,
        title=f"[bold {style}]{agent_type} OUTPUT[/bold {style}]",
        subtitle=f"[dim]{description}[/dim]",
        border_style=style,
        padding=(1, 2),
        expand=False
    ))

def display_step_execution(step_title: str, step_type: str, step_description: str):
    type_colors = {
        "research": "cyan",
        "processing": "yellow",
    }
    
    color = type_colors.get(step_type, "white")
    
    table = Table(show_header=False, border_style=color, box=None, padding=(0, 1))
    table.add_column(style="bold white", width=15)
    table.add_column(style=color)
    
    table.add_row("Step Type", step_type.upper())
    table.add_row("Title", step_title)
    table.add_row("Description", step_description)
    
    console.print(Panel(
        table,
        title=f"[bold {color}]EXECUTING STEP[/bold {color}]",
        border_style=color,
        padding=(1, 2)
    ))

def display_plan_details(plan):
    table = Table(title="Research Plan", 
                  show_header=True,
                  header_style="bold magenta",
                  border_style="magenta")
    
    table.add_column("Step #", style="bold yellow", width=8)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Title", style="white", width=30)
    table.add_column("Description", style="dim white", width=50)
    table.add_column("Status", style="green", width=10)
    
    for idx, step in enumerate(plan.steps, 1):
        status = "DONE" if step.execution_res else "PENDING"
        status_style = "green" if step.execution_res else "yellow"
        table.add_row(
            str(idx),
            step.step_type.upper(),
            step.title,
            step.description[:100] + "..." if len(step.description) > 100 else step.description,
            f"[{status_style}]{status}[/{status_style}]"
        )
    
    console.print(Panel(table, border_style="magenta", padding=(1, 2)))
    console.print()

@contextmanager
def capture_agent_output():
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    try:
        yield captured_output
    finally:
        sys.stdout = old_stdout

def display_report(report: str, export: bool = True):
    """Display the final report with styling"""
    console.print()
    console.rule("[bold cyan]Research Report Generated[/bold cyan]")
    console.print()
    
    report_panel = Panel(
        Markdown(report),
        title="[bold green]FINAL REPORT[/bold green]",
        border_style="green",
        padding=(2, 4),
        width=min(console.width, 150)
    )
    console.print(report_panel)
    
    # Export to file if requested
    if export:
        export_report(report)

def export_report(report: str):
    os.makedirs("output_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output_reports/research_report_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(report)
    
    console.print()
    console.print(Panel(
        f"[green]SUCCESS[/green] Report exported to:\n[cyan bold]{filename}[/cyan bold]",
        title="[bold yellow]EXPORT COMPLETE[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))

def display_error(error: Exception):
    error_panel = Panel(
        f"[red bold]Error Type:[/red bold] {type(error).__name__}\n"
        f"[red]Message:[/red] {str(error)}",
        title="[bold red]ERROR OCCURRED[/bold red]",
        border_style="red",
        padding=(1, 2)
    )
    console.print(error_panel)

def display_completion_summary(duration: float):
    console.print()
    console.rule("[bold green]Process Complete[/bold green]")
    console.print()
    
    summary_table = Table(show_header=False, border_style="green", box=None)
    summary_table.add_column(style="bold yellow")
    summary_table.add_column(style="green")
    
    summary_table.add_row("Status", "Completed Successfully")
    summary_table.add_row("Duration", f"{duration:.2f} seconds")
    summary_table.add_row("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    console.print(Panel(summary_table, border_style="green", padding=(1, 2)))

class EnhancedStateMachine(StateMachine):    
    def _planner_action(self):
        display_node_transition("PLANNER", "Analyzing query and creating research plan...")
        result = super()._planner_action()
        
        plan = self.state.get("current_plan")
        if plan:
            display_plan_details(plan)
        
        return result
    
    def _research_team_action(self):
        display_node_transition("RESEARCH_TEAM", "Coordinating research tasks...")
        return super()._research_team_action()
    
    def _research_action(self):
        current_plan = self.state.get("current_plan")
        for step in current_plan.steps:
            if not step.execution_res:
                break
        
        display_step_execution(step.title, step.step_type, step.description)
        
        # Capture the research output
        with capture_agent_output() as captured:
            result = super()._research_action()
            output = captured.getvalue()
        
        if output.strip():
            display_agent_output(output, "RESEARCHER")
        
        return result
    
    def _code_action(self):
        current_plan = self.state.get("current_plan")
        for step in current_plan.steps:
            if not step.execution_res:
                break
        
        display_step_execution(step.title, step.step_type, step.description)
        
        # Capture the code agent output
        with capture_agent_output() as captured:
            result = super()._code_action()
            output = captured.getvalue()
        
        if output.strip():
            display_agent_output(output, "CODER")
        
        return result
    
    def _reporter_action(self):
        display_node_transition("REPORTER", "Compiling final research report...")
        return super()._reporter_action()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReMind - AI Research Agent")
    parser.add_argument("--query", type=str, required=True, help="Research query")
    parser.add_argument("--model_name", type=str, default="gpt-4.1", help="LLM model name")
    parser.add_argument("--no-export", action="store_true", help="Skip exporting report to file")
    args = parser.parse_args()
    
    start_time = time.time()
    
    try:
        render_banner()
        console.print()
        
        display_query_info(args.query, args.model_name)
        
        console.print(Panel(
            "[cyan]Initializing research agent...[/cyan]",
            border_style="cyan"
        ))
        console.print()
        
        state_machine = EnhancedStateMachine(
            human_query=args.query,
            llm_client=get_client(args.model_name),
        )
        
        state_machine.run_until_end()
        
        report = state_machine.state.get("report")
        
        if report:
            display_report(report, export=not args.no_export)
        else:
            console.print("[yellow]WARNING: No report generated[/yellow]")
        
        duration = time.time() - start_time
        display_completion_summary(duration)
        
    except Exception as e:
        display_error(e)
        console.print("\n[dim]Exiting with error...[/dim]")
        exit(1)
    
    console.print()
    console.print("[dim]Thank you for using ReMind[/dim]")
    console.print()