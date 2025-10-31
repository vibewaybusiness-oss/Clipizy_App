"""
Enhanced Flux Workflow
Refactored Flux workflow with centralized utilities and improved error handling
"""

import json
import os
import random
from typing import Any, Dict, Tuple, Optional

from ..centralized_workflow_utilities import (
    BaseWorkflow, WorkflowType, WorkflowStatus, WorkflowValidationMixin,
    WorkflowLoggingMixin, WorkflowFileOperationMixin, WorkflowAsyncOperationMixin,
    create_workflow_logger, validate_workflow_parameters, create_temp_workflow_directory,
    cleanup_workflow_directory, save_workflow_result, load_workflow_config
)
from api.services.unified_services import handle_errors, ErrorContext


class EnhancedFluxWorkflow(BaseWorkflow):
    """Enhanced Flux workflow with centralized utilities"""
    
    def __init__(self):
        super().__init__(WorkflowType.AI_GENERATION, "flux_workflow")
        self.logger = create_workflow_logger("flux_workflow")
        self.package_dir = os.path.dirname(__file__)
        self.workflow_templates = self._load_workflow_templates()
    
    def _load_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load workflow templates"""
        templates = {}
        
        # Load standard flux workflow
        flux_workflow_path = os.path.join(self.package_dir, "flux", "flux_workflow.json")
        if os.path.exists(flux_workflow_path):
            templates["standard"] = load_workflow_config(flux_workflow_path)
        
        # Load LoRA flux workflow
        flux_lora_workflow_path = os.path.join(self.package_dir, "flux", "flux_lora_workflow.json")
        if os.path.exists(flux_lora_workflow_path):
            templates["lora"] = load_workflow_config(flux_lora_workflow_path)
        
        return templates
    
    @handle_errors("flux_workflow", "execute")
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Flux workflow"""
        # Validate parameters
        required_fields = ["prompt"]
        validate_workflow_parameters(parameters, required_fields)
        
        prompt = parameters["prompt"]
        lora = parameters.get("lora")
        steps = parameters.get("steps", 20)
        width = parameters.get("width", 1920)
        height = parameters.get("height", 1080)
        seed = parameters.get("seed", str(random.randint(1, 1000000)))
        model = parameters.get("model", "flux1-schnell.safetensors")
        negative_prompt = parameters.get("negative_prompt", "")
        
        # Create temp directory
        temp_dir = create_temp_workflow_directory(self.workflow_id)
        
        try:
            # Step 1: Generate workflow configuration
            self._update_progress(20.0)
            workflow_config, pattern, download_directory = await self._generate_workflow_config(
                prompt, lora, steps, width, height, seed, model, negative_prompt
            )
            
            # Step 2: Save workflow configuration
            self._update_progress(40.0)
            workflow_path = await self._save_workflow_config(workflow_config, temp_dir)
            
            # Step 3: Execute workflow (placeholder for actual ComfyUI execution)
            self._update_progress(60.0)
            execution_result = await self._execute_workflow(workflow_path, download_directory)
            
            # Step 4: Process results
            self._update_progress(80.0)
            results = await self._process_workflow_results(execution_result, pattern, download_directory)
            
            # Step 5: Compile final results
            self._update_progress(100.0)
            final_results = await self._compile_final_results(results, parameters)
            
            return final_results
            
        finally:
            # Cleanup temp directory
            cleanup_workflow_directory(temp_dir)
    
    async def _generate_workflow_config(
        self,
        prompt: str,
        lora: Optional[str],
        steps: int,
        width: int,
        height: int,
        seed: str,
        model: str,
        negative_prompt: str
    ) -> Tuple[Dict[str, Any], str, str]:
        """Generate workflow configuration"""
        try:
            self.logger.info(f"Generating workflow configuration for prompt: {prompt[:50]}...")
            
            # Choose workflow template
            if lora:
                if "lora" not in self.workflow_templates:
                    raise ValueError("LoRA workflow template not found")
                workflow_template = self.workflow_templates["lora"].copy()
                template_type = "lora"
            else:
                if "standard" not in self.workflow_templates:
                    raise ValueError("Standard workflow template not found")
                workflow_template = self.workflow_templates["standard"].copy()
                template_type = "standard"
            
            # Configure workflow parameters
            if template_type == "lora":
                # LoRA workflow configuration
                workflow_template["6"]["inputs"]["text"] = prompt
                workflow_template["9"]["inputs"]["filename_prefix"] = f"flux_{seed}"
                workflow_template["17"]["inputs"]["steps"] = steps
                workflow_template["12"]["inputs"]["unet_name"] = model
                workflow_template["25"]["inputs"]["noise_seed"] = int(seed)
                workflow_template["38"]["inputs"]["lora_name"] = lora
                workflow_template["46"]["inputs"]["batch_size"] = 1
                workflow_template["46"]["inputs"]["height"] = height
                workflow_template["46"]["inputs"]["width"] = width
                
                # Set negative prompt if provided
                if negative_prompt:
                    workflow_template["6"]["inputs"]["negative"] = negative_prompt
                
            else:
                # Standard workflow configuration
                workflow_template["6"]["inputs"]["text"] = prompt
                workflow_template["9"]["inputs"]["filename_prefix"] = f"flux_{seed}"
                workflow_template["17"]["inputs"]["steps"] = steps
                workflow_template["12"]["inputs"]["unet_name"] = model
                workflow_template["25"]["inputs"]["noise_seed"] = int(seed)
                workflow_template["27"]["inputs"]["batch_size"] = 1
                workflow_template["27"]["inputs"]["height"] = height
                workflow_template["27"]["inputs"]["width"] = width
                
                # Set negative prompt if provided
                if negative_prompt:
                    workflow_template["6"]["inputs"]["negative"] = negative_prompt
            
            # Set pattern and download directory
            pattern = f"flux_{seed}"
            download_directory = "/workspace/ComfyUI/output/"
            
            self.logger.info("Workflow configuration generated successfully")
            return workflow_template, pattern, download_directory
            
        except Exception as e:
            self.logger.error(f"Failed to generate workflow configuration: {e}")
            raise
    
    async def _save_workflow_config(self, workflow_config: Dict[str, Any], temp_dir: str) -> str:
        """Save workflow configuration to file"""
        try:
            self.logger.info("Saving workflow configuration")
            
            workflow_path = os.path.join(temp_dir, "workflow.json")
            save_workflow_result(workflow_config, workflow_path)
            
            self.logger.info(f"Workflow configuration saved to: {workflow_path}")
            return workflow_path
            
        except Exception as e:
            self.logger.error(f"Failed to save workflow configuration: {e}")
            raise
    
    async def _execute_workflow(self, workflow_path: str, download_directory: str) -> Dict[str, Any]:
        """Execute workflow (placeholder for actual ComfyUI execution)"""
        try:
            self.logger.info("Executing workflow")
            
            # This is a placeholder for actual ComfyUI execution
            # In a real implementation, this would:
            # 1. Send the workflow to ComfyUI API
            # 2. Monitor execution progress
            # 3. Handle errors and retries
            # 4. Return execution results
            
            # Simulate execution
            await asyncio.sleep(2)  # Simulate processing time
            
            execution_result = {
                "status": "completed",
                "execution_time": 2.0,
                "workflow_path": workflow_path,
                "download_directory": download_directory,
                "output_files": [
                    f"{download_directory}flux_123456_00001_.png",
                    f"{download_directory}flux_123456_00002_.png"
                ],
                "metadata": {
                    "execution_id": self.workflow_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            self.logger.info("Workflow executed successfully")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Failed to execute workflow: {e}")
            raise
    
    async def _process_workflow_results(
        self,
        execution_result: Dict[str, Any],
        pattern: str,
        download_directory: str
    ) -> Dict[str, Any]:
        """Process workflow execution results"""
        try:
            self.logger.info("Processing workflow results")
            
            # Process output files
            output_files = execution_result.get("output_files", [])
            processed_files = []
            
            for file_path in output_files:
                if os.path.exists(file_path):
                    file_info = {
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "created": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    }
                    processed_files.append(file_info)
            
            results = {
                "execution_result": execution_result,
                "output_files": processed_files,
                "pattern": pattern,
                "download_directory": download_directory,
                "total_files": len(processed_files)
            }
            
            self.logger.info(f"Processed {len(processed_files)} output files")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process workflow results: {e}")
            raise
    
    async def _compile_final_results(
        self,
        results: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile final workflow results"""
        try:
            self.logger.info("Compiling final results")
            
            final_results = {
                "workflow_id": self.workflow_id,
                "workflow_type": "flux_generation",
                "status": "completed",
                "parameters": parameters,
                "results": results,
                "metadata": {
                    "workflow_version": "2.0.0",
                    "execution_timestamp": self._start_time.isoformat() if self._start_time else None,
                    "completion_timestamp": self._end_time.isoformat() if self._end_time else None,
                    "execution_duration": (self._end_time - self._start_time).total_seconds() if self._start_time and self._end_time else None
                }
            }
            
            self.logger.info("Final results compiled successfully")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Failed to compile final results: {e}")
            raise


class EnhancedFluxService:
    """Enhanced Flux service with centralized utilities"""
    
    def __init__(self):
        self.logger = create_workflow_logger("flux_service")
        self.workflow = EnhancedFluxWorkflow()
    
    @handle_errors("flux_service", "generate_image")
    async def generate_image(
        self,
        prompt: str,
        lora: Optional[str] = None,
        steps: int = 20,
        width: int = 1920,
        height: int = 1080,
        seed: Optional[str] = None,
        model: str = "flux1-schnell.safetensors",
        negative_prompt: str = ""
    ) -> Dict[str, Any]:
        """Generate image with enhanced error handling"""
        try:
            self.logger.info(f"Starting image generation for prompt: {prompt[:50]}...")
            
            # Generate seed if not provided
            if not seed:
                seed = str(random.randint(1, 1000000))
            
            # Prepare parameters
            parameters = {
                "prompt": prompt,
                "lora": lora,
                "steps": steps,
                "width": width,
                "height": height,
                "seed": seed,
                "model": model,
                "negative_prompt": negative_prompt
            }
            
            # Execute workflow
            result = await self.workflow.run(parameters)
            
            self.logger.info(f"Image generation completed for prompt: {prompt[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise
    
    @handle_errors("flux_service", "generate_image_with_lora")
    async def generate_image_with_lora(
        self,
        prompt: str,
        lora: str,
        steps: int = 20,
        width: int = 1920,
        height: int = 1080,
        seed: Optional[str] = None,
        model: str = "flux1-schnell.safetensors",
        negative_prompt: str = ""
    ) -> Dict[str, Any]:
        """Generate image with LoRA"""
        return await self.generate_image(
            prompt=prompt,
            lora=lora,
            steps=steps,
            width=width,
            height=height,
            seed=seed,
            model=model,
            negative_prompt=negative_prompt
        )
    
    @handle_errors("flux_service", "generate_image_without_lora")
    async def generate_image_without_lora(
        self,
        prompt: str,
        steps: int = 20,
        width: int = 1920,
        height: int = 1080,
        seed: Optional[str] = None,
        model: str = "flux1-schnell.safetensors",
        negative_prompt: str = ""
    ) -> Dict[str, Any]:
        """Generate image without LoRA"""
        return await self.generate_image(
            prompt=prompt,
            lora=None,
            steps=steps,
            width=width,
            height=height,
            seed=seed,
            model=model,
            negative_prompt=negative_prompt
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return await self.workflow.health_check()


# Factory function for creating Flux service
def create_flux_service() -> EnhancedFluxService:
    """Create enhanced Flux service instance"""
    return EnhancedFluxService()


# Export
__all__ = [
    "EnhancedFluxWorkflow",
    "EnhancedFluxService",
    "create_flux_service"
]
