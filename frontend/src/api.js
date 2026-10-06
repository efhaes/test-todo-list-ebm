import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function listTodos(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (
      value === "" ||
      value === null ||
      value === undefined
    ) {
      return;
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return;
      }

      value.forEach((item) => {
        searchParams.append(key, item);
      });

      return;
    }

    searchParams.append(key, value);
  });

  const response = await api.get("/todos", {
    params: searchParams,
  });

  return response.data;
}

export async function createTodo(data) {
  const response = await api.post("/todos", data);

  return response.data;
}

export async function updateTodo(id, data) {
  const response = await api.patch(`/todos/${id}`, data);

  return response.data;
}

export async function deleteTodo(id) {
  const response = await api.delete(`/todos/${id}`);

  return response.data;
}

export async function seedTodos() {
  const response = await api.post("/todos/seed");

  return response.data;
}