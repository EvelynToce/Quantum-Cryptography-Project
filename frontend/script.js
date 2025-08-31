// Basic demo script to make the dashboard interactive without a backend.
// You can later replace the mock data / timeouts with real fetch() calls.

const mockAlgorithms = [
  // Classical set
  {
    id: 101,
    name: "RSA-2048",
    type: "Key Exchange / Signature",
    security: "Classical",
    family: "classical",
  },
  {
    id: 102,
    name: "ECDH P-256",
    type: "Key Exchange",
    security: "Classical",
    family: "classical",
  },
  {
    id: 103,
    name: "ECDSA P-256",
    type: "Signature",
    security: "Classical",
    family: "classical",
  },
  {
    id: 104,
    name: "AES-256-GCM",
    type: "Symmetric",
    security: "Classical",
    family: "classical",
  },
  // PQC set
  {
    id: 1,
    name: "CRYSTALS-Kyber",
    type: "KEM",
    security: "NIST Level 1",
    family: "pqc",
  },
  {
    id: 2,
    name: "CRYSTALS-Dilithium",
    type: "Signature",
    security: "NIST Level 2",
    family: "pqc",
  },
  {
    id: 3,
    name: "Falcon",
    type: "Signature",
    security: "NIST Level 1",
    family: "pqc",
  },
  {
    id: 4,
    name: "BIKE",
    type: "KEM (Alt)",
    security: "Experimental",
    family: "pqc",
  },
  {
    id: 5,
    name: "SPHINCS+ (SHA-256 128s)",
    type: "Signature",
    security: "NIST Level 1",
    family: "pqc",
  },
  {
    id: 6,
    name: "Classic McEliece 4608",
    type: "KEM",
    security: "NIST Level 1",
    family: "pqc",
  },
  {
    id: 7,
    name: "SABER (LightSaber)",
    type: "KEM",
    security: "NIST Level 1",
    family: "pqc",
  },
  {
    id: 8,
    name: "FrodoKEM-640",
    type: "KEM",
    security: "NIST Level 1",
    family: "pqc",
  },
];

const mockReports = [
  { id: 101, algoId: 1, status: "PASS", latencyMs: 37, ts: Date.now() - 60000 },
  { id: 102, algoId: 2, status: "PASS", latencyMs: 54, ts: Date.now() - 42000 },
  { id: 103, algoId: 3, status: "WARN", latencyMs: 71, ts: Date.now() - 15000 },
];

function $(sel) {
  return document.querySelector(sel);
}

function loadAlgorithms() {
  const classicalList = document.getElementById("classical-list");
  const pqcList = document.getElementById("pqc-list");
  if (!classicalList || !pqcList) return;
  classicalList.innerHTML = '<li style="opacity:.6">Loading...</li>';
  pqcList.innerHTML = '<li style="opacity:.6">Loading...</li>';
  setTimeout(() => {
    classicalList.innerHTML = "";
    pqcList.innerHTML = "";
    mockAlgorithms.forEach((a) => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${a.id}</strong> <span>${a.name}</span> <span style="opacity:.6;font-size:.65rem">${a.type} • ${a.security}</span>`;
      if (a.family === "classical") classicalList.appendChild(li);
      else pqcList.appendChild(li);
    });
  }, 400);
}

function applyAlgorithmFilter(filter) {
  const classicalDiv = document.getElementById("classical");
  const pqcDiv = document.getElementById("pqc");
  if (!classicalDiv || !pqcDiv) return;
  if (filter === "classical") {
    classicalDiv.style.display = "block";
    pqcDiv.style.display = "none";
  } else if (filter === "pqc") {
    classicalDiv.style.display = "none";
    pqcDiv.style.display = "block";
  } else {
    // all
    classicalDiv.style.display = "block";
    pqcDiv.style.display = "block";
  }
}

function loadReports() {
  const list = $("#report-list");
  list.innerHTML = '<li style="opacity:.6">Fetching reports...</li>';
  setTimeout(() => {
    list.innerHTML = "";
    mockReports.forEach((r) => {
      const li = document.createElement("li");
      const statusColor =
        r.status === "PASS"
          ? "var(--success)"
          : r.status === "WARN"
          ? "var(--warning)"
          : "var(--danger)";
      const date = new Date(r.ts).toLocaleTimeString();
      li.innerHTML = `<strong>#${r.id}</strong> Algo: ${r.algoId} <span style="color:${statusColor};font-weight:600">${r.status}</span> <span style="opacity:.6">${date}</span>`;
      list.appendChild(li);
    });
  }, 500);
}

function runTest(e) {
  e.preventDefault();
  const algoId = parseInt($("#algo").value, 10);
  const data = $("#data").value.trim() || "sample-bytes";
  const output = $("#test-result");
  output.textContent = "Running test...";
  const algo = mockAlgorithms.find((a) => a.id === algoId);
  if (!algo) {
    output.textContent = "Algorithm not found. Load algorithms first.";
    return;
  }
  setTimeout(() => {
    const latency = Math.round(30 + Math.random() * 50);
    const resultObj = {
      algorithm: algo.name,
      inputLength: data.length,
      simulatedLatencyMs: latency,
      signature: btoa(data).slice(0, 24) + "...",
      ok: true,
    };
    output.textContent = JSON.stringify(resultObj, null, 2);
  }, 600);
}

// Auto-load algorithms on first paint for nicer initial view.
window.addEventListener("DOMContentLoaded", () => {
  loadAlgorithms();
  loadReports();
  initPlasma();
  initPhotons();
  initAuthForms();
  initSectionRouting();
});

// Enhanced Photon background visualization with smoother animation
function initPhotons() {
  const canvas = document.getElementById("photons");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  let w,
    h,
    photons = [];
  let PHOTON_COUNT = 90;
  let lastTime = 0;
  let animationId;

  // Performance optimization
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";

  function resize() {
    w = canvas.width = Math.floor(window.innerWidth * 0.4);
    h = canvas.height = window.innerHeight;
    PHOTON_COUNT = Math.max(50, Math.floor(120 * (w / 800))); // Reduced count for better performance
    if (photons.length > PHOTON_COUNT) photons.length = PHOTON_COUNT;
  }

  window.addEventListener("resize", resize);
  resize();

  const palette = [
    [180, 220, 255],
    [120, 170, 255],
    [80, 140, 255],
    [140, 120, 255],
    [100, 200, 255],
    [160, 160, 255],
  ];

  function spawn() {
    const speed = 0.3 + Math.random() * 0.8;
    const angle = Math.random() * Math.PI * 2;
    const dist = Math.random() * Math.max(w, h) * 0.7;
    const baseX = w / 2 + Math.cos(angle) * dist * 0.2;
    const baseY = h / 2 + Math.sin(angle) * dist * 0.2;
    const driftAngle = angle + (Math.random() * 0.6 - 0.3);
    const color = palette[Math.floor(Math.random() * palette.length)];

    return {
      x: baseX,
      y: baseY,
      vx: Math.cos(driftAngle) * speed,
      vy: Math.sin(driftAngle) * speed,
      life: 0,
      maxLife: 500 + Math.random() * 800,
      r: (0.8 + Math.random() * 2.2) * 2.5,
      c: color,
      opacity: 0.8 + Math.random() * 0.2,
      pulsePhase: Math.random() * Math.PI * 2,
    };
  }

  // Initialize photons
  for (let i = 0; i < PHOTON_COUNT; i++) photons.push(spawn());

  function step(currentTime) {
    // Calculate delta time for smooth animation regardless of framerate
    const deltaTime = currentTime - lastTime;
    lastTime = currentTime;
    const normalizedDelta = Math.min(deltaTime / 16.67, 2); // Cap at 2x normal speed

    // Clear with smoother fade
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = "rgba(5,7,15,0.12)"; // Reduced for smoother trails
    ctx.fillRect(0, 0, w, h);

    ctx.globalCompositeOperation = "lighter";

    // Maintain photon count
    while (photons.length < PHOTON_COUNT) photons.push(spawn());

    for (let i = photons.length - 1; i >= 0; i--) {
      const p = photons[i];

      // Smooth movement with delta time
      p.x += p.vx * normalizedDelta;
      p.y += p.vy * normalizedDelta;
      p.life += normalizedDelta;
      p.pulsePhase += 0.05 * normalizedDelta;

      // Gentle attraction towards center-right with smoother physics
      const targetX = w * 0.6;
      const targetY = h * 0.5;
      const dx = targetX - p.x;
      const dy = targetY - p.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      // Smooth acceleration
      const attraction = 0.00003 * normalizedDelta;
      p.vx += (dx / distance) * attraction;
      p.vy += (dy / distance) * attraction;

      // Apply gentle damping for more natural movement
      p.vx *= 0.999;
      p.vy *= 0.999;

      // Check bounds and respawn
      if (
        p.x < -100 ||
        p.x > w + 100 ||
        p.y < -100 ||
        p.y > h + 100 ||
        p.life > p.maxLife
      ) {
        photons[i] = spawn();
        continue;
      }

      // Smoother opacity calculation with pulsing
      const lifeFade = Math.sin((p.life / p.maxLife) * Math.PI);
      const pulse = 0.5 + 0.5 * Math.sin(p.pulsePhase);
      const finalOpacity = lifeFade * p.opacity * (0.7 + 0.3 * pulse);

      // Enhanced gradient rendering
      const gradient = ctx.createRadialGradient(
        p.x,
        p.y,
        0,
        p.x,
        p.y,
        p.r * 25
      );
      const [r, g, b] = p.c;

      gradient.addColorStop(0, `rgba(${r},${g},${b},${0.4 * finalOpacity})`);
      gradient.addColorStop(0.2, `rgba(${r},${g},${b},${0.25 * finalOpacity})`);
      gradient.addColorStop(0.5, `rgba(${r},${g},${b},${0.1 * finalOpacity})`);
      gradient.addColorStop(1, "rgba(0,0,0,0)");

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * 22, 0, Math.PI * 2);
      ctx.fill();

      // Add a subtle inner glow
      const innerGradient = ctx.createRadialGradient(
        p.x,
        p.y,
        0,
        p.x,
        p.y,
        p.r * 8
      );
      innerGradient.addColorStop(
        0,
        `rgba(${r + 30},${g + 30},${b + 30},${0.6 * finalOpacity})`
      );
      innerGradient.addColorStop(
        0.7,
        `rgba(${r},${g},${b},${0.2 * finalOpacity})`
      );
      innerGradient.addColorStop(1, "rgba(0,0,0,0)");

      ctx.fillStyle = innerGradient;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * 8, 0, Math.PI * 2);
      ctx.fill();
    }

    animationId = requestAnimationFrame(step);
  }

  // Start animation
  animationId = requestAnimationFrame(step);

  // Cleanup function
  return () => {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
  };
}

// Enhanced Plasma noise background with smoother animation
function initPlasma() {
  const canvas = document.getElementById("plasma-bg");
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext("2d");
  let w, h, bw, bh;
  let lastTime = 0;
  let animationId;

  // Performance optimization
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    // Optimized buffer size for better performance
    bw = Math.min(300, Math.max(180, Math.floor(w / 6)));
    bh = Math.min(270, Math.max(150, Math.floor(h / 6)));
  }

  window.addEventListener("resize", resize);
  resize();

  // Enhanced color palette with smoother transitions
  const stops = [
    [0.0, [8, 16, 34]],
    [0.15, [25, 40, 65]],
    [0.3, [55, 186, 205]], // subdued cyan
    [0.5, [126, 54, 205]], // subdued violet
    [0.7, [195, 60, 168]], // subdued magenta
    [0.85, [150, 120, 200]], // transition color
    [1.0, [126, 194, 58]], // subdued lime
  ];

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function samplePalette(t) {
    t = Math.min(1, Math.max(0, t));
    for (let i = 0; i < stops.length - 1; i++) {
      const s0 = stops[i];
      const s1 = stops[i + 1];
      if (t >= s0[0] && t <= s1[0]) {
        const lt = (t - s0[0]) / (s1[0] - s0[0]);
        // Smooth interpolation
        const smoothT = lt * lt * (3 - 2 * lt); // Smoothstep
        return [
          Math.floor(lerp(s0[1][0], s1[1][0], smoothT)),
          Math.floor(lerp(s0[1][1], s1[1][1], smoothT)),
          Math.floor(lerp(s0[1][2], s1[1][2], smoothT)),
        ];
      }
    }
    return stops[stops.length - 1][1];
  }

  // Pre-create offscreen canvas for better performance
  const offscreenCanvas = document.createElement("canvas");
  const offscreenCtx = offscreenCanvas.getContext("2d");
  offscreenCanvas.width = bw;
  offscreenCanvas.height = bh;

  function frame(currentTime) {
    const deltaTime = currentTime - lastTime;
    lastTime = currentTime;

    // Smoother time progression
    const t = currentTime * 0.0003; // Slightly slower for smoother animation
    const DARKEN = 0.85; // Slightly brighter

    // Generate plasma into offscreen ImageData
    const img = offscreenCtx.createImageData(bw, bh);
    const data = img.data;

    for (let y = 0; y < bh; y++) {
      for (let x = 0; x < bw; x++) {
        const nx = x / bw;
        const ny = y / bh;

        // Enhanced plasma calculation with smoother waves
        const wave1 = Math.sin(nx * 7 + t * 1.8);
        const wave2 = Math.sin((nx + ny) * 4.5 - t * 1.2);
        const wave3 = Math.sin(Math.sqrt(nx * nx + ny * ny) * 8.5 + t * 0.9);
        const wave4 = Math.sin((nx - ny) * 3.2 + t * 1.5); // Additional wave for complexity

        const v = (wave1 + wave2 + wave3 + wave4) / 4; // -1..1
        const n = (v + 1) / 2; // 0..1

        let [r, g, b] = samplePalette(n);
        r = Math.floor(r * DARKEN);
        g = Math.floor(g * DARKEN);
        b = Math.floor(b * DARKEN);

        const idx = (y * bw + x) * 4;
        data[idx] = r;
        data[idx + 1] = g;
        data[idx + 2] = b;
        // Smoother alpha variation
        data[idx + 3] = Math.floor(
          180 * (0.5 + 0.5 * Math.sin(t * 0.6 + n * 2.5))
        );
      }
    }

    // Render to offscreen canvas
    offscreenCtx.putImageData(img, 0, 0);

    // Clear main canvas and draw scaled image
    ctx.clearRect(0, 0, w, h);
    ctx.globalCompositeOperation = "source-over";
    ctx.drawImage(offscreenCanvas, 0, 0, w, h);

    // Enhanced light overlay with smoother gradients
    ctx.globalCompositeOperation = "overlay";
    const grd = ctx.createRadialGradient(
      w * 0.25,
      h * 0.35,
      w * 0.05,
      w * 0.25,
      h * 0.35,
      w * 0.85
    );
    grd.addColorStop(0, "rgba(255,255,255,0.12)");
    grd.addColorStop(0.4, "rgba(255,255,255,0.06)");
    grd.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, w, h);

    animationId = requestAnimationFrame(frame);
  }

  animationId = requestAnimationFrame(frame);

  // Cleanup function
  return () => {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
  };
}

// Auth forms (mock only; not secure, just demo)
function initAuthForms() {
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const name = document.getElementById("signup-name").value.trim();
      const email = document
        .getElementById("signup-email")
        .value.trim()
        .toLowerCase();
      const pw = document.getElementById("signup-password").value;
      const pw2 = document.getElementById("signup-confirm").value;
      const org = document.getElementById("signup-org").value.trim();
      const out = document.getElementById("signup-result");
      if (pw !== pw2) {
        out.textContent = "Passwords do not match.";
        return;
      }
      const users = JSON.parse(localStorage.getItem("qsc_users") || "[]");
      if (users.some((u) => u.email === email)) {
        out.textContent = "Email already registered.";
        return;
      }
      users.push({ name, email, pwHash: btoa(pw), org, created: Date.now() });
      localStorage.setItem("qsc_users", JSON.stringify(users));
      out.textContent = "Account created. You can login now.";
      signupForm.reset();
    });
  }
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = document
        .getElementById("login-email")
        .value.trim()
        .toLowerCase();
      const pw = document.getElementById("login-password").value;
      const out = document.getElementById("login-result");
      const users = JSON.parse(localStorage.getItem("qsc_users") || "[]");
      const user = users.find(
        (u) => u.email === email && u.pwHash === btoa(pw)
      );
      if (user) {
        out.textContent = "Login success. Welcome " + user.name + "!";
        localStorage.setItem(
          "qsc_session",
          JSON.stringify({ email, ts: Date.now() })
        );
        updateCurrentNav("home");
      } else {
        out.textContent = "Invalid credentials.";
      }
    });
  }
}

// Nav helpers for active state + filter highlight
function updateCurrentNav(id) {
  const topLinks = document.querySelectorAll(".main-nav .menu-root > li > a");
  topLinks.forEach((a) => a.removeAttribute("aria-current"));
  if (id) {
    if (id === "home") {
      document.querySelector(".nav-home")?.setAttribute("aria-current", "page");
      return;
    }
    const active = Array.from(topLinks).find((a) => a.dataset.section === id);
    if (active) active.setAttribute("aria-current", "page");
  }
}

// Section routing: show only selected section
function initSectionRouting() {
  const links = document.querySelectorAll("[data-section]");
  const sections = document.querySelectorAll(".app-section");
  let current = null;
  // Home link behavior
  const homeLink = document.querySelector(".nav-home");
  if (homeLink) {
    homeLink.addEventListener("click", (e) => {
      e.preventDefault();
      if (current) {
        const curSec = document.getElementById(current);
        smoothClose(curSec, () => {
          current = null;
          updateCurrentNav("home");
        });
      } else {
        updateCurrentNav("home");
      }
    });
  }
  function smoothClose(sec, cb) {
    if (!sec) return cb && cb();
    // Ensure it's currently visible
    if (!sec.classList.contains("active")) return cb && cb();
    const full = sec.scrollHeight;
    // Prepare inline styles for animation
    sec.style.overflow = "hidden";
    sec.style.height = full + "px";
    sec.style.transition = "height .45s ease";
    // Force reflow
    // eslint-disable-next-line no-unused-expressions
    sec.offsetHeight;
    requestAnimationFrame(() => {
      sec.style.height = "0px";
    });
    const done = (e) => {
      if (e.propertyName !== "height") return; // fire once
      sec.removeEventListener("transitionend", done);
      sec.classList.remove("active");
      // cleanup
      sec.style.removeProperty("height");
      sec.style.removeProperty("overflow");
      sec.style.removeProperty("transition");
      cb && cb();
    };
    sec.addEventListener("transitionend", done);
  }
  function smoothOpen(sec) {
    if (!sec) return;
    // If already active do nothing
    if (sec.classList.contains("active")) return;
    sec.classList.add("active");
    // Optional open animation (height grow)
    const full = sec.scrollHeight;
    sec.style.overflow = "hidden";
    sec.style.height = "0px";
    sec.style.transition = "height .45s ease";
    // Force reflow
    // eslint-disable-next-line no-unused-expressions
    sec.offsetHeight;
    requestAnimationFrame(() => {
      sec.style.height = full + "px";
    });
    const done = (e) => {
      if (e.propertyName !== "height") return;
      sec.removeEventListener("transitionend", done);
      // allow natural height after opening
      sec.style.removeProperty("height");
      sec.style.removeProperty("overflow");
      sec.style.removeProperty("transition");
    };
    sec.addEventListener("transitionend", done);
  }
  function activate(id, filter) {
    // Apply algorithm filter first (if any) but only when opening algorithms
    if (id === "algorithms" && filter) {
      applyAlgorithmFilter(filter);
      highlightFilter(filter);
    }
    if (current === id) {
      const sec = document.getElementById(id);
      smoothClose(sec, () => {
        links.forEach((l) => {
          if (l.dataset.section === id) l.setAttribute("aria-pressed", "false");
        });
        current = null;
        updateCurrentNav("home");
      });
      return;
    }
    const prev = current ? document.getElementById(current) : null;
    if (prev) {
      smoothClose(prev, () => openNew());
    } else {
      openNew();
    }
    function openNew() {
      const target = document.getElementById(id);
      if (target) {
        smoothOpen(target);
        current = id;
        if (id === "algorithms") loadAlgorithms();
        if (id === "reports") loadReports();
        updateCurrentNav(id);
      }
      links.forEach((l) =>
        l.setAttribute(
          "aria-pressed",
          l.dataset.section === id ? "true" : "false"
        )
      );
    }
  }
  links.forEach((a) => {
    a.setAttribute("role", "button");
    a.setAttribute("aria-pressed", "false");
    a.addEventListener("click", (e) => {
      e.preventDefault();
      const id = a.dataset.section;
      if (id) activate(id, a.dataset.filter);
    });
    a.addEventListener("keydown", (e) => {
      if ((e.key === "Enter" || e.key === " ") && a.dataset.section) {
        e.preventDefault();
        activate(a.dataset.section, a.dataset.filter);
      }
    });
  });
  // default highlight for filters
  highlightFilter("all");
}
