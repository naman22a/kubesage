def build_agent_context(pod_with_logs):
    lines = []
    
    lines.append(
        f"[POD: {pod_with_logs['pod']} | phase={pod_with_logs['phase']} | restarts={pod_with_logs['restarts']}]"
    )

    if pod_with_logs["logs"]:
        for line in pod_with_logs["logs"].splitlines():
            lines.append(line)
    else:
        lines.append("<no logs available>")

    lines.append("")

    return "\n".join(lines)

def severity_color(level: str):
    mapping = {
        "HIGH": "bold red",
        "MEDIUM": "bold yellow",
        "LOW": "bold green"
    }
    return mapping.get(level.upper(), "white")
