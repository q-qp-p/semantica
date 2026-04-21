import type { GraphBehavior } from "./types";

export function createSearchFocusBehavior(): GraphBehavior {
  let lastSelectedNodeId = "";

  return {
    id: "search-focus",
    attach: () => {},
    detach: () => {
      lastSelectedNodeId = "";
    },
    onStateChange: (context, interactionState) => {
      const nextSelectedNodeId = interactionState.selectedNodeId;
      if (!nextSelectedNodeId || nextSelectedNodeId === lastSelectedNodeId) {
        lastSelectedNodeId = nextSelectedNodeId;
        return;
      }

      lastSelectedNodeId = nextSelectedNodeId;
      context.dispatchAction({ type: "centerSelection", nodeId: nextSelectedNodeId });
    },
  };
}
