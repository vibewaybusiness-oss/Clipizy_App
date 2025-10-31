# Workflows System

The workflows system provides comprehensive workflow orchestration, management, and utilities for complex business processes and AI/ML operations.

## Overview

This module contains workflow orchestration, management, and utility functions for handling complex business processes, AI/ML operations, and content generation workflows. It provides a unified approach to workflow management across the application.

## Architecture

```
api/workflows/
├── __init__.py                          # Workflow exports and utilities
├── README.md                           # This file
├── centralized_workflow_utilities.py   # Core workflow utilities and patterns
├── WORKFLOWS_REFACTORING_SUMMARY.md    # Refactoring documentation
├── generator/                          # Content generation workflows
├── comfyui/                           # ComfyUI workflow management
└── analyzer/                          # Analysis and processing workflows
```

## Core Components

### 1. Centralized Workflow Utilities (`centralized_workflow_utilities.py`)

The core workflow system that provides:

**Workflow Management:**
- `WorkflowStatus`: Workflow execution status
- `WorkflowType`: Workflow types and categories
- `WorkflowPriority`: Workflow priority levels
- `WorkflowManager`: Central workflow management
- `WorkflowExecutor`: Workflow execution engine

**Workflow Classes:**
- `BaseWorkflow`: Base workflow class
- `AsyncWorkflow`: Async workflow implementation
- `BatchWorkflow`: Batch processing workflow
- `PipelineWorkflow`: Pipeline-based workflow
- `ConditionalWorkflow`: Conditional workflow execution

**Workflow Mixins:**
- `WorkflowValidationMixin`: Workflow validation
- `WorkflowLoggingMixin`: Workflow logging
- `WorkflowFileOperationMixin`: File operations
- `WorkflowAsyncOperationMixin`: Async operations
- `WorkflowConfigurationMixin`: Configuration management

**Utility Functions:**
- `create_workflow()`: Create workflow instances
- `execute_workflow()`: Execute workflows
- `monitor_workflow()`: Monitor workflow progress
- `cancel_workflow()`: Cancel running workflows
- `get_workflow_status()`: Get workflow status

### 2. Content Generation Workflows (`generator/`)

Content generation and creation workflows:

**Music Generation:**
- Music clip generation workflows
- Audio processing pipelines
- Music analysis and enhancement
- Export and delivery workflows

**Video Generation:**
- Video creation workflows
- Video processing pipelines
- Video enhancement and effects
- Video export and delivery

**Image Generation:**
- Image creation workflows
- Image processing pipelines
- Image enhancement and effects
- Image export and delivery

### 3. ComfyUI Workflows (`comfyui/`)

ComfyUI workflow management and execution:

**Workflow Management:**
- ComfyUI workflow configuration
- Workflow execution and monitoring
- Resource management and optimization
- Error handling and recovery

**Workflow Types:**
- Image generation workflows
- Video processing workflows
- Audio processing workflows
- Multi-modal workflows

### 4. Analysis Workflows (`analyzer/`)

Analysis and processing workflows:

**Content Analysis:**
- Audio analysis workflows
- Video analysis workflows
- Image analysis workflows
- Text analysis workflows

**Data Processing:**
- Data extraction workflows
- Data transformation workflows
- Data validation workflows
- Data export workflows

## Usage Examples

### Basic Workflow Creation

```python
from api.workflows import BaseWorkflow, WorkflowStatus, WorkflowType

class MyWorkflow(BaseWorkflow):
    def __init__(self, workflow_id: str, user_id: str):
        super().__init__(
            workflow_id=workflow_id,
            user_id=user_id,
            workflow_type=WorkflowType.PROCESSING,
            priority=WorkflowPriority.NORMAL
        )
    
    async def execute(self):
        """Execute the workflow"""
        self.status = WorkflowStatus.RUNNING
        
        try:
            # Workflow logic
            result = await self.process_data()
            
            self.status = WorkflowStatus.COMPLETED
            self.result = result
            
            return result
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.error = str(e)
            raise
```

### Workflow with Mixins

```python
from api.workflows import (
    BaseWorkflow, 
    WorkflowValidationMixin, 
    WorkflowLoggingMixin,
    WorkflowFileOperationMixin
)

class AdvancedWorkflow(
    BaseWorkflow, 
    WorkflowValidationMixin, 
    WorkflowLoggingMixin,
    WorkflowFileOperationMixin
):
    def __init__(self, workflow_id: str, user_id: str):
        super().__init__(workflow_id, user_id)
        self.setup_logging()
        self.setup_validation()
    
    async def execute(self):
        # Validate input
        self.validate_input(self.input_data)
        
        # Log workflow start
        self.log_workflow_start()
        
        try:
            # Process files
            processed_files = await self.process_files(self.input_files)
            
            # Log progress
            self.log_progress(50, "Files processed")
            
            # Continue workflow
            result = await self.finalize_workflow(processed_files)
            
            # Log completion
            self.log_workflow_completion(result)
            
            return result
        except Exception as e:
            self.log_workflow_error(e)
            raise
```

### Workflow Management

```python
from api.workflows import WorkflowManager, create_workflow, execute_workflow

# Create workflow manager
workflow_manager = WorkflowManager()

# Create workflow
workflow = create_workflow(
    workflow_type="music_generation",
    user_id="123",
    input_data={"audio_file": "song.mp3", "style": "electronic"}
)

# Execute workflow
result = await execute_workflow(workflow)

# Monitor workflow
status = await workflow_manager.get_workflow_status(workflow.id)
print(f"Workflow status: {status}")

# Cancel workflow if needed
if status == "running":
    await workflow_manager.cancel_workflow(workflow.id)
```

### Pipeline Workflow

```python
from api.workflows import PipelineWorkflow

class MusicProcessingPipeline(PipelineWorkflow):
    def __init__(self, workflow_id: str, user_id: str):
        super().__init__(workflow_id, user_id)
        
        # Define pipeline steps
        self.add_step("audio_analysis", self.analyze_audio)
        self.add_step("music_generation", self.generate_music)
        self.add_step("video_creation", self.create_video)
        self.add_step("export", self.export_result)
    
    async def analyze_audio(self, input_data):
        # Audio analysis logic
        return {"bpm": 128, "key": "C major", "genre": "electronic"}
    
    async def generate_music(self, analysis_result):
        # Music generation logic
        return {"music_file": "generated_music.mp3"}
    
    async def create_video(self, music_result):
        # Video creation logic
        return {"video_file": "music_video.mp4"}
    
    async def export_result(self, video_result):
        # Export logic
        return {"export_url": "https://example.com/video.mp4"}
```

### Conditional Workflow

```python
from api.workflows import ConditionalWorkflow

class ConditionalProcessingWorkflow(ConditionalWorkflow):
    def __init__(self, workflow_id: str, user_id: str):
        super().__init__(workflow_id, user_id)
        
        # Define conditions and actions
        self.add_condition("is_audio", self.check_audio_type, self.process_audio)
        self.add_condition("is_video", self.check_video_type, self.process_video)
        self.add_condition("is_image", self.check_image_type, self.process_image)
    
    async def check_audio_type(self, input_data):
        return input_data.get("type") == "audio"
    
    async def check_video_type(self, input_data):
        return input_data.get("type") == "video"
    
    async def check_image_type(self, input_data):
        return input_data.get("type") == "image"
    
    async def process_audio(self, input_data):
        return await self.audio_processor.process(input_data)
    
    async def process_video(self, input_data):
        return await self.video_processor.process(input_data)
    
    async def process_image(self, input_data):
        return await self.image_processor.process(input_data)
```

## Workflow Status and Monitoring

### Workflow Status Tracking

```python
from api.workflows import WorkflowStatus, WorkflowManager

# Get workflow status
workflow_manager = WorkflowManager()
status = await workflow_manager.get_workflow_status("workflow_123")

if status == WorkflowStatus.RUNNING:
    print("Workflow is running")
elif status == WorkflowStatus.COMPLETED:
    print("Workflow completed successfully")
elif status == WorkflowStatus.FAILED:
    print("Workflow failed")
```

### Workflow Progress Monitoring

```python
from api.workflows import monitor_workflow

# Monitor workflow progress
async def monitor_workflow_progress(workflow_id: str):
    async for progress in monitor_workflow(workflow_id):
        print(f"Workflow {workflow_id}: {progress['percentage']}% complete")
        print(f"Current step: {progress['current_step']}")
        print(f"Message: {progress['message']}")
        
        if progress['percentage'] == 100:
            print("Workflow completed!")
            break
```

### Workflow Statistics

```python
from api.workflows import WorkflowManager

# Get workflow statistics
workflow_manager = WorkflowManager()
stats = await workflow_manager.get_workflow_statistics()

print(f"Total workflows: {stats['total_workflows']}")
print(f"Completed workflows: {stats['completed_workflows']}")
print(f"Failed workflows: {stats['failed_workflows']}")
print(f"Average execution time: {stats['avg_execution_time']}s")
```

## Error Handling and Recovery

### Workflow Error Handling

```python
from api.workflows import BaseWorkflow, WorkflowStatus

class ErrorHandlingWorkflow(BaseWorkflow):
    async def execute(self):
        try:
            # Workflow logic
            result = await self.process_data()
            return result
        except Exception as e:
            # Handle error
            self.status = WorkflowStatus.FAILED
            self.error = str(e)
            
            # Attempt recovery
            if await self.can_recover():
                return await self.recover_and_retry()
            else:
                raise
    
    async def can_recover(self):
        # Check if workflow can be recovered
        return self.retry_count < self.max_retries
    
    async def recover_and_retry(self):
        # Recovery logic
        self.retry_count += 1
        self.status = WorkflowStatus.RUNNING
        return await self.execute()
```

### Workflow Retry Logic

```python
from api.workflows import BaseWorkflow, retry_on_failure

class RetryableWorkflow(BaseWorkflow):
    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    async def unreliable_operation(self):
        # Operation that might fail
        return await external_api_call()
    
    async def execute(self):
        result = await self.unreliable_operation()
        return result
```

## Configuration Integration

### Workflow Configuration

```python
from api.config import get_config_value
from api.workflows import BaseWorkflow

class ConfigurableWorkflow(BaseWorkflow):
    def __init__(self, workflow_id: str, user_id: str):
        super().__init__(workflow_id, user_id)
        
        # Get configuration values
        self.timeout = get_config_value("workflows.timeout", 300)
        self.max_retries = get_config_value("workflows.max_retries", 3)
        self.parallel_execution = get_config_value("workflows.parallel_execution", False)
```

### Environment-Specific Configuration

```python
from api.config import get_config_manager

class EnvironmentAwareWorkflow(BaseWorkflow):
    def __init__(self, workflow_id: str, user_id: str):
        super().__init__(workflow_id, user_id)
        
        config = get_config_manager()
        self.environment = config.environment.value
        
        if self.environment == "production":
            self.debug_mode = False
            self.log_level = "WARNING"
        else:
            self.debug_mode = True
            self.log_level = "DEBUG"
```

## Performance Optimization

### Parallel Workflow Execution

```python
from api.workflows import BaseWorkflow
import asyncio

class ParallelWorkflow(BaseWorkflow):
    async def execute(self):
        # Execute multiple operations in parallel
        tasks = [
            self.process_audio(),
            self.process_video(),
            self.process_image()
        ]
        
        results = await asyncio.gather(*tasks)
        return self.combine_results(results)
```

### Workflow Caching

```python
from api.workflows import BaseWorkflow
from functools import lru_cache

class CachedWorkflow(BaseWorkflow):
    @lru_cache(maxsize=100)
    async def expensive_operation(self, input_data):
        # Expensive operation that can be cached
        return await self.perform_expensive_operation(input_data)
    
    async def execute(self):
        result = await self.expensive_operation(self.input_data)
        return result
```

## Testing

### Workflow Testing

```python
from api.workflows import BaseWorkflow, WorkflowStatus
import pytest

class TestWorkflow(BaseWorkflow):
    async def execute(self):
        return "test_result"

@pytest.mark.asyncio
async def test_workflow():
    workflow = TestWorkflow("test_workflow", "test_user")
    result = await workflow.execute()
    
    assert result == "test_result"
    assert workflow.status == WorkflowStatus.COMPLETED
```

### Workflow Integration Testing

```python
from api.workflows import WorkflowManager, create_workflow

@pytest.mark.asyncio
async def test_workflow_integration():
    workflow_manager = WorkflowManager()
    
    # Create and execute workflow
    workflow = create_workflow("test_workflow", "test_user")
    result = await workflow_manager.execute_workflow(workflow)
    
    # Verify result
    assert result == "test_result"
    
    # Verify workflow status
    status = await workflow_manager.get_workflow_status(workflow.id)
    assert status == WorkflowStatus.COMPLETED
```

## Best Practices

1. **Use Base Classes**: Inherit from appropriate base workflow classes
2. **Implement Error Handling**: Add comprehensive error handling
3. **Use Mixins**: Leverage workflow mixins for common functionality
4. **Monitor Progress**: Implement progress monitoring
5. **Handle Timeouts**: Set appropriate timeouts for workflows
6. **Use Configuration**: Integrate with configuration system
7. **Test Thoroughly**: Write comprehensive tests
8. **Document Workflows**: Document workflow purpose and usage

## Integration with Services

Workflows integrate with:
- **Services Layer**: Use services for business logic
- **Data Layer**: Access data through models
- **Configuration**: Use configuration for workflow settings
- **Logging**: Use centralized logging for workflow events
- **Monitoring**: Integrate with monitoring systems

## Workflow Orchestration

### Complex Workflow Orchestration

```python
from api.workflows import WorkflowManager, create_workflow

class WorkflowOrchestrator:
    def __init__(self):
        self.workflow_manager = WorkflowManager()
    
    async def orchestrate_complex_workflow(self, user_id: str, input_data: dict):
        # Create multiple workflows
        workflows = [
            create_workflow("audio_analysis", user_id, input_data),
            create_workflow("music_generation", user_id, input_data),
            create_workflow("video_creation", user_id, input_data)
        ]
        
        # Execute workflows in sequence
        results = []
        for workflow in workflows:
            result = await self.workflow_manager.execute_workflow(workflow)
            results.append(result)
        
        # Combine results
        return self.combine_workflow_results(results)
```

This workflows system provides comprehensive workflow orchestration and management capabilities that enable complex business processes and AI/ML operations to be executed reliably and efficiently.