// Anonymous session id kept in localStorage for progress tracking.
const KEY = "estudioquimica_session";

export function getSessionId() {
  let s = localStorage.getItem(KEY);
  if (!s) {
    s = "sess_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem(KEY, s);
  }
  return s;
}
