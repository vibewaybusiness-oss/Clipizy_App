# llm.py
# LLM database models (qwen-omni)
# ----------------------------------------------------------

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.dialects.postgresql import UUID as GUID

Base = declarative_base()

# ============================================================================
# LLM MODELS
# ============================================================================


class LLMWorkflowExecution(Base):
    """Database model for LLM workflow executions (qwen-omni)"""

    __tablename__ = "llm_workflow_executions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(255), unique=True, nullable=False, index=True)
    workflow_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)

    # Input data
    inputs = Column(JSON, nullable=False)
    model = Column(String(100), nullable=False, default="qwen-omni")
    prompt = Column(Text, nullable=False)
    stream = Column(Boolean, default=False)

    # Pod information
    pod_id = Column(String(255), index=True)
    pod_ip = Column(String(45))

    # LLM specific
    response_id = Column(String(255), index=True)

    # Results
    result = Column(JSON)
    response_text = Column(Text)
    error = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # User and project tracking
    user_id = Column(GUID(), index=True)
    project_id = Column(GUID(), index=True)

    # Credits and billing
    credits_spent = Column(Integer, default=0)

    # Performance metrics
    total_duration = Column(Integer)  # in nanoseconds
    load_duration = Column(Integer)  # in nanoseconds
    prompt_eval_count = Column(Integer)
    prompt_eval_duration = Column(Integer)  # in nanoseconds
    eval_count = Column(Integer)
    eval_duration = Column(Integer)  # in nanoseconds

    def __repr__(self):
        return f"<LLMWorkflowExecution(id={self.id}, request_id={self.request_id}, workflow_type={self.workflow_type}, status={self.status})>"


class LLMPod(Base):
    """Database model for LLM pods (qwen-omni)"""

    __tablename__ = "llm_pods"

    id = Column(String(255), primary_key=True)
    workflow_name = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="running", index=True)

    # Pod details
    ip_address = Column(String(45))
    port = Column(Integer, default=8188)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    paused_at = Column(DateTime)
    terminated_at = Column(DateTime)

    # Configuration
    template_id = Column(String(255))
    network_volume_id = Column(String(255))

    # Resource usage
    gpu_count = Column(Integer, default=1)
    memory_gb = Column(Integer, default=8)
    vcpu_count = Column(Integer, default=4)
    disk_gb = Column(Integer, default=20)

    def __repr__(self):
        return f"<LLMPod(id={self.id}, workflow_name={self.workflow_name}, status={self.status})>"


class LLMWorkflowConfig(Base):
    """Database model for LLM workflow configurations (qwen-omni)"""

    __tablename__ = "llm_workflow_configs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workflow_name = Column(String(100), unique=True, nullable=False, index=True)

    # Configuration
    max_queue_size = Column(Integer, default=3)
    network_volume_id = Column(String(255))
    template_id = Column(String(255))

    # Timeouts (in seconds)
    pause_timeout = Column(Integer, default=60)
    terminate_timeout = Column(Integer, default=300)

    # Resource requirements
    gpu_count = Column(Integer, default=1)
    memory_gb = Column(Integer, default=8)
    vcpu_count = Column(Integer, default=4)
    disk_gb = Column(Integer, default=20)

    # LLM specific settings
    default_model = Column(String(100), default="qwen-omni")
    max_tokens = Column(Integer, default=2048)
    temperature = Column(Float, default=0.7)

    # Metadata
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LLMWorkflowConfig(workflow_name={self.workflow_name}, max_queue_size={self.max_queue_size})>"


class LLMExecutionLog(Base):
    """Database model for LLM execution logs (qwen-omni)"""

    __tablename__ = "llm_execution_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    execution_id = Column(GUID(), nullable=False, index=True)
    request_id = Column(String(255), nullable=False, index=True)

    # Log details
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    details = Column(JSON)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LLMExecutionLog(execution_id={self.execution_id}, level={self.level}, message={self.message[:50]}...)>"


class LLMResourceUsage(Base):
    """Database model for LLM resource usage tracking (qwen-omni)"""

    __tablename__ = "llm_resource_usage"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    pod_id = Column(String(255), nullable=False, index=True)
    execution_id = Column(GUID(), index=True)

    # Resource metrics
    cpu_usage_percent = Column(Float)
    memory_usage_gb = Column(Float)
    gpu_usage_percent = Column(Float)
    gpu_memory_usage_gb = Column(Float)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LLMResourceUsage(pod_id={self.pod_id}, cpu_usage={self.cpu_usage_percent}%)>"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "LLMWorkflowExecution",
    "LLMPod",
    "LLMWorkflowConfig",
    "LLMExecutionLog",
    "LLMResourceUsage",
]
