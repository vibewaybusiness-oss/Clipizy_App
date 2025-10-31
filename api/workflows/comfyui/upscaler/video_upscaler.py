import json
import os
import random
from typing import Any, Dict, Tuple


class VideoUpscaler:
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)

    def upscale_video_workflow(self, input_path: str, frame_rate: float = 25.0, seed: str = "") -> Tuple[Dict[str, Any], str, str]:
        """
        Generate video upscaling workflow

        Args:
            input_path (str): Path to the input video
            frame_rate (float): Output frame rate (default: 25.0)
            seed (str): Seed for generation

        Returns:
            Tuple[Dict, str, str]: (upscaler_workflow, pattern, download_directory)
        """
        seed = seed or str(random.randint(1, 2**63 - 1))

        # Load workflow
        workflow_path = os.path.join(self.package_dir, "video_upscaler_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            upscaler_workflow = json.load(file)

            # Copy video to ComfyUI input directory
            video_filename = f"upscaler_input_{seed}.mp4"

            # Update workflow parameters
            upscaler_workflow["7"]["inputs"]["video"] = video_filename
            upscaler_workflow["8"]["inputs"]["filename_prefix"] = f"upscaler_{seed}"
            upscaler_workflow["8"]["inputs"]["frame_rate"] = frame_rate

        # Set pattern and download directory
        pattern = f"upscaler_{seed}"
        download_directory = "/workspace/ComfyUI/output/"

        return upscaler_workflow, pattern, download_directory