import { api } from "./client";

export const authApi = {
  register: (payload) => api.post("/auth/register", payload).then((r) => r.data),
  login: (payload) => api.post("/auth/login", payload).then((r) => r.data),
  demo: () => api.post("/auth/demo").then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data)
};

export const chatApi = {
  createSession: (payload) => api.post("/chat/sessions", payload).then((r) => r.data),
  listSessions: () => api.get("/chat/sessions").then((r) => r.data),
  getSession: (id) => api.get(`/chat/sessions/${id}`).then((r) => r.data),
  sendMessage: (id, payload) => api.post(`/chat/sessions/${id}/messages`, payload).then((r) => r.data),
  endSession: (id) => api.patch(`/chat/sessions/${id}/end`).then((r) => r.data)
};

export const memoryApi = {
  list: (params = {}) => api.get("/memory", { params }).then((r) => r.data),
  create: (payload) => api.post("/memory", payload).then((r) => r.data),
  update: (id, payload) => api.put(`/memory/${id}`, payload).then((r) => r.data),
  delete: (id) => api.delete(`/memory/${id}`).then((r) => r.data),
  retrieve: (payload) => api.post("/memory/retrieve", payload).then((r) => r.data),
  summarize: () => api.post("/memory/summarize").then((r) => r.data)
};

export const profileApi = {
  get: () => api.get("/profile").then((r) => r.data),
  update: (payload) => api.put("/profile", payload).then((r) => r.data),
  updatePreferences: (payload) => api.put("/profile/preferences", payload).then((r) => r.data),
  progress: () => api.get("/profile/progress").then((r) => r.data)
};

export const evalApi = {
  run: (payload) => api.post("/eval/run", payload).then((r) => r.data),
  results: () => api.get("/eval/results").then((r) => r.data)
};

export const adminApi = {
  stats: () => api.get("/admin/system-stats").then((r) => r.data)
};

