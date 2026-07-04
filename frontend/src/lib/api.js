import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  headers: { "Content-Type": "application/json" },
});

export const fetchTopics = () => api.get("/topics").then((r) => r.data);
export const fetchTopic = (id) => api.get(`/topics/${id}`).then((r) => r.data);
export const fetchContent = (id) => api.get(`/topics/${id}/content`).then((r) => r.data);
export const fetchVideos = (id) => api.get(`/topics/${id}/videos`).then((r) => r.data);
export const fetchExercises = (id) => api.get(`/topics/${id}/exercises`).then((r) => r.data);
export const fetchSummary = (id) => api.get(`/topics/${id}/summary`).then((r) => r.data);
export const generateSummary = (id) => api.post(`/topics/${id}/summary/generate`).then((r) => r.data);
export const submitAnswer = (payload) => api.post(`/exercises/answer`, payload).then((r) => r.data);
export const fetchProgress = (sid) => api.get(`/progress/${sid}`).then((r) => r.data);
export const fetchRevision = (sid, limit = 10) =>
  api.get(`/revision/questions`, { params: { session_id: sid, limit } }).then((r) => r.data);
export const saveOpenAnswer = (payload) => api.post(`/open-answers`, payload).then((r) => r.data);
export const fetchOpenAnswers = (sid) => api.get(`/open-answers/${sid}`).then((r) => r.data);
export const fetchOpenAnswer = (sid, exId) =>
  api.get(`/open-answers/${sid}/exercise/${exId}`).then((r) => r.data);
