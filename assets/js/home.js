(function () {
  "use strict";

  document.querySelectorAll("[data-year]").forEach(function (n) {
    n.textContent = String(new Date().getFullYear());
  });

  function showToast(msg) {
    var toast = document.getElementById("site-toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.style.display = "block";
    setTimeout(function () {
      toast.style.display = "none";
    }, 2200);
  }

  function copyText(code, el) {
    var done = function () {
      if (el) {
        el.classList.add("is-copied");
        setTimeout(function () {
          el.classList.remove("is-copied");
        }, 1200);
      }
      showToast(code + " copied — paste at checkout");
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).then(done).catch(fallback);
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
      done();
    }
  }

  document.querySelectorAll("[data-copy-code]").forEach(function (btn) {
    var activate = function () {
      copyText(btn.getAttribute("data-copy-code"), btn);
    };
    btn.addEventListener("click", activate);
    if (btn.getAttribute("tabindex") === "0") {
      btn.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      });
    }
  });

  var sticky = document.getElementById("aff-sticky");
  if (sticky) {
    var toggleSticky = function () {
      var show = window.scrollY >= 180;
      sticky.hidden = !show;
      document.body.classList.toggle("has-aff-sticky", show);
    };
    toggleSticky();
    window.addEventListener("scroll", toggleSticky, { passive: true });
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
    requestIdleCallback(loadGtag, { timeout: 8000 });
  } else {
    setTimeout(loadGtag, 3500);
  }

  document.querySelectorAll('a[href*="multilogin.com/pricing"]').forEach(function (link) {
    link.addEventListener("click", function () {
      if (typeof window.gtag !== "function") return;
      window.gtag("event", "select_promotion", {
        promotion_id: "multilogin_checkout",
        promotion_name: "SAAS50",
        creative_name: "homepage",
      });
    });
  });
})();
