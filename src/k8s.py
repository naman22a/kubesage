from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()


def list_pod_with_logs(pod_name, namespace="default", tail_lines=200):
    
    try:
        pods = v1.list_namespaced_pod(namespace)
        pods_list = list(filter(lambda p: p.metadata.name == pod_name, list(pods.items)))

        if len(pods_list) == 0:
            raise Exception('Pod not found')
    
        pod = pods_list[0]

        log = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=tail_lines,
            timestamps=True
        )

        return {
            "pod": pod_name,
            "phase": pod.status.phase,
            "restarts": sum(
                cs.restart_count for cs in (pod.status.container_statuses or [])
            ),
            "logs": log
        }

    except Exception as e:
        if "Pod not found" in str(e):
            return None
        else:
            print('Something went wrong', e)

if __name__ == "__main__":
    print(list_pod_with_logs('crash-pod'))