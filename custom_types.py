from pydantic import BaseModel, Field
from typing import List, Optional

class K8sObservation(BaseModel):
    """Raw facts observed from the Kubernetes cluster"""
    resource_type: str = Field(description="Type of Kubernetes resource (Pod, Node, Deployment, etc.)")
    name: str = Field(description="Name of the Kubernetes resource")
    namespace: Optional[str] = Field(description="Namespace of the resource, if applicable")
    status: str = Field(description="Current status or phase of the resource")
    details: List[str] = Field(description="Key factual observations (events, conditions, exit codes, etc.)")

class K8sDiagnosis(BaseModel):
    """Root cause analysis based on observations"""
    summary: str = Field(description="Concise explanation of the root cause")
    confidence: float = Field(
        description="Confidence level in the diagnosis (0.0 to 1.0)"
    )


class K8sRecommendation(BaseModel):
    """Suggested remediation steps"""
    action: str = Field(description="Recommended action")
    risk_level: str = Field(
        description="Risk level of the action (low, medium, high)"
    )
    requires_approval: bool = Field(
        description="Whether human approval is required before execution"
    )


class K8sAction(BaseModel):
    """Action taken or proposed by the agent"""
    executed: bool = Field(description="Whether the action was executed")
    description: Optional[str] = Field(description="Description of the action taken")
    reason: Optional[str] = Field(description="Reason if action was not executed")


class K8sAgentResult(BaseModel):
    """Final structured output of the Kubernetes agent"""
    observation: K8sObservation
    diagnosis: K8sDiagnosis
    recommendations: List[K8sRecommendation]
    action: Optional[K8sAction]

