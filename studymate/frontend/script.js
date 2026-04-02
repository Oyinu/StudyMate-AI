const BASE = "https://studymate-ai-oq99.onrender.com/api";

// ─── STATE ──────────────────────────────────────────────────
let currentUser = null;
let selectedFile = null;
let uploadedDocId = null;
let activeQuiz = null;
let cbtAnswers = {};
let cbtTheoryAnswers = {};
let cbtCurrentIdx = 0;
let cbtAllQuestions = [];
let cbtTimer = null;
let cbtSecondsLeft = 0;
let cbtStartTime = null;

// ─── TOAST ──────────────────────────────────────────────────
function showToast(msg, type = "") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "toast show " + type;
  setTimeout(() => (t.className = "toast"), 3000);
}

// ─── AUTH ────────────────────────────────────────────────────
function showAuth(view) {
  document
    .getElementById("loginPage")
    .classList.toggle("hidden", view !== "login");
  document
    .getElementById("registerPage")
    .classList.toggle("hidden", view !== "register");
}

async function doLogin() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const errEl = document.getElementById("loginError");
  const btn = document.getElementById("loginBtn");

  if (!email || !password) {
    errEl.textContent = "Please fill in all fields.";
    errEl.classList.add("show");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Signing in...";
  errEl.classList.remove("show");

  try {
    const res = await fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.error || "Login failed";
      errEl.classList.add("show");
      return;
    }
    localStorage.setItem("studymate_token", data.token);
    currentUser = data.user;
    enterApp();
  } catch {
    errEl.textContent = "Connection error. Is the backend running?";
    errEl.classList.add("show");
  } finally {
    btn.disabled = false;
    btn.textContent = "Sign in";
  }
}

async function doRegister() {
  const name = document.getElementById("regName").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const errEl = document.getElementById("registerError");
  const btn = document.getElementById("registerBtn");

  if (!name || !email || !password) {
    errEl.textContent = "Please fill in all fields.";
    errEl.classList.add("show");
    return;
  }
  if (password.length < 6) {
    errEl.textContent = "Password must be at least 6 characters.";
    errEl.classList.add("show");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Creating account...";
  errEl.classList.remove("show");

  try {
    const res = await fetch(`${BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.error || "Registration failed";
      errEl.classList.add("show");
      return;
    }
    localStorage.setItem("studymate_token", data.token);
    currentUser = data.user;
    enterApp();
  } catch {
    errEl.textContent = "Connection error. Is the backend running?";
    errEl.classList.add("show");
  } finally {
    btn.disabled = false;
    btn.textContent = "Create account";
  }
}

function doLogout() {
  localStorage.removeItem("studymate_token");
  currentUser = null;
  location.reload();
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("studymate_token")}`,
  };
}

function enterApp() {
  document.getElementById("loginPage").classList.add("hidden");
  document.getElementById("registerPage").classList.add("hidden");
  document.getElementById("appLayout").classList.remove("hidden");
  document.getElementById("userName").textContent = currentUser.name;
  document.getElementById("userEmail").textContent = currentUser.email;
  document.getElementById("userAvatar").textContent = currentUser.name
    .charAt(0)
    .toUpperCase();
  showPage("generate");
  loadDashboardStats();
  loadQuizList();
}

async function checkAuth() {
  const token = localStorage.getItem("studymate_token");
  if (!token) return;
  try {
    const res = await fetch(`${BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      localStorage.removeItem("studymate_token");
      return;
    }
    const data = await res.json();
    currentUser = data.user;
    enterApp();
  } catch {
    /* stay on login */
  }
}

// ─── PAGES ──────────────────────────────────────────────────
function showPage(name) {
  ["generate", "dashboard", "cbt", "results"].forEach((p) => {
    document.getElementById("page-" + p).classList.toggle("hidden", p !== name);
    document.getElementById("nav-" + p).classList.toggle("active", p === name);
  });
  if (name === "dashboard") {
    loadDashboardStats();
    loadQuizList();
  }
}

// ─── UPLOAD & GENERATE ───────────────────────────────────────
function handlePDFSelect(input) {
  if (!input.files.length) return;
  selectedFile = input.files[0];
  const zone = document.getElementById("uploadZone");
  zone.classList.add("has-file");
  document.getElementById("uploadTitle").textContent = selectedFile.name;
  document.getElementById("uploadSub").textContent =
    (selectedFile.size / 1024 / 1024).toFixed(2) + " MB — ready to upload";
}

function toggleOpt(btn) {
  btn.classList.toggle("on");
}
function selectOpt(btn) {
  btn
    .closest(".opts")
    .querySelectorAll(".opt")
    .forEach((b) => b.classList.remove("on"));
  btn.classList.add("on");
}
function getSelected(group) {
  return (
    document.querySelector(`#opts-${group} .opt.on`)?.textContent.trim() || ""
  );
}

async function doGenerate() {
  if (!selectedFile) {
    showToast("Please upload a PDF first", "error");
    return;
  }

  const types = [];
  document
    .querySelectorAll("#page-generate .opts")[0]
    .querySelectorAll(".opt.on")
    .forEach((b) => types.push(b.textContent.trim().toLowerCase()));
  if (!types.length) {
    showToast("Select at least one question type", "error");
    return;
  }

  const diff = getSelected("diff").toLowerCase() || "medium";
  const numMcq = parseInt(getSelected("mcq")) || 10;
  const numTheory = parseInt(getSelected("theory")) || 5;

  const btn = document.getElementById("genBtn");
  const lb = document.getElementById("loadingBar");
  const ll = document.getElementById("loadingLabel");
  btn.disabled = true;
  btn.textContent = "Working...";
  lb.classList.add("show");

  try {
    // Step 1: Upload PDF
    ll.textContent = "Uploading PDF to server...";
    const formData = new FormData();
    formData.append("file", selectedFile);
    const uploadRes = await fetch(`${BASE}/upload/pdf`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("studymate_token")}`,
      },
      body: formData,
    });
    const uploadData = await uploadRes.json();
    if (!uploadRes.ok) {
      showToast(uploadData.error || "Upload failed", "error");
      return;
    }
    uploadedDocId = uploadData.document.id;

    // Step 2: Generate questions
    ll.textContent = "Generating questions with AI...";
    const genRes = await fetch(`${BASE}/quiz/generate`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        document_id: uploadedDocId,
        difficulty: diff,
        num_mcq: types.includes("mcq") ? numMcq : 0,
        num_theory: types.includes("theory") ? numTheory : 0,
        question_types: types,
      }),
    });
    const genData = await genRes.json();
    if (!genRes.ok) {
      showToast(genData.error || "Generation failed", "error");
      return;
    }

    showToast("Quiz generated successfully!", "success");
    loadQuizList();
    startCBT(genData.quiz);
    showPage("cbt");
  } catch (e) {
    showToast("Connection error. Make sure the backend is running.", "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate Questions from PDF";
    lb.classList.remove("show");
  }
}

// ─── DASHBOARD ───────────────────────────────────────────────
async function loadDashboardStats() {
  try {
    const res = await fetch(`${BASE}/results/stats`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    if (data.stats) {
      document.getElementById("stat-quizzes").textContent =
        data.stats.total_quizzes;
      document.getElementById("stat-attempts").textContent =
        data.stats.total_attempts;
      document.getElementById("stat-avg").textContent =
        data.stats.average_score + "%";
      document.getElementById("stat-best").textContent =
        data.stats.best_score + "%";
    }
  } catch {
    /* ignore */
  }
}

async function loadQuizList() {
  try {
    const res = await fetch(`${BASE}/quiz/`, { headers: authHeaders() });
    const data = await res.json();
    const list = document.getElementById("quizList");
    if (!data.quizzes || !data.quizzes.length) {
      list.innerHTML = `<div class="empty-state"><span class="empty-icon">📄</span><p>No quizzes yet. Upload a PDF to get started.</p></div>`;
      return;
    }
    list.innerHTML = data.quizzes
      .map(
        (q) => `
      <div class="quiz-card">
        <div class="quiz-info">
          <div class="quiz-title">${q.title}</div>
          <div class="quiz-meta">
            <span>${q.num_mcq} MCQs · ${q.num_theory} Theory</span>
            <span>${timeAgo(q.created_at)}</span>
            <span class="badge badge-${q.difficulty}">${q.difficulty}</span>
          </div>
          <div class="prog-wrap"><div class="prog-bar" style="width:${Math.random() * 40 + 50}%"></div></div>
        </div>
        <div class="quiz-actions">
          <button class="btn-sm" onclick="doShareQuiz('${q.id}')">Share</button>
          <button class="btn-sm primary" onclick="loadAndStartCBT('${q.id}')">Start CBT</button>
        </div>
      </div>`,
      )
      .join("");
  } catch {
    /* ignore */
  }
}

async function loadAndStartCBT(quizId) {
  try {
    const res = await fetch(`${BASE}/quiz/${quizId}`, {
      headers: authHeaders(),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast("Could not load quiz", "error");
      return;
    }
    startCBT(data.quiz);
    showPage("cbt");
  } catch {
    showToast("Connection error", "error");
  }
}

async function doShareQuiz(quizId) {
  try {
    const res = await fetch(`${BASE}/quiz/${quizId}/share`, {
      method: "POST",
      headers: authHeaders(),
    });
    const data = await res.json();
    if (res.ok) {
      navigator.clipboard?.writeText(data.share_link);
      showToast("Share link copied to clipboard!", "success");
    }
  } catch {
    showToast("Could not create share link", "error");
  }
}

// ─── CBT ENGINE ──────────────────────────────────────────────
function startCBT(quiz) {
  activeQuiz = quiz;
  cbtAnswers = {};
  cbtTheoryAnswers = {};
  cbtCurrentIdx = 0;
  cbtAllQuestions = [];

  const mcqs = (quiz.questions?.mcq || []).map((q, i) => ({
    ...q,
    type: "mcq",
    idx: i,
  }));
  const theory = (quiz.questions?.theory || []).map((q, i) => ({
    ...q,
    type: "theory",
    idx: i,
  }));
  cbtAllQuestions = [...mcqs, ...theory];

  const totalMins = Math.ceil(cbtAllQuestions.length * 1.5);
  cbtSecondsLeft = totalMins * 60;
  cbtStartTime = Date.now();

  document.getElementById("cbtTitle").textContent = quiz.title;
  document.getElementById("cbtMeta").textContent =
    `${mcqs.length} MCQs · ${theory.length} Theory · ${totalMins} minutes`;

  if (cbtTimer) clearInterval(cbtTimer);
  cbtTimer = setInterval(() => {
    cbtSecondsLeft--;
    const m = Math.floor(cbtSecondsLeft / 60);
    const s = cbtSecondsLeft % 60;
    document.getElementById("timerDisplay").textContent =
      m + ":" + String(s).padStart(2, "0");
    const pill = document.getElementById("timerPill");
    if (cbtSecondsLeft <= 300) {
      pill.className = "timer-pill";
    } else {
      pill.className = "timer-pill timer-ok";
    }
    if (cbtSecondsLeft <= 0) {
      clearInterval(cbtTimer);
      doSubmitCBT();
    }
  }, 1000);

  buildDotNav();
  renderCBTQuestion();
}

function buildDotNav() {
  const nav = document.getElementById("dotNav");
  nav.innerHTML = cbtAllQuestions
    .map(
      (_, i) =>
        `<div class="dot ${i === 0 ? "active" : ""}" onclick="jumpTo(${i})"></div>`,
    )
    .join("");
}

function updateDots() {
  const dots = document.querySelectorAll(".dot-nav .dot");
  dots.forEach((d, i) => {
    d.className = "dot";
    if (i === cbtCurrentIdx) d.classList.add("active");
    else if (cbtAllQuestions[i]?.type === "mcq" && cbtAnswers[i] !== undefined)
      d.classList.add("done");
    else if (cbtAllQuestions[i]?.type === "theory" && cbtTheoryAnswers[i])
      d.classList.add("done");
  });
}

function updateProgress() {
  const pct = (((cbtCurrentIdx + 1) / cbtAllQuestions.length) * 100).toFixed(0);
  document.getElementById("cbtProgressFill").style.width = pct + "%";
  document.getElementById("cbtMeta").textContent =
    `Question ${cbtCurrentIdx + 1} of ${cbtAllQuestions.length} · ${activeQuiz.difficulty} difficulty`;
}

function renderCBTQuestion() {
  const q = cbtAllQuestions[cbtCurrentIdx];
  if (!q) return;
  const container = document.getElementById("cbtQuestions");
  const isLast = cbtCurrentIdx === cbtAllQuestions.length - 1;
  document.getElementById("nextBtn").textContent = isLast
    ? "Submit Quiz →"
    : "Next →";
  updateDots();
  updateProgress();

  if (q.type === "mcq") {
    const selAns = cbtAnswers[cbtCurrentIdx];
    container.innerHTML = `
      <div class="question-card">
        <div class="q-tag">Question ${cbtCurrentIdx + 1} — Multiple Choice</div>
        <div class="q-text">${q.question}</div>
        <div class="options">
          ${(q.options || [])
            .map((opt, oi) => {
              const letter = ["A", "B", "C", "D"][oi];
              const isSel = selAns === letter;
              return `<div class="opt-row ${isSel ? "sel" : ""}" onclick="selectMCQ('${letter}')">
              <div class="opt-letter">${letter}</div>
              <span>${opt.replace(/^[A-D]\.\s*/, "")}</span>
            </div>`;
            })
            .join("")}
        </div>
      </div>`;
  } else {
    const saved = cbtTheoryAnswers[cbtCurrentIdx] || "";
    container.innerHTML = `
      <div class="theory-card">
        <div class="q-tag">Question ${cbtCurrentIdx + 1} — Theory</div>
        <div class="q-text">${q.question}</div>
        <textarea class="theory-textarea" id="theoryInput" placeholder="Type your answer here..." oninput="saveTheory()">${saved}</textarea>
        <button class="reveal-btn" onclick="toggleModelAns(this)">Show model answer</button>
        <div class="model-ans">${q.model_answer || ""}</div>
      </div>`;
  }
}

function selectMCQ(letter) {
  cbtAnswers[cbtCurrentIdx] = letter;
  renderCBTQuestion();
}

function saveTheory() {
  const val = document.getElementById("theoryInput")?.value || "";
  cbtTheoryAnswers[cbtCurrentIdx] = val;
}

function toggleModelAns(btn) {
  const ans = btn.nextElementSibling;
  const show = ans.style.display !== "block";
  ans.style.display = show ? "block" : "none";
  btn.textContent = show ? "Hide model answer" : "Show model answer";
}

function jumpTo(i) {
  cbtCurrentIdx = i;
  renderCBTQuestion();
}
function cbtPrev() {
  if (cbtCurrentIdx > 0) {
    cbtCurrentIdx--;
    renderCBTQuestion();
  }
}
function cbtNext() {
  if (cbtCurrentIdx < cbtAllQuestions.length - 1) {
    cbtCurrentIdx++;
    renderCBTQuestion();
  } else {
    doSubmitCBT();
  }
}

async function doSubmitCBT() {
  if (!activeQuiz) return;
  clearInterval(cbtTimer);
  const timeTaken = Math.floor((Date.now() - cbtStartTime) / 1000);

  // Convert indexed answers to string-keyed
  const mcqMap = {};
  const theoryMap = {};
  Object.entries(cbtAnswers).forEach(([i, v]) => {
    mcqMap[String(i)] = v;
  });
  Object.entries(cbtTheoryAnswers).forEach(([i, v]) => {
    theoryMap[String(i)] = v;
  });

  try {
    const res = await fetch(`${BASE}/results/submit`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        quiz_id: activeQuiz.id,
        mcq_answers: mcqMap,
        theory_answers: theoryMap,
        time_taken: timeTaken,
      }),
    });
    const data = await res.json();
    if (res.ok) {
      showResults(data.result, activeQuiz);
      showPage("results");
    } else {
      showToast("Could not submit quiz: " + (data.error || ""), "error");
    }
  } catch {
    showToast("Connection error submitting quiz", "error");
  }
}

// ─── RESULTS ─────────────────────────────────────────────────
function showResults(result, quiz) {
  const pct = result.mcq_percentage;
  const gradeColor =
    pct >= 70 ? "var(--green-dark)" : pct >= 50 ? "#854F0B" : "#A32D2D";
  const gradeBg =
    pct >= 70
      ? "var(--green-light)"
      : pct >= 50
        ? "var(--amber-light)"
        : "var(--red-light)";
  const msg =
    pct >= 70
      ? "Excellent work!"
      : pct >= 50
        ? "Good effort. Keep studying!"
        : "Keep going — practice makes perfect.";

  // Build feedback list
  const fbHtml = (result.feedback || [])
    .map(
      (f) => `
    <div class="fb-row ${f.is_correct ? "correct" : "wrong"}">
      <div class="fb-icon">${f.is_correct ? "✓" : "✗"}</div>
      <div>
        <div style="font-weight:500;margin-bottom:2px">${f.question}</div>
        ${!f.is_correct ? `<div class="text-small text-muted">Your answer: ${f.student_answer || "—"} &nbsp;·&nbsp; Correct: ${f.correct_answer}</div>` : ""}
      </div>
    </div>`,
    )
    .join("");

  document.getElementById("resultsContent").innerHTML = `
    <div class="result-hero">
      <div class="score-ring">
        <div class="score-num">${pct}%</div>
        <div class="score-lbl">score</div>
      </div>
      <div class="grade-pill" style="background:${gradeBg};color:${gradeColor}">Grade: ${result.grade}</div>
      <p class="result-msg">${msg}</p>
      <p class="result-sub">You answered ${result.mcq_score} out of ${result.total_mcq} MCQs correctly in ${result.time_display}.</p>
      <div class="result-stats">
        <div class="stat-card"><div class="stat-label">MCQ Score</div><div class="stat-value">${result.mcq_score}/${result.total_mcq}</div></div>
        <div class="stat-card"><div class="stat-label">Time Taken</div><div class="stat-value">${result.time_display}</div></div>
        <div class="stat-card"><div class="stat-label">Theory Done</div><div class="stat-value">${result.theory_submitted}/${result.total_theory}</div></div>
      </div>
      <div class="result-actions">
        <button class="btn-sm primary" onclick="showPage('cbt')">Retry Quiz</button>
        <button class="btn-sm" onclick="showPage('generate')">New Quiz</button>
        <button class="btn-sm" onclick="showPage('dashboard')">My Quizzes</button>
      </div>
    </div>
    ${fbHtml ? `<div class="card mt-2"><div class="card-title">MCQ Feedback</div><div class="feedback-list">${fbHtml}</div></div>` : ""}`;
}

// ─── UTILS ───────────────────────────────────────────────────
function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso)) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return Math.floor(diff / 60) + "m ago";
  if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
  return Math.floor(diff / 86400) + "d ago";
}

// ─── INIT ────────────────────────────────────────────────────
checkAuth();
