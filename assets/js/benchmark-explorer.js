(function () {
  "use strict";

  var COMPARE_MAP = {
    "multilogin-x": "/compare/multilogin-alternatives/",
    gologin: "/compare/multilogin-vs-gologin/",
    adspower: "/compare/multilogin-vs-adspower/",
    "dolphin-anty": "/compare/multilogin-vs-dolphin-anty/",
    incogniton: "/compare/multilogin-vs-incogniton/",
    kameleo: "/compare/multilogin-vs-kameleo/",
    "octo-browser": "/compare/multilogin-vs-octo-browser/",
    undetectable: "/compare/multilogin-vs-undetectable/"
  };

  var state = { rows: [], report: null };

  function $(id) {
    return document.getElementById(id);
  }

  function bandClass(band) {
    if (band === "A") return "band-a";
    if (band === "B") return "band-b";
    return "band-c";
  }

  function compareUrl(id) {
    return COMPARE_MAP[id] || "/compare/multilogin-alternatives/";
  }

  function renderMeta(report) {
    var el = $("benchmark-meta");
    if (!el || !report) return;
    el.innerHTML =
      "<p class=\"small\"><strong>Report:</strong> " +
      report.report_id +
      " · <strong>Methodology:</strong> v" +
      report.methodology_version +
      " · <strong>Published:</strong> " +
      report.published +
      " · <a href=\"" +
      (report.full_report_url || "#") +
      "\">Full report</a> · <a href=\"/data/benchmark-matrix-" +
      report.report_id +
      ".json\">Download JSON</a></p>";
  }

  function renderStats(rows) {
    var stats = $("benchmark-stats");
    if (!stats) return;
    var bands = { A: 0, B: 0, C: 0 };
    var blockers = 0;
    rows.forEach(function (r) {
      bands[r.band] = (bands[r.band] || 0) + 1;
      if (r.blocker) blockers += 1;
    });
    stats.innerHTML =
      "<div class=\"metric\"><strong>" +
      rows.length +
      "</strong><span>Shown</span></div>" +
      "<div class=\"metric\"><strong>" +
      bands.A +
      "</strong><span>Band A</span></div>" +
      "<div class=\"metric\"><strong>" +
      bands.B +
      "</strong><span>Band B</span></div>" +
      "<div class=\"metric\"><strong>" +
      blockers +
      "</strong><span>Blockers</span></div>";
  }

  function filteredRows() {
    var q = ($("benchmark-search") && $("benchmark-search").value.toLowerCase()) || "";
    var band = $("benchmark-band") ? $("benchmark-band").value : "all";
    var blockersOnly = $("benchmark-blockers") && $("benchmark-blockers").checked;
  return state.rows
      .filter(function (r) {
        if (band !== "all" && r.band !== band) return false;
        if (blockersOnly && !r.blocker) return false;
        if (q && r.name.toLowerCase().indexOf(q) === -1 && r.id.indexOf(q) === -1) return false;
        return true;
      })
      .sort(function (a, b) {
        return b.score - a.score;
      });
  }

  function renderTable() {
    var tbody = $("benchmark-tbody");
    if (!tbody) return;
    var rows = filteredRows();
    renderStats(rows);
    if (!rows.length) {
      tbody.innerHTML = "<tr><td colspan=\"6\">No platforms match filters.</td></tr>";
      return;
    }
    tbody.innerHTML = rows
      .map(function (r) {
        return (
          "<tr>" +
          "<td><strong>" +
          r.name +
          "</strong><br><span class=\"small\">" +
          r.id +
          "</span></td>" +
          "<td><span class=\"band-pill " +
          bandClass(r.band) +
          "\">" +
          r.band +
          "</span></td>" +
          "<td>" +
          r.score.toFixed(1) +
          "</td>" +
          "<td>" +
          r.evidence_level +
          "</td>" +
          "<td>" +
          (r.blocker ? "<span class=\"text-danger\">Yes</span>" : "No") +
          "</td>" +
          "<td class=\"small\">" +
          r.caveat +
          "</td>" +
          "<td><a href=\"" +
          compareUrl(r.id) +
          "\">Compare</a></td>" +
          "</tr>"
        );
      })
      .join("");
  }

  function exportCsv() {
    var rows = filteredRows();
    var lines = ["id,name,score,band,evidence_level,blocker,caveat"];
    rows.forEach(function (r) {
      lines.push(
        [
          r.id,
          '"' + r.name.replace(/"/g, '""') + '"',
          r.score,
          r.band,
          r.evidence_level,
          r.blocker,
          '"' + (r.caveat || "").replace(/"/g, '""') + '"'
        ].join(",")
      );
    });
    var blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "benchmark-" + (state.report && state.report.report_id) + "-export.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function loadDataset(url) {
    return fetch(url).then(function (res) {
      if (!res.ok) throw new Error("Failed to load dataset");
      return res.json();
    });
  }

  function applyReport(report) {
    state.report = report;
    state.rows = report.platforms || [];
    renderMeta(report);
    renderTable();
  }

  function wireControls() {
    ["benchmark-search", "benchmark-band", "benchmark-blockers"].forEach(function (id) {
      var el = $(id);
      if (el) {
        el.addEventListener("input", renderTable);
        el.addEventListener("change", renderTable);
      }
    });
    var exportBtn = $("benchmark-export");
    if (exportBtn) exportBtn.addEventListener("click", exportCsv);
    var select = $("benchmark-dataset");
    if (select) {
      select.addEventListener("change", function () {
        loadDataset(select.value)
          .then(applyReport)
          .catch(function () {
            showError("Could not load selected dataset.");
          });
      });
    }
  }

  function showError(msg) {
    var tbody = $("benchmark-tbody");
    if (tbody) tbody.innerHTML = "<tr><td colspan=\"6\">" + msg + "</td></tr>";
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!$("benchmark-explorer")) return;
    wireControls();
    var select = $("benchmark-dataset");
    var initial = select ? select.value : "/data/benchmark-matrix-2026-04.json";
    loadDataset(initial)
      .then(applyReport)
      .catch(function () {
        showError("Unable to load benchmark data. Try again or download JSON from /data/.");
      });
  });
})();
