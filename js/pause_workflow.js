import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const postContinue = (nodeId) => fetch("/pause_workflow/continue/" + nodeId, { method: "POST" });
const postCancel = () => fetch("/pause_workflow/cancel", { method: "POST" });

app.registerExtension({
  name: "wywywywy-pause",
  nodeCreated(node) {
    if (node.comfyClass === "PauseWorkflowNode") {
      const continueBtn = node.addWidget("button", "✔️ Continue", "CONTINUE", () => {
        postContinue(node.id);
      });

      const cancelBtn = node.addWidget("button", "⛔ Cancel", "CANCEL", () => {
        postCancel();
      });
    }
  },
  setup() {
    // handle workflow cancel by other means
    const original_api_interrupt = api.interrupt;
    api.interrupt = function () {
      postCancel();
      original_api_interrupt.apply(this, arguments);
    }
  },
});