from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Evidence(BaseModel):
    source: str  # logs | events | pod_status | config
    reference: Optional[str] = None
    description: str


class ProposedAction(BaseModel):
    action_type: ActionType
    title: str
    description: str

    kubectl_command: Optional[str] = None
    requires_confirmation: bool
    risk_level: RiskLevel

    expected_outcome: str
    rollback_strategy: Optional[str] = None

class RootCause(BaseModel):
    summary: str
    confidence: ConfidenceLevel
    contributing_factors: List[str]

class K8sAgentResult(BaseModel):
    pod_name: str
    namespace: str

    overall_status: str  # e.g. "CrashLoopBackOff", "Degraded", "Healthy"

    root_cause: RootCause

    evidence: List[Evidence]

    risk_assessment: RiskLevel
    blast_radius: str  # e.g. "Single pod", "Deployment", "Namespace-wide"

    proposed_actions: List[ProposedAction]

    requires_user_confirmation: bool

    summary: str
