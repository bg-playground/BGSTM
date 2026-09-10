(() => {
  const renderMermaid = async () => {
    if (typeof mermaid === "undefined") {
      return;
    }

    mermaid.initialize({ startOnLoad: false });

    const nodes = document.querySelectorAll(".mermaid:not([data-processed='true'])");
    if (!nodes.length) {
      return;
    }

    await mermaid.run({ nodes });
  };

  // The script is loaded at the end of the document, so render immediately
  // for the initial page load rather than waiting for a Material lifecycle event.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderMermaid, { once: true });
  } else {
    void renderMermaid();
  }

  // Re-render new diagrams after MkDocs Material instant-navigation events.
  if (typeof document$ !== "undefined") {
    document$.subscribe(() => {
      void renderMermaid();
    });
  }
})();
