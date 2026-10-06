<script setup>
import { reactive, ref, watch, onMounted } from "vue";
import {
  listTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  seedTodos,
} from "./api";

import "./style.css";

const STATUSES = ["pending", "progress", "done"];
const PRIORITIES = ["low", "medium", "high"];

const filters = reactive({
  search: "",
  status: [],
  priority: [],
  sort_by: "created_at",
  order: "desc",
  page: 1,
  page_size: 10,
});

const data = reactive({
  items: [],
  total: 0,
  total_pages: 0,
});

const form = reactive({
  title: "",
  status: "pending",
  priority: "medium",
  description: "",
});

const editForm = reactive({
  id: null,
  title: "",
  status: "pending",
  priority: "medium",
  description: "",
});

const loading = ref(false);
const saving = ref(false);
const error = ref("");
const info = ref("");
const showEditModal = ref(false);

let searchTimer = null;

async function fetchTodos() {
  loading.value = true;
  error.value = "";

  try {
    const response = await listTodos(filters);

    data.items = response.items;
    data.total = response.total;
    data.total_pages = response.total_pages;

    if (
      data.items.length === 0 &&
      filters.page > 1 &&
      data.total_pages > 0
    ) {
      filters.page = data.total_pages;
    }
  } catch (e) {
    error.value = getErrorMessage(e);
  } finally {
    loading.value = false;
  }
}

function getErrorMessage(error) {
  if (error.response?.data?.detail) {
    if (Array.isArray(error.response.data.detail)) {
      return error.response.data.detail
        .map((item) => item.msg)
        .join(", ");
    }

    return error.response.data.detail;
  }

  return error.message || "Terjadi kesalahan.";
}

function showInfo(message) {
  info.value = message;

  setTimeout(() => {
    info.value = "";
  }, 3000);
}

function resetPage() {
  filters.page = 1;
}

function resetFilters() {
  filters.search = "";
  filters.status = [];
  filters.priority = [];
  filters.sort_by = "created_at";
  filters.order = "desc";
  filters.page = 1;
}

async function addTodo() {
  if (!form.title.trim()) return;

  saving.value = true;
  error.value = "";

  try {
    await createTodo({
      title: form.title.trim(),
      status: form.status,
      priority: form.priority,
      description: form.description.trim() || null,
    });

    form.title = "";
    form.description = "";
    form.status = "pending";
    form.priority = "medium";

    filters.page = 1;

    await fetchTodos();

    showInfo("Todo berhasil ditambahkan.");
  } catch (e) {
    error.value = getErrorMessage(e);
  } finally {
    saving.value = false;
  }
}

function openEdit(todo) {
  editForm.id = todo.id;
  editForm.title = todo.title;
  editForm.status = todo.status;
  editForm.priority = todo.priority;
  editForm.description = todo.description || "";

  showEditModal.value = true;
}

function closeEdit() {
  showEditModal.value = false;
}

async function saveEdit() {
  if (!editForm.title.trim()) return;

  saving.value = true;
  error.value = "";

  try {
    await updateTodo(editForm.id, {
      title: editForm.title.trim(),
      status: editForm.status,
      priority: editForm.priority,
      description: editForm.description.trim() || null,
    });

    closeEdit();

    await fetchTodos();

    showInfo("Todo berhasil diperbarui.");
  } catch (e) {
    error.value = getErrorMessage(e);
  } finally {
    saving.value = false;
  }
}

async function changeStatus(todo, status) {
  try {
    await updateTodo(todo.id, {
      status,
    });

    await fetchTodos();

    showInfo("Status berhasil diperbarui.");
  } catch (e) {
    error.value = getErrorMessage(e);
  }
}

async function changePriority(todo, priority) {
  try {
    await updateTodo(todo.id, {
      priority,
    });

    await fetchTodos();

    showInfo("Prioritas berhasil diperbarui.");
  } catch (e) {
    error.value = getErrorMessage(e);
  }
}

async function removeTodo(todo) {
  const confirmed = confirm(
    `Apakah kamu yakin ingin menghapus "${todo.title}"?`
  );

  if (!confirmed) return;

  try {
    await deleteTodo(todo.id);

    await fetchTodos();

    showInfo("Todo berhasil dihapus.");
  } catch (e) {
    error.value = getErrorMessage(e);
  }
}

async function seed() {
  try {
    const response = await seedTodos(1000);

    filters.page = 1;

    await fetchTodos();

    showInfo(`${response.inserted} todo berhasil ditambahkan.`);
  } catch (e) {
    error.value = getErrorMessage(e);
  }
}

function formatDate(value) {
  if (!value) return "-";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

watch(
  () => [
    filters.status.slice(),
    filters.priority.slice(),
    filters.sort_by,
    filters.order,
    filters.page_size,
  ],
  () => {
    resetPage();
    fetchTodos();
  }
);

watch(
  () => filters.search,
  () => {
    clearTimeout(searchTimer);

    resetPage();

    searchTimer = setTimeout(() => {
      fetchTodos();
    }, 300);
  }
);

watch(
  () => filters.page,
  () => {
    fetchTodos();
  }
);

onMounted(() => {
  fetchTodos();
});
</script>

<template>
  <div class="app">

    <!-- HEADER -->
    <header class="header">
      <div>
        <p class="eyebrow">TASK MANAGEMENT</p>
        <h1>Todo List</h1>
        <p class="subtitle">
          Kelola tugas kamu dengan mudah dan terorganisir.
        </p>
      </div>

      <button class="btn btn-secondary" @click="seed">
        + Generate 1000 Data
      </button>
    </header>

    <!-- ALERT -->
    <div v-if="error" class="alert alert-error">
      <span>{{ error }}</span>

      <button @click="error = ''">
        ×
      </button>
    </div>

    <div v-if="info" class="alert alert-success">
      {{ info }}
    </div>

    <!-- TOOLBAR -->
    <section class="toolbar">

      <div class="search-box">
        <span class="search-icon">⌕</span>

        <input
          v-model="filters.search"
          type="search"
          placeholder="Cari todo..."
        />
      </div>

      <select v-model="filters.sort_by" class="select">
        <option value="created_at">Terbaru</option>
        <option value="updated_at">Terakhir diubah</option>
        <option value="title">Judul</option>
        <option value="status">Status</option>
        <option value="priority">Prioritas</option>
      </select>

      <select v-model="filters.order" class="select">
        <option value="desc">Descending</option>
        <option value="asc">Ascending</option>
      </select>

      <select v-model.number="filters.page_size" class="select">
        <option :value="10">10 / halaman</option>
        <option :value="25">25 / halaman</option>
        <option :value="50">50 / halaman</option>
        <option :value="100">100 / halaman</option>
      </select>

      <button class="btn btn-light" @click="resetFilters">
        Reset
      </button>

    </section>

    <!-- FILTER -->
    <section class="filter-row">

      <div class="filter-group">
        <span class="filter-label">Status</span>

        <label
          v-for="status in STATUSES"
          :key="status"
          class="checkbox"
        >
          <input
            v-model="filters.status"
            type="checkbox"
            :value="status"
          />

          <span>{{ status }}</span>
        </label>
      </div>

      <div class="filter-group">
        <span class="filter-label">Prioritas</span>

        <label
          v-for="priority in PRIORITIES"
          :key="priority"
          class="checkbox"
        >
          <input
            v-model="filters.priority"
            type="checkbox"
            :value="priority"
          />

          <span>{{ priority }}</span>
        </label>
      </div>

    </section>

    <!-- ADD TODO -->
    <section class="panel add-panel">

      <div class="panel-header">
        <div>
          <h2>Tambah Todo</h2>
          <p>Buat tugas baru untuk dikerjakan.</p>
        </div>
      </div>

      <form class="add-form" @submit.prevent="addTodo">

        <div class="form-field field-title">
          <label>Judul</label>

          <input
            v-model="form.title"
            type="text"
            maxlength="255"
            placeholder="Contoh: Membuat API Todo"
            required
          />
        </div>

        <div class="form-field field-description">
          <label>Deskripsi</label>

          <input
            v-model="form.description"
            type="text"
            placeholder="Deskripsi singkat..."
          />
        </div>

        <div class="form-field">
          <label>Prioritas</label>

          <select v-model="form.priority">
            <option
              v-for="priority in PRIORITIES"
              :key="priority"
              :value="priority"
            >
              {{ priority }}
            </option>
          </select>
        </div>

        <div class="form-field">
          <label>Status</label>

          <select v-model="form.status">
            <option
              v-for="status in STATUSES"
              :key="status"
              :value="status"
            >
              {{ status }}
            </option>
          </select>
        </div>

        <button
          class="btn btn-primary add-button"
          type="submit"
          :disabled="saving"
        >
          {{ saving ? "Menyimpan..." : "Tambah Todo" }}
        </button>

      </form>

    </section>

    <!-- TODO TABLE -->
    <section class="panel">

      <div class="panel-header table-heading">
        <div>
          <h2>Daftar Todo</h2>
          <p>{{ data.total }} tugas ditemukan</p>
        </div>

        <div class="loading-text" v-if="loading">
          Memuat data...
        </div>
      </div>

      <div class="table-wrapper">

        <table>

          <thead>
            <tr>
              <th>Todo</th>
              <th>Status</th>
              <th>Prioritas</th>
              <th>Terakhir Diubah</th>
              <th class="action-column">Action</th>
            </tr>
          </thead>

          <tbody>

            <tr
              v-for="todo in data.items"
              :key="todo.id"
            >

              <td>
                <div class="todo-title">
                  {{ todo.title }}
                </div>

                <div
                  v-if="todo.description"
                  class="todo-description"
                >
                  {{ todo.description }}
                </div>
              </td>

              <td>
                <select
                  :value="todo.status"
                  :class="['status-select', todo.status]"
                  @change="
                    changeStatus(
                      todo,
                      $event.target.value
                    )
                  "
                >
                  <option
                    v-for="status in STATUSES"
                    :key="status"
                    :value="status"
                  >
                    {{ status }}
                  </option>
                </select>
              </td>

              <td>
                <select
                  :value="todo.priority"
                  :class="['priority-select', todo.priority]"
                  @change="
                    changePriority(
                      todo,
                      $event.target.value
                    )
                  "
                >
                  <option
                    v-for="priority in PRIORITIES"
                    :key="priority"
                    :value="priority"
                  >
                    {{ priority }}
                  </option>
                </select>
              </td>

              <td class="date">
                {{ formatDate(todo.updated_at) }}
              </td>

              <td class="actions">

                <button
                  class="action-btn edit"
                  title="Edit Todo"
                  @click="openEdit(todo)"
                >
                  Edit
                </button>

                <button
                  class="action-btn delete"
                  title="Hapus Todo"
                  @click="removeTodo(todo)"
                >
                  Hapus
                </button>

              </td>

            </tr>

            <tr v-if="!loading && data.items.length === 0">
              <td colspan="5" class="empty">
                <div class="empty-icon">✓</div>
                <strong>Tidak ada todo</strong>
                <p>
                  Belum ada tugas yang sesuai dengan filter.
                </p>
              </td>
            </tr>

          </tbody>

        </table>

      </div>

      <!-- PAGINATION -->
      <div class="pagination">

        <span>
          Halaman
          <strong>{{ filters.page }}</strong>
          dari
          <strong>{{ data.total_pages || 1 }}</strong>
        </span>

        <div class="pagination-buttons">

          <button
            class="btn btn-light"
            :disabled="filters.page <= 1"
            @click="filters.page--"
          >
            ← Sebelumnya
          </button>

          <button
            class="btn btn-light"
            :disabled="
              filters.page >= data.total_pages ||
              data.total_pages === 0
            "
            @click="filters.page++"
          >
            Berikutnya →
          </button>

        </div>

      </div>

    </section>

    <!-- EDIT MODAL -->
    <div
      v-if="showEditModal"
      class="modal-overlay"
      @click.self="closeEdit"
    >

      <div class="modal">

        <div class="modal-header">
          <div>
            <p class="eyebrow">EDIT TODO</p>
            <h2>Edit Todo</h2>
          </div>

          <button
            class="close-button"
            @click="closeEdit"
          >
            ×
          </button>
        </div>

        <form
          class="edit-form"
          @submit.prevent="saveEdit"
        >

          <div class="form-field">
            <label>Judul</label>

            <input
              v-model="editForm.title"
              type="text"
              maxlength="255"
              required
            />
          </div>

          <div class="form-field">
            <label>Deskripsi</label>

            <textarea
              v-model="editForm.description"
              rows="4"
              placeholder="Deskripsi..."
            ></textarea>
          </div>

          <div class="form-grid">

            <div class="form-field">
              <label>Status</label>

              <select v-model="editForm.status">
                <option
                  v-for="status in STATUSES"
                  :key="status"
                  :value="status"
                >
                  {{ status }}
                </option>
              </select>
            </div>

            <div class="form-field">
              <label>Prioritas</label>

              <select v-model="editForm.priority">
                <option
                  v-for="priority in PRIORITIES"
                  :key="priority"
                  :value="priority"
                >
                  {{ priority }}
                </option>
              </select>
            </div>

          </div>

          <div class="modal-actions">

            <button
              type="button"
              class="btn btn-light"
              @click="closeEdit"
            >
              Batal
            </button>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="saving"
            >
              {{ saving ? "Menyimpan..." : "Simpan Perubahan" }}
            </button>

          </div>

        </form>

      </div>

    </div>

  </div>
</template>