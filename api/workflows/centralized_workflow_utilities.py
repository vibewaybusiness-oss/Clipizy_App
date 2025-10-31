"""
Centralized Workflow Utilities
Common patterns and utilities for all workflow operations
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Callable

import numpy as np

# Simplified service classes to avoid circular imports
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime
import uuid

class ValidationMixin:
    """Simplified validation mixin"""
    def _validate_uuid(self, value: str, field_name: str = "id") -> str:
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            raise ValueError(f"Invalid {field_name}: {value}")

class LoggingMixin:
    """Simplified logging mixin"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

class FileOperationMixin:
    """Simplified file operation mixin"""
    def _generate_file_id(self) -> str:
        return str(uuid.uuid4())

class AsyncOperationMixin:
    """Simplified async operation mixin"""
    pass

class ConfigurationMixin:
    """Simplified configuration mixin"""
    def _get_config_value(self, key: str, default: Any = None) -> Any:
        import os
        return os.getenv(key, default)

class ServiceLogger:
    """Simplified service logger"""
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(service_name)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

class ErrorContext:
    """Simplified error context"""
    def __init__(self, operation: str, service: str, **kwargs):
        self.operation = operation
        self.service = service
        self.timestamp = datetime.utcnow()

def handle_errors(service_name: str, operation_name: str, reraise: bool = True):
    """Simplified error handling decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(service_name)
                logger.error(f"{operation_name} failed: {e}")
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowType(Enum):
    """Workflow types"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    PROCESSING = "processing"
    VISUALIZATION = "visualization"
    AI_GENERATION = "ai_generation"


class WorkflowPriority(Enum):
    """Workflow priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class WorkflowValidationMixin(ValidationMixin):
    """Mixin for workflow-specific validation"""
    
    def _validate_workflow_parameters(self, parameters: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Validate workflow parameters"""
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a dictionary")
        
        missing_fields = [field for field in required_fields if field not in parameters]
        if missing_fields:
            raise ValueError(f"Missing required parameters: {missing_fields}")
        
        return parameters
    
    def _validate_file_paths(self, file_paths: Union[str, List[str]]) -> List[str]:
        """Validate file paths"""
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        validated_paths = []
        for path in file_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            validated_paths.append(path)
        
        return validated_paths
    
    def _validate_output_path(self, output_path: str) -> str:
        """Validate output path"""
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        return output_path
    
    def _validate_workflow_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration"""
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Validate required config fields
        required_fields = ["workflow_type", "priority"]
        for field in required_fields:
            if field not in config:
                config[field] = "normal" if field == "priority" else "processing"
        
        return config


class WorkflowLoggingMixin(LoggingMixin):
    """Mixin for workflow-specific logging"""
    
    def _log_workflow_start(self, workflow_id: str, workflow_type: str, **kwargs):
        """Log workflow start"""
        self.logger.info(
            f"Starting workflow {workflow_id}",
            operation="workflow_start",
            additional_data={
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                **kwargs
            }
        )
    
    def _log_workflow_progress(self, workflow_id: str, progress: float, **kwargs):
        """Log workflow progress"""
        self.logger.info(
            f"Workflow {workflow_id} progress: {progress:.1f}%",
            operation="workflow_progress",
            additional_data={
                "workflow_id": workflow_id,
                "progress": progress,
                **kwargs
            }
        )
    
    def _log_workflow_completion(self, workflow_id: str, result: Any, **kwargs):
        """Log workflow completion"""
        self.logger.info(
            f"Workflow {workflow_id} completed successfully",
            operation="workflow_completion",
            additional_data={
                "workflow_id": workflow_id,
                "result": str(result),
                **kwargs
            }
        )
    
    def _log_workflow_error(self, workflow_id: str, error: Exception, **kwargs):
        """Log workflow error"""
        self.logger.error(
            f"Workflow {workflow_id} failed: {str(error)}",
            operation="workflow_error",
            additional_data={
                "workflow_id": workflow_id,
                "error": str(error),
                **kwargs
            },
            exc_info=True
        )


class WorkflowFileOperationMixin(FileOperationMixin):
    """Mixin for workflow-specific file operations"""
    
    def _create_temp_workflow_dir(self, workflow_id: str) -> str:
        """Create temporary directory for workflow"""
        temp_dir = os.path.join(tempfile.gettempdir(), f"workflow_{workflow_id}")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def _cleanup_workflow_files(self, workflow_id: str, temp_dir: str):
        """Clean up workflow temporary files"""
        try:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                self.logger.debug(f"Cleaned up workflow temp directory: {temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup workflow temp directory {temp_dir}: {e}")
    
    def _save_workflow_result(self, workflow_id: str, result: Any, output_path: str) -> str:
        """Save workflow result to file"""
        self._validate_output_path(output_path)
        
        if isinstance(result, dict):
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        elif isinstance(result, (list, tuple)):
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
        else:
            with open(output_path, 'w') as f:
                f.write(str(result))
        
        self.logger.info(f"Saved workflow result to: {output_path}")
        return output_path


class WorkflowAsyncOperationMixin(AsyncOperationMixin):
    """Mixin for workflow-specific async operations"""
    
    async def _execute_workflow_step(self, step_name: str, step_func: Callable, *args, **kwargs):
        """Execute a workflow step with error handling"""
        try:
            self.logger.debug(f"Executing workflow step: {step_name}")
            
            if asyncio.iscoroutinefunction(step_func):
                result = await step_func(*args, **kwargs)
            else:
                result = step_func(*args, **kwargs)
            
            self.logger.debug(f"Completed workflow step: {step_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow step {step_name} failed: {str(e)}")
            raise
    
    async def _execute_workflow_steps(self, steps: List[Tuple[str, Callable, tuple, dict]]):
        """Execute multiple workflow steps in sequence"""
        results = []
        
        for step_name, step_func, args, kwargs in steps:
            result = await self._execute_workflow_step(step_name, step_func, *args, **kwargs)
            results.append((step_name, result))
        
        return results


class WorkflowConfigurationMixin(ConfigurationMixin):
    """Mixin for workflow-specific configuration"""
    
    def _get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow configuration"""
        return {
            "max_concurrent_workflows": self._get_int_config("MAX_CONCURRENT_WORKFLOWS", 5),
            "workflow_timeout": self._get_int_config("WORKFLOW_TIMEOUT", 3600),
            "temp_dir": self._get_config_value("WORKFLOW_TEMP_DIR", "/tmp/workflows"),
            "output_dir": self._get_config_value("WORKFLOW_OUTPUT_DIR", "/tmp/workflow_outputs"),
            "enable_cleanup": self._get_bool_config("WORKFLOW_ENABLE_CLEANUP", True),
            "max_retries": self._get_int_config("WORKFLOW_MAX_RETRIES", 3),
            "retry_delay": self._get_int_config("WORKFLOW_RETRY_DELAY", 5)
        }


class BaseWorkflow(
    WorkflowValidationMixin,
    WorkflowLoggingMixin,
    WorkflowFileOperationMixin,
    WorkflowAsyncOperationMixin,
    WorkflowConfigurationMixin
):
    """Base class for all workflows"""
    
    def __init__(self, workflow_type: WorkflowType, workflow_name: str = None):
        self.workflow_type = workflow_type
        self.workflow_name = workflow_name or f"{workflow_type.value}_workflow"
        self.logger = ServiceLogger(self.workflow_name)
        self.config = self._get_workflow_config()
        self._workflow_id = None
        self._status = WorkflowStatus.PENDING
        self._start_time = None
        self._end_time = None
        self._progress = 0.0
        self._result = None
        self._error = None
        self._temp_dir = None
    
    @property
    def workflow_id(self) -> str:
        """Get workflow ID"""
        if not self._workflow_id:
            self._workflow_id = str(uuid.uuid4())
        return self._workflow_id
    
    @property
    def status(self) -> WorkflowStatus:
        """Get workflow status"""
        return self._status
    
    @property
    def progress(self) -> float:
        """Get workflow progress"""
        return self._progress
    
    @property
    def result(self) -> Any:
        """Get workflow result"""
        return self._result
    
    @property
    def error(self) -> Optional[Exception]:
        """Get workflow error"""
        return self._error
    
    def _update_status(self, status: WorkflowStatus):
        """Update workflow status"""
        self._status = status
        if status == WorkflowStatus.RUNNING and not self._start_time:
            self._start_time = datetime.utcnow()
        elif status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            self._end_time = datetime.utcnow()
    
    def _update_progress(self, progress: float):
        """Update workflow progress"""
        self._progress = max(0.0, min(100.0, progress))
        self._log_workflow_progress(self.workflow_id, self._progress)
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the workflow"""
        pass
    
    async def run(self, parameters: Dict[str, Any]) -> Any:
        """Run the workflow with error handling"""
        try:
            self._update_status(WorkflowStatus.RUNNING)
            self._log_workflow_start(self.workflow_id, self.workflow_type.value)
            
            # Create temp directory
            self._temp_dir = self._create_temp_workflow_dir(self.workflow_id)
            
            # Execute workflow
            result = await self.execute(parameters)
            
            # Update status and result
            self._result = result
            self._update_status(WorkflowStatus.COMPLETED)
            self._update_progress(100.0)
            self._log_workflow_completion(self.workflow_id, result)
            
            return result
            
        except Exception as e:
            self._error = e
            self._update_status(WorkflowStatus.FAILED)
            self._log_workflow_error(self.workflow_id, e)
            raise
        
        finally:
            # Cleanup temp files
            if self.config["enable_cleanup"] and self._temp_dir:
                self._cleanup_workflow_files(self.workflow_id, self._temp_dir)
    
    async def health_check(self) -> Dict[str, Any]:
        """Workflow health check"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type.value,
            "workflow_name": self.workflow_name,
            "status": self._status.value,
            "progress": self._progress,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "duration_seconds": (self._end_time - self._start_time).total_seconds() if self._start_time and self._end_time else None,
            "has_error": self._error is not None,
            "error_message": str(self._error) if self._error else None,
            "timestamp": datetime.utcnow().isoformat()
        }


class AsyncWorkflow(BaseWorkflow):
    """Async workflow implementation"""
    def __init__(self, workflow_name: str, **kwargs):
        super().__init__(workflow_name, **kwargs)
    
    async def execute_async(self, *args, **kwargs):
        """Execute workflow asynchronously"""
        return await self.execute(*args, **kwargs)

class BatchWorkflow(BaseWorkflow):
    """Batch workflow implementation"""
    def __init__(self, workflow_name: str, **kwargs):
        super().__init__(workflow_name, **kwargs)
    
    def execute_batch(self, items: list, *args, **kwargs):
        """Execute workflow on a batch of items"""
        results = []
        for item in items:
            result = self.execute(item, *args, **kwargs)
            results.append(result)
        return results

class PipelineWorkflow(BaseWorkflow):
    """Pipeline workflow implementation"""
    def __init__(self, workflow_name: str, **kwargs):
        super().__init__(workflow_name, **kwargs)
        self.stages = []
    
    def add_stage(self, stage):
        """Add a stage to the pipeline"""
        self.stages.append(stage)
    
    def execute_pipeline(self, *args, **kwargs):
        """Execute pipeline stages sequentially"""
        result = None
        for stage in self.stages:
            result = stage.execute(result, *args, **kwargs)
        return result

class ConditionalWorkflow(BaseWorkflow):
    """Conditional workflow implementation"""
    def __init__(self, workflow_name: str, **kwargs):
        super().__init__(workflow_name, **kwargs)
        self.conditions = []
    
    def add_condition(self, condition, workflow):
        """Add a conditional branch"""
        self.conditions.append((condition, workflow))
    
    def execute_conditional(self, *args, **kwargs):
        """Execute workflow based on conditions"""
        for condition, workflow in self.conditions:
            if condition(*args, **kwargs):
                return workflow.execute(*args, **kwargs)
        return None

class WorkflowManager:
    """Workflow manager"""
    def __init__(self):
        self.workflows = {}
    
    def register_workflow(self, name: str, workflow):
        """Register a workflow"""
        self.workflows[name] = workflow
    
    def get_workflow(self, name: str):
        """Get a workflow by name"""
        return self.workflows.get(name)

class WorkflowExecutor:
    """Workflow executor"""
    def __init__(self):
        self.manager = WorkflowManager()
    
    def execute_workflow(self, name: str, *args, **kwargs):
        """Execute a workflow by name"""
        workflow = self.manager.get_workflow(name)
        if workflow:
            return workflow.execute(*args, **kwargs)
        return None

class WorkflowOrchestrator:
    """Orchestrator for managing multiple workflows"""
    
    def __init__(self):
        self.logger = ServiceLogger("workflow_orchestrator")
        self._active_workflows: Dict[str, BaseWorkflow] = {}
        self._workflow_history: List[Dict[str, Any]] = []
        self._max_concurrent = 5
    
    async def submit_workflow(self, workflow: BaseWorkflow, parameters: Dict[str, Any]) -> str:
        """Submit a workflow for execution"""
        if len(self._active_workflows) >= self._max_concurrent:
            raise RuntimeError(f"Maximum concurrent workflows ({self._max_concurrent}) reached")
        
        workflow_id = workflow.workflow_id
        self._active_workflows[workflow_id] = workflow
        
        # Start workflow execution
        asyncio.create_task(self._execute_workflow(workflow, parameters))
        
        self.logger.info(f"Submitted workflow {workflow_id}")
        return workflow_id
    
    async def _execute_workflow(self, workflow: BaseWorkflow, parameters: Dict[str, Any]):
        """Execute a workflow"""
        try:
            result = await workflow.run(parameters)
            
            # Record in history
            self._workflow_history.append({
                "workflow_id": workflow.workflow_id,
                "workflow_type": workflow.workflow_type.value,
                "status": workflow.status.value,
                "result": str(result),
                "start_time": workflow._start_time.isoformat() if workflow._start_time else None,
                "end_time": workflow._end_time.isoformat() if workflow._end_time else None,
                "duration_seconds": (workflow._end_time - workflow._start_time).total_seconds() if workflow._start_time and workflow._end_time else None
            })
            
        except Exception as e:
            self.logger.error(f"Workflow {workflow.workflow_id} execution failed: {e}")
            
            # Record failure in history
            self._workflow_history.append({
                "workflow_id": workflow.workflow_id,
                "workflow_type": workflow.workflow_type.value,
                "status": "failed",
                "error": str(e),
                "start_time": workflow._start_time.isoformat() if workflow._start_time else None,
                "end_time": workflow._end_time.isoformat() if workflow._end_time else None
            })
        
        finally:
            # Remove from active workflows
            if workflow.workflow_id in self._active_workflows:
                del self._active_workflows[workflow.workflow_id]
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        if workflow_id in self._active_workflows:
            workflow = self._active_workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "progress": workflow.progress,
                "result": workflow.result,
                "error": str(workflow.error) if workflow.error else None
            }
        return None
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        return [
            {
                "workflow_id": workflow_id,
                "workflow_type": workflow.workflow_type.value,
                "status": workflow.status.value,
                "progress": workflow.progress
            }
            for workflow_id, workflow in self._active_workflows.items()
        ]
    
    def get_workflow_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflow history"""
        return self._workflow_history[-limit:]


# Utility functions for common workflow operations
def create_workflow_logger(workflow_name: str) -> ServiceLogger:
    """Create a logger for a workflow"""
    return ServiceLogger(workflow_name)


def create_workflow(workflow_type: str, workflow_name: str, **kwargs):
    """Create a workflow instance"""
    if workflow_type == "async":
        return AsyncWorkflow(workflow_name, **kwargs)
    elif workflow_type == "batch":
        return BatchWorkflow(workflow_name, **kwargs)
    elif workflow_type == "pipeline":
        return PipelineWorkflow(workflow_name, **kwargs)
    elif workflow_type == "conditional":
        return ConditionalWorkflow(workflow_name, **kwargs)
    else:
        return BaseWorkflow(workflow_name, **kwargs)

def execute_workflow(workflow, *args, **kwargs):
    """Execute a workflow"""
    return workflow.execute(*args, **kwargs)

def monitor_workflow(workflow):
    """Monitor a workflow's status"""
    return {
        "status": workflow.status.value,
        "progress": workflow.progress,
        "error": str(workflow.error) if workflow.error else None
    }

def cancel_workflow(workflow):
    """Cancel a workflow"""
    workflow.cancel()
    return True

def get_workflow_status(workflow):
    """Get workflow status"""
    return workflow.status.value

def get_workflow_statistics(workflow):
    """Get workflow statistics"""
    return {
        "status": workflow.status.value,
        "progress": workflow.progress,
        "start_time": workflow.start_time,
        "end_time": workflow.end_time,
        "duration": workflow.duration,
        "error": str(workflow.error) if workflow.error else None
    }

def generate_workflow_id() -> str:
    """Generate a unique workflow ID"""
    return str(uuid.uuid4())


def validate_workflow_parameters(parameters: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """Validate workflow parameters"""
    if not isinstance(parameters, dict):
        raise ValueError("Parameters must be a dictionary")
    
    missing_fields = [field for field in required_fields if field not in parameters]
    if missing_fields:
        raise ValueError(f"Missing required parameters: {missing_fields}")
    
    return parameters


def create_temp_workflow_directory(workflow_id: str) -> str:
    """Create temporary directory for workflow"""
    temp_dir = os.path.join(tempfile.gettempdir(), f"workflow_{workflow_id}")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def cleanup_workflow_directory(temp_dir: str):
    """Clean up workflow temporary directory"""
    try:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
    except Exception as e:
        logging.warning(f"Failed to cleanup workflow temp directory {temp_dir}: {e}")


def save_workflow_result(result: Any, output_path: str) -> str:
    """Save workflow result to file"""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    if isinstance(result, dict):
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
    elif isinstance(result, (list, tuple)):
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
    else:
        with open(output_path, 'w') as f:
            f.write(str(result))
    
    return output_path


def load_workflow_config(config_path: str) -> Dict[str, Any]:
    """Load workflow configuration from file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def execute_system_command(command: List[str], timeout: int = 300) -> Tuple[int, str, str]:
    """Execute system command with timeout"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout} seconds")


# Export all utilities
__all__ = [
    # Enums
    "WorkflowStatus",
    "WorkflowType", 
    "WorkflowPriority",
    
    # Mixins
    "WorkflowValidationMixin",
    "WorkflowLoggingMixin",
    "WorkflowFileOperationMixin",
    "WorkflowAsyncOperationMixin",
    "WorkflowConfigurationMixin",
    
    # Base classes
    "BaseWorkflow",
    "WorkflowOrchestrator",
    
    # Utility functions
    "create_workflow_logger",
    "generate_workflow_id",
    "validate_workflow_parameters",
    "create_temp_workflow_directory",
    "cleanup_workflow_directory",
    "save_workflow_result",
    "load_workflow_config",
    "execute_system_command"
]
