import json
import os
import random
from typing import Any, Dict, Tuple


class MMAudio:
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)

    def generate_audio_for_video_workflow(self,
                                input_path: str,
                                prompt: str = "",
                                negative_prompt: str = "",
                                steps: int = 25,
                                cfg: float = 4.5,
                                seed: str = "",
                                mask_away_clip: bool = False,
                                force_offload: bool = True,
                                loop_count: int = 0,
                                crf: int = 19,
                                save_metadata: bool = True,
                                trim_to_audio: bool = False) -> Tuple[Dict[str, Any], str, str]:
        """
        Generate audio for input video using MMAudio model workflow

        Args:
            input_path (str): Path to the input video
            prompt (str): Positive prompt for audio generation
            negative_prompt (str): Negative prompt for audio generation
            steps (int): Number of sampling steps (default: 25)
            cfg (float): CFG scale (default: 4.5)
            seed (str): Random seed
            mask_away_clip (bool): Whether to mask away clip (default: False)
            force_offload (bool): Force model offloading (default: True)
            loop_count (int): Number of loops (default: 0)
            crf (int): Video compression quality (default: 19)
            save_metadata (bool): Save metadata (default: True)
            trim_to_audio (bool): Trim video to audio length (default: False)

        Returns:
            Tuple[Dict, str, str]: (mmaudio_workflow, pattern, download_directory)
        """

        seed = seed or str(random.randint(1, 2**63 - 1))

        # Load workflow
        workflow_path = os.path.join(self.package_dir, "mmAudio_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            mmaudio_workflow = json.load(file)

        # Generate unique filename prefix
        filename_prefix = f"MMaudio_{seed}"

        # Update workflow parameters
        mmaudio_workflow["91"]["inputs"]["video"] = f"{filename_prefix}.mp4"
        mmaudio_workflow["92"]["inputs"]["steps"] = steps
        mmaudio_workflow["92"]["inputs"]["cfg"] = cfg
        mmaudio_workflow["92"]["inputs"]["seed"] = int(seed)
        mmaudio_workflow["92"]["inputs"]["prompt"] = prompt
        mmaudio_workflow["92"]["inputs"]["negative_prompt"] = negative_prompt
        mmaudio_workflow["92"]["inputs"]["mask_away_clip"] = mask_away_clip
        mmaudio_workflow["92"]["inputs"]["force_offload"] = force_offload
        mmaudio_workflow["97"]["inputs"]["loop_count"] = loop_count
        mmaudio_workflow["97"]["inputs"]["filename_prefix"] = filename_prefix
        mmaudio_workflow["97"]["inputs"]["crf"] = crf
        mmaudio_workflow["97"]["inputs"]["save_metadata"] = save_metadata
        mmaudio_workflow["97"]["inputs"]["trim_to_audio"] = trim_to_audio

        # Set pattern and download directory
        pattern = filename_prefix
        download_directory = "/workspace/ComfyUI/output/"

        return mmaudio_workflow, pattern, download_directory