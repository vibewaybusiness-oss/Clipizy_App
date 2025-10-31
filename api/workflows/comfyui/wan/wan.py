import json
import os
import random
from typing import Any, Dict, Tuple


class Wan:
    def __init__(self):
        self.package_dir = os.path.dirname(__file__)

    def generate_video_from_text_workflow(self,
                                  prompt: str = "",
                                  negative_prompt: str = "色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走",
                                  width: int = 832,
                                  height: int = 480,
                                  num_frames: int = 121,
                                  frame_rate: int = 16,
                                  seed: str = "") -> Tuple[Dict[str, Any], str, str]:
        """
        Generate video from text prompt using Wan 2.2 text-to-video model

        Args:
            prompt (str): Positive prompt for video generation
            negative_prompt (str): Negative prompt for video generation
            width (int): Video width (default: 832)
            height (int): Video height (default: 480)
            num_frames (int): Number of frames (default: 121)
            frame_rate (int): Frames per second (default: 16)
            seed (str): Seed for generation

        Returns:
            Tuple[Dict, str, str]: (wan_workflow, pattern, download_directory)
        """

        seed = seed or str(random.randint(1, 2**63 - 1))

        # Load workflow
        workflow_path = os.path.join(self.package_dir, "wan2.2_t2v_lightx_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            wan_workflow = json.load(file)

        # Update workflow parameters
        wan_workflow["6"]["inputs"]["text"] = prompt
        wan_workflow["7"]["inputs"]["text"] = negative_prompt
        wan_workflow["67"]["inputs"]["noise_seed"] = int(seed)
        wan_workflow["61"]["inputs"]["width"] = width
        wan_workflow["61"]["inputs"]["height"] = height
        wan_workflow["61"]["inputs"]["length"] = num_frames
        wan_workflow["28"]["inputs"]["frame_rate"] = frame_rate
        wan_workflow["28"]["inputs"]["filename_prefix"] = f"wan_ttv_{seed}"

        # Set pattern and download directory
        pattern = f"wan_ttv_{seed}"
        download_directory = "/workspace/ComfyUI/output/"

        return wan_workflow, pattern, download_directory

    def generate_video_from_image_camera_control_workflow(self,
                                  input_image_path: str,
                                  prompt: str = "",
                                  negative_prompt: str = "色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走",
                                  width: int = 1280,
                                  height: int = 720,
                                  num_frames: int = 81,
                                  frame_rate: int = 16,
                                  seed: str = "",
                                  camera_motions: list = None,
                                  speed: float = 0.2) -> Tuple[Dict[str, Any], str, str]:
        """
        Generate video from input image using Wan 2.2 image-to-video model with camera control

        Args:
            input_image_path (str): Path to the input image
            prompt (str): Positive prompt for video generation
            negative_prompt (str): Negative prompt for video generation
            width (int): Video width (default: 1280)
            height (int): Video height (default: 720)
            num_frames (int): Number of frames (default: 81)
            frame_rate (int): Frames per second (default: 16)
            seed (str): Seed for generation
            camera_motions (list): List of camera motion types - options: Static, Pan Up, Pan Down, Pan Left, Pan Right, Zoom In, Zoom Out, Roll Clockwise, Roll Anticlockwise, Tilt Down, Tilt Up, Tilt Left, Tilt Right (default: ["Static"])
            speed (float): Camera motion speed (default: 0.2)

        Returns:
            Tuple[Dict, str, str]: (wan_workflow, pattern, download_directory)
        """

        seed = seed or str(random.randint(1, 2**63 - 1))

        # Set default camera motions if none provided
        if camera_motions is None:
            camera_motions = ["Static"]

        # Ensure we have at least 6 motion types (pad with Static if needed)
        while len(camera_motions) < 6:
            camera_motions.append("Static")

        # Take only the first 6 motions
        camera_motions = camera_motions[:6]

        # Load workflow
        workflow_path = os.path.join(self.package_dir, "wan2.2_itv_camera_control_workflow.json")
        with open(workflow_path, 'r', encoding='utf-8-sig') as file:
            wan_workflow = json.load(file)

        image_filename = f"wan_input_{seed}.png"

        # Update workflow parameters
        wan_workflow["127"]["inputs"]["positive_prompt"] = prompt
        wan_workflow["127"]["inputs"]["negative_prompt"] = negative_prompt
        wan_workflow["27"]["inputs"]["seed"] = int(seed)
        wan_workflow["117"]["inputs"]["seed"] = int(seed)
        wan_workflow["30"]["inputs"]["filename_prefix"] = f"wan_camera_{seed}"
        wan_workflow["30"]["inputs"]["frame_rate"] = frame_rate
        wan_workflow["58"]["inputs"]["image"] = image_filename
        wan_workflow["97"]["inputs"]["width"] = width
        wan_workflow["97"]["inputs"]["height"] = height
        wan_workflow["63"]["inputs"]["num_frames"] = num_frames
        wan_workflow["139"]["inputs"]["num_frames"] = num_frames

        # Update camera control parameters from the list
        wan_workflow["142"]["inputs"]["motion_type1"] = camera_motions[0]
        wan_workflow["142"]["inputs"]["motion_type2"] = camera_motions[1]
        wan_workflow["142"]["inputs"]["motion_type3"] = camera_motions[2]
        wan_workflow["142"]["inputs"]["motion_type4"] = camera_motions[3]
        wan_workflow["142"]["inputs"]["motion_type5"] = camera_motions[4]
        wan_workflow["142"]["inputs"]["motion_type6"] = camera_motions[5]
        wan_workflow["142"]["inputs"]["speed"] = speed
        wan_workflow["142"]["inputs"]["frame_length"] = num_frames

        # Set pattern and download directory
        pattern = f"wan_camera_{seed}"
        download_directory = "/workspace/ComfyUI/temp/"

        return wan_workflow, pattern, download_directory