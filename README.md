# KvarplataTracker

Учёт коммунальных платежей и показаний счётчиков (ХВС, ГВС, электричество) + аренда.
Замена Excel-таблицы «Счетчики.xlsx» на веб-приложение для домашнего сервера.

## Стек

- **Backend**: Python FastAPI + SQLAlchemy (async) + SQLite
- **Frontend**: Vue 3 + TypeScript + Vite + Pinia
- **Proxy**: Nginx (статика + `/api` → backend)
- **Развёртывание**: Docker Compose

## Быстрый старт (Docker)

```bash
docker compose up -d --build
```

Приложение будет доступно на `http://localhost:8080`.

## Локальная разработка без Docker

**Backend:**

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173 (проксирует /api на :8000)
```

## Структура

```
├── docker-compose.yml
├── Dockerfile.backend      # FastAPI + uvicorn
├── Dockerfile.frontend     # Vue build → nginx
├── nginx/default.conf      # SPA + proxy
├── backend/
│   ├── app/
│   │   ├── main.py         # Entrypoint
│   │   ├── models.py       # ORM: Tariff, Reading, MonthlyCost
│   │   ├── schemas.py      # Pydantic
│   │   ├── database.py     # Async engine
│   │   ├── routers/        # readings, tariffs, summary
│   │   └── services/calculator.py  # Логика расчёта
│   └── alembic/            # Миграции
├── frontend/
│   └── src/
│       ├── api/            # HTTP-клиент
│       ├── stores/         # Pinia (year)
│       ├── views/          # Dashboard, Readings, Tariffs
│       └── components/
└── data/                   # SQLite (volume, персистентно)
```

## API

Swagger-документация: `http://localhost:8080/api/docs` (или `:8000/docs` напрямую).

| Method | Path | Описание |
|--------|------|----------|
| GET | `/api/readings` | Показания (опц. фильтр `?year=`) |
| POST | `/api/readings` | Добавить показания |
| PUT | `/api/readings/{id}` | Изменить |
| DELETE | `/api/readings/{id}` | Удалить |
| GET | `/api/tariffs` | Все тарифы |
| PUT | `/api/tariffs` | Обновить/создать тариф |
| GET | `/api/summary?year=2026` | Расчёт по месяцам за год |
| GET | `/api/summary/stats?year=2026` | Статистика за год |
| GET | `/api/export/xlsx` | Выгрузить все данные книгой Excel (листы: показания, тарифы, расходы, итоги) |
| GET | `/api/export/csv/all` | Выгрузить все данные архивом ZIP с CSV-файлами по таблицам |
| GET | `/api/export/csv/readings` | Показания в CSV |
| GET | `/api/export/csv/tariffs` | Тарифы в CSV |
| GET | `/api/export/csv/monthly` | Помесячные расходы в CSV |
| GET | `/api/export/csv/totals` | Итоги по годам в CSV |

CSV-файлы используют кодировку UTF-8 (с BOM) и разделитель `;`, поэтому корректно открываются в локализованном Excel. В интерфейсе кнопки «Excel» и «CSV» находятся в верхней панели.

## Расчёт

```
расход_мес = показание_тек − показание_пред
стоимость  = расход × тариф + аренда
```

Первое показание в базе служит базовой точкой — за месяц его постановки
начисления равны нулю (как в исходной таблице, «Март» = 0).

## Бэкап

Вся база — один файл `data/kvarplata.db`. Достаточно периодически копировать его.
