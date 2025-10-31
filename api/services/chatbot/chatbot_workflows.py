from typing import Dict, Any, List

class ChatbotWorkflows:
    """Service for getting available pipelines for project types"""
    
    def __init__(self):
        self.pipelines = self._initialize_pipelines()
    
    def get_pipelines_for_project_type(self, project_type: str) -> Dict[str, Any]:
        """Get available pipelines for a project type"""
        
        try:
            if not project_type:
                return {
                    "success": False,
                    "error": "Project type is required",
                    "pipelines": []
                }
            
            project_pipelines = self.pipelines.get(project_type, [])
            
            if not project_pipelines:
                return {
                    "success": False,
                    "error": f"No pipelines found for project type: {project_type}",
                    "pipelines": []
                }
            
            return {
                "success": True,
                "pipelines": project_pipelines,
                "project_type": project_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pipelines": []
            }
    
    def _initialize_pipelines(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize pipeline definitions for each project type"""
        
        return {
            "music_video_clip": [
                {
                    "id": "looped-static",
                    "name": "Looped Static",
                    "description": "Static image with looping animation",
                    "video_type": "looped-static",
                    "required_fields": [
                        "prompt_user_input",
                        "visual_style",
                        "duration"
                    ],
                    "optional_fields": [
                        "reference_images",
                        "video_style",
                        "animation_style"
                    ]
                },
                {
                    "id": "looped-animated",
                    "name": "Looped Animated",
                    "description": "Animated looping video",
                    "video_type": "looped-animated",
                    "required_fields": [
                        "prompt_user_input",
                        "visual_style",
                        "duration"
                    ],
                    "optional_fields": [
                        "reference_images",
                        "animation_style",
                        "video_style"
                    ]
                },
                {
                    "id": "recurring-scenes",
                    "name": "Recurring Scenes",
                    "description": "Multiple scenes that transition smoothly",
                    "video_type": "recurring-scenes",
                    "required_fields": [
                        "prompt_user_input",
                        "visual_style",
                        "duration",
                        "number_of_scenes"
                    ],
                    "optional_fields": [
                        "reference_images",
                        "video_transition",
                        "audio_transition"
                    ]
                }
            ],
            "video_clip": [
                {
                    "id": "standard-video",
                    "name": "Standard Video",
                    "description": "Standard video generation pipeline",
                    "required_fields": [
                        "prompt_user_input",
                        "visual_style",
                        "duration"
                    ],
                    "optional_fields": [
                        "reference_images",
                        "video_format"
                    ]
                }
            ],
            "business_ad": [
                {
                    "id": "business-ad-standard",
                    "name": "Business Ad Standard",
                    "description": "Standard business advertisement pipeline",
                    "required_fields": [
                        "prompt_user_input",
                        "visual_style",
                        "duration"
                    ],
                    "optional_fields": [
                        "reference_images",
                        "brand_colors",
                        "logo"
                    ]
                }
            ],
            "automate_workflow": [
                {
                    "id": "automation-standard",
                    "name": "Automation Workflow",
                    "description": "Automated workflow pipeline",
                    "required_fields": [
                        "prompt_user_input",
                        "workflow_type"
                    ],
                    "optional_fields": [
                        "reference_images",
                        "automation_params"
                    ]
                }
            ]
        }

_chatbot_workflows = None

def get_chatbot_workflows() -> ChatbotWorkflows:
    """Get singleton chatbot workflows instance"""
    
    global _chatbot_workflows
    if _chatbot_workflows is None:
        _chatbot_workflows = ChatbotWorkflows()
    return _chatbot_workflows

