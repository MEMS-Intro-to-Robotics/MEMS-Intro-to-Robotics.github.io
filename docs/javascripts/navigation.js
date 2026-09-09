// Reveal the sidebar category containing a directly linked page heading.
function revealNavigationAnchor() {
  if (!window.location.hash) return;
  document.querySelectorAll('.md-nav--secondary a[href]').forEach((link) => {
    if (link.hash !== window.location.hash) return;
    let category = link.closest('details.toc-category');
    while (category) {
      category.open = true;
      category = category.parentElement.closest('details.toc-category');
    }
  });
}

window.addEventListener('hashchange', revealNavigationAnchor);
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', revealNavigationAnchor);
} else {
  revealNavigationAnchor();
}
