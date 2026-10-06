
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // Proxy: semua request ke /api/... diteruskan ke backend FastAPI.
    // Contoh: browser memanggil /api/todos -> diteruskan ke http://127.0.0.1:8000/todos
    // Keuntungannya, browser merasa semuanya satu origin, jadi tidak ada masalah CORS.
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});