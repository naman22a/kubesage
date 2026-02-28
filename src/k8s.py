from kubernetes import client, config
import os
import dotenv
import boto3
import json
from datetime import datetime, timedelta

dotenv.load_dotenv()
config.load_kube_config()

def get_pod_logs(cluster_name: str, pod_name: str, namespace: str = 'default'):
    cloudwatch = boto3.client("cloudwatch", region_name=os.environ['REGION'])
    client = boto3.client("logs", region_name=os.environ['REGION'])

    # Get Restart Count
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=15)

    metrics_response = cloudwatch.get_metric_statistics(
        Namespace="ContainerInsights",
        MetricName="pod_number_of_container_restarts",
        Dimensions=[
            {"Name": "ClusterName", "Value": cluster_name},
            {"Name": "PodName", "Value": pod_name},
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Maximum"],
    )

    datapoints = metrics_response.get("Datapoints", [])
    restarts = 0

    if datapoints:
        latest = max(datapoints, key=lambda x: x["Timestamp"])
        restarts = int(latest["Maximum"])

    # Get logs
    log_group = f"/aws/containerinsights/{cluster_name}/application"

    paginator = client.get_paginator("describe_log_streams")

    matching_streams = []

    for page in paginator.paginate(
        logGroupName=log_group,
        orderBy="LastEventTime",
        descending=True
    ):
        for stream in page["logStreams"]:
            stream_name = stream["logStreamName"]

            if pod_name in stream_name and f"_{namespace}_" in stream_name:
                matching_streams.append(stream_name)

    if not matching_streams:
        raise Exception(f"No log streams found for {namespace}/{pod_name}")

    logs = []

    for log_stream in matching_streams:
        next_token = None

        while True:
            kwargs = {
                "logGroupName": log_group,
                "logStreamName": log_stream,
                "startFromHead": True
            }

            if next_token:
                kwargs["nextToken"] = next_token

            response = client.get_log_events(**kwargs)

            for event in response["events"]:
                message = event["message"]

                try:
                    parsed = json.loads(message)
                    logs.append(parsed.get("log", "").strip())
                except json.JSONDecodeError:
                    logs.append(message)

            if next_token == response["nextForwardToken"]:
                break

            next_token = response["nextForwardToken"]

    return { 
        "pod": pod_name,
        "restarts": restarts,
        "logs": "\n".join(logs),
    }

v1 = client.CoreV1Api()

def list_pod_with_logs_old(pod_name, namespace="default", tail_lines=200):
    
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
    # print(list_pod_with_logs_old('oom-deployment'))
    print(get_pod_logs('kubesage-demo-cluster','oom-deployment-5c5f9dd698-k8pkh'))
