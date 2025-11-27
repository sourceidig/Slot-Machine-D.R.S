# Slot Machine D.R.S.

Sistema de control de máquinas tragamonedas para múltiples sucursales.

## Requisitos

- Python 3.10+
- MySQL 8.0+
- XAMPP o MySQL Server (Windows)

## Instalación

### 1. Configurar la Base de Datos MySQL

Abrir MySQL desde XAMPP o línea de comandos y crear la base de datos:

\`\`\`sql
CREATE DATABASE control_maquinas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
\`\`\`

### 2. Instalar Dependencias

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Configurar Django

Editar `slot_machine_drs/settings.py` si es necesario (usuario/contraseña de MySQL):

\`\`\`python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "control_maquinas",
        "USER": "root",          # Cambiar si es necesario
        "PASSWORD": "",          # Agregar contraseña si es necesario
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {"charset": "utf8mb4"},
    }
}
\`\`\`

### 4. Ejecutar Migraciones

\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 5. Crear Superusuario Administrador

\`\`\`bash
python manage.py createsuperuser
\`\`\`

Ingresar:
- Username (nombre de usuario)
- Email (opcional)
- Password (contraseña)
- Nombre completo
- Role: seleccionar "admin"

### 6. Iniciar el Servidor

\`\`\`bash
python manage.py runserver
\`\`\`

Abrir el navegador en: http://127.0.0.1:8000/

## Estructura del Proyecto

\`\`\`
slot_machine_drs/
├── core/                      # App principal
│   ├── models.py             # Modelos de BD
│   ├── views.py              # Vistas
│   ├── forms.py              # Formularios
│   ├── urls.py               # URLs
│   └── admin.py              # Admin de Django
├── templates/                # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── turno.html
│   ├── registro.html
│   └── ...
├── static/                   # Archivos estáticos
├── slot_machine_drs/        # Configuración del proyecto
│   ├── settings.py
│   └── urls.py
└── manage.py
\`\`\`

## Roles y Permisos

### Admin
- Dashboard con métricas
- Gestión de turnos (vista)
- Registro de lecturas
- Tablas con filtros avanzados
- CRUD de Máquinas, Zonas, Sucursales, Usuarios
- Reportes

### Usuario/Atendedora
- Gestión de turnos (abrir/cerrar)
- Registro de lecturas de máquinas
- Tablas de sus propias lecturas

## Funcionalidades Clave

### Turno
- Abrir turno (sucursal, zona, fecha, tipo)
- Solo un turno abierto por usuario
- Cerrar turno (calcula total automático)

### Registro de Máquinas
- Seleccionar máquina de la zona
- Ingresar entrada/salida/total
- Botón placeholder para IA/OCR (futuro)
- Validación de turno abierto

### Tablas y Reportes
- Filtros por fecha, sucursal, zona, máquina, usuario
- Exportar a Excel (.xlsx)
- Visualización de lecturas

### Admin CRUD
- Gestionar sucursales
- Gestionar zonas
- Gestionar máquinas
- Gestionar usuarios

## Integración IA (Futuro)

El botón "Escanear pantalla con IA" está preparado para integración futura:
- Endpoint: `/api/ia/capturar/`
- Por ahora devuelve datos dummy
- Ver comentarios en `core/views.py` para integrar OCR real

## Tecnologías

- **Backend**: Django 5.0
- **Base de Datos**: MySQL 8.0
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Exportación**: openpyxl (Excel)

## Soporte

Para problemas o consultas, revisar la documentación de Django en:
https://docs.djangoproject.com/
