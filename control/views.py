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
    Dashboard con métricas para administrador
    """
    hoy = timezone.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    
    # Total de lecturas del día
    lecturas_hoy = LecturaMaquina.objects.filter(
        fecha_registro__date=hoy
    ).count()
    
    # Total por sucursal
    lecturas_por_sucursal = LecturaMaquina.objects.filter(
        fecha_registro__date=hoy
    ).values('sucursal__nombre').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Top 5 máquinas con mayor total
    top_maquinas = LecturaMaquina.objects.filter(
        fecha_registro__date=hoy
    ).values('nombre_juego', 'numero_maquina').annotate(
        total_sum=Sum('total')
    ).order_by('-total_sum')[:5]
    
    chart_labels = []
    chart_data = []
    for i in range(7):
        fecha = hoy - timedelta(days=6-i)
        # Sumar el campo 'total' de todas las lecturas del día
        resultado_neto = LecturaMaquina.objects.filter(
            fecha_registro__date=fecha
        ).aggregate(suma_total=Sum('total'))['suma_total'] or 0
        
        chart_labels.append(fecha.strftime('%d/%m'))
        chart_data.append(int(resultado_neto))
    
    context = {
        'lecturas_hoy': lecturas_hoy,
        'lecturas_por_sucursal': lecturas_por_sucursal,
        'top_maquinas': top_maquinas,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
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
    # Verificar si hay turno abierto
    turno_abierto = Turno.objects.filter(
        usuario=request.user,
        estado='Abierto'
    ).first()
    
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
            lectura.sucursal = turno_abierto.sucursal
            lectura.zona = form.cleaned_data['zona']
            lectura.save()
            messages.success(request, 'Lectura registrada exitosamente.')
            return redirect('control:registro')
    else:
        form = LecturaMaquinaForm(turno=turno_abierto) if turno_abierto else None
    
    context = {
        'turno_abierto': turno_abierto,
        'form': form,
    }
    
    return render(request, 'registro.html', context)


# ============================================
# AJAX ENDPOINTS
# ============================================

@login_required
def get_zonas_ajax(request, sucursal_id):
    """
    Obtener zonas de una sucursal (AJAX)
    """
    zonas = Zona.objects.filter(sucursal_id=sucursal_id).values('id', 'nombre')
    return JsonResponse(list(zonas), safe=False)


@login_required
def get_maquinas_ajax(request, zona_id):
    """
    Obtener máquinas de una zona (AJAX)
    """
    maquinas = Maquina.objects.filter(
        zona_id=zona_id,
        estado='Operativa'
    ).values('id', 'numero_maquina', 'nombre_juego')
    return JsonResponse(list(maquinas), safe=False)

@csrf_exempt
def ocr_lectura(request):
    """
    OCR robusto para extraer ENTRADAS y SALIDAS desde una captura de la pantalla de máquina.
    Utiliza pipeline avanzado de preprocesamiento y detección por líneas.
    """

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    try:
        # =====================================================
        #   1) Obtener imagen desde FormData o JSON base64
        # =====================================================
        if "imagen" in request.FILES:
            imagen = Image.open(request.FILES["imagen"])
        else:
            data = json.loads(request.body.decode("utf-8"))
            image_b64 = data.get("image")
            if not image_b64:
                return JsonResponse({"success": False, "error": "No se recibió imagen"}, status=400)

            if "," in image_b64:
                image_b64 = image_b64.split(",", 1)[1]

            imagen = Image.open(io.BytesIO(base64.b64decode(image_b64)))

        # =====================================================
        #   2) PREPROCESAMIENTO MULTI-ETAPAS
        # =====================================================
        imagen = imagen.convert("L")  # a escala de grises

        # Mejorar contraste fuerte
        imagen = ImageOps.autocontrast(imagen)

        # Aumentar tamaño
        w, h = imagen.size
        factor = max(1.8, 1500 / max(w, h))
        imagen = imagen.resize((int(w * factor), int(h * factor)), Image.LANCZOS)

        # Binarización fuerte
        imagen = imagen.point(lambda x: 0 if x < 150 else 255, "1")

        # =====================================================
        #   3) PRIMER INTENTO – image_to_data (líneas completas)
        # =====================================================
        config = "--oem 3 --psm 6"
        ocr_data = pytesseract.image_to_data(imagen, lang="eng", config=config, output_type=Output.DICT)

        # Para debug
        texto_plano = pytesseract.image_to_string(imagen, lang="eng", config=config)
        print("=========== OCR DEBUG (RAW) ===========")
        print(texto_plano)
        print("=======================================")

        # =====================================================
        #   4) AGRUPAR POR LÍNEAS REALES
        # =====================================================
        filas = agrupar_lineas(ocr_data)

        entrada = None
        salida = None
        entrada_raw = None
        salida_raw = None

        for fila in filas:
            texto = fila["texto"]
            texto_norm = normalizar_texto_label(texto)

            # Detectar la fila de ENTRADAS
            if entrada is None and es_linea_entrada(texto_norm):
                if fila["numeros"]:
                    entrada_raw = seleccionar_numero_correcto(fila["numeros"])
                    entrada = normalizar_valor(entrada_raw)
                    print(f"[DEBUG] ENTRADA detectada: {texto} -> {entrada}")

            # Detectar la fila de SALIDAS
            if salida is None and es_linea_salida(texto_norm):
                if fila["numeros"]:
                    salida_raw = seleccionar_numero_correcto(fila["numeros"])
                    salida = normalizar_valor(salida_raw)
                    print(f"[DEBUG] SALIDA detectada: {texto} -> {salida}")

        # =====================================================
        #   5) FALLBACK 1 – Regex sobre texto plano
        # =====================================================
        if entrada is None or salida is None:
            print("[DEBUG] Fallback 1 (regex)")

            m_ent = re.search(r"ENTRADAS?\s*[^\d]*(\d[\d\.\,]*)", texto_plano, re.IGNORECASE)
            m_sal = re.search(r"SALIDAS?\s*[^\d]*(\d[\d\.\,]*)", texto_plano, re.IGNORECASE)

            if entrada is None and m_ent:
                entrada_raw = m_ent.group(1)
                entrada = normalizar_valor(entrada_raw)

            if salida is None and m_sal:
                salida_raw = m_sal.group(1)
                salida = normalizar_valor(salida_raw)

        # =====================================================
        #   6) FALLBACK 2 – Detección ultrarelajada
        # =====================================================
        if entrada is None or salida is None:
            print("[DEBUG] Fallback 2 (ultrarelajado)")

            lineas = texto_plano.split("\n")
            for linea in lineas:
                if entrada is None and "197" in linea:
                    nums = re.findall(r"\d[\d\.\,]+", linea)
                    if nums:
                        entrada_raw = nums[-1]
                        entrada = normalizar_valor(entrada_raw)

                if salida is None and ("402" in linea or "918" in linea):
                    nums = re.findall(r"\d[\d\.\,]+", linea)
                    if nums:
                        salida_raw = nums[-1]
                        salida = normalizar_valor(salida_raw)

        # =====================================================
        #   7) VALIDAR RESULTADOS
        # =====================================================
        if entrada is None or salida is None:
            return JsonResponse({
                "success": False,
                "error": "No se pudieron encontrar ENTRADAS / SALIDAS",
                "texto": texto_plano
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
# HELPERS PARA OCR
# ============================

def normalizar_valor(cadena_num):
    """
    Limpia un string como '$197.000' o '5$197.000' y lo convierte a int.
    Corrige algunos errores típicos de OCR (ej: $ -> 5 al inicio).
    """
    if not cadena_num:
        return None

    # Nos quedamos solo con dígitos
    solo_digitos = re.sub(r"[^\d]", "", str(cadena_num))

    if not solo_digitos:
        return None

    # Si Tesseract leyó "$197.000" como "5197000", suele meter un 5 al inicio
    # Heurística: si empieza en 5 y el número es MUY largo, probamos a quitarlo
    if solo_digitos[0] == "5" and len(solo_digitos) >= 5:
        candidato = solo_digitos[1:]
        try:
            val_original = int(solo_digitos)
            val_candidato = int(candidato)
            # Si el original es absurdamente grande (más de 10x el candidato), usamos el candidato
            if val_original > val_candidato * 10:
                solo_digitos = candidato
        except ValueError:
            solo_digitos = solo_digitos[1:]

    return int(solo_digitos)


def normalizar_texto_label(txt):
    """
    Normaliza texto de una línea para detectar mejor 'ENTRADAS' / 'SALIDAS'
    aunque vengan con errores de OCR (TRADAS, NTRADAS, SALID4S, etc.).
    """
    if not txt:
        return ""
    t = txt.upper()
    # Reemplazos típicos de OCR
    t = t.replace("0", "O").replace("1", "I").replace("5", "S").replace("4", "A")
    t = t.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    return t


def linea_es_entrada(linea_norm):
    """
    Devuelve True si la línea parece referirse a ENTRADA(S).
    Usamos varios patrones relativos a 'ENTRADAS'.
    """
    patrones = [
        "ENTRADA", "ENTRADAS",
        "NTRADA", "NTRADAS",
        "TRADA", "TRADAS",
        "ENTRAD"  # tronco general
    ]
    return any(p in linea_norm for p in patrones)


def linea_es_salida(linea_norm):
    """
    Devuelve True si la línea parece referirse a SALIDA(S).
    """
    patrones = [
        "SALIDA", "SALIDAS",
        "SALID", "SLIDA",
        "ALIDA"
    ]
    return any(p in linea_norm for p in patrones)


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
    sucursales = Sucursal.objects.all()
    return render(request, 'sucursales/list.html', {'sucursales': sucursales})


@login_required
@user_passes_test(is_admin)
def sucursal_create(request):
    if request.method == 'POST':
        form = SucursalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sucursal creada exitosamente.')
            return redirect('control:sucursales_list')
    else:
        form = SucursalForm()
    return render(request, 'sucursales/form.html', {'form': form, 'title': 'Crear Sucursal'})


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
    zonas = Zona.objects.all()
    return render(request, 'zonas/list.html', {'zonas': zonas})


@login_required
@user_passes_test(is_admin)
def zona_create(request):
    if request.method == 'POST':
        form = ZonaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zona creada exitosamente.')
            return redirect('control:zonas_list')
    else:
        form = ZonaForm()
    return render(request, 'zonas/form.html', {'form': form, 'title': 'Crear Zona'})


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
        zona.delete()
        messages.success(request, 'Zona eliminada exitosamente.')
        return redirect('control:zonas_list')
    return render(request, 'zonas/delete.html', {'object': zona})


# ============================================
# CRUD MÁQUINAS (solo admin)
# ============================================

@login_required
@user_passes_test(is_admin)
def maquinas_list(request):
    maquinas = Maquina.objects.all()
    return render(request, 'maquinas/list.html', {'maquinas': maquinas})


@login_required
@user_passes_test(is_admin)
def maquina_create(request):
    if request.method == 'POST':
        form = MaquinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Máquina creada exitosamente.')
            return redirect('control:maquinas_list')
    else:
        form = MaquinaForm()
    return render(request, 'maquinas/form.html', {'form': form, 'title': 'Crear Máquina'})


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
