# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Slot Machine D.R.S.** — Sistema de gestión de máquinas tragamonedas. Django 4.1 + MariaDB/MySQL + Tesseract OCR. Aplicación en español (Chile) para registrar lecturas de máquinas, gestionar turnos, cuadraturas de caja y recaudaciones.

## Commands

```bash
# Development server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## Tests

```bash
# Con MariaDB corriendo (producción/NAS):
python manage.py test control
python manage.py test control.tests.LecturaMaquinaCalculosTest
python manage.py test control -v 2

# Sin MariaDB (desarrollo local, usa SQLite en memoria):
python manage.py test control --settings=slot_machine_drs.settings_test
python manage.py test control -v 2 --settings=slot_machine_drs.settings_test
```

**Estado actual:** 108 tests en verde cubriendo modelos, utils, OCR, formularios, decoradores, middleware y vistas.

## Local Development

El proyecto usa `python-dotenv` para cargar variables de entorno desde `.env` automáticamente.

### Configuración local

Crear archivo `.env` en la raíz del proyecto (nunca subir a GitHub):
DJANGO_SECRET_KEY=clave-local-desarrollo-12345
DJANGO_DEBUG=True
DB_NAME=bd_prueba
DB_USER=root
DB_PASSWORD=1234
DB_HOST=127.0.0.1
DB_PORT=3306

### Requisitos locales
- MySQL 8.0 corriendo en localhost
- Base de datos `bd_prueba` existente
- Tesseract instalado en el sistema
- `pip install python-dotenv` incluido en requirements.txt

### Flujo de trabajo
1. Desarrollar y probar en `http://127.0.0.1:8000`
2. Cuando esté listo: `git add -A && git commit -m "..." && git push`
3. Actualizar producción en el NAS (ver sección Production Deployment)

## Database

MariaDB 10.3 requerido en producción. MySQL 8.0 en desarrollo local. Config via variables de entorno (.env).

## Architecture

**Single Django app** — toda la lógica de negocio vive en `control/`. No hay apps secundarias.

### Models (`control/models.py` — 25+ models)

- **Auth:** `Usuario` (custom `AbstractUser`, campo `rol` con 6 roles: admin, gerente, supervisor, tecnico, encargado, asistente)
- **Org structure:** `Sucursal` → `Zona` → `Maquina`
- **Operations:** `Turno` → `LecturaMaquina` → `CierreMaquina`
- **Finance:** `CuadraturaCajaDiaria`, `EncuadreCajaAdmin`, `CierreTurno*`
- **Reporting:** `InformeRecaudacion*`, `ControlLecturas*`, `CicloRecaudacion`

### Views (`control/views.py` — ~5100 lines)

Archivo monolítico. Contiene:
- Auth: `login_view`, `logout_view`
- CRUD: Sucursales, Zonas, Máquinas, Usuarios
- Flujo de turno: `crear_turno`, `cierre_turno_*`
- Lecturas: `registro_lectura`, `guardar_lectura`
- Reconciliación: `cuadratura_caja_diaria`, `encuadre_caja_admin`
- **OCR API:** `POST /api/ocr-lectura/` — recibe imagen, retorna `{success, entrada, salida, total}`
- Endpoints AJAX para filtrado dinámico
- Exportación Excel con openpyxl

### Access Control

Roles via decoradores en `control/decorators.py`:
- `@role_required('admin', 'gerente')` — restringe vista a roles listados
- `@readonly_for('supervisor')` — permite lectura pero bloquea escritura

Roles `encargado` y `asistente` deben seleccionar `Sucursal` antes de cualquier acción (`SucursalEncargadoMiddleware`).

### OCR Flow

1. Frontend (`static/js/ocr_capturas.js`): abre modal de cámara via MediaDevices API
2. POST imagen a `/api/ocr-lectura/`
3. Backend: preprocesado PIL → pytesseract (`--oem 3 --psm 6`) → parseo de dígitos
4. Retorna entrada/salida/total que auto-completan el formulario

Tesseract debe estar instalado a nivel de sistema.

### URL Structure

Todas las URLs bajo app `control/`, incluidas desde `slot_machine_drs/urls.py`. Patrón: `control:<name>`.

### Templates

Todos heredan de `templates/base.html`. Menú dinámico generado por `control/menu.py` según rol del usuario.

### Middleware (orden importa)

1. Middleware estándar Django
2. `AlertaSesionCerradaMiddleware`
3. `SucursalEncargadoMiddleware`
4. `ErrorHandlerMiddleware` → `logs/django_errors.log`

### Settings

- `AUTH_USER_MODEL = 'control.Usuario'`
- Idioma: `es-cl`, Timezone: `America/Santiago`
- Sesión: máximo 8 horas
- Logging: archivo `logs/django_errors.log` (se crea automáticamente)
- `python-dotenv` carga `.env` automáticamente al inicio

## Production Deployment

El sistema corre en un NAS Synology expuesto via Cloudflare Tunnel.

### Infraestructura

- **NAS:** Synology 4GB RAM, MariaDB 10.3 nativo (puerto 3307)
- **Dominio:** pazagamesdrs.cl via Cloudflare Tunnel (Starlink CGNAT, sin IP pública)
- **Contenedores Docker** en red `plazanet`:
  - `plazagames` — Django + Gunicorn (puerto 8000)
  - `cloudflared` — túnel Cloudflare
- **Archivos proyecto:** `/volume1/docker/plazagames`
- **Variables de entorno:** `/volume1/docker/plazagames/.env`

### Variables de entorno producción (.env en NAS)
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
DB_NAME=bd_plazagames
DB_USER=django
DB_PASSWORD=...
DB_HOST=192.168.1.24
DB_PORT=3307
CSRF_TRUSTED_ORIGINS=https://pazagamesdrs.cl

### Actualizar producción después de git push

```bash
ssh nacho@192.168.1.24
cd /volume1/docker/plazagames
git pull
sudo docker stop plazagames && sudo docker rm plazagames
sudo nohup docker build -t plazagames:latest . > /tmp/build.log 2>&1 &
tail -f /tmp/build.log
# Cuando aparezca "Successfully built":
sudo docker run -d --name plazagames --restart always \
  -p 8000:8000 \
  --env-file .env \
  --network plazanet \
  plazagames:latest
```

### Notas importantes

- Usar **Django 4.1** (no 5.x) por compatibilidad con MariaDB 10.3
- El build tarda ~10 minutos por compilación de Tesseract
- `CSRF_TRUSTED_ORIGINS` debe incluir `https://pazagamesdrs.cl`
- Tunnel ID: `32f29c4e-36f4-43af-861f-bb41116acb64`
- Credenciales cloudflared: `/volume1/docker/cloudflared/`
- `.env` nunca se sube a GitHub (está en .gitignore)