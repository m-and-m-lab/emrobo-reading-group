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
  function hasEnded(el) {
    var start = null;
    try { start = wallTimeToDate(el.getAttribute("data-start"), SITE_TZ); } catch (e) { start = null; }
    if (!start) return false;
    // Sessions without a time are stamped at noon; they count as past once the day is over.
    var minutes = el.getAttribute("data-tbd") === "true" ? 12 * 60 : (parseInt(el.getAttribute("data-duration"), 10) || 90);
    return start.getTime() + minutes * 60000 < now;
  }

  // Featured "next session" card on the home page.
  each(document.querySelectorAll("[data-next]"), function (box) {
    var cards = Array.prototype.slice.call(box.querySelectorAll(".next__card[data-start]"));
    var next = cards.filter(function (c) { return !hasEnded(c); })[0];
    cards.forEach(function (c) { c.hidden = c !== next; });
    var empty = box.querySelector("[data-next-empty]");
    if (empty) empty.hidden = !!next;
  });

  // Upcoming tables: hide sessions that have ended, mark the next one.
  each(document.querySelectorAll("tbody[data-upcoming]"), function (tbody) {
    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr[data-start]"));
    var remaining = rows.filter(function (row) {
      var past = hasEnded(row);
      row.classList.toggle("is-past", past);
      return !past;
    });
    if (tbody.hasAttribute("data-skip-first") && remaining[0]) {
      remaining[0].classList.add("is-past");   // already featured above
      remaining = remaining.slice(1);
    }
    if (remaining[0]) {
      var label = remaining[0].querySelector(".next-label");
      if (label) label.hidden = false;
    }
    var empty = tbody.querySelector("[data-empty]");
    if (empty) empty.hidden = remaining.length > 0 || tbody.hasAttribute("data-skip-first");
    var section = tbody.closest && tbody.closest(".section--tight");
    if (section && remaining.length === 0) section.hidden = true;
  });

  // ---- Reference library: search plus a single-topic filter -------------------
  each(document.querySelectorAll("[data-library]"), function (tools) {
    var scope = document.querySelector(tools.getAttribute("data-library"));
    if (!scope) return;
    var input = tools.querySelector("input[type=search]");
    var buttons = tools.querySelectorAll("button[data-topic-filter]");
    var none = scope.querySelector("[data-no-results]");
    var state = { topic: "all", q: "" };
    function apply() {
      var any = false;
      each(scope.querySelectorAll("[data-topic]"), function (topic) {
        var topicOk = state.topic === "all" || topic.getAttribute("data-topic") === state.topic;
        var shown = 0;
        each(topic.querySelectorAll("[data-item]"), function (item) {
          var show = topicOk && (!state.q || item.textContent.toLowerCase().indexOf(state.q) !== -1);
          item.classList.toggle("is-filtered", !show);
          if (show) shown++;
        });
        topic.classList.toggle("is-filtered", shown === 0);
        if (shown) any = true;
      });
      if (none) none.hidden = any;
    }
    each(buttons, function (b) {
      b.addEventListener("click", function () {
        state.topic = b.getAttribute("data-topic-filter");
        each(buttons, function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        apply();
      });
    });
    if (input) input.addEventListener("input", function () { state.q = input.value.trim().toLowerCase(); apply(); });
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
