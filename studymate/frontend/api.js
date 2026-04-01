const BASE_URL = "https://studymate-ai-2duq.onrender.com";

function getToken() {
  return localStorage.getItem("studymate_token");
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  };
}

// ─── AUTH ────────────────────────────────────────────────────
export async function registerUser(name, email, password) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  return res.json();
}

export async function loginUser(email, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function getMe() {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: authHeaders(),
  });
  return res.json();
}

// ─── UPLOAD ──────────────────────────────────────────────────
export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/upload/pdf`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });
  return res.json();
}

// ─── QUIZ ────────────────────────────────────────────────────
export async function generateQuiz(documentId, settings) {
  const res = await fetch(`${BASE_URL}/quiz/generate`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ document_id: documentId, ...settings }),
  });
  return res.json();
}

export async function getMyQuizzes() {
  const res = await fetch(`${BASE_URL}/quiz/`, {
    headers: authHeaders(),
  });
  return res.json();
}

export async function getQuiz(quizId) {
  const res = await fetch(`${BASE_URL}/quiz/${quizId}`, {
    headers: authHeaders(),
  });
  return res.json();
}

export async function shareQuiz(quizId) {
  const res = await fetch(`${BASE_URL}/quiz/${quizId}/share`, {
    method: "POST",
    headers: authHeaders(),
  });
  return res.json();
}

export async function getSharedQuiz(quizId) {
  const res = await fetch(`${BASE_URL}/quiz/shared/${quizId}`);
  return res.json();
}

// ─── RESULTS ─────────────────────────────────────────────────
export async function submitResult(quizId, mcqAnswers, theoryAnswers, timeTaken) {
  const res = await fetch(`${BASE_URL}/results/submit`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      quiz_id: quizId,
      mcq_answers: mcqAnswers,
      theory_answers: theoryAnswers,
      time_taken: timeTaken,
    }),
  });
  return res.json();
}

export async function getQuizResults(quizId) {
  const res = await fetch(`${BASE_URL}/results/quiz/${quizId}`, {
    headers: authHeaders(),
  });
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${BASE_URL}/results/stats`, {
    headers: authHeaders(),
  });
  return res.json();
}
