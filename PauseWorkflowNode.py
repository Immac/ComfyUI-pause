import comfy
from server import PromptServer
from aiohttp import web
import threading
from comfy.model_management import InterruptProcessingException


class AnyType(str):
    """A special type that always compares equal to any value."""

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")


class PauseWorkflowNode:
    _instance = None  # Singleton pattern
    status_by_id = {}
    events_by_id = {}  # Dictionary to store threading.Event objects for each node

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any1": (any_type,),
            },
            "optional": {
                "any2": (any_type,),
            },
            "hidden": {
                "id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = (
        any_type,
        any_type,
    )
    RETURN_NAMES = (
        "any1",
        "any2",
    )
    FUNCTION = "execute"
    CATEGORY = "utils"
    OUTPUT_NODE = True

    def execute(self, any1=None, any2=None, id=None):
        # print(f"Pausing workflow for {id}")
        self.status_by_id[id] = "paused"
        
        # Create an event for this node if it doesn't exist
        if id not in self.events_by_id:
            self.events_by_id[id] = threading.Event()
        
        # Clear the event to ensure it's in waiting state
        self.events_by_id[id].clear()
        
        # Wait for the event to be set (when continue or cancel is called)
        self.events_by_id[id].wait()

        if self.status_by_id[id] == "cancelled":
            # print(f"Cancelled workflow for {id}")
            # Clean up the event
            del self.events_by_id[id]
            raise InterruptProcessingException()

        # Clean up the event after successful continuation
        del self.events_by_id[id]
        return {"result": (any1, any2)}


@PromptServer.instance.routes.post("/pause_workflow/continue/{node_id}")
async def handle_continue(request):
    node_id = request.match_info["node_id"].strip()
    # print(f"Continuing node {node_id}")
    PauseWorkflowNode.status_by_id[node_id] = "continue"
    
    # Set the event to wake up the waiting execute method
    if node_id in PauseWorkflowNode.events_by_id:
        PauseWorkflowNode.events_by_id[node_id].set()
    
    return web.json_response({"status": "ok"})


@PromptServer.instance.routes.post("/pause_workflow/cancel")
async def handle_cancel(request):
    for node_id in PauseWorkflowNode.status_by_id:
        # print(f"Cancelling node {node_id}")
        PauseWorkflowNode.status_by_id[node_id] = "cancelled"
        
        # Set the event to wake up the waiting execute method
        if node_id in PauseWorkflowNode.events_by_id:
            PauseWorkflowNode.events_by_id[node_id].set()
    
    return web.json_response({"status": "ok"})
