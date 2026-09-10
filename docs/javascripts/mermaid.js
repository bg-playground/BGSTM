document$.subscribe(() => {
  if (typeof mermaid === "undefined") {
    return;
  }

  mermaid.initialize({ startOnLoad: false });
  mermaid.run({ nodes: document.querySelectorAll(".mermaid") });
});
