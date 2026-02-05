from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()


def list_pods_with_logs(namespace="default", tail_lines=200):
    pods = v1.list_namespaced_pod(namespace)
    result = []

    for pod in pods.items:
        pod_name = pod.metadata.name

        try:
            log = v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail_lines,
                timestamps=True
            )
        except Exception as e:
            log = f"ERROR fetching logs: {e}"

        result.append({
            "pod": pod_name,
            "phase": pod.status.phase,
            "restarts": sum(
                cs.restart_count for cs in (pod.status.container_statuses or [])
            ),
            "logs": log
        })

    return result

if __name__ == "__main__":
    list_pods_with_logs()