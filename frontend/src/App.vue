<template>
  <div class="layout">
    <header class="topbar">
      <div class="topbar-inner">
        <RouterLink to="/" class="brand" aria-label="KvarplataTracker — на главную">
          <span class="brand-logo">
            <svg
              viewBox="0 0 24 24"
              width="17"
              height="17"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M3 10.5 12 3l9 7.5" />
              <path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5" />
            </svg>
          </span>
          <span class="brand-text">Kvarplata<span>Tracker</span></span>
        </RouterLink>

        <nav class="nav" aria-label="Основная навигация">
          <RouterLink to="/" class="nav-link">Обзор</RouterLink>
          <RouterLink to="/readings" class="nav-link">Показания</RouterLink>
          <RouterLink to="/tariffs" class="nav-link">Тарифы</RouterLink>
        </nav>

        <div class="export-actions" aria-label="Выгрузка данных">
          <a class="export-link" href="/api/export/xlsx" title="Скачать все данные одной книгой Excel (показания, тарифы, расходы, итоги)">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <path d="M7 10l5 5 5-5" />
              <path d="M12 15V3" />
            </svg>
            Excel
          </a>
          <a class="export-link" href="/api/export/csv/all" title="Скачать все данные архивом ZIP — отдельные CSV-файлы по таблицам">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <path d="M7 10l5 5 5-5" />
              <path d="M12 15V3" />
            </svg>
            CSV
          </a>
        </div>
      </div>
    </header>

    <main class="page-container">
      <RouterView />
    </main>

    <footer class="footer">KvarplataTracker · учёт коммунальных платежей</footer>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Top bar */
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--bg) 82%, transparent);
  backdrop-filter: blur(12px) saturate(160%);
  -webkit-backdrop-filter: blur(12px) saturate(160%);
}

.topbar-inner {
  display: flex;
  align-items: center;
  max-width: 1160px;
  margin: 0 auto;
  padding: 10px 20px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text);
}

.brand-logo {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #fff;
  background: var(--accent-gradient);
  box-shadow: 0 8px 16px -8px var(--accent-glow);
}

.brand-text {
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.01em;
}

.brand-text span {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.nav {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.export-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid var(--border);
}

.export-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 13px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  color: var(--text-muted);
  background: var(--surface);
  font-weight: 650;
  font-size: 0.9rem;
  text-decoration: none;
  white-space: nowrap;
  transition: color 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
}

.export-link:hover {
  color: var(--accent);
  background: var(--accent-soft);
  border-color: var(--accent);
}

@media (prefers-color-scheme: dark) {
  .export-link {
    background: var(--surface-2);
  }
}

.nav-link {
  padding: 8px 15px;
  border-radius: 10px;
  color: var(--text-muted);
  font-weight: 650;
  font-size: 0.93rem;
  text-decoration: none;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.nav-link:hover {
  color: var(--text);
  background: color-mix(in srgb, var(--text) 6%, transparent);
}

.nav-link.router-link-active,
.nav-link.router-link-exact-active {
  color: var(--accent);
  background: var(--accent-soft);
}

/* Page container & footer */
.page-container {
  flex: 1;
  width: 100%;
  max-width: 1160px;
  margin: 0 auto;
  padding: 28px 20px 48px;
}

.footer {
  padding: 24px 20px 34px;
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-faint);
}

@media (max-width: 700px) {
  .topbar-inner {
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 16px;
  }

  .nav {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-left: 0;
  }

  .export-actions {
    order: 2;
    margin-left: auto;
    padding-left: 0;
    border-left: 0;
  }

  .nav-link {
    flex: 1 1 auto;
    text-align: center;
  }
}
</style>
