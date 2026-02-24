import io
from contextlib import redirect_stdout
from pprint import pprint
import argparse
import os
import time
import dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
import typer

from strands import Agent
from strands.models.ollama import OllamaModel

from k8s import list_pod_with_logs
from constants import system_prompt
from custom_types import K8sAgentResult
from fns import build_agent_context, severity_color

dotenv.load_dotenv()

console = Console()


app = typer.Typer(help="KubeSage - Kubernetes Debugging Agent")

@app.command()
def analyze(
    pod: str = typer.Option(..., "--pod", "-p", help="Pod name to analyze"),
    namespace: str = typer.Option("default", "--namespace", "-ns", help="Kubernetes namespace"),
):
    run_analysis(pod, namespace)

ollama_model = OllamaModel(
  host="http://localhost:11434",
  model_id=os.environ['MODEL_ID']
)

agent = Agent(
  model=ollama_model,
  system_prompt=system_prompt
)

def run_analysis(pod_name: str, namespace: str):
    console.print("[bold cyan]Starting KubeSage analysis...[/bold cyan]")
    namespace = namespace if namespace else 'default'


    header = Text()
    header.append("KubeSage\n", style="bold cyan")
    header.append("AI-Powered Kubernetes Debugging Assistant", style="white")
    console.print(
        Panel(
            header,
            box=box.ROUNDED,
            padding=(1, 4),
            border_style="cyan"
        )
    )
    console.print()

    

    # pod = list_pod_with_logs(pod_name=pod_name, namespace=namespace)
    # logs_context = build_agent_context(pod)

    console.print(f"[bold]Pod:[/bold] {pod_name}")
    console.print(f"[bold]Namespace:[/bold] {namespace}")
    console.print()

    console.rule("[bold blue]🚀 Initializing Debug Session")

    steps = [
        "Fetching last 200 log lines...",
        "Building diagnostic context...",
        "Running analysis with LLM...",
        "Structuring findings..."
    ]

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:

        for step in steps:
            task = progress.add_task(f"[yellow]{step}", total=None)
            time.sleep(0.8)  # simulate work
            progress.remove_task(task)
            console.print(f"[bold green]✔[/bold green] {step}")

    console.rule("[bold green]✅ Analysis Complete")
    console.print()

    # prompt = f"""
    # TASK:
    # Determine why the pod is failing and recommend safe remediation.

    # CLUSTER LOGS:
    # {logs_context}
    # """

    # print("[✔] Running analysis with LLM...")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        pass
        # result = agent(prompt, 
        #                structured_output_model=K8sAgentResult)
    # print("[✔] Completed analysis with LLM...")

    # result: K8sAgentResult = result.structured_output
    result_dict = {
      "pod_name": "api-server-7f9c8d6b9c-2xkqj",
      "namespace": "default",
      "overall_status": "CrashLoopBackOff",
      "root_cause": {
        "summary": "Application container is crashing due to missing environment variable DATABASE_URL.",
        "confidence": "HIGH",
        "contributing_factors": [
          "DATABASE_URL not defined in pod environment",
          "Recent config change removed secret reference",
          "Application does not handle missing config gracefully"
        ]
      },
      "evidence": [
        {
          "source": "logs",
          "reference": "kubectl logs api-server-7f9c8d6b9c-2xkqj",
          "description": "Error: DATABASE_URL is not set. Application exiting."
        },
        {
          "source": "pod_status",
          "reference": "kubectl describe pod api-server-7f9c8d6b9c-2xkqj",
          "description": "Pod is in CrashLoopBackOff state with 5 restarts in the last 10 minutes."
        },
        {
          "source": "config",
          "reference": "deployment/api-server",
          "description": "Environment variable DATABASE_URL is missing from container spec."
        }
      ],
      "risk_assessment": "MEDIUM",
      "blast_radius": "Deployment",
      "proposed_actions": [
        {
          "action_type": "READ",
          "title": "Verify environment variables in deployment",
          "description": "Inspect the deployment spec to confirm missing DATABASE_URL configuration.",
          "kubectl_command": "kubectl get deployment api-server -o yaml",
          "requires_confirmation": False,
          "risk_level": "LOW",
          "expected_outcome": "Confirmation that DATABASE_URL is absent or misconfigured.",
          "rollback_strategy": None
        },
        {
          "action_type": "WRITE",
          "title": "Restore DATABASE_URL environment variable",
          "description": "Patch the deployment to include DATABASE_URL from the correct secret.",
          "kubectl_command": "kubectl set env deployment/api-server DATABASE_URL=<from-secret>",
          "requires_confirmation": True,
          "risk_level": "MEDIUM",
          "expected_outcome": "Pod restarts successfully and enters Running state.",
          "rollback_strategy": "kubectl rollout undo deployment/api-server",
          "diff_preview": "--- deployment/api-server\n+++ deployment/api-server\n@@\n- DATABASE_URL: <missing>\n+ DATABASE_URL: <value>"
        }
      ],
      "requires_user_confirmation": True,
      "summary": "The pod is repeatedly crashing because a required environment variable (DATABASE_URL) is missing. Restoring the configuration should resolve the issue."
    }

    result = K8sAgentResult(**result_dict)

    console.print("\n")
    console.rule("[bold cyan]🧠 KUBESAGE DIAGNOSTIC REPORT")

    # ─── Pod Info Panel ──────────────────────────────────────────
    pod_info = f"""
    [bold]Pod:[/bold] {result.pod_name}
    [bold]Namespace:[/bold] {result.namespace}
    [bold]Status:[/bold] {result.overall_status}
    [bold]Blast Radius:[/bold] {result.blast_radius}
    [bold]Risk Level:[/bold] [{severity_color(result.risk_assessment)}]{result.risk_assessment}[/]
    """

    console.print(Panel(pod_info, title="📦 Pod Information", border_style="cyan"))

    # ─── Root Cause ──────────────────────────────────────────────
    root_cause_text = Text()
    root_cause_text.append("Summary:\n", style="bold")
    root_cause_text.append(result.root_cause.summary + "\n\n")

    root_cause_text.append(
        f"Confidence: {result.root_cause.confidence}\n",
        style=severity_color(result.root_cause.confidence)
    )

    root_cause_text.append("\nContributing Factors:\n", style="bold")
    for factor in result.root_cause.contributing_factors:
        root_cause_text.append(f" • {factor}\n")

    console.print(Panel(root_cause_text, title="🔎 Root Cause Analysis", border_style="magenta"))

    # ─── Evidence Table ──────────────────────────────────────────
    table = Table(title="📜 Evidence Collected", box=box.ROUNDED)
    table.add_column("Source", style="cyan")
    table.add_column("Reference", style="yellow")
    table.add_column("Description", style="white")

    for e in result.evidence:
        table.add_row(e.source, e.reference, e.description)

    console.print(table)

    # ─── Proposed Actions ────────────────────────────────────────
    console.rule("[bold green]🛠 Proposed Actions")

    for idx, action in enumerate(result.proposed_actions, start=1):
        risk_style = severity_color(action.risk_level)

        action_panel = f"""
    [bold]Type:[/bold] {action.action_type}
    [bold]Risk:[/bold] [{risk_style}]{action.risk_level}[/]
    [bold]Title:[/bold] {action.title}
    [bold]Description:[/bold] {action.description}
    [bold]Expected Outcome:[/bold] {action.expected_outcome}
    [bold]Rollback Strategy:[/bold] {action.rollback_strategy or "N/A"}
    """

        console.print(Panel(action_panel, title=f"Action {idx}", border_style="green"))

        # Show command as syntax-highlighted block
        syntax = Syntax(action.kubectl_command, "bash", theme="monokai", line_numbers=False)
        console.print(syntax)

        # ─── Interactive Confirmation for WRITE ──────────────────
        if action.action_type == "WRITE" and action.requires_confirmation:

            console.print("\n⚠  This action will modify cluster state.", style="bold red")

            # Fake diff preview (for now static example)
            diff_preview = [x.diff_preview for x in result.proposed_actions if x.action_type == "WRITE"][0]

            console.print(Panel(
                Syntax(diff_preview, "diff", theme="monokai"),
                title="🔍 Diff Preview",
                border_style="yellow"
            ))

            if Confirm.ask("Do you want to apply this change?"):
                console.print("✔ Applying change...", style="bold green")
                # Here you would actually run the kubectl command
            else:
                console.print("✖ Skipped.", style="bold red")

    # ─── Final Summary ───────────────────────────────────────────
    console.rule("[bold cyan]📌 Final Summary")
    console.print(result.summary, style="bold")

    if result.requires_user_confirmation:
        console.print("\nUser confirmation required before execution.", style="yellow")

if __name__ == "__main__":
    app()
