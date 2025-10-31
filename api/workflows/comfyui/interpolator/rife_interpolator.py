import json
import os
import random
from typing import Any, Dict, Tuple


class RifeInterpolator:
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)

    def interpolate_video_workflow(self,
                         input_path: str = None,
                         multiplier: int = 4,
                         target_fps: float = 24.0,
                         ckpt_name: str = "rife47.pth",
                         fast_mode: bool = True,
                         ensemble: bool = True,
                         clear_cache_after_n_frames: int = 10,
                         seed: str = "") -> Tuple[Dict[str, Any], str, str]:
        """
        Generate RIFE video interpolation workflow

        Args:
            input_path (str): Path to the input video
            multiplier (int): Frame interpolation multiplier (default: 4)
            target_fps (float): Target frame rate for output
            ckpt_name (str): RIFE checkpoint model name (default: "rife47.pth")
            fast_mode (bool): Enable fast mode (default: True)
            ensemble (bool): Enable ensemble mode (default: True)
            clear_cache_after_n_frames (int): Clear cache after N frames (default: 10)
            seed (str): Seed for generation

        Returns:
            Tuple[Dict, str, str]: (rife_workflow, pattern, download_directory)
        """
        seed = seed or str(random.randint(1, 2**63 - 1))

        # Load workflow
        workflow_path = os.path.join(self.package_dir, "rife_interpolator_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            rife_workflow = json.load(file)

        # Copy video to ComfyUI input directory
        video_filename = f"rife_input_{seed}.mp4"

        # Configure workflow parameters
        rife_workflow["4"]["inputs"]["filename_prefix"] = f"rife_{seed}"
        rife_workflow["4"]["inputs"]["frame_rate"] = target_fps
        rife_workflow["6"]["inputs"]["ckpt_name"] = ckpt_name
        rife_workflow["6"]["inputs"]["clear_cache_after_n_frames"] = clear_cache_after_n_frames
        rife_workflow["6"]["inputs"]["multiplier"] = multiplier
        rife_workflow["6"]["inputs"]["fast_mode"] = fast_mode
        rife_workflow["6"]["inputs"]["ensemble"] = ensemble
        rife_workflow["8"]["inputs"]["video"] = video_filename

        # Set pattern and download directory
        pattern = f"rife_{seed}"
        download_directory = "/workspace/ComfyUI/output/"

        return rife_workflow, pattern, download_directory

