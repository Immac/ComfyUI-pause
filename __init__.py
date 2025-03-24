from .PauseWorkflowNode import PauseWorkflowNode

WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "PauseWorkflowNode": PauseWorkflowNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PauseWorkflowNode": "Pause Workflow Node",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
