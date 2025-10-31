import json
import os
import random
from typing import Any, Dict, Tuple


class Flux:
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)


    def generate_image_with_lora(self, prompt: str="", lora: str="", steps: int=20, width: int=1920, height: int=1080, seed: str="", model: str="flux1-schnell.safetensors", negative_prompt: str="") -> Tuple[Dict[str, Any], str, str]:
        """
        Generate image with LoRA using flux_lora.json workflow
        Args:
            prompt (str): Text prompt for image generation
            lora (str): Name of the LoRA model to use
            steps (int): Number of generation steps
            width (int): Width of output image
            height (int): Height of output image
            seed (str): Seed for generation
            model (str): Model name
            negative_prompt (str): Negative prompt to avoid certain elements
        Returns:
            Tuple[Dict, str, str]: (flux_workflow, pattern, download_directory)
        """

        # Load the workflow template
        workflow_path = os.path.join(self.package_dir, "flux_lora_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            flux_lora_workflow = json.load(file)

        # Configure workflow parameters
        flux_lora_workflow["6"]["inputs"]["text"] = prompt
        flux_lora_workflow["9"]["inputs"]["filename_prefix"] = f"flux_{seed}"
        flux_lora_workflow["17"]["inputs"]["steps"] = steps
        flux_lora_workflow["12"]["inputs"]["unet_name"] = model
        flux_lora_workflow["25"]["inputs"]["noise_seed"] = int(seed)
        flux_lora_workflow["38"]["inputs"]["lora_name"] = lora
        flux_lora_workflow["46"]["inputs"]["batch_size"] = 1
        flux_lora_workflow["46"]["inputs"]["height"] = height
        flux_lora_workflow["46"]["inputs"]["width"] = width

        # Set pattern and download directory
        pattern = f"flux_{seed}"
        download_directory = "/workspace/ComfyUI/output/"

        return flux_lora_workflow, pattern, download_directory

    def generate_image_without_lora(self, prompt: str="", steps: int=20, width: int=1920, height: int=1080, seed: str="", model: str="flux1-schnell.safetensors", negative_prompt: str="") -> Tuple[Dict[str, Any], str, str]:
        """
        Generate image without LoRA using flux_workflow.json workflow
        Args:
            prompt (str): Text prompt for image generation
            steps (int): Number of generation steps
            width (int): Width of output image
            height (int): Height of output image
            seed (str): Seed for generation
            model (str): Model name
            negative_prompt (str): Negative prompt to avoid certain elements
        Returns:
            Tuple[Dict, str, str]: (flux_workflow, pattern, download_directory)
        """

        # Load the workflow template
        workflow_path = os.path.join(self.package_dir, "flux_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            flux_workflow = json.load(file)

        # Configure workflow parameters
        flux_workflow["6"]["inputs"]["text"] = prompt
        flux_workflow["9"]["inputs"]["filename_prefix"] = f"flux_{seed}"
        flux_workflow["17"]["inputs"]["steps"] = steps
        flux_workflow["12"]["inputs"]["unet_name"] = model
        flux_workflow["25"]["inputs"]["noise_seed"] = int(seed)
        flux_workflow["27"]["inputs"]["batch_size"] = 1
        flux_workflow["27"]["inputs"]["height"] = height
        flux_workflow["27"]["inputs"]["width"] = width

        # Set pattern and download directory
        pattern = f"flux_{seed}"
        download_directory = "/workspace/ComfyUI/output/"

        return flux_workflow, pattern, download_directory

    def generate_image_workflow(self, prompt: str="", lora: str=None, steps: int=30, width: int=1920, height: int=1080, seed: str=None, model: str="flux1-schnell.safetensors", negative_prompt: str="") -> Tuple[Dict[str, Any], str, str]:
        """
        Generate image workflow with or without LoRA based on lora parameter
        Args:
            prompt (str): Text prompt for image generation
            lora (str): Name of the LoRA model to use (None for no LoRA)
            steps (int): Number of generation steps
            width (int): Width of output image
            height (int): Height of output image
            seed (str): Seed for generation
            model (str): Model name
            negative_prompt (str): Negative prompt to avoid certain elements
        Returns:
            Tuple[Dict, str, str]: (flux_workflow, pattern, download_directory)
        """

        seed = seed or str(random.randint(1, 2**63 - 1))

        # Generate the appropriate workflow
        if lora is None or lora == "":
            return self.generate_image_without_lora(prompt, steps, width, height, seed, model, negative_prompt)
        else:
            return self.generate_image_with_lora(prompt, lora, steps, width, height, seed, model, negative_prompt)