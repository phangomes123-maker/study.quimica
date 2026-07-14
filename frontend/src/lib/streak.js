// Streak tracking (localStorage): counts consecutive days with any activity.
const KEY = "estudioquimica_streak";

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
}
function yesterday() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
}

export function pingStreak() {
  const state = getStreak();
  const t = today();
  if (state.lastDay === t) return state;

  if (state.lastDay === yesterday()) {
    state.count = (state.count || 0) + 1;
  } else {
    state.count = 1;
  }
  state.lastDay = t;
  state.best = Math.max(state.best || 0, state.count);
  localStorage.setItem(KEY, JSON.stringify(state));
  return state;
}

export function getStreak() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "{}");
  } catch {
    return {};
  }
}
