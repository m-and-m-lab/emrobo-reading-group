(function () {
  "use strict";

  var SITE_TZ = window.SITE_TZ || "America/Detroit";

  // ---- Mobile navigation ----------------------------------------------------
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // ---- Time zone helpers ----------------------------------------------------
  // Offset (ms) between UTC and the wall clock in `tz` at instant `date`.
  function tzOffset(date, tz) {
    var parts = {};
    new Intl.DateTimeFormat("en-US", {
      timeZone: tz, hourCycle: "h23",
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit"
    }).formatToParts(date).forEach(function (p) { parts[p.type] = p.value; });
    var asUtc = Date.UTC(+parts.year, +parts.month - 1, +parts.day, +parts.hour, +parts.minute, +parts.second);
    return asUtc - date.getTime();
  }

  // "2026-10-01T16:00" interpreted as wall-clock time in `tz`.
  function wallTimeToDate(iso, tz) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso || "");
    if (!m) return null;
    var guess = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
    var t = guess - tzOffset(new Date(guess), tz);
    return new Date(guess - tzOffset(new Date(t), tz));
  }

  var viewerTz = null;
  try { viewerTz = Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) { /* older browsers */ }

  // ---- Sessions: past / up next / local time -------------------------------
  var now = Date.now();
  var sessions = Array.prototype.slice.call(document.querySelectorAll(".session[data-start]"));

  sessions.forEach(function (el) {
    var start;
    try { start = wallTimeToDate(el.getAttribute("data-start"), SITE_TZ); } catch (e) { start = null; }
    if (!start) return;
    var minutes = parseInt(el.getAttribute("data-duration"), 10) || 90;
    el._past = start.getTime() + minutes * 60000 < now;
    el.classList.toggle("is-past", el._past);

    var hint = el.querySelector(".js-local-time");
    var hasTime = !/T12:00$/.test(el.getAttribute("data-start")) || el.querySelector(".js-upcoming-only");
    if (hint && hasTime && !el._past && viewerTz && viewerTz !== SITE_TZ) {
      hint.textContent = "(" + start.toLocaleString(undefined, {
        weekday: "short", hour: "numeric", minute: "2-digit", timeZoneName: "short"
      }) + " your time)";
      hint.hidden = false;
    }
  });

  Array.prototype.forEach.call(document.querySelectorAll(".session-list"), function (list) {
    var items = Array.prototype.slice.call(list.querySelectorAll(".session[data-start]"));
    var upcoming = items.filter(function (el) { return !el._past; });

    if (list.hasAttribute("data-upcoming-only")) {
      var limit = parseInt(list.getAttribute("data-limit"), 10) || 3;
      items.forEach(function (el) { el.hidden = el._past || upcoming.indexOf(el) >= limit; });
      var empty = list.querySelector(".js-empty");
      if (empty) empty.hidden = upcoming.length > 0;
    }

    if (upcoming[0]) {
      upcoming[0].classList.add("is-next");
      var badge = upcoming[0].querySelector(".tag--next");
      if (badge) badge.hidden = false;
    }
  });

  // ---- Filters and search ---------------------------------------------------
  Array.prototype.forEach.call(document.querySelectorAll("[data-filter-group]"), function (group) {
    var scope = document.querySelector(group.getAttribute("data-filter-group"));
    if (!scope) return;
    var state = { kind: "all", query: "" };
    var buttons = group.querySelectorAll("button[data-filter]");
    var search = group.querySelector("input[type=search]");

    function apply() {
      var anyVisible = false;
      Array.prototype.forEach.call(scope.querySelectorAll("[data-kind]"), function (el) {
        var kindOk = state.kind === "all" || el.getAttribute("data-kind") === state.kind;
        var textOk = !state.query || el.textContent.toLowerCase().indexOf(state.query) !== -1;
        var show = kindOk && textOk;
        el.classList.toggle("is-filtered", !show);
        if (show) anyVisible = true;
      });
      Array.prototype.forEach.call(scope.querySelectorAll("[data-filter-section]"), function (section) {
        section.classList.toggle("is-filtered", !section.querySelector("[data-kind]:not(.is-filtered)"));
      });
      var none = scope.querySelector(".js-no-results");
      if (none) none.hidden = anyVisible;
    }

    Array.prototype.forEach.call(buttons, function (button) {
      button.addEventListener("click", function () {
        state.kind = button.getAttribute("data-filter");
        Array.prototype.forEach.call(buttons, function (b) {
          b.setAttribute("aria-pressed", b === button ? "true" : "false");
        });
        apply();
      });
    });

    if (search) {
      search.addEventListener("input", function () {
        state.query = search.value.trim().toLowerCase();
        apply();
      });
    }
  });
})();
