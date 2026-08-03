(function () {
  "use strict";

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-copy"));
      if (!target) return;
      var text = target.textContent.trim();
      var original = button.textContent;
      function done() {
        button.textContent = button.getAttribute("data-copied-label") || "Copied";
        window.setTimeout(function () { button.textContent = original; }, 1800);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done);
      }
    });
  });
}());
