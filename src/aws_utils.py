import boto3
import json
from datetime import datetime

sns_client = boto3.client("sns")

def send_risk_alert_sns(topic_arn: str, result):
    """
    Sends an SNS alert if risk is HIGH or MEDIUM.
    """

    risk = result.risk_assessment.upper()

    if risk not in ["HIGH", "MEDIUM"]:
        return

    message = {
        "pod": result.pod_name,
        "namespace": result.namespace,
        "status": result.overall_status,
        "risk": result.risk_assessment,
        "summary": result.summary,
        "root_cause": result.root_cause.summary,
        "blast_radius": result.blast_radius,
    }

    sns_client.publish(
        TopicArn=topic_arn,
        Subject=f"KubeSage Alert - {risk} Risk Detected",
        Message=json.dumps(message, indent=2),
    )

dynamodb = boto3.resource("dynamodb")

def store_analysis_result(table_name: str, result):
    """
    Stores analysis result in DynamoDB.
    """

    table = dynamodb.Table(table_name)

    item = {
        "pod_name": result.pod_name,
        "timestamp": datetime.utcnow().isoformat(),
        "namespace": result.namespace,
        "status": result.overall_status,
        "risk": result.risk_assessment,
        "summary": result.summary,
        "blast_radius": result.blast_radius,
        "analysis_json": json.loads(result.model_dump_json()),
    }

    table.put_item(Item=item)
