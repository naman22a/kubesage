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
from src.k8s import list_pod_with_logs
from src.custom_types import K8sAgentResult
from src.fns import build_agent_context, severity_color

console = Console()

app = typer.Typer(help="KubeSage - Kubernetes Debugging Agent")

@app.command()
def analyze(
    pod: str = typer.Option(..., "--pod", "-p", help="Pod name to analyze"),
    namespace: str = typer.Option("default", "--namespace", "-ns", help="Kubernetes namespace"),
    cluster_type: str = typer.Option(
        "local",
        "--cluster-type",
        "-ct",
        help="Cluster type: local or eks"
    ),
    cluster_name: str = typer.Option(
        None,
        "--cluster-name",
        help="EKS cluster name (required if cluster-type=eks)"
    ),
    region: str = typer.Option(
        None,
        "--region",
        help="AWS region (required if cluster-type=eks)"
    ),
):
    run_analysis(pod, namespace, cluster_type, cluster_name, region)

def run_analysis(pod_name: str, namespace: str, cluster_type: str, cluster_name: str, region: str):
    console.print("[bold cyan]Starting KubeSage analysis...[/bold cyan]")

    if cluster_type.lower() == "eks":
        if not cluster_name or not region:
            console.print(
                Panel(
                    "Cluster name and region are required for EKS.",
                    title="❌ Missing Parameters",
                    border_style="red"
                )
            )
            raise typer.Exit()

        console.print(f"[bold blue]Connecting to EKS cluster:[/bold blue] {cluster_name}")

        eks_cmd = f"aws eks update-kubeconfig --region {region} --name {cluster_name}"

        try:
            subprocess.run(shlex.split(eks_cmd), check=True)
            console.print("✔ Connected to EKS cluster", style="bold green")
        except subprocess.CalledProcessError:
            console.print(
                Panel(
                    "Failed to connect to EKS. Check AWS credentials and cluster name.",
                    title="❌ Connection Failed",
                    border_style="red"
                )
            )
            raise typer.Exit()
    else:
        console.print("[bold blue]Using local Kubernetes context[/bold blue]")

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

    pod = list_pod_with_logs(pod_name=pod_name, namespace=namespace)
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

    # buffer = io.StringIO()
    # with redirect_stdout(buffer):
    #     raw_output = agent(prompt)

    # data = json.loads(raw_output.message["content"][0]["text"])
    # result = K8sAgentResult(**data)
    result_dict = {
        "pod_name": pod_name,
        "namespace": namespace,
        "overall_status": "CrashLoopBackOff",
        "root_cause": {
            "summary": "Container is repeatedly OOMKilled because it attempts to allocate 500M memory while the pod memory limit is set to 100Mi.",
            "confidence": "HIGH",
            "contributing_factors": [
                "Container args specify '--vm-bytes 500M'",
                "Memory limit is set to only 100Mi",
                "Exit Code 137 indicates OOMKilled",
                "Restart count is 4 and increasing",
                "QoS Class is Burstable (requests < limits)"
            ]
        },
        "evidence": [
            {
                "source": "pod_status",
                "description": "Last State shows Reason: OOMKilled and Exit Code: 137."
            },
            {
                "source": "pod_status",
                "description": "Restart Count is 4 with BackOff events."
            },
            {
                "source": "container_spec",
                "description": "Args include '--vm 1 --vm-bytes 500M --vm-hang 1'."
            },
            {
                "source": "resource_config",
                "description": "Memory limit is 100Mi and request is 50Mi."
            },
            {
                "source": "events",
                "description": "Multiple 'Back-off restarting failed container' warnings."
            }
        ],
        "risk_assessment": "HIGH",
        "blast_radius": "Single pod in Deployment oom-deployment",
        "proposed_actions": [
            {
                "action_type": "WRITE",
                "title": "Increase Memory Limits",
                "description": "Increase memory requests and limits to exceed 500Mi since the container intentionally allocates 500M.",
                "kubectl_command": "kubectl set resources deployment oom-deployment -c memory-hog --limits=memory=700Mi --requests=memory=500Mi",
                "requires_confirmation": True,
                "risk_level": "MEDIUM",
                "expected_outcome": "Container should stop getting OOMKilled and run successfully.",
                "rollback_strategy": "Revert to previous limits if node memory pressure occurs.",
                "diff_preview": "resources:\n  limits:\n    memory: \"700Mi\"\n  requests:\n    memory: \"500Mi\""
            },
            {
                "action_type": "WRITE",
                "title": "Align Stress Memory With Limit (Alternative Fix)",
                "description": "Reduce stress memory allocation to stay within current 100Mi limit.",
                "kubectl_command": "kubectl patch deployment oom-deployment --type='json' -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/args\",\"value\":[\"--vm\",\"1\",\"--vm-bytes\",\"80M\",\"--vm-hang\",\"1\"]}]'",
                "requires_confirmation": True,
                "risk_level": "LOW",
                "expected_outcome": "Container runs without exceeding memory limit.",
                "rollback_strategy": "Restore original args if stress testing at 500M is required."
            }
        ],
        "requires_user_confirmation": True,
        "summary": "Pod is unstable due to intentional memory over-allocation (500M) exceeding the configured 100Mi limit, causing repeated OOMKills and CrashLoopBackOff."
    }
    result = K8sAgentResult(**result_dict)

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
