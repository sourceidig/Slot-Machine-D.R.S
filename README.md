# Slot Machine D.R.S.

Sistema de control de máquinas tragamonedas para múltiples sucursales con funcionalidad OCR.

## Requisitos

- Python 3.10+
- MySQL 8.0+
- XAMPP o MySQL Server (Windows)
- **Tesseract OCR** (para funcionalidad de escaneo de pantallas)

## Instalación

### 1. Instalar Tesseract OCR

**En Windows:**
1. Descargar el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecutar el instalador (recomendado: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. Instalar en la ruta predeterminada: `C:\Program Files\Tesseract-OCR\`
4. Agregar Tesseract al PATH del sistema:
   - Panel de Control → Sistema → Configuración avanzada del sistema
   - Variables de entorno → Variable del sistema "Path" → Editar
   - Agregar: `C:\Program Files\Tesseract-OCR\`
   - Reiniciar el símbolo del sistema o IDE

**En Linux (Ubuntu/Debian):**
\`\`\`bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
\`\`\`

**En macOS:**
\`\`\`bash
brew install tesseract
\`\`\`

**Verificar instalación:**
\`\`\`bash
tesseract --version
\`\`\`

### 2. Configurar la Base de Datos MySQL

Abrir MySQL desde XAMPP o línea de comandos y crear la base de datos:

\`\`\`sql
CREATE DATABASE control_maquinas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
\`\`\`

### 3. Instalar Dependencias Python

\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Dependencias incluidas:**
- Django 5.0.2 - Framework web
- mysqlclient 2.2.4 - Conector MySQL
- openpyxl 3.1.2 - Exportación a Excel
- Pillow 10.2.0 - Procesamiento de imágenes
- **pytesseract 0.3.10 - OCR de texto en imágenes**

### 4. Configurar Django

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

### 5. Ejecutar Migraciones

\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 6. Crear Superusuario Administrador

\`\`\`bash
python manage.py createsuperuser
\`\`\`

Ingresar:
- Username (nombre de usuario)
- Email (opcional)
- Password (contraseña)
- Nombre completo
- Role: seleccionar "admin"

### 7. Iniciar el Servidor

\`\`\`bash
python manage.py runserver
\`\`\`

Abrir el navegador en: http://127.0.0.1:8000/

## Estructura del Proyecto

\`\`\`
slot_machine_drs/
├── core/                      # App principal
│   ├── models.py             # Modelos de BD
│   ├── views.py              # Vistas (incluye vista OCR)
│   ├── forms.py              # Formularios
│   ├── urls.py               # URLs
│   └── admin.py              # Admin de Django
├── templates/                # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── turno.html
│   ├── registro.html        # Incluye modal de cámara
│   └── ...
├── static/                   # Archivos estáticos
│   ├── js/
│   │   └── ocr_captura.js   # Script de captura OCR
│   └── css/
├── slot_machine_drs/        # Configuración del proyecto
│   ├── settings.py
│   └── urls.py
├── requirements.txt          # Dependencias
└── manage.py
\`\`\`

## Roles y Permisos

### Admin
- Dashboard con métricas
- Gestión de turnos (vista)
- Registro de lecturas
- **Captura OCR con cámara**
- Tablas con filtros avanzados
- CRUD de Máquinas, Zonas, Sucursales, Usuarios
- Reportes

### Usuario/Atendedora
- Gestión de turnos (abrir/cerrar)
- Registro de lecturas de máquinas
- **Captura OCR con cámara**
- Tablas de sus propias lecturas

## Funcionalidades Clave

### Turno
- Abrir turno (sucursal, fecha, tipo)
- Solo un turno abierto por usuario
- Cerrar turno (calcula total automático)
- Validación de fechas (2 días atrás a 1 día adelante)

### Registro de Máquinas
- Seleccionar zona (filtra máquinas dinámicamente)
- Seleccionar máquina de la zona
- Ingresar entrada/salida/total
- **Captura OCR con cámara (NUEVA)**
- Botón simulación IA (datos dummy)
- Validación de turno abierto

### Captura OCR con Cámara (NUEVO)

**Cómo funciona:**
1. El usuario presiona el botón "Capturar con Cámara (OCR)"
2. Se abre un modal con la vista de la cámara del dispositivo
3. El usuario enfoca la pantalla de la máquina tragamonedas
4. Presiona "Tomar Foto" para capturar la imagen
5. Presiona "Procesar con OCR" para analizar la imagen
6. El servidor usa Tesseract OCR para extraer texto
7. Busca las palabras "Entrada" y "Salida" + números
8. Rellena automáticamente los campos del formulario

**Endpoint:** `/api/ocr-lectura/`
- Método: POST
- Acepta: multipart/form-data con imagen
- Respuesta: JSON con {success, entrada, salida, total}

**Tecnología:**
- **Frontend:** MediaDevices API (acceso a cámara del navegador)
- **Backend:** Tesseract OCR + PIL (Python Imaging Library)
- **OCR:** Extracción de texto con configuración optimizada para números

**Mejoras recomendadas:**
- Ajustar la configuración de Tesseract según el formato de pantalla
- Agregar preprocesamiento de imagen (contraste, recorte)
- Entrenar Tesseract con fuentes específicas de las máquinas
- Implementar validación de valores extraídos

### Tablas y Reportes
- Filtros por fecha, sucursal, zona, máquina, usuario
- Exportar a Excel (.xlsx)
- Visualización de lecturas

### Admin CRUD
- Gestionar sucursales
- Gestionar zonas
- Gestionar máquinas
- Gestionar usuarios

## Configuración Avanzada de Tesseract

Si los resultados del OCR no son óptimos, puedes ajustar la configuración en `core/views.py`:

\`\`\`python
# Configuración actual (optimizada para números)
custom_config = r'--oem 3 --psm 6 outputbase digits'

# Otras opciones:
# --oem 3: Motor OCR LSTM
# --psm 6: Asume un bloque uniforme de texto
# --psm 4: Asume una sola columna de texto
# --psm 11: Texto disperso
# outputbase digits: Solo reconoce dígitos
\`\`\`

**Para mejorar precisión:**
1. Tomar fotos con buena iluminación
2. Enfocar correctamente la pantalla
3. Evitar reflejos y sombras
4. Mantener la cámara estable
5. Usar preprocesamiento de imagen si es necesario

## Mantenimiento y Limpieza

### Limpieza de datos antiguos
\`\`\`python
# En Django shell (python manage.py shell)
from core.models import LecturaMaquina
from datetime import datetime, timedelta

# Eliminar lecturas de hace más de 6 meses
fecha_limite = datetime.now() - timedelta(days=180)
LecturaMaquina.objects.filter(fecha_registro__lt=fecha_limite).delete()
\`\`\`

### Backup de base de datos
\`\`\`bash
# Exportar
mysqldump -u root -p control_maquinas > backup_$(date +%Y%m%d).sql

# Importar
mysql -u root -p control_maquinas < backup_20250101.sql
\`\`\`

### Logs de errores OCR
Los errores de OCR se registran en la consola del servidor. Para producción, configurar logging en `settings.py`:

\`\`\`python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'ocr_errors.log',
        },
    },
    'loggers': {
        'core.views': {
            'handlers': ['file'],
            'level': 'ERROR',
        },
    },
}
\`\`\`

## Tecnologías

- **Backend**: Django 5.0
- **Base de Datos**: MySQL 8.0
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **OCR**: Tesseract 5.x + pytesseract
- **Procesamiento de Imágenes**: Pillow (PIL)
- **Exportación**: openpyxl (Excel)

## Troubleshooting

### Error: "Tesseract no encontrado"
- Verificar que Tesseract esté instalado: `tesseract --version`
- Verificar que esté en el PATH del sistema
- En Windows, reiniciar el IDE después de agregar al PATH

### Error: "No se puede acceder a la cámara"
- Verificar permisos del navegador
- Usar HTTPS en producción (HTTP solo funciona en localhost)
- Algunos navegadores requieren permisos explícitos

### OCR no detecta valores correctamente
- Mejorar iluminación al tomar la foto
- Ajustar configuración de Tesseract en `core/views.py`
- Considerar preprocesamiento de imagen (contraste, umbral)

### Error de CSRF al enviar imagen
- Verificar que el CSRF token esté incluido en el request
- El script `ocr_captura.js` maneja esto automáticamente

## Soporte

Para problemas o consultas:
- Documentación de Django: https://docs.djangoproject.com/
- Documentación de Tesseract: https://github.com/tesseract-ocr/tesseract
- pytesseract: https://github.com/madmaze/pytesseract
