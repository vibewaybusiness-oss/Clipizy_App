# runpod.py
# RunPod database models
# ----------------------------------------------------------

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID as GUID

Base = declarative_base()


class RunPodUser(Base):
    """Database model for RunPod users"""

    __tablename__ = "runpod_users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    runpod_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True)
    min_balance = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime)

    pods = relationship("RunPodPod", back_populates="user")

    def __repr__(self):
        return f"<RunPodUser(id={self.id}, email={self.email})>"


class RunPodPod(Base):
    """Database model for RunPod pods"""

    __tablename__ = "runpod_pods"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    runpod_pod_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    image_name = Column(String(255), nullable=False)

    status = Column(String(50), nullable=False, default="running", index=True)
    desired_status = Column(String(50))
    uptime_seconds = Column(Integer, default=0)
    cost_per_hr = Column(Float, default=0.0)

    ip = Column(String(45))
    public_ip = Column(String(45))
    port_mappings = Column(JSON)

    machine_id = Column(String(255))
    gpu_count = Column(Integer, default=1)
    memory_in_gb = Column(Float)
    vcpu_count = Column(Integer)

    network_volume_id = Column(String(255))
    volume_in_gb = Column(Float)
    volume_mount_path = Column(String(500))
    container_disk_in_gb = Column(Integer, default=20)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_started_at = Column(DateTime)
    last_used_at = Column(DateTime)
    terminated_at = Column(DateTime)

    user_id = Column(GUID(), ForeignKey("runpod_users.id"), nullable=False, index=True)

    user = relationship("RunPodUser", back_populates="pods")
    executions = relationship("RunPodExecution", back_populates="pod")
    health_checks = relationship("RunPodHealthCheck", back_populates="pod")

    def __repr__(self):
        return f"<RunPodPod(id={self.id}, runpod_pod_id={self.runpod_pod_id}, name={self.name}, status={self.status})>"


class RunPodExecution(Base):
    """Database model for RunPod workflow executions"""

    __tablename__ = "runpod_executions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    execution_id = Column(String(255), unique=True, nullable=False, index=True)

    workflow_name = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)

    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON)
    error = Column(Text)

    pod_id = Column(GUID(), ForeignKey("runpod_pods.id"), nullable=False, index=True)

    prompt_id = Column(String(255), index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    user_id = Column(GUID(), index=True)
    project_id = Column(GUID(), index=True)

    credits_spent = Column(Integer, default=0)
    execution_time_seconds = Column(Integer)

    pod = relationship("RunPodPod", back_populates="executions")

    def __repr__(self):
        return f"<RunPodExecution(id={self.id}, execution_id={self.execution_id}, workflow_name={self.workflow_name}, status={self.status})>"


class RunPodNetworkVolume(Base):
    """Database model for RunPod network volumes"""

    __tablename__ = "runpod_network_volumes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    runpod_volume_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    size = Column(Float, nullable=False)
    data_center_id = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime)

    def __repr__(self):
        return f"<RunPodNetworkVolume(id={self.id}, name={self.name}, size={self.size})>"


class RunPodGpuType(Base):
    """Database model for RunPod GPU types"""

    __tablename__ = "runpod_gpu_types"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    runpod_gpu_id = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    memory_in_gb = Column(Float, nullable=False)
    secure_cloud = Column(Boolean, default=False)
    community_cloud = Column(Boolean, default=False)
    lowest_price = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime)

    def __repr__(self):
        return f"<RunPodGpuType(id={self.id}, display_name={self.display_name}, memory_in_gb={self.memory_in_gb})>"


class RunPodTemplate(Base):
    """Database model for RunPod templates"""

    __tablename__ = "runpod_templates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    runpod_template_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_name = Column(String(255), nullable=False)
    gpu_type_ids = Column(JSON)

    is_public = Column(Boolean, default=False)
    is_runpod = Column(Boolean, default=False)
    is_endpoint_bound = Column(Boolean, default=False)

    env = Column(JSON)
    docker_args = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime)

    def __repr__(self):
        return f"<RunPodTemplate(id={self.id}, name={self.name}, is_public={self.is_public})>"


class RunPodHealthCheck(Base):
    """Database model for RunPod health checks"""

    __tablename__ = "runpod_health_checks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    pod_id = Column(GUID(), ForeignKey("runpod_pods.id"), nullable=False, index=True)

    is_healthy = Column(Boolean, nullable=False)
    status = Column(String(50), nullable=False)
    response_time_ms = Column(Float)
    error_message = Column(Text)

    check_type = Column(String(50), default="general")
    endpoint = Column(String(500))

    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pod = relationship("RunPodPod", back_populates="health_checks")

    def __repr__(self):
        return f"<RunPodHealthCheck(id={self.id}, pod_id={self.pod_id}, is_healthy={self.is_healthy})>"


class RunPodUsageLog(Base):
    """Database model for RunPod usage logging"""

    __tablename__ = "runpod_usage_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    pod_id = Column(GUID(), ForeignKey("runpod_pods.id"), nullable=False, index=True)
    execution_id = Column(GUID(), ForeignKey("runpod_executions.id"), index=True)

    cpu_usage_percent = Column(Float)
    memory_usage_gb = Column(Float)
    gpu_usage_percent = Column(Float)
    gpu_memory_usage_gb = Column(Float)
    network_io_bytes = Column(Integer)
    disk_io_bytes = Column(Integer)

    cost_per_hour = Column(Float)
    estimated_cost = Column(Float)

    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<RunPodUsageLog(id={self.id}, pod_id={self.pod_id}, cpu_usage={self.cpu_usage_percent}%)>"


class RunPodConfiguration(Base):
    """Database model for RunPod configuration settings"""

    __tablename__ = "runpod_configurations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(255), unique=True, nullable=False, index=True)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)

    is_active = Column(Boolean, default=True)
    config_type = Column(String(50), default="general")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RunPodConfiguration(id={self.id}, config_key={self.config_key}, config_type={self.config_type})>"


__all__ = [
    "RunPodUser",
    "RunPodPod",
    "RunPodExecution",
    "RunPodNetworkVolume",
    "RunPodGpuType",
    "RunPodTemplate",
    "RunPodHealthCheck",
    "RunPodUsageLog",
    "RunPodConfiguration",
]
