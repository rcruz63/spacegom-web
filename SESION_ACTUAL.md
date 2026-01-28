# Sesión Actual

**Fecha:** 28/01/2025  
**Duración:** (dejar en blanco si no lo anotaste)

---

## 🎯 Objetivo de la Sesión

- [x] Migrar la app a **DynamoDB 100%** (sin SQLite ni archivos locales en runtime).
- [x] Añadir **load_dotenv** para cargar `.env` con credenciales AWS y poder probar acceso.

---

## 📊 Estado Actual

### ✅ Qué Funciona

- **Persistencia DynamoDB**: Planetas en `SpacegomPlanets`; juegos, personal, misiones, órdenes y tareas en `SpacegomGames` (Single Table Design).
- **Capa de acceso**: `app/aws_client.py` (boto3, `item_from_decimal` / `item_to_decimal`), `app/planets_repo.py` (Planet DTO, CRUD planetas).
- **GameState**: Carga/guardado solo en DynamoDB; `METADATA`, `LOG#*`, `PERSONNEL#*`, `MISSION#*`, `ORDER#*`, `TASK#*`. Sin escritura a disco.
- **Rutas y managers**: `TradeManager`, commerce, personnel, missions, games y event_handlers usan `GameState` / `planets_repo`. Sin `get_db` ni SQLite.
- **`.env`**: `load_dotenv` en `app/main.py` (antes de cualquier import AWS). Variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`. Hay `.env.example` de referencia.
- **init_db**: No-op; la app no crea tablas SQLite.

### ❌ Qué Está Roto

- (Nada crítico detectado en esta sesión.) Si al comprar no se muestran tiradas/modificadores/efectos de moral, conviene **verificarlo** al retomar.

### ⚠️ Problemas Conocidos

- **Tablas DynamoDB**: Deben existir en AWS (`SpacegomPlanets`, `SpacegomGames`). Si no: `python app/aws_setup.py`.
- **Scripts legacy**: `import_planets.py`, `update_planets_from_excel.py`, `main2.py`, `fix_db.py` siguen usando SQLite. No migrados.
- **Migración de datos**: `migrate_to_dynamodb.py` puede requerir ajustes al esquema actual de `entity_id` si se han cambiado formatos.

---

## 📝 Archivos Modificados

### Nuevos archivos
- `app/aws_client.py`: Cliente DynamoDB, tablas, helpers Decimal.
- `app/planets_repo.py`: Planet DTO y acceso a `SpacegomPlanets`.
- `.env.example`: Plantilla de variables AWS (sin valores).

### Archivos modificados
- `app/main.py`: `load_dotenv` al inicio; docstring actualizado.
- `app/database.py`: `init_db` convertido en no-op.
- `app/game_state.py`: Refactor completo a DynamoDB (load/save, entidades, logs).
- `app/trade_manager.py`: Sin `db`; usa `GameState` y `planets_repo`.
- `app/event_handlers.py`: Handlers sin `db`; usan `GameState`.
- `app/event_logger.py`: Usa `game.append_event_log`.
- `app/personnel_manager.py`: `update_employee_roll_stats` compatible con dicts.
- `app/routes/commerce.py`: Sin `get_db`; `GameState` y `TradeManager(game_id)`.
- `app/routes/games.py`: Sin `get_db`; `GameState` para setup y avance de tiempo.
- `app/routes/missions.py`: Sin `get_db`; `GameState` para misiones.
- `app/routes/personnel_routes.py`: Sin `get_db`; `GameState` para personal y tareas.
- `app/routes/planets.py`: Usa `planets_repo` (ya estaba en sesiones anteriores).
- `app/aws_client.py`: Docstring con variables de entorno y `load_dotenv`.
- `pyproject.toml`: Dependencia `python-dotenv>=1.0.0`.

### Archivos eliminados
- (Ninguno.)

---

## 🚀 Próximos Pasos

1. **Comprobar `.env`**: Debe tener `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (formato boto3).
2. **Tablas DynamoDB**: Si no existen, ejecutar `python app/aws_setup.py` (con credenciales cargadas).
3. **Arrancar app**: `uv run dev` o `uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
4. **Probar flujos**: Listar juegos, crear partida, comercio, personal, misiones. Revisar que las tiradas/modificadores/moral en compra se muestren bien.
5. **(Opcional)** Revisar `migrate_to_dynamodb.py` si vas a migrar datos existentes al esquema actual.
6. **Otros datos** Para la generación de nombres en el setup se utilizan unos ficheros csv. Estudiar la mejor manera de sustituirlos
7. **Datos estaticos** Hay algunos diccionarios de datos, como los datos de las naves o diccionarios para interpretar los valores de la tabla planets que hay que estudiar la mejor manera en la nueva arquitectura.

### Notas importantes
- `.env` está en `.gitignore`; no subir credenciales.
- Para DynamoDB local: `DYNAMODB_ENDPOINT_URL` en `.env` (ej. `http://localhost:8000`).

---

## 💻 Comandos Pendientes

### Servidores en ejecución
- [ ] Servidor FastAPI en `127.0.0.1:8000`

### Comandos para ejecutar al retomar
```bash
# Instalar deps (por si acaso)
uv sync

# Crear tablas DynamoDB en AWS (si no existen)
uv run python app/aws_setup.py

# Arrancar app (carga .env desde raíz del proyecto)
uv run dev
# o: uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Verificar acceso a DynamoDB
```bash
uv run python -c "
from app.main import app
from app.aws_client import get_planets_table
t = get_planets_table()
print('Tabla:', t.table_name)
r = t.scan(Limit=1)
print('Scan OK, count:', r.get('Count', 0))
"
```

---

## 📚 Referencias Útiles

- `CONTEXT_ACTUALIZADO.md`: Estado general del proyecto y características.
- `docs/aws_setup.md`, `docs/migrate_to_dynamodb.md`: AWS y migración.
- `.env.example`: Variables de entorno esperadas.

---

## 💭 Notas Adicionales

- La app ya **no escribe en disco** (state, logs, SQLite). Todo persistido en DynamoDB.
- `main2.py` y scripts de import/Excel siguen con SQLite; no se han migrado.
