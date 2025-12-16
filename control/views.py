from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from PIL import Image, ImageOps
from datetime import time
from django.core.exceptions import ValidationError
from django.db import IntegrityError

import re, base64
import json
import re


from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .models import Usuario, Sucursal, Zona, Maquina, Turno, LecturaMaquina
from .forms import (
    TurnoForm, LecturaMaquinaForm, SucursalForm, ZonaForm, 
    MaquinaForm, UsuarioForm, UsuarioEditForm
)

import pytesseract
from pytesseract import Output
from PIL import Image
import io
from django.views.decorators.csrf import csrf_exempt

# Helper function para verificar si es admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# Helper function para verificar si es usuario
def is_usuario(user):
    return user.is_authenticated and user.role == 'usuario'


# ============================================
# AUTENTICACIÓN
# ============================================

def login_view(request):
    """
    Vista de login
    """
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('control:dashboard')
        else:
            return redirect('control:turno')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirigir según el rol
            if user.role == 'admin':
                return redirect('control:dashboard')
            else:
                return redirect('control:turno')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')


@login_required
def logout_view(request):
    """
    Vista de logout
    """
    logout(request)
    return redirect('control:login')

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ============================================
# DASHBOARD (solo admin)
# ============================================

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    """
    Dashboard empresarial con KPIs y filtros
    """
    hoy = timezone.now().date()

    # =========================
    # 1. Filtros (GET)
    # =========================
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    sucursal_id = request.GET.get('sucursal')

    # Fechas por defecto: últimos 7 días
    if not fecha_hasta:
        fecha_hasta = hoy
    else:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()

    if not fecha_desde:
        fecha_desde = fecha_hasta - timedelta(days=6)
    else:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()

    # =========================
    # 2. Query base
    # =========================
    inicio = timezone.make_aware(datetime.combine(fecha_desde, time.min))
    fin = timezone.make_aware(datetime.combine(fecha_hasta, time.max))

    lecturas = LecturaMaquina.objects.filter(fecha_registro__range=(inicio, fin))

    if sucursal_id:
        lecturas = lecturas.filter(sucursal_id=sucursal_id)

    # =========================
    # 3. KPIs empresariales
    # =========================
    kpis = lecturas.aggregate(
        total_entrada=Sum('entrada'),
        total_salida=Sum('salida'),
        total_neto=Sum('total'),
        maquinas_activas=Count('maquina', distinct=True),
        total_lecturas=Count('id')
    )

    # Evitar None
    for k in kpis:
        kpis[k] = kpis[k] or 0

    # =========================
    # 4. Gráfico: Neto por día
    # =========================
    chart_labels = []
    chart_data = []

    fecha_cursor = fecha_desde
    while fecha_cursor <= fecha_hasta:
        inicio_dia = timezone.make_aware(datetime.combine(fecha_cursor, time.min))
        fin_dia = timezone.make_aware(datetime.combine(fecha_cursor, time.max))

        total_dia = LecturaMaquina.objects.filter(
            fecha_registro__range=(inicio_dia, fin_dia)
        )

        if sucursal_id:
            total_dia = total_dia.filter(sucursal_id=sucursal_id)

        total_dia = total_dia.aggregate(suma=Sum('total'))['suma'] or 0

        chart_labels.append(fecha_cursor.strftime('%d/%m'))
        chart_data.append(int(total_dia))

        fecha_cursor += timedelta(days=1)

    # =========================
    # 5. Top / Bottom máquinas
    # =========================
    top_maquinas = lecturas.values(
        'numero_maquina', 'nombre_juego'
    ).annotate(
        neto=Sum('total')
    ).order_by('-neto')[:5]

    bottom_maquinas = lecturas.values(
        'numero_maquina', 'nombre_juego'
    ).annotate(
        neto=Sum('total')
    ).order_by('neto')[:5]

    context = {
        # KPIs
        'kpis': kpis,

        # Gráfico
        'chart_labels': chart_labels,
        'chart_data': chart_data,

        # Tablas
        'top_maquinas': top_maquinas,
        'bottom_maquinas': bottom_maquinas,

        # Filtros
        'sucursales': Sucursal.objects.all().order_by('nombre'),
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }

    return render(request, 'dashboard.html', context)


# ============================================
# TURNO
# ============================================

@login_required
def turno_view(request):
    """
    Vista de gestión de turnos para usuarios
    """
    # Obtener turno abierto del usuario
    turno_abierto = Turno.objects.filter(
        usuario=request.user,
        estado='Abierto'
    ).first()
    
    if request.method == 'POST':
        if not turno_abierto:
            # Iniciar nuevo turno
            form = TurnoForm(request.POST)
            if form.is_valid():
                turno = form.save(commit=False)
                turno.usuario = request.user
                turno.estado = 'Abierto'
                try:
                    turno.full_clean()
                    turno.save()
                    messages.success(request, 'Turno iniciado exitosamente.')
                    return redirect('control:turno')
                except Exception as e:
                    messages.error(request, str(e))
        else:
            messages.warning(request, 'Ya tiene un turno abierto.')
    
    form = TurnoForm() if not turno_abierto else None
    
    # Contar lecturas del turno abierto
    cantidad_lecturas = 0
    if turno_abierto:
        cantidad_lecturas = LecturaMaquina.objects.filter(
            turno=turno_abierto
        ).count()
    
    context = {
        'turno_abierto': turno_abierto,
        'cantidad_lecturas': cantidad_lecturas,
        'form': form,
        'sucursales': Sucursal.objects.all(),
    }
    
    return render(request, 'turno.html', context)


@login_required
def cerrar_turno(request, turno_id):
    """
    Cerrar un turno
    """
    turno = get_object_or_404(Turno, id=turno_id, usuario=request.user)
    
    if turno.estado == 'Abierto':
        # Calcular total de cierre
        total = LecturaMaquina.objects.filter(turno=turno).aggregate(
            total_sum=Sum('total')
        )['total_sum'] or 0
        
        turno.estado = 'Cerrado'
        turno.total_cierre = Decimal(str(total))
        turno.save()
        
        messages.success(request, f'Turno cerrado exitosamente. Total: ${turno.total_cierre:,.0f}')
    else:
        messages.warning(request, 'El turno ya está cerrado.')
    
    return redirect('control:turno')


# ============================================
# REGISTRO DE LECTURAS
# ============================================

@login_required
def registro_view(request):
    """
    Vista de registro de lecturas de máquinas
    """
    turno_abierto = Turno.objects.filter(
        usuario=request.user,
        estado='Abierto'
    ).first()

    zona_guardada_id = request.session.get('ultima_zona')

    if request.method == 'POST':

        if not turno_abierto:
            messages.error(
                request,
                'Debe iniciar un turno en la pestaña "Turno" antes de registrar lecturas.'
            )
            return redirect('control:turno')

        form = LecturaMaquinaForm(request.POST, turno=turno_abierto)

        if form.is_valid():
            lectura = form.save(commit=False)
            lectura.turno = turno_abierto
            lectura.usuario = request.user

            #  Campos derivados
            lectura.sucursal = turno_abierto.sucursal
            lectura.zona = form.cleaned_data['zona']

            # ⬅️ AÑADIR ESTO:
            if lectura.maquina:
                lectura.numero_maquina = lectura.maquina.numero_maquina
                lectura.nombre_juego = lectura.maquina.nombre_juego

            try:
                lectura.full_clean()
                lectura.save()
            except IntegrityError:
                messages.error(
                    request,
                    'Ya existe una lectura para esa máquina en este turno.'
                )
            except ValidationError as e:
                messages.error(request, '; '.join(e.messages))
            else:
                request.session['ultima_zona'] = lectura.zona.id
                messages.success(request, 'Lectura registrada exitosamente.')
                return redirect('control:registro')
        else:
            messages.error(request, "Formulario inválido. Revise los datos enviados.")

    else:
        if turno_abierto:
            if zona_guardada_id:
                form = LecturaMaquinaForm(
                    turno=turno_abierto,
                    initial={'zona': zona_guardada_id}
                )
            else:
                form = LecturaMaquinaForm(turno=turno_abierto)
        else:
            form = None

    context = {
        'turno_abierto': turno_abierto,
        'form': form,
        'zona_guardada': zona_guardada_id,
    }

    return render(request, 'registro.html', context)


# ============================================
# AJAX ENDPOINTS
# ============================================

@login_required
def get_zonas_ajax(request, sucursal_id):
    zonas = Zona.objects.filter(
        sucursal_id=sucursal_id,
        is_active=True
    ).values('id', 'nombre')
    return JsonResponse(list(zonas), safe=False)


def get_maquinas_ajax(request, zona_id):
    maquinas = Maquina.objects.filter(
        zona_id=zona_id,
        estado='Operativa',
        zona__is_active=True
    ).values('id', 'numero_maquina', 'nombre_juego')
    return JsonResponse(list(maquinas), safe=False)
# ============================
#             OCR 
# ============================

@csrf_exempt
def ocr_lectura(request):

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    try:
        # ============================
        # 1. Cargar imagen
        # ============================
        if "imagen" in request.FILES:
            imagen = Image.open(request.FILES["imagen"])
        else:
            data = json.loads(request.body.decode("utf-8"))
            b64 = data.get("image")
            if not b64:
                return JsonResponse({"success": False, "error": "No se recibió imagen"}, status=400)
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            imagen = Image.open(io.BytesIO(base64.b64decode(b64)))

        # ============================
        # 2. Preprocesamiento
        # ============================
        imagen = imagen.convert("L")
        imagen = ImageOps.autocontrast(imagen)

        w, h = imagen.size
        factor = max(2.0, 1500 / max(w, h))
        imagen = imagen.resize((int(w * factor), int(h * factor)), Image.LANCZOS)

        imagen = imagen.point(lambda x: 0 if x < 150 else 255, "1")

        config = "--oem 3 --psm 6"

        # OCR crudo (texto completo)
        texto_plano = pytesseract.image_to_string(imagen, lang="eng", config=config)
        print("===== OCR RAW =====")
        print(texto_plano)

        # OCR estructurado (por líneas)
        data = pytesseract.image_to_data(imagen, lang="eng", config=config, output_type=Output.DICT)
        filas = agrupar_lineas(data)

        entrada = None
        salida = None
        entrada_raw = None
        salida_raw = None

        # ============================
        # 3. Buscar ENTRADAS / SALIDAS
        # ============================
        for f in filas:
            txt_norm = normalizar_texto_label(f["texto"])

            # ---- ENTRADAS ----
            if entrada is None and es_linea_entrada(txt_norm) and f["numeros"]:
                entrada_raw, entrada_str = extraer_monto_desde_tokens(f["numeros"])
                entrada = normalizar_valor(entrada_str)
                print("[OK] ENTRADA:", entrada_raw, "->", entrada)

            # ---- SALIDAS ----
            if salida is None and es_linea_salida(txt_norm) and f["numeros"]:
                salida_raw, salida_str = extraer_monto_desde_tokens(f["numeros"])
                salida = normalizar_valor(salida_str)
                print("[OK] SALIDA:", salida_raw, "->", salida)

        # ============================
        # 4. Fallback: número en línea siguiente para SALIDAS
        # ============================
        if salida is None:
            for i in range(len(filas) - 1):
                txt_norm = normalizar_texto_label(filas[i]["texto"])
                if es_linea_salida(txt_norm):
                    nums_sig = filas[i + 1]["numeros"]
                    if nums_sig:
                        salida_raw, salida_str = extraer_monto_desde_tokens(nums_sig)
                        salida = normalizar_valor(salida_str)
                        print("[OK] SALIDA EN LÍNEA SIGUIENTE:", salida_raw, "->", salida)
                        break

        # ============================
        # 5. Fallback regex general
        # ============================
        if entrada is None:
            m = re.search(r"ENTRADAS?\s*[^\d]*(\d[\d\.\,]*)", texto_plano, re.IGNORECASE)
            if m:
                entrada_raw = m.group(1)
                entrada = normalizar_valor(entrada_raw)

        if salida is None:
            m = re.search(r"SALIDAS?\s*[^\d]*(\d[\d\.\,]*)", texto_plano, re.IGNORECASE)
            if m:
                salida_raw = m.group(1)
                salida = normalizar_valor(salida_raw)

        # ============================
        # 6. Validación final
        # ============================
        if entrada is None or salida is None:
            return JsonResponse({
                "success": False,
                "error": "No se encontraron ENTRADAS / SALIDAS",
                "debug": texto_plano
            }, status=400)

        total = entrada - salida

        return JsonResponse({
            "success": True,
            "entrada": entrada,
            "salida": salida,
            "total": total,
            "entrada_raw": entrada_raw,
            "salida_raw": salida_raw,
            "mensaje": "OCR procesado correctamente"
        })

    except Exception as e:
        print("Error OCR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)



# ============================
# HELPERS OCR
# ============================

def agrupar_lineas(ocr_data):
    filas = {}
    n = len(ocr_data["text"])

    for i in range(n):
        txt = ocr_data["text"][i]
        if not txt or not txt.strip():
            continue

        key = (ocr_data["block_num"][i], ocr_data["par_num"][i], ocr_data["line_num"][i])
        top = ocr_data["top"][i]

        if key not in filas:
            filas[key] = {"texto": "", "numeros": [], "top": top}
        else:
            filas[key]["top"] = min(filas[key]["top"], top)

        filas[key]["texto"] += " " + txt

        if any(c.isdigit() for c in txt):
            filas[key]["numeros"].append(txt)

    return sorted(filas.values(), key=lambda f: f["top"])


def normalizar_texto_label(s):
    if not s:
        return ""
    s = s.upper()
    reemplazos = {
        "0": "O", "1": "I", "5": "S", "4": "A", "|": "I",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"
    }
    for k, v in reemplazos.items():
        s = s.replace(k, v)
    return s


def es_linea_entrada(txt):
    patrones = ["ENTRADA", "ENTRADAS", "NTRADA", "TRADA", "ENTRAD"]
    return any(p in txt for p in patrones)


def es_linea_salida(txt):
    patrones = [
        "SALIDA", "SALIDAS",
        "SLIDA", "SALID", "SALD", "SALDA",
        "SALAS", "SADAS", "SAD", "SAAS",
        "ALIDAS", "IDAS", " DAS "
    ]
    return any(p in txt for p in patrones)


def extraer_monto_desde_tokens(tokens):
    """
    A partir de los tokens numéricos de una fila, intenta reconstruir el monto
    completo (por ejemplo '$402.' + '100' -> '402100').
    Devuelve (raw_para_debug, cadena_numerica_para_normalizar).
    """
    raw = " ".join(tokens)
    solo_digitos = re.sub(r"[^\d]", "", raw)

    # Si al juntar todo tenemos un número grande, se recorta a 6 dígitos
    # (197000, 402100, 713540, 918640 = 6 dígitos)
    if len(solo_digitos) >= 5:
        if len(solo_digitos) > 6:
            solo_digitos = solo_digitos[:6]
        return raw, solo_digitos

    # Si es muy corto, usamos el token más "largo" como fallback
    candidato = seleccionar_numero_correcto(tokens)
    return candidato, candidato


def seleccionar_numero_correcto(nums):
    nums_limpios = [(n, len(re.sub(r"[^\d]", "", n))) for n in nums]
    nums_limpios.sort(key=lambda x: x[1], reverse=True)
    return nums_limpios[0][0]


def normalizar_valor(raw):
    if raw is None:
        return None
    s = re.sub(r"[^\d]", "", str(raw))
    if not s:
        return None
    # Corregir caso '$' leído como '5' al inicio
    if s.startswith("5") and len(s) >= 6:
        s = s[1:]
    return int(s)



@login_required
def ia_capturar_dummy(request):
    """
    Endpoint dummy para simular captura de IA/OCR
    
    INTEGRACIÓN FUTURA:
    - Aquí se debe integrar el servicio de OCR/IA
    - Capturar imagen de la pantalla de la máquina
    - Procesar con OCR para extraer entrada, salida, total
    - Devolver los valores extraídos
    
    Por ahora devuelve valores de ejemplo para testing
    """
    # Simular valores capturados por IA
    datos_dummy = {
        'success': True,
        'entrada': 150000,
        'salida': 30000,
        'total': 120000,
        'mensaje': 'Datos capturados exitosamente (DEMO)'
    }
    
    return JsonResponse(datos_dummy)


# ============================================
# TABLAS Y REPORTES
# ============================================

@login_required
def tablas_view(request):
    """
    Vista de tablas de lecturas con filtros
    """
    lecturas = LecturaMaquina.objects.all()
    
    # Filtros base para usuario normal
    if request.user.role == 'usuario':
        # Mostrar lecturas del turno abierto o del día si no hay turno abierto
        turno_abierto = Turno.objects.filter(
            usuario=request.user,
            estado='Abierto'
        ).first()
        
        if turno_abierto:
            lecturas = lecturas.filter(turno=turno_abierto)
        else:
            hoy = timezone.now().date()
            lecturas = lecturas.filter(
                usuario=request.user,
                fecha_registro__date=hoy
            )
    
    # Filtros para admin (más completos)
    if request.user.role == 'admin':
        sucursal_id = request.GET.get('sucursal')
        zona_id = request.GET.get('zona')
        maquina_id = request.GET.get('maquina')
        usuario_id = request.GET.get('usuario')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        if sucursal_id:
            lecturas = lecturas.filter(sucursal_id=sucursal_id)
        if zona_id:
            lecturas = lecturas.filter(zona_id=zona_id)
        if maquina_id:
            lecturas = lecturas.filter(maquina_id=maquina_id)
        if usuario_id:
            lecturas = lecturas.filter(usuario_id=usuario_id)
        if fecha_desde:
            lecturas = lecturas.filter(fecha_registro__date__gte=fecha_desde)
        if fecha_hasta:
            lecturas = lecturas.filter(fecha_registro__date__lte=fecha_hasta)
    
    # Filtro de fecha para usuario
    fecha = request.GET.get('fecha')
    if fecha and request.user.role == 'usuario':
        lecturas = lecturas.filter(fecha_registro__date=fecha)
    
    lecturas = lecturas.order_by('-fecha_registro')[:200]  # Limitar a 200 registros
    
    # Calcular totales
    total_entrada = lecturas.aggregate(Sum('entrada'))['entrada__sum'] or 0
    total_salida = lecturas.aggregate(Sum('salida'))['salida__sum'] or 0
    total_total = lecturas.aggregate(Sum('total'))['total__sum'] or 0
    
    context = {
        'lecturas': lecturas,
        'total_entrada': total_entrada,
        'total_salida': total_salida,
        'total_total': total_total,
        'sucursales': Sucursal.objects.all(),
        'zonas': Zona.objects.all(),
        'maquinas': Maquina.objects.all(),
        'usuarios': Usuario.objects.filter(role='usuario'),
    }
    
    return render(request, 'tablas.html', context)


@login_required
def export_excel(request):
    """
    Exportar lecturas a Excel
    """
    # Obtener las mismas lecturas que en tablas_view con filtros
    lecturas = LecturaMaquina.objects.all()
    
    if request.user.role == 'usuario':
        turno_abierto = Turno.objects.filter(
            usuario=request.user,
            estado='Abierto'
        ).first()
        
        if turno_abierto:
            lecturas = lecturas.filter(turno=turno_abierto)
        else:
            hoy = timezone.now().date()
            lecturas = lecturas.filter(
                usuario=request.user,
                fecha_registro__date=hoy
            )
    
    if request.user.role == 'admin':
        sucursal_id = request.GET.get('sucursal')
        zona_id = request.GET.get('zona')
        maquina_id = request.GET.get('maquina')
        usuario_id = request.GET.get('usuario')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        if sucursal_id:
            lecturas = lecturas.filter(sucursal_id=sucursal_id)
        if zona_id:
            lecturas = lecturas.filter(zona_id=zona_id)
        if maquina_id:
            lecturas = lecturas.filter(maquina_id=maquina_id)
        if usuario_id:
            lecturas = lecturas.filter(usuario_id=usuario_id)
        if fecha_desde:
            lecturas = lecturas.filter(fecha_registro__date__gte=fecha_desde)
        if fecha_hasta:
            lecturas = lecturas.filter(fecha_registro__date__lte=fecha_hasta)
    
    fecha = request.GET.get('fecha')
    if fecha and request.user.role == 'usuario':
        lecturas = lecturas.filter(fecha_registro__date=fecha)
    
    lecturas = lecturas.order_by('-fecha_registro')
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Lecturas de Máquinas"
    
    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Headers
    headers = [
        'Fecha', 'Sucursal', 'Zona', 'Nº Máquina', 'Juego',
        'Entrada', 'Salida', 'Total', 'Usuario', 'Nota'
    ]
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for row_num, lectura in enumerate(lecturas, 2):
        ws.cell(row=row_num, column=1).value = lectura.fecha_registro.strftime('%d/%m/%Y %H:%M')
        ws.cell(row=row_num, column=2).value = lectura.sucursal.nombre
        ws.cell(row=row_num, column=3).value = lectura.zona.nombre
        ws.cell(row=row_num, column=4).value = lectura.numero_maquina
        ws.cell(row=row_num, column=5).value = lectura.nombre_juego
        ws.cell(row=row_num, column=6).value = lectura.entrada
        ws.cell(row=row_num, column=7).value = lectura.salida
        ws.cell(row=row_num, column=8).value = lectura.total
        ws.cell(row=row_num, column=9).value = lectura.usuario.nombre
        ws.cell(row=row_num, column=10).value = lectura.nota
    
    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=lecturas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    wb.save(response)
    return response


# ============================================
# CRUD SUCURSALES (solo admin)
# ============================================

@login_required
@user_passes_test(is_admin)
def sucursales_list(request):
    query = request.GET.get('q')

    sucursales = Sucursal.objects.filter(is_active=True)

    if query:
        sucursales = sucursales.filter(nombre__icontains=query)

    return render(request, 'sucursales/list.html', {
        'sucursales': sucursales,
        'query': query
    })


@login_required
@user_passes_test(is_admin)
def sucursal_create(request):
    if request.method == 'POST':
        form = SucursalForm(request.POST)
        if form.is_valid():
            form.save()

            if 'guardar_otro' in request.POST:
                messages.success(request, 'Sucursal guardada. Puede agregar otra.')
                return redirect('control:sucursal_create')
            else:
                messages.success(request, 'Sucursal creada exitosamente.')
                return redirect('control:sucursales_list')
    else:
        form = SucursalForm()

    return render(request, 'sucursales/form.html', {
        'form': form,
        'title': 'Crear Sucursal'
    })



@login_required
@user_passes_test(is_admin)
def sucursal_edit(request, pk):
    sucursal = get_object_or_404(Sucursal, pk=pk)
    if request.method == 'POST':
        form = SucursalForm(request.POST, instance=sucursal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sucursal actualizada exitosamente.')
            return redirect('control:sucursales_list')
    else:
        form = SucursalForm(instance=sucursal)
    return render(request, 'sucursales/form.html', {'form': form, 'title': 'Editar Sucursal'})


@login_required
@user_passes_test(is_admin)
def sucursal_delete(request, pk):
    sucursal = get_object_or_404(Sucursal, pk=pk)
    if request.method == 'POST':
        sucursal.delete()
        messages.success(request, 'Sucursal eliminada exitosamente.')
        return redirect('control:sucursales_list')
    return render(request, 'sucursales/delete.html', {'object': sucursal})


# ============================================
# CRUD ZONAS (solo admin)
# ============================================

@login_required
@user_passes_test(is_admin)
def zonas_list(request):
    sucursal_id = request.GET.get('sucursal')

    zonas = Zona.objects.filter(is_active=True, sucursal__is_active=True)

    if sucursal_id:
        zonas = zonas.filter(sucursal_id=sucursal_id)

    return render(request, 'zonas/list.html', {
        'zonas': zonas,
        'sucursales': Sucursal.objects.filter(is_active=True),
        'sucursal_id': sucursal_id
    })


@login_required
@user_passes_test(is_admin)
def zona_create(request):
    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            form.save()

            if 'guardar_otro' in request.POST:
                messages.success(request, 'Zona guardada. Puede agregar otra.')
                return redirect('control:zona_create')
            else:
                messages.success(request, 'Zona creada exitosamente.')
                return redirect('control:zonas_list')
    else:
        form = ZonaForm()

    return render(request, 'zonas/form.html', {
        'form': form,
        'title': 'Crear Zona'
    })



@login_required
@user_passes_test(is_admin)
def zona_edit(request, pk):
    zona = get_object_or_404(Zona, pk=pk)
    if request.method == 'POST':
        form = ZonaForm(request.POST, instance=zona)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zona actualizada exitosamente.')
            return redirect('control:zonas_list')
    else:
        form = ZonaForm(instance=zona)
    return render(request, 'zonas/form.html', {'form': form, 'title': 'Editar Zona'})


@login_required
@user_passes_test(is_admin)
def zona_delete(request, pk):
    zona = get_object_or_404(Zona, pk=pk)

    if request.method == 'POST':
        zona.is_active = False
        zona.save()

        # Desactivar máquinas asociadas
        Maquina.objects.filter(zona=zona).update(is_active=False)

        messages.success(
            request,
            'Zona desactivada correctamente. El histórico fue conservado.'
        )
        return redirect('control:zonas_list')

    return render(request, 'zonas/delete.html', {
        'object': zona
    })



# ============================================
# CRUD MÁQUINAS (solo admin)
# ============================================

@login_required
@user_passes_test(is_admin)
def maquinas_list(request):
    sucursal_id = request.GET.get('sucursal')
    zona_id = request.GET.get('zona')

    maquinas = Maquina.objects.filter(
        sucursal__is_active=True,
        zona__is_active=True
    )

    if sucursal_id:
        maquinas = maquinas.filter(sucursal_id=sucursal_id)

    if zona_id:
        maquinas = maquinas.filter(zona_id=zona_id)

    return render(request, 'maquinas/list.html', {
        'maquinas': maquinas,
        'sucursales': Sucursal.objects.filter(is_active=True),
        'zonas': Zona.objects.filter(is_active=True),
        'sucursal_id': sucursal_id,
        'zona_id': zona_id
    })



@login_required
@user_passes_test(is_admin)
def maquina_create(request):
    if request.method == 'POST':
        form = MaquinaForm(request.POST)
        if form.is_valid():
            form.save()

            if 'guardar_otro' in request.POST:
                messages.success(request, 'Máquina guardada. Puede agregar otra.')
                return redirect('control:maquina_create')
            else:
                messages.success(request, 'Máquina creada exitosamente.')
                return redirect('control:maquinas_list')
    else:
        form = MaquinaForm()

    return render(request, 'maquinas/form.html', {
        'form': form,
        'title': 'Crear Máquina'
    })


@login_required
@user_passes_test(is_admin)
def maquina_edit(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk)
    if request.method == 'POST':
        form = MaquinaForm(request.POST, instance=maquina)
        if form.is_valid():
            form.save()
            messages.success(request, 'Máquina actualizada exitosamente.')
            return redirect('control:maquinas_list')
    else:
        form = MaquinaForm(instance=maquina)
    return render(request, 'maquinas/form.html', {'form': form, 'title': 'Editar Máquina'})


@login_required
@user_passes_test(is_admin)
def maquina_delete(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk)
    if request.method == 'POST':
        maquina.delete()
        messages.success(request, 'Máquina eliminada exitosamente.')
        return redirect('control:maquinas_list')
    return render(request, 'maquinas/delete.html', {'object': maquina})

@login_required
@user_passes_test(lambda u: u.is_authenticated and getattr(u, "role", "") == "admin")
def maquina_update_estado(request, pk):
    if request.method != "POST":
        return redirect("control:maquinas_list")

    maquina = get_object_or_404(Maquina, pk=pk)

    nuevo_estado = request.POST.get("estado")
    estados_validos = [e[0] for e in Maquina.ESTADO_CHOICES]

    if nuevo_estado not in estados_validos:
        messages.error(request, "Estado inválido.")
        return redirect("control:maquinas_list")

    maquina.estado = nuevo_estado
    maquina.save(update_fields=["estado"])

    messages.success(request, f"Estado actualizado a: {nuevo_estado}")
    return redirect("control:maquinas_list")
# ============================================
# CRUD USUARIOS (solo admin)
# ============================================

@login_required
@user_passes_test(is_admin)
def usuarios_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/list.html', {'usuarios': usuarios})


@login_required
@user_passes_test(is_admin)
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('control:usuarios_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form.html', {'form': form, 'title': 'Crear Usuario'})


@login_required
@user_passes_test(is_admin)
def usuario_edit(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            usuario.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('control:usuarios_list')
    else:
        form = UsuarioEditForm(instance=usuario)
    return render(request, 'usuarios/form.html', {'form': form, 'title': 'Editar Usuario'})


@login_required
@user_passes_test(is_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('control:usuarios_list')
    return render(request, 'usuarios/delete.html', {'object': usuario})

def normalizar_valor(valor_raw: str) -> int:
    """
    Recibe algo como '197.000', '$402,100', '713.540' y devuelve 197000, 402100, 713540.
    """
    if not valor_raw:
        return 0
    solo_digitos = re.sub(r'[^\d]', '', valor_raw)
    return int(solo_digitos) if solo_digitos else 0

# =============================================
# HELPERS OCR DEFINITIVOS
# =============================================

def agrupar_lineas(ocr_data):
    filas = {}
    n = len(ocr_data["text"])

    for i in range(n):
        txt = ocr_data["text"][i]
        if not txt or txt.strip() == "":
            continue

        key = (ocr_data["block_num"][i], ocr_data["par_num"][i], ocr_data["line_num"][i])
        top = ocr_data["top"][i]

        if key not in filas:
            filas[key] = {"texto": "", "numeros": [], "top": top}
        else:
            filas[key]["top"] = min(filas[key]["top"], top)

        filas[key]["texto"] += " " + txt

        if any(c.isdigit() for c in txt):
            filas[key]["numeros"].append(txt)

    return sorted(filas.values(), key=lambda f: f["top"])


def normalizar_texto_label(s):
    if not s:
        return ""
    s = s.upper()
    reemplazos = {
        "0": "O", "1": "I", "5": "S", "4": "A", "|": "I", "/": "",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"
    }
    for k, v in reemplazos.items():
        s = s.replace(k, v)
    return s


def es_linea_entrada(txt):
    patrones = ["ENTRADA", "NTRADA", "TRADA", "ENTRAD", "ENTRADAS"]
    return any(p in txt for p in patrones)


def es_linea_salida(txt):
    patrones = ["SALIDA", "SALIDAS", "SLIDA", "ALIDA", "SALID"]
    return any(p in txt for p in patrones)


def seleccionar_numero_correcto(nums):
    """
    Escoge el valor más largo (normalmente el de dinero).
    """
    nums_limpios = [(n, len(re.sub(r"[^\d]", "", n))) for n in nums]
    nums_limpios.sort(key=lambda x: x[1], reverse=True)
    return nums_limpios[0][0]


def normalizar_valor(raw):
    if not raw:
        return None
    s = re.sub(r"[^\d]", "", raw)
    if s.startswith("5") and len(s) >= 6:  # el $ mal leído como 5
        s = s[1:]
    return int(s) if s else None
