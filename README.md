# SmartHome

Умный дом: FastAPI + PostgreSQL + статический фронт за nginx.

## Структура репозитория

```
SmartHomeServer/
├── docker-compose.yml     # orchestration: web + api + db
├── README.md
├── backend/               # FastAPI, SQLAlchemy, Alembic
│   ├── Dockerfile
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── api/
│   ├── db/
│   └── alembic/
├── frontend/              # статика + nginx (образ web)
│   ├── Dockerfile
│   ├── nginx.conf
│   └── *.html, *.js, *.css
└── docs/                  # в т.ч. инструкция для ESP
```

Корень содержит только **compose**, **README** и каталоги сервисов — без смешивания кода бэка и фронта.

## Запуск (Docker)

Из **корня** репозитория:

```bash
docker compose up --build
```

| Сервис | Снаружи | Назначение |
|--------|---------|------------|
| **web** | http://localhost:8080 | nginx: статика, прокси `/api/` → api |
| **api** | http://localhost:8000 | FastAPI (ESP, отладка) |
| **db** | localhost:5432 | PostgreSQL |

Почему **8080**, а не 80: на многих системах порт 80 уже занят (nginx, apache). Внутри контейнера web по-прежнему **80**.

- **Сайт:** http://localhost:8080/  
- **Swagger через nginx:** http://localhost:8080/docs  
- **API / Swagger напрямую:** http://localhost:8000 и http://localhost:8000/docs  

Интеграция фронта с API (`fetch('/api/...')` при открытии с **:8080**) — следующий шаг; прокси в `frontend/nginx.conf` уже настроен.

## Локальная разработка бэка (без Docker)

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # при необходимости поправь DATABASE_URL
.venv/bin/alembic upgrade head
.venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Нужен запущенный PostgreSQL, совместимый с `DATABASE_URL`.

---

## API (кратко)

### Датчики в `POST /api/update` (`readings`)

- **float:** temperature, humidity  
- **bool:** movement, gas, night_light, day_light  

Остальное (vent, розетки, rgb, servo и т.д.) — **устройства**, состояние в ответе `devices`, не в `readings`.

### Устройства

По комнатам 1 и 2: `night_light`, `day_light`, `vent`, `socket_tv`, `socket_ac`.  
**servo** — только комната **2**. **rgb** — только комната **1**.

### ESP32 → сервер

```
POST /api/update
```

```json
{
  "readings": [
    {"sensor_name": "temperature", "room_id": 1, "value": 22.5},
    {"sensor_name": "humidity", "room_id": 1, "value": 45.0},
    {"sensor_name": "night_light", "room_id": 1, "value": 1.0}
  ]
}
```

Ответ **POST** — только `received` (сколько показаний принято).  
Актуальное состояние реле и сценарий — **`GET /api/update`** (без тела): `devices`, `scenario`, `auto_mode`.

### Фронт / клиент

| Метод | Путь |
|-------|------|
| GET | /api/sensors/latest?room_id=1 |
| GET | /api/sensors/latest/{sensor_name}?room_id=1 |
| GET | /api/devices |
| GET/POST | /api/devices/{type}?room_id=… |

**Инструкция для ESP по сети:** [docs/ESP_SETUP_FOR_FRIEND.md](docs/ESP_SETUP_FOR_FRIEND.md) — для запросов к API удобно хост: **8000** или тот же хост с **8080** и путём `/api/...`.
