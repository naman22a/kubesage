from pick import pick
from kubernetes import client, config
from kubernetes.client import configuration

config.load_kube_config()

def list_pods_with_logs():
    try:
        #Load Minikube configuration
        config.load_kube_config()

        #Create Kubernetes API client
        v1 = client.CoreV1Api()

        # List pods in all namespaces
        pods = v1.list_pod_for_all_namespaces(watch=False)

        # Print details of each pod and retrieve logs
        for pod in pods.items:
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            pod_ip = pod.status.pod_ip
            node_name = pod.spec.node_name

            print(f"Name: {pod_name}, Namespace: {namespace}, IP: {pod_ip}, Node: {node_name}")

            #Retrieve and print logs for each container in the pod
            for container in pod.spec.containers:
                container_name = container.name
                print(f"Logs for container {container_name}:")
                try:
                    logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, container=container_name, tail_lines=5)
                    print(logs)
                except Exception as e:
                    print(f"Error getting logs for pod {pod_name}, container {container_name}: {e}")

    except Exception as e:
        print(f"Error: {e}")

def pod_config_list():
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    option, _ = pick(contexts, title="Pick the context to load",
                     default_index=active_index)
    # Configs can be set in Configuration class directly or using helper
    # utility
    config.load_kube_config(context=option)

    print(f"Active host is {configuration.Configuration().host}")

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for item in ret.items:
        print(
            "%s\t%s\t%s" %
            (item.status.pod_ip,
             item.metadata.namespace,
             item.metadata.name))

