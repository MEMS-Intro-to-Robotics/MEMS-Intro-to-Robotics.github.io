window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex|math-render"
  }
};

// Render equations stored in data-latex attributes
function renderLabMath() {
  // Display math
  document.querySelectorAll('.math-display[data-latex]').forEach(function(el) {
    var wrapper = document.createElement('div');
    wrapper.className = 'math-render';
    wrapper.style.textAlign = 'center';
    wrapper.style.margin = '1em 0';
    wrapper.textContent = '\\[' + el.dataset.latex + '\\]';
    el.parentNode.insertBefore(wrapper, el);
    el.remove();
  });
  // Inline math
  document.querySelectorAll('.math-inline[data-latex]').forEach(function(el) {
    var wrapper = document.createElement('span');
    wrapper.className = 'math-render';
    wrapper.textContent = '\\(' + el.dataset.latex + '\\)';
    el.parentNode.insertBefore(wrapper, el);
    el.remove();
  });
}

document$.subscribe(function() {
  renderLabMath();
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
})
