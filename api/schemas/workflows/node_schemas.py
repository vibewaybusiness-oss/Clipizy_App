from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class InputPort(BaseModel):
    """Input port definition for workflow nodes"""
    id: str
    type: str  # 'text', 'image', 'video', 'music'
    required: bool = True
    description: str = ""
    default_value: Optional[Any] = None

class OutputPort(BaseModel):
    """Output port definition for workflow nodes"""
    id: str
    type: str  # 'text', 'image', 'video', 'music'
    description: str = ""

class NodeConfig(BaseModel):
    """Configuration schema for workflow nodes"""
    type: str
    default: Any
    description: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None

class NodeSchema(BaseModel):
    """Schema definition for workflow nodes"""
    id: str
    type: str  # 'text-input', 'text-to-text', 'text-to-image', etc.
    title: str
    description: str
    inputs: List[InputPort] = []
    outputs: List[OutputPort] = []
    validation_required: bool = False
    execution_function: str
    ui_component: str
    config_schema: Dict[str, NodeConfig] = {}
    category: str = "general"  # 'input', 'processing', 'output'
    icon: str = "default"
    color: str = "#6b7280"

class WorkflowConnection(BaseModel):
    """Connection between workflow nodes"""
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str

class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    category: str  # 'music-clip', 'animation', 'scene', 'custom'
    nodes: List[NodeSchema]
    connections: List[WorkflowConnection]
    metadata: Dict[str, Any] = {}
    version: str = "1.0.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow"""
    workflow_id: str
    initial_data: Dict[str, Any] = {}
    auto_mode: bool = True
    validation_required: bool = False

class WorkflowExecutionResponse(BaseModel):
    """Response from workflow execution"""
    job_id: str
    status: str
    message: str
    estimated_duration: Optional[int] = None
    estimated_cost: Optional[int] = None

class NodeExecutionRequest(BaseModel):
    """Request to execute a single node"""
    node_id: str
    node_type: str
    node_data: Dict[str, Any]
    inputs: Dict[str, Any]
    job_id: str

class NodeExecutionResponse(BaseModel):
    """Response from node execution"""
    success: bool
    output: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
    execution_time: Optional[float] = None

class NodeValidationRequest(BaseModel):
    """Request to validate a node output"""
    node_id: str
    job_id: str
    validation_data: Dict[str, Any]
    validated: bool

class NodeValidationResponse(BaseModel):
    """Response from node validation"""
    success: bool
    message: str
    next_nodes: List[str] = []
    can_proceed: bool = False
