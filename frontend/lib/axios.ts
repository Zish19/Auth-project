import axios from "axios";

const api = axios.create({
  baseURL: "/api/backend",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export function normalizeApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }

    if (typeof error.message === "string") {
      return error.message;
    }
  }

  return "Something went wrong. Please try again.";
}

export default api;
