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

  function wireAffSticky() {
    var bar = document.getElementById("aff-sticky");
    if (!bar) {
      return;
    }

    function toggle() {
      var show = window.scrollY >= 280;
      bar.hidden = !show;
      document.body.classList.toggle("has-aff-sticky", show);
    }

    toggle();
    window.addEventListener("scroll", toggle, { passive: true });
  }

  function loadGtag() {
    if (document.body && document.body.classList.contains("home-page")) {
      return;
    }
    var s = document.createElement("script");
    s.src = "https://www.googletagmanager.com/gtag/js?id=AW-18118906401";
    s.async = true;
    s.onload = function () {
      window.gtag("js", new Date());
      window.gtag("config", "AW-18118906401");
    };
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    document.head.appendChild(s);
  }

  function wireAffiliateClicks() {
    document.querySelectorAll('a[href*="/go/multilogin"]').forEach(function (link) {
      link.addEventListener("click", function () {
        if (typeof window.gtag !== "function") {
          return;
        }
        window.gtag("event", "select_promotion", {
          promotion_id: "multilogin_checkout",
          promotion_name: "SAAS50",
          creative_name: "inner_page",
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setYear();
    wireCopyButtons();
    wireAffSticky();
    wireAffiliateClicks();
    if ("requestIdleCallback" in window) {
      requestIdleCallback(loadGtag, { timeout: 8000 });
    } else {
      setTimeout(loadGtag, 3500);
    }
  });
})();
