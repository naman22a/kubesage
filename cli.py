import io
from contextlib import redirect_stdout
import time
import json
import subprocess
import shlex
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
import typer

from src.agent import agent
from src.k8s import get_pod_logs
from src.custom_types import K8sAgentResult
from src.fns import build_agent_context, severity_color

console = Console()

app = typer.Typer(help="KubeSage - Kubernetes Debugging Agent")

@app.command()
def analyze(
    pod: str = typer.Option(..., "--pod", "-p", help="Pod name to analyze"),
    namespace: str = typer.Option("default", "--namespace", "-ns", help="Kubernetes namespace"),
):
    run_analysis(pod, namespace)

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

    pod = get_pod_logs(cluster_name='kubesage-demo-cluster', pod_name=pod_name, namespace=namespace)
    if not pod:
        console.print(Panel(f'We could not find a pod named {pod_name}', title="⚠️  Pod Not found", border_style="red"))
        return

    logs_context = build_agent_context(pod)

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
            time.sleep(0.8)
            progress.remove_task(task)
            console.print(f"[bold green]✔[/bold green] {step}")

    console.rule("[bold green]✅ Analysis Complete")
    console.print()

    prompt = f"""
    TASK:
    Determine why the pod is failing and recommend safe remediation.

    CLUSTER LOGS:
    {logs_context}
    """

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        raw_output = agent(prompt)

    data = json.loads(raw_output.message["content"][0]["text"])
    result = K8sAgentResult(**data)
    # result_dict = {
    #     "pod_name": pod_name,
    #     "namespace": namespace,
    #     "overall_status": "CrashLoopBackOff",
    #     "root_cause": {
    #         "summary": "Pod is hitting OOMKilled due to memory limit exceeded.",
    #         "confidence": "HIGH",
    #         "contributing_factors": [
    #             "Container requests 50Mi but args stress 500M memory",
    #             "Memory limit is set too low (100Mi)",
    #             "Single replica causing no redundancy"
    #         ]
    #     },
    #     "evidence": [
    #         {
    #             "source": "pod_status",
    #             "description": "Pod restarted 3 times in last 5 minutes due to OOMKilled."
    #         },
    #         {
    #             "source": "logs",
    #             "description": "Container logs show 'Killed process' messages consistent with OOM."
    #         },
    #         {
    #             "source": "config",
    #             "reference": "Deployment spec",
    #             "description": "Memory limits set too low for container workload."
    #         }
    #     ],
    #     "risk_assessment": "HIGH",
    #     "blast_radius": "Single pod",
    #     "proposed_actions": [
    #         {
    #             "action_type": "WRITE",
    #             "title": "Increase Memory Limit",
    #             "description": "Update the container memory limits and requests to accommodate stress workload.",
    #             "kubectl_command": "kubectl set resources deployment oom-deployment -c memory-hog --limits=memory=600Mi --requests=memory=300Mi",
    #             "requires_confirmation": True,
    #             "risk_level": "MEDIUM",
    #             "expected_outcome": "Pod should run without being OOMKilled.",
    #             "rollback_strategy": "Revert memory limit to previous values if new crashes occur.",
    #             "diff_preview": "resources:\n  limits:\n    memory: '600Mi'\n  requests:\n    memory: '300Mi'"
    #         },
    #         {
    #             "action_type": "WRITE",
    #             "title": "Add Horizontal Pod Autoscaler",
    #             "description": "Deploy an HPA to automatically scale pods based on memory usage.",
    #             "kubectl_command": "kubectl autoscale deployment oom-deployment --cpu-percent=50 --min=1 --max=3",
    #             "requires_confirmation": True,
    #             "risk_level": "LOW",
    #             "expected_outcome": "Deployment scales to handle memory load spikes.",
    #             "rollback_strategy": "Remove HPA if scaling causes issues."
    #         }
    #     ],
    #     "requires_user_confirmation": True,
    #     "summary": "Pod is unstable due to memory limits; recommended to increase memory and consider autoscaling."
    # }
    # result = K8sAgentResult(**result_dict)

    console.print("\n")
    console.rule("[bold cyan]🧠 KUBESAGE DIAGNOSTIC REPORT")

    pod_info = f"""
    [bold]Pod:[/bold] {result.pod_name}
    [bold]Namespace:[/bold] {result.namespace}
    [bold]Status:[/bold] {result.overall_status}
    [bold]Blast Radius:[/bold] {result.blast_radius}
    [bold]Risk Level:[/bold] [{severity_color(result.risk_assessment)}]{result.risk_assessment}[/]
    """

    console.print(Panel(pod_info, title="📦 Pod Information", border_style="cyan"))

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

    table = Table(title="📜 Evidence Collected", box=box.ROUNDED)
    table.add_column("Source", style="cyan")
    table.add_column("Reference", style="yellow")
    table.add_column("Description", style="white")

    for e in result.evidence:
        table.add_row(e.source, e.reference, e.description)

    console.print(table)

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

        print(action.kubectl_command)

        if action.action_type == "WRITE" and action.requires_confirmation:

            console.print("\n⚠  This action will modify cluster state.", style="bold red")

            diff_preview = [x.diff_preview for x in result.proposed_actions if x.action_type == "WRITE"][0]

            console.print(Panel(
                Syntax(diff_preview, "diff", theme="monokai"),
                title="🔍 Diff Preview",
                border_style="yellow"
            ))

            if Confirm.ask("Do you want to apply this change?"):
                console.print("✔ Applying change...", style="bold green")
                if action.action_type == 'WRITE':
                    subprocess.run(shlex.split(action.kubectl_command))
            else:
                console.print("✖ Skipped.", style="bold red")

    console.rule("[bold cyan]📌 Final Summary")
    console.print(result.summary, style="bold")

    if result.requires_user_confirmation:
        console.print("\nUser confirmation required before execution.", style="yellow")

if __name__ == "__main__":
    app()
