(function () {
  "use strict";

  var SITE_TZ = window.SITE_TZ || "America/Detroit";
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }

  // ---- Mobile navigation ----------------------------------------------------
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (toggle) {
    toggle.addEventListener("click", function () { setNav(!document.body.classList.contains("nav-open")); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setNav(false); });
    if (nav) nav.addEventListener("click", function (e) { if (e.target.closest && e.target.closest("a")) setNav(false); });
  }

  // ---- Upcoming sessions: hide the ones that have ended, mark the next -------
  // Offset (ms) between UTC and the wall clock in `tz` at instant `date`.
  function tzOffset(date, tz) {
    var parts = {};
    new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hourCycle: "h23",
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit"
    }).formatToParts(date).forEach(function (p) { parts[p.type] = p.value; });
    return Date.UTC(+parts.year, +parts.month - 1, +parts.day, +parts.hour, +parts.minute, +parts.second) - date.getTime();
  }
  // "2026-10-16T16:00" read as wall-clock time in `tz`.
  function wallTimeToDate(iso, tz) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso || "");
    if (!m) return null;
    var guess = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
    var t = guess - tzOffset(new Date(guess), tz);
    return new Date(guess - tzOffset(new Date(t), tz));
  }

  var now = Date.now();
  each(document.querySelectorAll("tbody[data-upcoming]"), function (tbody) {
    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr[data-start]"));
    var remaining = rows.filter(function (row) {
      var start = null;
      try { start = wallTimeToDate(row.getAttribute("data-start"), SITE_TZ); } catch (e) { start = null; }
      if (!start) return true;
      // Sessions without a time are stamped at noon; they count as past once the day is over.
      var minutes = row.getAttribute("data-tbd") === "true" ? 12 * 60 : (parseInt(row.getAttribute("data-duration"), 10) || 90);
      var past = start.getTime() + minutes * 60000 < now;
      row.classList.toggle("is-past", past);
      return !past;
    });
    if (remaining[0]) {
      var label = remaining[0].querySelector(".next-label");
      if (label) label.hidden = false;
    }
    var empty = tbody.querySelector("[data-empty]");
    if (empty) empty.hidden = remaining.length > 0;
  });

  // ---- Search in "Further reading" --------------------------------------------
  each(document.querySelectorAll("input[data-search]"), function (input) {
    var scope = document.querySelector(input.getAttribute("data-search"));
    if (!scope) return;
    var none = scope.querySelector("[data-no-results]");
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var any = false;
      each(scope.querySelectorAll("[data-item]"), function (item) {
        var show = !q || item.textContent.toLowerCase().indexOf(q) !== -1;
        item.classList.toggle("is-filtered", !show);
        if (show) any = true;
      });
      each(scope.querySelectorAll("[data-topic]"), function (topic) {
        topic.classList.toggle("is-filtered", !topic.querySelector("[data-item]:not(.is-filtered)"));
      });
      if (none) none.hidden = any;
    });
  });

  // ---- Copy the presenter outline ---------------------------------------------
  each(document.querySelectorAll("[data-copy]"), function (btn) {
    var src = document.querySelector(btn.getAttribute("data-copy"));
    var status = btn.parentNode.querySelector("[data-copy-status]");
    if (!src) return;
    var timer = 0;
    function report(msg) {
      if (!status) return;
      status.textContent = msg;
      clearTimeout(timer);
      timer = setTimeout(function () { status.textContent = ""; }, 4000);
    }
    function showInstead() {
      src.hidden = false;
      var range = document.createRange();
      range.selectNodeContents(src);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      report("Selected below. Press Ctrl+C or ⌘C to copy.");
    }
    btn.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(src.textContent).then(function () { report("Copied."); }, showInstead);
      } else {
        showInstead();
      }
    });
  });
})();
