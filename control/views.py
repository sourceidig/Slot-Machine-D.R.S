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
import base64

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .models import Usuario, Sucursal, Zona, Maquina, Turno, LecturaMaquina
from .forms import (
    TurnoForm, LecturaMaquinaForm, SucursalForm, ZonaForm, 
    MaquinaForm, UsuarioForm, UsuarioEditForm
)

import pytesseract
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
    Vista que recibe una imagen y extrae Entrada y Salida usando Tesseract OCR.
    Soporta:
    - request.FILES['imagen']
    - JSON {"image": "data:image/png;base64,..."}
    """
    import base64
    import re
    from PIL import ImageOps

    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'error': 'Método no permitido'},
            status=405
        )

    try:
        imagen = None

        # 1) Imagen enviada como archivo (FormData)
        if 'imagen' in request.FILES:
            imagen_file = request.FILES['imagen']
            imagen = Image.open(imagen_file)

        # 2) Imagen enviada como base64 (desde el canvas)
        else:
            data = json.loads(request.body.decode('utf-8'))
            image_b64 = data.get('image')

            if not image_b64:
                return JsonResponse(
                    {'success': False, 'error': 'No se recibió imagen'},
                    status=400
                )

            # viene como 'data:image/png;base64,AAAA...'
            if ',' in image_b64:
                image_b64 = image_b64.split(",", 1)[1]

            image_bytes = base64.b64decode(image_b64)
            imagen = Image.open(io.BytesIO(image_bytes))

        # ============================
        # 🔧 PREPROCESADO PARA OCR
        # ============================
        # Escala de grises
        imagen = imagen.convert("L")

        # Auto-contraste
        imagen = ImageOps.autocontrast(imagen)

        # Aumentar resolución (doble tamaño)
        w, h = imagen.size
        imagen = imagen.resize((w * 2, h * 2), Image.LANCZOS)

        # Binarización simple
        imagen = imagen.point(lambda x: 255 if x > 150 else 0, mode="1")

        # ============================
        # 🧠 EJECUTAR TESSERACT
        # ============================
        texto_extraido = pytesseract.image_to_string(
            imagen,
            lang="eng",         # usamos eng porque suele ser más estable que spa
            config="--oem 3 --psm 6"
        )

        print("=========== TEXTO OCR ===========")
        print(texto_extraido)
        print("=================================")

        # ============================
        # 🔍 BUSCAR ENTRADAS / SALIDAS
        # ============================
        def normalizar_num(n_str: str) -> int:
            """Quita todo lo que no sea dígito y lo convierte a int."""
            solo_digitos = re.sub(r"[^\d]", "", n_str)
            return int(solo_digitos) if solo_digitos else 0

        entrada = None
        salida = None

        # 1) Intento con regex usando las palabras ENTRADAS / SALIDAS
        entrada_match = re.search(
            r"ENTRADAS?\s*[^\d]*([\d\.\,]+)",
            texto_extraido,
            re.IGNORECASE
        )
        salida_match = re.search(
            r"SALIDAS?\s*[^\d]*([\d\.\,]+)",
            texto_extraido,
            re.IGNORECASE
        )

        if entrada_match:
            entrada = normalizar_num(entrada_match.group(1))

        if salida_match:
            salida = normalizar_num(salida_match.group(1))

        # ============================
        # 🚨 FALLBACK: SOLO NÚMEROS GRANDES
        # ============================
        if entrada is None or salida is None:
            # Buscar todos los "números tipo monto"
            # (3 o más dígitos, con o sin puntos)
            crudos = re.findall(r"[\d][\d\.\,]{2,}", texto_extraido)

            candidatos = []
            for n in crudos:
                val = normalizar_num(n)
                # Filtramos números chicos que suelen ser ruido
                if val >= 1000:
                    candidatos.append(val)

            # Eliminamos duplicados manteniendo el orden
            vistos = set()
            candidatos_unicos = []
            for v in candidatos:
                if v not in vistos:
                    vistos.add(v)
                    candidatos_unicos.append(v)

            print("CANDIDATOS NUMÉRICOS:", candidatos_unicos)

            if len(candidatos_unicos) >= 2:
                # Ordenamos de menor a mayor
                ordenados = sorted(candidatos_unicos)
                # Regla heurística:
                # - entrada = número más pequeño
                # - salida  = siguiente número
                if entrada is None:
                    entrada = ordenados[0]
                if salida is None:
                    salida = ordenados[1]

        # ============================
        # ❌ SI IGUAL NO PUDIMOS
        # ============================
        if entrada is None or salida is None:
            return JsonResponse({
                'success': False,
                'error': 'No se pudieron encontrar ENTRADAS / SALIDAS',
                'texto_ocr': texto_extraido
            }, status=400)

        total = entrada - salida

        # ============================
        # ✅ RESPUESTA OK
        # ============================
        return JsonResponse({
            'success': True,
            'mensaje': 'Datos detectados correctamente.',
            'entrada': entrada,
            'salida': salida,
            'total': total,
            'texto_ocr': texto_extraido
        })

    except Exception as e:
        print("Error OCR:", e)
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar la imagen: {e}'
        }, status=500)



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
