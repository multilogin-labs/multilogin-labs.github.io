(function () {
  "use strict";

  function setYear() {
    var yearNodes = document.querySelectorAll("[data-year]");
    var year = String(new Date().getFullYear());
    yearNodes.forEach(function (node) {
      node.textContent = year;
    });
  }

  function copyCode(code) {
    if (!code) {
      return;
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).catch(function () {
        fallbackCopy(code);
      });
      return;
    }

    fallbackCopy(code);
  }

  function fallbackCopy(code) {
    var helper = document.createElement("textarea");
    helper.value = code;
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    document.body.removeChild(helper);
  }

  function wireCopyButtons() {
    var buttons = document.querySelectorAll("[data-copy-code]");
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var code = button.getAttribute("data-copy-code");
        copyCode(code);
        showToast(code + " copied");
      });
    });
  }

  function showToast(message) {
    var toast = document.getElementById("site-toast");
    if (!toast) {
      return;
    }

    toast.textContent = message;
    toast.style.display = "block";

    window.setTimeout(function () {
      toast.style.display = "none";
    }, 2600);
  }

  document.addEventListener("DOMContentLoaded", function () {
    setYear();
    wireCopyButtons();
  });
})();
