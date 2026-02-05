def build_agent_context(pods_with_logs):
    lines = []

    for pod in pods_with_logs:
        lines.append(
            f"[POD: {pod['pod']} | phase={pod['phase']} | restarts={pod['restarts']}]"
        )

        if pod["logs"]:
            for line in pod["logs"].splitlines():
                lines.append(line)
        else:
            lines.append("<no logs available>")

        lines.append("")

    return "\n".join(lines)
