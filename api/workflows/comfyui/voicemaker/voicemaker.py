import json
import os
import random
from typing import Any, Dict, Tuple


class Voicemaker:
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)


    def generate_voiceover_workflow(self, text: str="", audio_input: str="", model: str="VibeVoice-1.5B", diffusion_steps: int=20, seed: str="", cfg_scale: float=1.3, temperature: float=0.95, top_p: float=0.95, use_sampling: bool=False, attention_type: str="auto", free_memory_after_generate: bool=True) -> Tuple[Dict[str, Any], str, str]:
        """
        Generate voiceover using vibe_voice_workflow.json workflow
        Args:
            text (str): Text to convert to speech
            audio_input (str): Path to reference audio file for voice cloning
            model (str): VibeVoice model to use
            diffusion_steps (int): Number of diffusion steps
            seed (str): Random seed for generation
            cfg_scale (float): Classifier-free guidance scale
            temperature (float): Sampling temperature
            top_p (float): Top-p sampling parameter
            use_sampling (bool): Whether to use sampling
            attention_type (str): Attention mechanism type
            free_memory_after_generate (bool): Whether to free memory after generation
        Returns:
            Tuple[Dict, str, str]: (voiceover_workflow, pattern, download_directory)
        """

        seed = seed or str(random.randint(1, 2**63 - 1))

        # Load workflow
        workflow_path = os.path.join(self.package_dir, "vibe_voice_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            voiceover_workflow = json.load(file)

        # Configure workflow parameters
        voiceover_workflow["15"]["inputs"]["audio"] = audio_input
        voiceover_workflow["36"]["inputs"]["text"] = text
        voiceover_workflow["36"]["inputs"]["model"] = model
        voiceover_workflow["36"]["inputs"]["attention_type"] = attention_type
        voiceover_workflow["36"]["inputs"]["free_memory_after_generate"] = free_memory_after_generate
        voiceover_workflow["36"]["inputs"]["diffusion_steps"] = diffusion_steps
        voiceover_workflow["36"]["inputs"]["seed"] = int(seed)
        voiceover_workflow["36"]["inputs"]["cfg_scale"] = cfg_scale
        voiceover_workflow["36"]["inputs"]["use_sampling"] = use_sampling
        voiceover_workflow["36"]["inputs"]["temperature"] = temperature
        voiceover_workflow["36"]["inputs"]["top_p"] = top_p

        # Set pattern and download directory
        pattern = f"voiceover_{seed}"
        download_directory = "/workspace/ComfyUI/output/"

        return voiceover_workflow, pattern, download_directory
