# CLAUDE.md — Plaza Games DRS

Sistema de gestión de máquinas tragamonedas. Django 4.1 + MariaDB/MySQL + Tesseract OCR. App en español (Chile).

---

## Flujo de trabajo

- El usuario escribe los cambios en `peticion.txt` y dice "lee peticion.txt". Leerlo y aplicarlo directamente.
- Los cambios son siempre acotados: el usuario especifica el archivo, qué cambiar y qué NO tocar.

---

## Comandos frecuentes

```bash
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
python manage.py test control --settings=slot_machine_drs.settings_test   # sin MariaDB
python manage.py test control                                               # con MariaDB
```

---

## Arquitectura

**Una sola app Django:** `control/`. No hay apps secundarias.

| Archivo | Contenido | Líneas |
|---|---|---|
| `control/views.py` | TODA la lógica de vistas | ~5370 |
| `control/models.py` | 25+ modelos | ~700 |
| `control/utils.py` | `get_referencia_anterior()`, `calcular_numerales_caja()` | ~140 |
| `control/decorators.py` | `@role_required()`, `@readonly_for()`, constantes de roles | ~80 |
| `control/middleware.py` | 4 middlewares personalizados | ~120 |
| `control/signals.py` | Audit log + signal de borrado en cascada | ~60 |
| `control/urls.py` | ~60 rutas, patrón `control:<name>` | ~153 |

Templates en `templates/<modulo>/`. Todos heredan de `templates/base.html`.

### Clases de layout (base.html / design system)

| Clase | Uso |
|---|---|
| `pg-card` | Contenedor principal de página |
| `pg-card-body` | Cuerpo del pg-card |
| `pg-header` / `pg-header-green` | Cabecera de sección con título y botón volver |
| `action-bar` | Barra sticky inferior con botones Guardar/Cancelar |
| `btn-pg-primary` / `btn-pg-secondary` | Botones principales de formulario |
| `section-title` | Subtítulo de sección (uppercase, pequeño) |

---

## Modelos — jerarquía y propósito

```
Sucursal → Zona → Maquina

Turno → LecturaMaquina          ← datos CRUDOS en vivo (borrar si se borra el Control)
      → ControlLecturas          ← datos OFICIALES guardados
           → ControlLecturasLinea

CuadraturaCajaDiaria            ← caja por turno (tiene FK a Turno, puede ser NULL)
CicloRecaudacion                ← ciclo mensual por sucursal
InformeRecaudacion → InformeRecaudacionLinea
```

**Regla crítica:** `LecturaMaquina` son datos en vivo. `ControlLecturasLinea` son datos oficiales.
- El dashboard y acumulados históricos usan `ControlLecturasLinea`, NO `LecturaMaquina`.
- Si se borra un `ControlLecturas`, el signal en `signals.py` elimina sus `LecturaMaquina` asociadas.

---

## Roles

`admin`, `gerente`, `supervisor`, `encargado`, `asistente`, `tecnico`

- `@role_required(*ROLES_X)` — restringe acceso
- `@readonly_for('supervisor')` — permite GET, bloquea POST
- `encargado` y `asistente` necesitan turno abierto (`SucursalEncargadoMiddleware`)

Constantes de grupos de roles definidas en `decorators.py` (`ROLES_TURNO`, `ROLES_CONFIG_EDIT`, etc.).

---

## Reglas de negocio críticas

### get_referencia_anterior() — `control/utils.py`

Calcula qué contador usar como base para una lectura nueva. Orden de prioridad:

1. Si es el primer día del ciclo → `maquina.contador_inicial_entrada/salida`
2. Lectura del mismo día de turno anterior (`LecturaMaquina`, mismo día) → válido
3. Último `ControlLecturas` anterior a esa fecha (`.order_by("-fecha_trabajo", "-id").first()`) → usa su línea
4. Fallback → `contador_inicial` de la máquina

**No busca `LecturaMaquina` de días anteriores** — eso causa datos fantasma.

### calcular_numerales_caja() — `control/utils.py`

- **`numeral_dia`** → viene de `ControlLecturas.total_general` filtrado por `sucursal + fecha + turno__tipo_turno`
- **`numeral_acumulado`** → `numeral_dia + anterior.numeral_acumulado`
- La caja anterior se busca por `fecha__lte + creado_el DESC`, **NO por tipo_turno** (el campo turno puede ser NULL en `CuadraturaCajaDiaria`)
- Usa `exclude_pk` para evitar referencia circular al editar

### RTP — fórmula única en todo el sistema

```python
rtp = (entrada - salida) / entrada * 100  # ganancia del local
```

- Positivo → local ganó / Negativo → local perdió
- `Maquina.rtp_creacion` → estático, ingresado al crear, nunca se modifica por código
- `Maquina.rtp_objetivo` → se actualiza en `LecturaMaquina.save()` con cada lectura
- En templates usar filtro `rtp_pct` de `custom_filters`, no `widthratio`

### Numerales en formulario de caja (encargada/supervisor)

La sucursal y fecha vienen pre-cargadas desde el servidor → el AJAX de numerales **no se dispara automáticamente**. El template `cuadratura_diaria/create.html` tiene un auto-trigger en `DOMContentLoaded` que llama `onHeaderChange()` con 200ms de delay cuando hay `turno_tipo_fijo`.

### Fórmulas cuadratura_diaria/create.html

```
subtotal = sorteos + gastos + sueldos + regalos + jugados
total    = subtotal - redbank - transfer + prestamos
descuadre = desglose_efectivo - total
ganancia  = desglose_efectivo - caja_inicial - (prestamos_ant + prestamos_hoy)
```

**NO incluir caja anterior ni numeral día en el subtotal.**

### JS en cuadratura_diaria/create.html

| Función | Responsabilidad |
|---|---|
| `setupDetalle({tbodyId, addBtnId, diaInputId, prefix})` | Configura cada sección de detalle (gastos/sueldos/regalos/jugados). Retorna `{addRow, recalcTotal}` |
| `addRow(nombre, monto)` | Agrega fila al tbody; oculta `[prefix]_empty_row` |
| `recalcTotal()` | Suma montos del tbody → actualiza input hidden + display |
| `recalcUI()` | Recalcula subtotal/total/descuadre/ganancia (solo visual) |
| `buildHiddenDetalles()` | Serializa ítems a inputs hidden antes del submit |
| `cargarNumerales()` | AJAX a `ajax_cuadratura_diaria_numerales` con sucursal+fecha+turno |
| `onHeaderChange()` | Llama cargarNumerales + recalcDesglose + recalcUI |

Los IDs de tbody son `gastos_items_body`, `sueldos_items_body`, `regalos_items_body`, `jugados_items_body`.
Cada sección tiene una fila vacía con id `[prefix]_empty_row` que se oculta al agregar ítems.

El formulario tiene `max-width: 780px; margin: 0 auto;` en el `pg-card`.

---

## Secciones de views.py (para ubicar código rápido)

Buscar por estas funciones ancla:

| Módulo | Función ancla |
|---|---|
| Auth | `def login_view` |
| Dashboard | `def dashboard` |
| Máquinas/Zonas/Sucursales | `def maquina_list` |
| Turnos | `def turno_view` |
| Registro lecturas | `def registro_lectura` |
| Control (guardar) | `def guardar_control` |
| Cuadratura diaria | `def cuadratura_diaria_create` |
| Cuadratura zonas | `def cuadratura_zona` |
| Cierre de turno | `def cierre_turno` |
| Recaudación | `def recaudacion` |
| AJAX numerales | `def ajax_cuadratura_diaria_numerales` |
| OCR API | `def api_ocr_lectura` |

---

## OCR

1. Frontend (`static/js/ocr_capturas.js`): captura con MediaDevices API
2. POST imagen a `/api/ocr-lectura/`
3. Backend: PIL preprocesa → pytesseract (`--oem 3 --psm 6`) → parseo de dígitos
4. Retorna `{success, entrada, salida, total}` que autocompletan el formulario

Tesseract debe estar instalado a nivel de sistema.

---

## Settings relevantes

- `AUTH_USER_MODEL = 'control.Usuario'`
- Idioma: `es-cl` / Timezone: `America/Santiago`
- Sesión: máximo 8 horas
- DB: MariaDB 10.3 producción, MySQL 8.0 desarrollo (puerto 3307 en producción, 3306 local)
- **Usar Django 4.1** (no 5.x) — incompatible con MariaDB 10.3
- Logging → `logs/django_errors.log`

### Middleware (orden importa)

1. Estándar Django
2. `AlertaSesionCerradaMiddleware`
3. `SucursalEncargadoMiddleware`
4. `ErrorHandlerMiddleware`

---

## Infraestructura producción

- **NAS Synology** con MariaDB 10.3 nativo
- **Dominio:** `pazagamesdrs.cl` via Cloudflare Tunnel
- **Docker:** contenedor `plazagames` (Django + Gunicorn puerto 8000) en red `plazanet`
- **Archivos:** `/volume1/docker/plazagames`
- Build tarda ~10 min (compila Tesseract)
- `.env` nunca se sube a GitHub

---

## Lo que NO hacer

- No editar archivos en `migrations/` a mano
- No usar `LecturaMaquina` para acumulados históricos en dashboard (usar `ControlLecturasLinea`)
- No buscar caja anterior por `turno__tipo_turno` (el FK turno puede ser NULL)
- No agregar `LecturaMaquina` de días anteriores como referencia en `get_referencia_anterior()`
- No cambiar la fórmula de RTP sin actualizar todos los puntos donde se calcula
- No incluir `cajaAnteriorVal` ni `numeralDiaVal` en el cálculo de `subtotal` de cuadratura diaria
- No tocar `setupDetalle`, `recalcTotal`, `buildHiddenDetalles` al hacer cambios visuales en create.html