import comfy
from server import PromptServer
from aiohttp import web
import time
from comfy.model_management import InterruptProcessingException


class AnyType(str):
    """A special type that always compares equal to any value."""

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")


class PauseWorkflowNode:
    _instance = None  # Singleton pattern
    status_by_id = {}

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

        while self.status_by_id[id] == "paused":
            time.sleep(0.1)

        if self.status_by_id[id] == "cancelled":
            # print(f"Cancelled workflow for {id}")
            raise InterruptProcessingException()

        return {"result": (any1, any2)}


@PromptServer.instance.routes.post("/pause_workflow/continue/{node_id}")
async def handle_continue(request):
    node_id = request.match_info["node_id"].strip()
    # print(f"Continuing node {node_id}")
    PauseWorkflowNode.status_by_id[node_id] = "continue"
    return web.json_response({"status": "ok"})


@PromptServer.instance.routes.post("/pause_workflow/cancel")
async def handle_cancel(request):
    for node_id in PauseWorkflowNode.status_by_id:
        # print(f"Cancelling node {node_id}")
        PauseWorkflowNode.status_by_id[node_id] = "cancelled"
    return web.json_response({"status": "ok"})
