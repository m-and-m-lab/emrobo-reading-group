(function () {
  "use strict";

  var SITE_TZ = window.SITE_TZ || "America/Detroit";
  var reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
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

  // "2026-10-16T16:00" interpreted as wall-clock time in `tz`.
  function wallTimeToDate(iso, tz) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso || "");
    if (!m) return null;
    var guess = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
    var t = guess - tzOffset(new Date(guess), tz);
    return new Date(guess - tzOffset(new Date(t), tz));
  }

  var viewerTz = null;
  try { viewerTz = Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) { /* older browsers */ }

  // ---- Sessions: past, next up, local time ----------------------------------
  var now = Date.now();
  each(document.querySelectorAll(".session[data-start]"), function (el) {
    var iso = el.getAttribute("data-start");
    var start = null;
    try { start = wallTimeToDate(iso, SITE_TZ); } catch (e) { start = null; }
    if (!start) return;
    // Sessions without a time are stamped at noon; they count as past once the day is over.
    var tbd = /T12:00$/.test(iso) && !el.querySelector(".js-upcoming-only");
    var minutes = parseInt(el.getAttribute("data-duration"), 10) || 90;
    var end = start.getTime() + (tbd ? 12 * 60 : minutes) * 60000;
    el._past = end < now;
    el.classList.toggle("is-past", el._past);

    var hint = el.querySelector(".js-local-time");
    if (hint && !tbd && !el._past && viewerTz && viewerTz !== SITE_TZ) {
      hint.textContent = "(" + start.toLocaleString(undefined, {
        weekday: "short", hour: "numeric", minute: "2-digit", timeZoneName: "short"
      }) + " your time)";
      hint.hidden = false;
    }
  });

  each(document.querySelectorAll(".session-list[data-upcoming-only]"), function (list) {
    var items = Array.prototype.slice.call(list.querySelectorAll(".session[data-start]"));
    var upcoming = items.filter(function (el) { return !el._past; });
    var limit = parseInt(list.getAttribute("data-limit"), 10) || 3;
    items.forEach(function (el) { el.hidden = !!el._past || upcoming.indexOf(el) >= limit; });
    var empty = list.querySelector(".js-empty");
    if (empty) empty.hidden = upcoming.length > 0;
    if (upcoming[0]) {
      upcoming[0].classList.add("is-next");
      var badge = upcoming[0].querySelector(".tag--next");
      if (badge) badge.hidden = false;
    }
  });

  // ---- Filters and search -------------------------------------------------
  each(document.querySelectorAll("[data-filter-group]"), function (group) {
    var scope = document.querySelector(group.getAttribute("data-filter-group"));
    if (!scope) return;
    var state = { kind: "all", query: "" };
    var buttons = group.querySelectorAll("button[data-filter]");
    var search = group.querySelector("input[type=search]");

    function apply() {
      var anyVisible = false;
      each(scope.querySelectorAll("[data-kind]"), function (el) {
        var kindOk = state.kind === "all" || el.getAttribute("data-kind") === state.kind;
        var textOk = !state.query || el.textContent.toLowerCase().indexOf(state.query) !== -1;
        var show = kindOk && textOk;
        el.classList.toggle("is-filtered", !show);
        if (show && !el.hidden) anyVisible = true;
      });
      each(scope.querySelectorAll("[data-filter-section]"), function (section) {
        section.classList.toggle("is-filtered", !section.querySelector("[data-kind]:not(.is-filtered)"));
      });
      var none = scope.querySelector(".js-no-results");
      if (none) none.hidden = anyVisible;
    }

    each(buttons, function (button) {
      button.addEventListener("click", function () {
        state.kind = button.getAttribute("data-filter");
        each(buttons, function (b) { b.setAttribute("aria-pressed", b === button ? "true" : "false"); });
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

  // ---- "On this page": light up the joint of the section being read --------
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc__link"));
  var tocTargets = tocLinks.map(function (a) {
    return document.getElementById(decodeURIComponent(a.hash.slice(1)));
  });
  if (tocLinks.length) {
    var spyQueued = false;
    var spy = function () {
      spyQueued = false;
      var line = window.innerHeight * 0.3;
      var current = 0;
      tocTargets.forEach(function (t, i) {
        if (t && t.getBoundingClientRect().top - line <= 0) current = i;
      });
      if (window.innerHeight + window.pageYOffset >= document.documentElement.scrollHeight - 4) {
        current = tocLinks.length - 1;
      }
      tocLinks.forEach(function (a, i) {
        if (i === current) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
    };
    var queueSpy = function () {
      if (!spyQueued) { spyQueued = true; window.requestAnimationFrame(spy); }
    };
    window.addEventListener("scroll", queueSpy, { passive: true });
    window.addEventListener("resize", queueSpy);
    spy();
  }

  // ---- Fig. 1: layers and the drawer motion ---------------------------------
  var fig = document.querySelector("[data-fig]");
  if (fig) initFigure(fig);

  function initFigure(fig) {
    var svg = fig.querySelector("svg.fig1");
    if (!svg) return;
    var caption = fig.querySelector(".fig__caption");
    var defaultCaption = caption ? caption.innerHTML : "";
    var canHover = !!(window.matchMedia && window.matchMedia("(hover: hover)").matches);

    function describe(chip) {
      if (!caption) return;
      var off = chip.getAttribute("aria-pressed") === "false";
      caption.textContent = "";
      var b = document.createElement("b");
      b.textContent = chip.textContent + (off ? " (hidden)" : "");
      caption.appendChild(b);
      caption.appendChild(document.createTextNode(chip.getAttribute("data-caption") || ""));
    }
    function reset() { if (caption) caption.innerHTML = defaultCaption; }

    each(fig.querySelectorAll(".layer-chip"), function (chip) {
      var id = chip.getAttribute("data-layer");
      var layer = svg.querySelector('.layer[data-layer="' + id + '"]');
      if (!layer) { chip.hidden = true; return; }
      chip.addEventListener("click", function () {
        var on = chip.getAttribute("aria-pressed") !== "true";
        chip.setAttribute("aria-pressed", on ? "true" : "false");
        layer.classList.toggle("is-off", !on);
        describe(chip);
      });
      chip.addEventListener("focus", function () { describe(chip); });
      chip.addEventListener("blur", function () { if (!fig.hasAttribute("data-focus")) reset(); });
      if (canHover) {
        chip.addEventListener("mouseenter", function () {
          fig.setAttribute("data-focus", id);
          layer.classList.add("is-focus");
          describe(chip);
        });
        chip.addEventListener("mouseleave", function () {
          fig.removeAttribute("data-focus");
          layer.classList.remove("is-focus");
          if (document.activeElement !== chip) reset();
        });
      }
    });

    // The arm follows the drawer handle with the same two-link IK used to draw it.
    var q0 = parseFloat(svg.getAttribute("data-q0")) || 30;
    var S = [284, 186], L = 100, FRONT = 512, FX0 = FRONT - q0, CAM = [341, 214];
    function $(id) { return svg.querySelector("#" + id); }
    var el = {
      a1o: $("fig-a1-o"), a1i: $("fig-a1-i"), a2o: $("fig-a2-o"), a2i: $("fig-a2-i"),
      elbow: $("fig-elbow"), gripper: $("fig-gripper"), drawer: $("fig-drawer"), grasp: $("fig-grasp"),
      e1: $("fig-e1"), e2: $("fig-e2"), e3: $("fig-e3"), nE: $("fig-nE"), nW: $("fig-nW"), nT: $("fig-nT"),
      manip: $("fig-manip"), manipFill: $("fig-manip-fill"), occ: $("fig-occ"), chain: $("fig-chain")
    };
    var motionBtn = fig.querySelector("[data-motion]");
    if (!el.a1o || !el.gripper || !motionBtn || reduceMotion) return;

    function r1(v) { return Math.round(v * 10) / 10; }
    function setLine(n, a, b) {
      if (!n) return;
      n.setAttribute("x1", r1(a[0])); n.setAttribute("y1", r1(a[1]));
      n.setAttribute("x2", r1(b[0])); n.setAttribute("y2", r1(b[1]));
    }
    function setCircle(n, p) { if (n) { n.setAttribute("cx", r1(p[0])); n.setAttribute("cy", r1(p[1])); } }
    function pt(p) { return r1(p[0]) + " " + r1(p[1]); }
    function ellipsePath(c, rx, ry, deg) {
      var t = deg * Math.PI / 180, ax = rx * Math.cos(t), ay = rx * Math.sin(t);
      var p1 = [c[0] + ax, c[1] + ay], p2 = [c[0] - ax, c[1] - ay];
      var arc = "A" + rx + " " + ry + " " + r1(deg) + " 1 1 ";
      return "M" + pt(p1) + " " + arc + pt(p2) + " " + arc + pt(p1) + " Z";
    }
    function occlusionPath(W) {
      var top = [W[0] - 2, 197], bot = [W[0] - 2, 215];
      function ext(p) { var k = (520 - CAM[0]) / (p[0] - CAM[0]); return [520, CAM[1] + (p[1] - CAM[1]) * k]; }
      return "M" + pt(top) + " L" + pt(ext(top)) + " L" + pt(ext(bot)) + " L" + pt(bot) + " Z";
    }
    function pose(q) {
      var fx = FRONT - q, W = [fx - 46, 206], T = [W[0] + 27, 206];
      var dx = W[0] - S[0], dy = W[1] - S[1], d = Math.sqrt(dx * dx + dy * dy);
      var th = Math.atan2(dy, dx) - Math.acos(Math.min(1, d / (2 * L)));
      var E = [S[0] + L * Math.cos(th), S[1] + L * Math.sin(th)];
      setLine(el.a1o, S, E); setLine(el.a1i, S, E);
      setLine(el.a2o, E, W); setLine(el.a2i, E, W);
      setCircle(el.elbow, E);
      el.gripper.setAttribute("transform", "translate(" + pt(W) + ")");
      var shift = "translate(" + r1(fx - FX0) + " 0)";
      if (el.drawer) el.drawer.setAttribute("transform", shift);
      if (el.grasp) el.grasp.setAttribute("transform", shift);
      setLine(el.e1, S, E); setLine(el.e2, E, W); setLine(el.e3, W, T);
      setCircle(el.nE, E); setCircle(el.nW, W); setCircle(el.nT, T);
      var ed = ellipsePath(T, 7, 24, Math.atan2(T[1] - S[1], T[0] - S[0]) * 180 / Math.PI);
      if (el.manip) el.manip.setAttribute("d", ed);
      if (el.manipFill) el.manipFill.setAttribute("d", ed);
      if (el.occ) el.occ.setAttribute("d", occlusionPath(W));
      if (el.chain) { el.chain.setAttribute("x1", r1(T[0])); el.chain.setAttribute("y1", r1(T[1])); }
    }

    // A slow push and pull on the drawer; starts from the drawn pose, so nothing jumps.
    var PERIOD = 7000, AMP = 12;
    var playing = true, inView = true, raf = 0, t0 = 0, phase = 0;
    function frame(ts) {
      if (!t0) t0 = ts - phase;
      phase = ts - t0;
      pose(q0 - AMP * (1 - Math.cos(2 * Math.PI * phase / PERIOD)) / 2);
      raf = window.requestAnimationFrame(frame);
    }
    function start() {
      if (raf || !playing || !inView || document.hidden) return;
      t0 = 0;
      raf = window.requestAnimationFrame(frame);
    }
    function stop() { if (raf) window.cancelAnimationFrame(raf); raf = 0; }

    motionBtn.hidden = false;
    motionBtn.setAttribute("aria-label", "Pause the drawer animation");
    motionBtn.addEventListener("click", function () {
      playing = !playing;
      motionBtn.setAttribute("data-state", playing ? "playing" : "paused");
      motionBtn.textContent = playing ? "Pause" : "Play";
      motionBtn.setAttribute("aria-label", playing ? "Pause the drawer animation" : "Play the drawer animation");
      if (playing) start(); else stop();
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        if (inView) start(); else stop();
      }).observe(svg);
    }
    document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });
    start();
  }

  // ---- Copy buttons -----------------------------------------------------------
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
    function selectInstead() {
      var details = src.closest ? src.closest("details") : null;
      if (details) details.open = true;
      var range = document.createRange();
      range.selectNodeContents(src);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      report("Selected. Press Ctrl+C or ⌘C to copy.");
    }
    btn.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(src.textContent).then(function () { report("Copied."); }, selectInstead);
      } else {
        selectInstead();
      }
    });
  });
})();
