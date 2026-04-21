import type { GraphBehavior } from "./types";
import type { GraphViewMode } from "../types";

export function createViewModeSwitchBehavior(): GraphBehavior {
  let lastViewMode: GraphViewMode | null = null;

  return {
    id: "view-mode-switch",
    attach: () => {},
    detach: () => {
      lastViewMode = null;
    },
    onStateChange: (context, interactionState) => {
      if (interactionState.viewMode === lastViewMode) {
        return;
      }

      lastViewMode = interactionState.viewMode;
      const nextSelectedNodeId = interactionState.selectedNodeId;

      if (interactionState.viewMode === "focused" && nextSelectedNodeId) {
        context.dispatchAction({ type: "focusNode", nodeId: nextSelectedNodeId });
        return;
      }

      context.dispatchAction({ type: "fitView" });
    },
  };
}
