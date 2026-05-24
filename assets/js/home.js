(function () {
  "use strict";

  var year = String(new Date().getFullYear());
  document.querySelectorAll("[data-year]").forEach(function (n) {
    n.textContent = year;
  });

  function copyText(code) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).catch(fallback);
    } else {
      fallback();
    }
    function fallback() {
      var t = document.createElement("textarea");
      t.value = code;
      document.body.appendChild(t);
      t.select();
      document.execCommand("copy");
      document.body.removeChild(t);
    }
    var toast = document.getElementById("site-toast");
    if (toast) {
      toast.textContent = code + " copied";
      toast.style.display = "block";
      setTimeout(function () {
        toast.style.display = "none";
      }, 2200);
    }
  }

  document.querySelectorAll("[data-copy-code]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      copyText(btn.getAttribute("data-copy-code"));
    });
  });

  var sticky = document.getElementById("aff-sticky");
  if (sticky) {
    document.body.classList.add("has-aff-sticky");
    function onScroll() {
      sticky.hidden = window.scrollY < 240;
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function loadGtag() {
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

  if ("requestIdleCallback" in window) {
    requestIdleCallback(loadGtag, { timeout: 3500 });
  } else {
    setTimeout(loadGtag, 1800);
  }
})();
