from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta, time
from decimal import Decimal

from control.utils import calcular_numerales_caja
from .models import CierreTurno, CierreTurnoZona, CierreTurnoMovimiento, CierreTurnoPago, CierreTurnoDenominacion, CicloRecaudacion
from .forms import CierreTurnoForm, CierreTurnoZonaFormSet, CierreTurnoMovimientoFormSet, CierreTurnoPagoFormSet, CierreTurnoDenFormSet
from .models import CuadraturaDetalle
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Q
import calendar
from datetime import date
import json
import re
import base64
import io

from PIL import Image, ImageOps
import pytesseract
from pytesseract import Output

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .models import (
    Usuario, Sucursal, Zona, Maquina, Turno, LecturaMaquina,
    CuadraturaCajaDiaria, EncuadreCajaAdmin
)

from .forms import (
    TurnoForm, LecturaMaquinaForm, SucursalForm, ZonaForm,
    MaquinaForm, UsuarioForm, UsuarioEditForm,
    CuadraturaCajaDiariaForm, EncuadreCajaAdminForm
)

#===========================
#Recaudación/Dia 0
#===========================
@login_required
@transaction.atomic
def iniciar_dia_0(request):
    if request.method != "POST":
        return redirect("control:recaudacion")

    sucursal_id = request.POST.get("sucursal_id")
    if not sucursal_id:
        messages.error(request, "Debes seleccionar un local.")
        return redirect("control:recaudacion")

    sucursal = get_object_or_404(Sucursal, id=sucursal_id)

    # 1) máquinas del local
    maquinas = Maquina.objects.filter(sucursal=sucursal, is_active=True)

    actualizadas = 0
    sin_historial = 0

    for m in maquinas:
        # 2) buscar el ÚLTIMO registro de esa máquina
        # Ajusta el modelo usado según tu sistema real:
        ultimo = LecturaMaquina.objects.filter(maquina=m).order_by("-fecha_registro", "-id").first()

        if ultimo:
            m.contador_inicial_entrada = ultimo.entrada
            m.contador_inicial_salida = ultimo.salida
            m.save(update_fields=["contador_inicial_entrada", "contador_inicial_salida"])
            actualizadas += 1
        else:
            sin_historial += 1

    # 3) guardar “marca” de ciclo (día 0) por local
    CicloRecaudacion.objects.update_or_create(
        sucursal=sucursal,
        defaults={"inicio_ciclo": timezone.localdate()},
    )

    messages.success(
        request,
        f"Día 0 iniciado para '{sucursal.nombre}'. Máquinas actualizadas: {actualizadas}. Sin historial: {sin_historial}."
    )
    return redirect("control:recaudacion")


@login_required
def recaudacion_view(request):
    sucursales = Sucursal.objects.filter(is_active=True).order_by("nombre")
    hoy = timezone.localdate()
    return render(request, "recaudacion/recaudacion.html", {"sucursales": sucursales, "hoy": hoy})





# ==========================
# ROLES
# ==========================

def is_admin(user):
    return user.is_authenticated and getattr(user, "role", "") == "admin"

def is_usuario(user):
    return user.is_authenticated and getattr(user, "role", "") == "usuario"


# ==========================
# AUTH
# ==========================

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("control:dashboard")
        return redirect("control:turno")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == "admin":
                return redirect("control:dashboard")
            return redirect("control:turno")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("control:login")


# Ruta a Tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@login_required
def ajax_cuadratura_mensual_data(request):
    sucursal_id = request.GET.get("sucursal_id")
    mes = request.GET.get("mes")  # "2026-01"

    if not sucursal_id or not mes:
        return JsonResponse({"ok": False, "error": "Faltan parámetros"}, status=400)

    y, m = map(int, mes.split("-"))
    last_day = calendar.monthrange(y, m)[1]
    fecha_desde = date(y, m, 1)
    fecha_hasta = date(y, m, last_day)

    qs = (
        LecturaMaquina.objects
        .filter(
            zona__sucursal_id=sucursal_id,
            fecha_registro__range=(fecha_desde, fecha_hasta),  
        )
        .values("zona_id", "zona__nombre")
        .annotate(
            entrada=Sum("entrada"),
            salida=Sum("salida"),
            total=Sum("total"),
        )
        .order_by("zona__nombre")
    )

    data = []
    for row in qs:
        data.append({
            "zona_id": row["zona_id"],
            "zona_nombre": row["zona__nombre"],
            "entrada": row["entrada"] or 0,
            "salida": row["salida"] or 0,
            "total": row["total"] or 0,
        })

    return JsonResponse({"ok": True, "zonas": data})
# ============================================
# CUADRATURA CAJA DIARIA (ATENDEDORAS)
# ============================================
@login_required
def cuadratura_create(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)

    # Aquí renderizas el TEMPLATE DE "columna roja"
    # OJO: debe existir templates/cuadratura/create_turno.html  (o create.html si así lo llamas)
    return render(request, "cuadratura/create_turno.html", {
        "turno": turno,
        "sucursal": turno.sucursal,
        # "zonas": ...
        # "lecturas": ...
    })

@login_required
def cuadratura_list(request):
    return render(request, "cuadratura/list.html")

@login_required
def cuadratura_detail(request, pk):
    return render(request, "cuadratura/detail.html", {"pk": pk})

def _parse_detalles_from_post(post):
    """
    Lee inputs hidden con formato:
      detalles[0][tipo], detalles[0][nombre], detalles[0][monto]
    Retorna lista: [{"tipo":..., "nombre":..., "monto": int}, ...]
    """
    detalles = []
    idx = 0
    while True:
        k_tipo = f"detalles[{idx}][tipo]"
        k_nom = f"detalles[{idx}][nombre]"
        k_mon = f"detalles[{idx}][monto]"

        if k_tipo not in post and k_nom not in post and k_mon not in post:
            break

        tipo = (post.get(k_tipo) or "").strip().upper()
        nombre = (post.get(k_nom) or "").strip()
        monto_raw = (post.get(k_mon) or "").strip()

        # limpia puntos y basura
        monto_raw = monto_raw.replace(".", "")
        monto_raw = "".join(ch for ch in monto_raw if ch.isdigit() or ch == "-" )

        try:
            monto = int(monto_raw) if monto_raw not in ("", "-") else 0
        except ValueError:
            monto = 0

        # evita filas vacías
        if tipo and (nombre or monto != 0):
            detalles.append({"tipo": tipo, "nombre": nombre, "monto": monto})

        idx += 1

    return detalles


def _sum_tipo(cuadratura, tipo: str) -> int:
    return (
        CuadraturaDetalle.objects
        .filter(cuadratura=cuadratura, tipo=tipo)
        .aggregate(s=Sum("monto"))["s"]
        or 0
    )


def _upsert_cuadratura_diaria(*, sucursal, fecha, defaults):
    """
    Detecta si ya existe una cuadratura para (sucursal, fecha) y la actualiza.
    Si no existe, la crea.
    """
    obj = CuadraturaCajaDiaria.objects.filter(sucursal=sucursal, fecha=fecha).order_by("-creado_el").first()
    if obj:
        for k, v in defaults.items():
            setattr(obj, k, v)
        return obj, False
    return CuadraturaCajaDiaria(sucursal=sucursal, fecha=fecha, **defaults), True


def _recalcular_totales(cuadratura):
    """
    Implementa la lógica del bloc de notas.
    - Día 1 del ciclo: base anterior = caja_inicial del local
    - Día siguiente: base anterior = desglose_efectivo_total del día anterior (última cuadratura dentro del ciclo)
    - base_total = base_anterior + numeral_dia + prestamos
    - restas principales: sorteos, gastos, sueldos, regalos, jugados
    - restas adicionales: redbank, transfer
    - total_calculado = base_total - (restas)
    - descuadre = desglose_total - total_calculado
    - ganancia: (definimos UNA regla, ver abajo)
    - total_efectivo = desglose_total - retiro_diario
    """

    # 1) Numerales (backend es la verdad)
    numeral_dia, numeral_acum = calcular_numerales_caja(cuadratura.sucursal, cuadratura.fecha)
    cuadratura.numeral_dia = numeral_dia
    cuadratura.numeral_acumulado = numeral_acum

    # 2) Caja anterior = última caja registrada antes de esta fecha, SIN filtro de ciclo
    # (el efectivo físico no depende del ciclo de recaudación)
    prev = CuadraturaCajaDiaria.objects.filter(
        sucursal=cuadratura.sucursal,
        fecha__lt=cuadratura.fecha
    ).order_by("-fecha", "-creado_el").first()

    if prev is None:
        base_anterior = (cuadratura.sucursal.caja_inicial or 0)
    else:
        base_anterior = int(prev.total_efectivo or 0)

    # (si quieres guardar caja anterior en el modelo, aquí NO tienes campo.
    #  Solo lo usamos para cálculo)

    # 3) Base total
    prestamos = (cuadratura.prestamos or 0)  # puede ser negativo/positivo
    base_total = (base_anterior or 0) + (cuadratura.numeral_dia or 0) + prestamos

    # 4) Restas
    restas_principales = (
        (cuadratura.sorteos_dia or 0)
        + (cuadratura.gastos_dia or 0)
        + (cuadratura.sueldo_b_dia or 0)
        + (cuadratura.regalos_dia or 0)
        + (cuadratura.jugados_dia or 0)
    )

    restas_adicionales = (cuadratura.redbank_dia or 0) + (cuadratura.transfer_dia or 0)

    total_calculado = (base_total or 0) - (restas_principales or 0) - (restas_adicionales or 0)

    # 5) Desglose real contado
    # desglose_efectivo_total es un @property, se accede directamente
    desglose_total = cuadratura.desglose_efectivo_total or 0

    # 6) Descuadre (lo que conté vs lo que debería dar)
    cuadratura.descuadre_dia = desglose_total - (total_calculado or 0)

    # 7) Prestamos acumulados = prestamos de dias anteriores + dia actual
    prestamos_dia = int(cuadratura.prestamos or 0)
    if prev:
        prestamos_acum = int(prev.prestamos_acum or 0) + prestamos_dia
    else:
        prestamos_acum = prestamos_dia
    cuadratura.prestamos_acum = prestamos_acum

    # 8) Ganancia = desglose efectivo - caja inicial - prestamos acumulados
    caja_inicial_sucursal = int(cuadratura.sucursal.caja_inicial or 0)
    cuadratura.ganancia = desglose_total - caja_inicial_sucursal - prestamos_acum

    # 8) Total efectivo (contado menos retiro)
    cuadratura.total_efectivo = desglose_total - (cuadratura.retiro_diario or 0)

    return cuadratura

@login_required
def cuadratura_diaria_create(request):
    if request.method == "POST":
        form = CuadraturaCajaDiariaForm(request.POST)

        if form.is_valid():
            sucursal = form.cleaned_data.get("sucursal")
            fecha = form.cleaned_data["fecha"]

            if not sucursal:
                messages.error(request, "Debes seleccionar un Local (Sucursal).")
                return render(request, "cuadratura_diaria/create.html", {
                    "form": form,
                    "sucursales": Sucursal.objects.filter(is_active=True).order_by("nombre"),
                    "mes_default": timezone.localdate().strftime("%Y-%m"),
                })

            with transaction.atomic():
                existente = CuadraturaCajaDiaria.objects.filter(
                    sucursal=sucursal,
                    fecha=fecha
                ).first()

                cuadratura = form.save(commit=False)
                if existente:
                    cuadratura.id = existente.id

                cuadratura.usuario = request.user
                cuadratura.sucursal = sucursal

                # Asignar campos ef_* manualmente
                for field in ['ef_20000', 'ef_10000', 'ef_5000', 'ef_2000', 'ef_1000', 'ef_monedas']:
                    setattr(cuadratura, field, form.cleaned_data.get(field, 0))

                # desglose_efectivo_total es un @property, se calcula automáticamente
                # total_efectivo = lo que queda en caja después del retiro diario
                cuadratura.total_efectivo = cuadratura.desglose_efectivo_total - (cuadratura.retiro_diario or 0)

                # timestamps (por tu tema MySQL)
                if not cuadratura.creado_el:
                    cuadratura.creado_el = timezone.now()
                cuadratura.actualizado_el = timezone.now()

                cuadratura.save()

                # Detalles
                detalles_list = _parse_detalles_from_post(request.POST)
                CuadraturaDetalle.objects.filter(cuadratura=cuadratura).delete()

                for d in detalles_list:
                    CuadraturaDetalle.objects.create(
                        cuadratura=cuadratura,
                        tipo=d["tipo"],
                        nombre=d["nombre"],
                        monto=d["monto"],
                        detalle="",
                    )

                # Re-sumar desde BD
                cuadratura.gastos_dia   = _sum_tipo(cuadratura, "GASTOS")
                cuadratura.sueldo_b_dia = _sum_tipo(cuadratura, "SUELDOS")
                cuadratura.regalos_dia  = _sum_tipo(cuadratura, "REGALOS")
                cuadratura.taxi_dia     = _sum_tipo(cuadratura, "TAXI")
                cuadratura.jugados_dia  = _sum_tipo(cuadratura, "JUGADOS")
                cuadratura.otros_1_dia  = _sum_tipo(cuadratura, "OTROS")

                # Recalcular totales ahora que está todo seteado
                _recalcular_totales(cuadratura)

                cuadratura.actualizado_el = timezone.now()
                cuadratura.save()

                # ✅ ACTUALIZAR LA CUADRATURA DEL DÍA SIGUIENTE
                siguiente_dia = cuadratura.fecha + timedelta(days=1)
                cuadratura_siguiente = CuadraturaCajaDiaria.objects.filter(
                    sucursal=cuadratura.sucursal,
                    fecha=siguiente_dia
                ).first()

                if cuadratura_siguiente:
                    cuadratura_siguiente.caja = cuadratura.desglose_efectivo_total
                    cuadratura_siguiente.save()

            messages.success(request, "Cuadratura guardada (creada o actualizada) exitosamente.")
            return redirect("control:cuadratura_diaria_list")

        # Si el formulario no es válido
        sucursal_id = request.POST.get("sucursal")
        fecha_post = request.POST.get("fecha") or timezone.now().date()
        try:
            sucursal_obj = Sucursal.objects.get(pk=sucursal_id)
            prev = CuadraturaCajaDiaria.objects.filter(
                sucursal=sucursal_obj, fecha__lt=fecha_post
            ).order_by("-fecha", "-creado_el").first()
            caja_anterior = int(prev.total_efectivo or 0) if prev else int(sucursal_obj.caja_inicial or 0)
        except (Sucursal.DoesNotExist, ValueError, TypeError):
            sucursal_obj = None
            caja_anterior = 0

        non_field_errors = form.errors.get("__all__", [])
        es_duplicado = any("Sucursal" in str(e) and "Fecha" in str(e) for e in non_field_errors)
        if es_duplicado:
            nombre_sucursal = sucursal_obj.nombre if sucursal_obj else "el local seleccionado"
            messages.error(
                request,
                f"⚠️ Ya existe una Cuadratura Diaria para <strong>{nombre_sucursal}</strong> "
                f"en la fecha <strong>{fecha_post}</strong>. "
                f"No se puede crear un duplicado. Si desea modificarla, búsquela en el listado y edítela desde allí."
            )
        else:
            messages.error(request, "Formulario inválido. Revise los datos enviados.")

    else:
        form = CuadraturaCajaDiariaForm(initial={"fecha": timezone.now().date()})
        sucursales = Sucursal.objects.filter(is_active=True).order_by("nombre")
        primera_sucursal = sucursales.first()

        if primera_sucursal:
            fecha = timezone.now().date()
            prev = CuadraturaCajaDiaria.objects.filter(
                sucursal=primera_sucursal, fecha__lt=fecha
            ).order_by("-fecha", "-creado_el").first()
            caja_anterior = int(prev.total_efectivo or 0) if prev else int(primera_sucursal.caja_inicial or 0)
            caja_inicial = int(primera_sucursal.caja_inicial or 0)
            prestamos_acum_ant = int(prev.prestamos_acum or 0) if prev else 0
        else:
            caja_anterior = 0
            caja_inicial = 0
            prestamos_acum_ant = 0

    return render(request, "cuadratura_diaria/create.html", {
        "form": form,
        "sucursales": Sucursal.objects.filter(is_active=True).order_by("nombre"),
        "mes_default": timezone.localdate().strftime("%Y-%m"),
        "caja_anterior": caja_anterior,
        "caja_inicial": caja_inicial,
        "prestamos_acum_ant": prestamos_acum_ant,
    })
@login_required
def cuadratura_diaria_list(request):
    cuadraturas = CuadraturaCajaDiaria.objects.all().select_related("sucursal", "usuario")

    # -------------------------
    # Filtros (GET)
    # -------------------------
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")
    sucursal_id = request.GET.get("sucursal")

    if sucursal_id:
        cuadraturas = cuadraturas.filter(sucursal_id=sucursal_id)

    if fecha_desde:
        cuadraturas = cuadraturas.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        cuadraturas = cuadraturas.filter(fecha__lte=fecha_hasta)

    cuadraturas = cuadraturas.order_by("-fecha", "-creado_el")

    return render(
        request,
        "cuadratura_diaria/list.html",
        {
            "cuadraturas": cuadraturas,
            "sucursales": Sucursal.objects.filter(is_active=True).order_by("nombre"),
        },
    )



@login_required
def cuadratura_diaria_detail(request, pk):
    cuadratura = get_object_or_404(CuadraturaCajaDiaria, pk=pk)
    caja_anterior_obj = CuadraturaCajaDiaria.objects.filter(
        sucursal=cuadratura.sucursal,
        fecha__lt=cuadratura.fecha
    ).order_by("-fecha", "-creado_el").first()
    caja_anterior = int(caja_anterior_obj.total_efectivo or 0) if caja_anterior_obj else int(cuadratura.sucursal.caja_inicial or 0)
    return render(request, "cuadratura_diaria/detail.html", {
        "cuadratura": cuadratura,
        "caja_anterior": caja_anterior,
    })
@login_required
def cuadratura_diaria_edit(request, pk):
    cuadratura = get_object_or_404(CuadraturaCajaDiaria, pk=pk)

    if request.method == "POST":
        form = CuadraturaCajaDiariaForm(request.POST, instance=cuadratura)
        if form.is_valid():
            c = form.save(commit=False)

            # Recalcular acumulados y totales igual que en create
            c.sorteos_acum = (c.sorteos_ant or 0) + (c.sorteos_dia or 0)
            c.gastos_acum = (c.gastos_ant or 0) + (c.gastos_dia or 0)
            c.sueldo_b_acum = (c.sueldo_b_ant or 0) + (c.sueldo_b_dia or 0)
            c.redbank_acum = (c.redbank_ant or 0) + (c.redbank_dia or 0)
            c.regalos_acum = (c.regalos_ant or 0) + (c.regalos_dia or 0)
            c.taxi_acum = (c.taxi_ant or 0) + (c.taxi_dia or 0)
            c.jugados_acum = (c.jugados_ant or 0) + (c.jugados_dia or 0)
            c.transfer_acum = (c.transfer_ant or 0) + (c.transfer_dia or 0)
            c.otros_1_acum = (c.otros_1_ant or 0) + (c.otros_1_dia or 0)
            c.otros_2_acum = (c.otros_2_ant or 0) + (c.otros_2_dia or 0)
            c.otros_3_acum = (c.otros_3_ant or 0) + (c.otros_3_dia or 0)
            c.descuadre_acum = (c.descuadre_ant or 0) + (c.descuadre_dia or 0)

            # Guardar campos de desglose de billetes
            for field in ['ef_20000', 'ef_10000', 'ef_5000', 'ef_2000', 'ef_1000', 'ef_monedas']:
                setattr(c, field, form.cleaned_data.get(field, 0))

            # Recalcular ganancia, numeral_dia, descuadre y total_efectivo correctamente
            _recalcular_totales(c)

            c.actualizado_el = timezone.now()
            c.save()

            # Propagar cambios en cascada a todos los días siguientes de la misma sucursal
            # Para que la caja_anterior de cada día siguiente quede actualizada
            dias_siguientes = CuadraturaCajaDiaria.objects.filter(
                sucursal=c.sucursal,
                fecha__gt=c.fecha
            ).order_by("fecha", "creado_el")

            for siguiente in dias_siguientes:
                _recalcular_totales(siguiente)
                siguiente.actualizado_el = timezone.now()
                siguiente.save()

            messages.success(request, "Cuadratura actualizada y días siguientes recalculados.")
            return redirect("control:cuadratura_diaria_detail", pk=c.pk)
        else:
            messages.error(request, "Formulario inválido.")
    else:
        form = CuadraturaCajaDiariaForm(instance=cuadratura)

    caja_anterior_obj = CuadraturaCajaDiaria.objects.filter(
        sucursal=cuadratura.sucursal,
        fecha__lt=cuadratura.fecha
    ).order_by("-fecha", "-creado_el").first()
    caja_anterior = int(caja_anterior_obj.total_efectivo or 0) if caja_anterior_obj else int(cuadratura.sucursal.caja_inicial or 0)
    sucursales = Sucursal.objects.filter(is_active=True).order_by("nombre")

    return render(request, "cuadratura_diaria/create.html", {
        "form": form,
        "cuadratura": cuadratura,
        "caja_anterior": caja_anterior,
        "caja_inicial": int(cuadratura.sucursal.caja_inicial or 0),
        "prestamos_acum_ant": int(caja_anterior_obj.prestamos_acum or 0) if caja_anterior_obj else 0,
        "mes_default": timezone.localdate().strftime("%Y-%m"),
        "sucursales": sucursales,
        "editar": True,
    })



@login_required
def cuadratura_diaria_recalcular_todo(request):
    """
    Recalcula total_efectivo y ganancia de TODAS las cuadraturas en orden cronológico.
    Esto propaga correctamente la cadena: caja_anterior → ganancia → total_efectivo → siguiente día.
    Solo accesible para admins.
    """
    if request.user.role != "admin":
        messages.error(request, "Solo los administradores pueden recalcular.")
        return redirect("control:cuadratura_diaria_list")

    if request.method != "POST":
        total = CuadraturaCajaDiaria.objects.count()
        return render(request, "cuadratura_diaria/recalcular.html", {"total": total})

    # Procesar en orden cronológico para que cada día vea el total_efectivo correcto del día anterior
    cuadraturas = CuadraturaCajaDiaria.objects.select_related("sucursal").order_by("fecha", "creado_el")
    actualizadas = 0

    for c in cuadraturas:
        try:
            _recalcular_totales(c)
            c.actualizado_el = timezone.now()
            c.save()
            actualizadas += 1
        except Exception as e:
            messages.warning(request, f"Error en {c.sucursal} {c.fecha}: {e}")

    messages.success(request, f"✅ {actualizadas} cuadraturas recalculadas correctamente.")
    return redirect("control:cuadratura_diaria_list")

@login_required
def cuadratura_diaria_delete(request, pk):
    cuadratura = get_object_or_404(CuadraturaCajaDiaria, pk=pk)

    if request.method == "POST":
        cuadratura.delete()
        messages.success(request, "Cuadratura eliminada.")
        return redirect("control:cuadratura_diaria_list")

    return render(request, "cuadratura_diaria/delete.html", {"cuadratura": cuadratura})



@login_required
def cuadratura_diaria_recalcular_todo(request):
    """
    Recalcula total_efectivo y ganancia de TODAS las cuadraturas en orden cronológico.
    Esto propaga correctamente la cadena: caja_anterior → ganancia → total_efectivo → siguiente día.
    Solo accesible para admins.
    """
    if request.user.role != "admin":
        messages.error(request, "Solo los administradores pueden recalcular.")
        return redirect("control:cuadratura_diaria_list")

    if request.method != "POST":
        total = CuadraturaCajaDiaria.objects.count()
        return render(request, "cuadratura_diaria/recalcular.html", {"total": total})

    # Procesar en orden cronológico para que cada día vea el total_efectivo correcto del día anterior
    cuadraturas = CuadraturaCajaDiaria.objects.select_related("sucursal").order_by("fecha", "creado_el")
    actualizadas = 0

    for c in cuadraturas:
        try:
            _recalcular_totales(c)
            c.actualizado_el = timezone.now()
            c.save()
            actualizadas += 1
        except Exception as e:
            messages.warning(request, f"Error en {c.sucursal} {c.fecha}: {e}")

    messages.success(request, f"✅ {actualizadas} cuadraturas recalculadas correctamente.")
    return redirect("control:cuadratura_diaria_list")

@login_required
def cuadratura_diaria_delete(request, pk):
    cuadratura = get_object_or_404(CuadraturaCajaDiaria, pk=pk)

    if request.method == "POST":
        cuadratura.delete()
        messages.success(request, "Cuadratura eliminada.")
        return redirect("control:cuadratura_diaria_list")

    return render(request, "cuadratura_diaria/delete.html", {"cuadratura": cuadratura})

@login_required
def cuadratura_diaria_export_excel(request):
    qs = CuadraturaCajaDiaria.objects.all().select_related("sucursal", "usuario")

    # mismos filtros que el listado
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")
    sucursal_id = request.GET.get("sucursal")

    if sucursal_id:
        qs = qs.filter(sucursal_id=sucursal_id)
    if fecha_desde:
        qs = qs.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__lte=fecha_hasta)

    qs = qs.order_by("-fecha", "-creado_el")

    wb = Workbook()
    ws = wb.active
    ws.title = "Cuadraturas Caja"

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    headers = [
        "Fecha", "Sucursal", "Usuario",
        "Zona 1", "Zona 2", "Numeral Total",
        "Gastos Día", "Ganancia",
        "Caja", "Retiro Diario", "Total Efectivo",
        "Observaciones",
    ]

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    row = 2
    for c in qs:
        ws.cell(row=row, column=1).value = c.fecha.strftime("%d/%m/%Y") if c.fecha else ""
        ws.cell(row=row, column=2).value = c.sucursal.nombre if c.sucursal else ""
        ws.cell(row=row, column=3).value = getattr(c.usuario, "nombre", "") if c.usuario else ""

        # Estas referencias no existen en models -> CuadraturaCajaDiaria
       # ws.cell(row=row, column=4).value = int(c.zona_1 or 0)
       # ws.cell(row=row, column=5).value = int(c.zona_2 or 0)
       # ws.cell(row=row, column=6).value = int(c.numeral_total or 0)

       # Creo que estas son las que corresponden
        ws.cell(row=row, column=4).value = int(c.numeral_dia or 0)
        ws.cell(row=row, column=5).value = int(c.numeral_acumulado or 0)
        # No se es total_efectivo falta por correguir
        ws.cell(row=row, column=6).value = int(c.total_efectivo or 0)
        
        
        # método del modelo
        ws.cell(row=row, column=7).value = int(c.total_gastos_dia() or 0)

        ws.cell(row=row, column=8).value = int(c.ganancia or 0)

        ws.cell(row=row, column=9).value = int(c.caja or 0)
        ws.cell(row=row, column=10).value = int(c.retiro_diario or 0)
        ws.cell(row=row, column=11).value = int(c.total_efectivo or 0)

        ws.cell(row=row, column=12).value = (c.observaciones or "")
        row += 1

    # ancho automático
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[column].width = max_length + 2

    filename = f"cuadraturas_caja_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

# ============================================
# ENCUADRE CAJA (SOLO ADMIN)
# ============================================
from django.db.models import Q
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment



@login_required
@user_passes_test(is_admin, login_url="/login/")
def encuadre_create(request):
    if request.method == "POST":
        form = EncuadreCajaAdminForm(request.POST)
        if form.is_valid():
            encuadre = form.save(commit=False)

            encuadre.usuario_admin = request.user
            encuadre.sucursal = form.cleaned_data["sucursal"]


            # total caja
            encuadre.total_caja = (
                (encuadre.caja_numeral or 0)
                + (encuadre.prestamos or 0)
                - (encuadre.redbank_retiros or 0)
            )

            # total entregado
            total_billetes = (
                (encuadre.billete_20000 or 0) * 20000
                + (encuadre.billete_10000 or 0) * 10000
                + (encuadre.billete_5000 or 0) * 5000
                + (encuadre.billete_2000 or 0) * 2000
                + (encuadre.billete_1000 or 0) * 1000
            )
            total_entregado = total_billetes + (encuadre.monedas_total or 0)

            # descuadre
            encuadre.descuadre = encuadre.total_caja - total_entregado

            encuadre.save()
            messages.success(request, "Encuadre de caja creado exitosamente.")
            return redirect("control:encuadre_list")
        else:
            messages.error(request, "Formulario inválido. Revise los datos enviados.")
    else:
        form = EncuadreCajaAdminForm(initial={"fecha": timezone.now().date()})

    return render(request, "encuadre/create.html", {"form": form})


@login_required
@user_passes_test(is_admin, login_url="/login/")
def encuadre_list(request):
    encuadres = EncuadreCajaAdmin.objects.all().select_related("sucursal", "usuario_admin")
    return render(request, "encuadre/list.html", {"encuadres": encuadres})


@login_required
@user_passes_test(is_admin, login_url="/login/")
def encuadre_detail(request, pk):
    encuadre = get_object_or_404(EncuadreCajaAdmin, pk=pk)
    return render(request, "encuadre/detail.html", {"encuadre": encuadre})


# ============================================
# DASHBOARD (SOLO ADMIN)
# ============================================

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    hoy = timezone.now().date()

    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")
    sucursal_id = request.GET.get("sucursal")

    if not fecha_hasta:
        fecha_hasta = hoy
    else:
        fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()

    if not fecha_desde:
        fecha_desde = fecha_hasta - timedelta(days=6)
    else:
        fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()

    inicio = timezone.make_aware(datetime.combine(fecha_desde, time.min))
    fin = timezone.make_aware(datetime.combine(fecha_hasta, time.max))

    lecturas = LecturaMaquina.objects.filter(fecha_registro__range=(inicio, fin))

    if sucursal_id:
        lecturas = lecturas.filter(sucursal_id=sucursal_id)

    kpis = lecturas.aggregate(
        total_entrada=Sum("entrada"),
        total_salida=Sum("salida"),
        total_neto=Sum("total"),
        maquinas_activas=Count("maquina", distinct=True),
        total_lecturas=Count("id"),
    )

    for k in kpis:
        kpis[k] = kpis[k] or 0

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

        total_dia = total_dia.aggregate(suma=Sum("total"))["suma"] or 0

        chart_labels.append(fecha_cursor.strftime("%d/%m"))
        chart_data.append(int(total_dia))
        fecha_cursor += timedelta(days=1)

    top_maquinas = lecturas.values("numero_maquina", "nombre_juego").annotate(
        neto=Sum("total")
    ).order_by("-neto")[:5]

    bottom_maquinas = lecturas.values("numero_maquina", "nombre_juego").annotate(
        neto=Sum("total")
    ).order_by("neto")[:5]

    context = {
        "kpis": kpis,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "top_maquinas": top_maquinas,
        "bottom_maquinas": bottom_maquinas,
        "sucursales": Sucursal.objects.all().order_by("nombre"),
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }

    return render(request, "dashboard.html", context)


# ============================================
# TURNO
# ============================================

@login_required
def turno_view(request):
    turno_abierto = Turno.objects.filter(usuario=request.user, estado="Abierto").first()

    if request.method == "POST":
        if not turno_abierto:
            # El usuario es enviado al POST
            form = TurnoForm(request.POST, user=request.user)
            if form.is_valid():
                turno = form.save(commit=False)
                turno.usuario = request.user
                turno.estado = "Abierto"
                # Se fuerza la sucursal si es atendedora
                if request.user.role == "usuario" and request.user.sucursal:
                    turno.sucursal = request.user.sucursal

                try:
                    turno.full_clean()
                    turno.save()
                    messages.success(request, "Turno iniciado exitosamente.")
                    return redirect("control:turno")
                except Exception as e:
                    messages.error(request, str(e))
        else:
            messages.warning(request, "Ya tiene un turno abierto.")
    else:
        # Le pasamos el usuario al formulario cuando se carga la página
        form = TurnoForm(user=request.user) if not turno_abierto else None

    cantidad_lecturas = 0
    if turno_abierto:
        cantidad_lecturas = LecturaMaquina.objects.filter(turno=turno_abierto).count()

    context = {
        "turno_abierto": turno_abierto,
        "cantidad_lecturas": cantidad_lecturas,
        "form": form,
        "sucursales": Sucursal.objects.all(),
    }

    return render(request, "turno.html", context)


@login_required
def cerrar_turno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id, usuario=request.user)

    if turno.estado == "Abierto":
        total = LecturaMaquina.objects.filter(turno=turno).aggregate(
            total_sum=Sum("total")
        )["total_sum"] or 0

        turno.estado = "Cerrado"
        turno.total_cierre = Decimal(str(total))
        turno.save()

        messages.success(
            request, f"Turno cerrado exitosamente. Total: ${turno.total_cierre:,.0f}"
        )
    else:
        messages.warning(request, "El turno ya está cerrado.")

    return redirect("control:cierre_turno", turno_id=turno.id)

@login_required
def registro_view(request):
    turno_abierto = Turno.objects.filter(usuario=request.user, estado__iexact="abierto").first()
    zona_guardada_id = request.session.get("ultima_zona")

    if request.method == "POST":
        if not turno_abierto:
            messages.error(
                request,
                'Debe iniciar un turno en la pestaña "Turno" antes de registrar lecturas.',
            )
            return redirect("control:turno")

        form = LecturaMaquinaForm(request.POST, turno=turno_abierto)

        if form.is_valid():
            lectura = form.save(commit=False)
            lectura.turno = turno_abierto
            lectura.usuario = request.user
            lectura.sucursal = turno_abierto.sucursal
            lectura.zona = form.cleaned_data["zona"]

            if lectura.maquina:
                lectura.numero_maquina = lectura.maquina.numero_maquina
                lectura.nombre_juego = lectura.maquina.nombre_juego

            try:
                lectura.total = int(lectura.entrada or 0) - int(lectura.salida or 0)
                lectura.full_clean()
                lectura.save()
            except IntegrityError:
                messages.error(request, "Ya existe una lectura para esa máquina en este turno.")
            except ValidationError as e:
                messages.error(request, "; ".join(e.messages))
            else:
                request.session["ultima_zona"] = lectura.zona.id

                # Calcular la siguiente máquina en orden dentro de la zona
                maquinas_zona = list(
                    Maquina.objects.filter(
                        zona=lectura.zona,
                        estado="Operativa",
                        sucursal__is_active=True,
                    ).order_by("numero_maquina").values_list("id", flat=True)
                )
                if lectura.maquina and lectura.maquina.id in maquinas_zona:
                    idx = maquinas_zona.index(lectura.maquina.id)
                    siguiente_idx = idx + 1
                    if siguiente_idx < len(maquinas_zona):
                        request.session["siguiente_maquina"] = maquinas_zona[siguiente_idx]
                    else:
                        request.session.pop("siguiente_maquina", None)
                else:
                    request.session.pop("siguiente_maquina", None)

                messages.success(request, f"Lectura registrada. Máquina {lectura.maquina.numero_maquina} guardada.")
                return redirect("control:registro")
        else:
            messages.error(request, "Formulario inválido. Revise los datos enviados.")

    else:
        if turno_abierto:
            siguiente_maquina_id = request.session.pop("siguiente_maquina", None)
            initial = {}
            if zona_guardada_id:
                initial["zona"] = zona_guardada_id
            if siguiente_maquina_id:
                initial["maquina"] = siguiente_maquina_id
            form = LecturaMaquinaForm(turno=turno_abierto, initial=initial if initial else None)
        else:
            form = None
        siguiente_maquina_id = None  # ya fue consumida

    context = {
        "turno_abierto": turno_abierto,
        "form": form,
        "zona_guardada": zona_guardada_id,
    }

    return render(request, "registro.html", context)


# ============================================
# AJAX
# ============================================
@login_required
def _get_caja_anterior(sucursal: Sucursal, fecha):
    # última cuadratura anterior a esa fecha
    ultima = (CuadraturaCajaDiaria.objects
              .filter(sucursal=sucursal, fecha__lt=fecha)
              .order_by("-fecha")
              .first())
    if ultima:
        # caja del día anterior = lo que quedó como efectivo / caja para el siguiente día
        return int(ultima.total_efectivo or 0)
    # si no hay anterior, base = caja inicial del local
    return int(sucursal.caja_inicial or 0)

def ajax_cuadratura_detalles(request):
    sucursal_id = request.GET.get("sucursal_id")
    fecha = request.GET.get("fecha")

    if not sucursal_id or not fecha:
        return JsonResponse({"ok": False, "error": "Faltan parámetros."})

    sucursal = Sucursal.objects.filter(id=sucursal_id).first()
    if not sucursal:
        return JsonResponse({"ok": False, "error": "Sucursal no existe."})

    cuadratura = (
        CuadraturaCajaDiaria.objects
        .filter(sucursal=sucursal, fecha=fecha)
        .order_by("-creado_el")
        .first()
    )

    if not cuadratura:
        return JsonResponse({"ok": True, "exists": False, "detalles": []})

    detalles = list(
        CuadraturaDetalle.objects
        .filter(cuadratura=cuadratura)
        .values("tipo", "nombre", "monto")
        .order_by("tipo", "creado_en")
    )

    return JsonResponse({
        "ok": True,
        "exists": True,
        "id": cuadratura.id,
        "detalles": detalles,
        # opcional: para depurar
        "gastos_dia": cuadratura.gastos_dia,
        "sueldo_b_dia": cuadratura.sueldo_b_dia,
    })
@login_required
def ajax_cuadratura_diaria_numerales(request):
    sucursal_id = request.GET.get("sucursal_id")
    fecha_str = request.GET.get("fecha")

    if not sucursal_id or not fecha_str:
        return JsonResponse({"ok": False, "error": "missing_params"})

    try:
        fecha = timezone.datetime.fromisoformat(fecha_str).date()
    except Exception:
        return JsonResponse({"ok": False, "error": "bad_date"})

    sucursal = Sucursal.objects.filter(id=sucursal_id, is_active=True).first()
    if not sucursal:
        return JsonResponse({"ok": False, "error": "bad_sucursal"})

    # === Cálculo principal ===
    numeral_dia, numeral_acumulado = calcular_numerales_caja(sucursal, fecha)

    # Caja anterior = última caja registrada antes de esta fecha, SIN filtro de ciclo
    # (el efectivo físico no depende del ciclo de recaudación)
    caja_anterior_obj = CuadraturaCajaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__lt=fecha
    ).order_by("-fecha", "-creado_el").first()

    if caja_anterior_obj:
        caja_anterior = int(caja_anterior_obj.total_efectivo or 0)
    else:
        caja_anterior = int(sucursal.caja_inicial or 0)
    

    # Prestamos acumulados del día anterior
    prestamos_acum_ant = int(caja_anterior_obj.prestamos_acum or 0) if caja_anterior_obj else 0

    return JsonResponse({
        "ok": True,
        "numeral_dia": numeral_dia,
        "numeral_acumulado": numeral_acumulado,
        "caja_anterior": caja_anterior,
        "caja_inicial": int(sucursal.caja_inicial or 0),
        "prestamos_acum_ant": prestamos_acum_ant,
    })

@login_required
def zonas_por_sucursal(request):
    sucursal_id = request.GET.get("sucursal_id")

    zonas = (
        Zona.objects
        .filter(sucursal_id=sucursal_id, is_active=True)
        .order_by("nombre")
    )

    data = [{"id": z.id, "nombre": z.nombre} for z in zonas]
    return JsonResponse(data, safe=False)

@login_required
def get_zonas_ajax(request, sucursal_id):
    zonas = Zona.objects.filter(
        sucursal_id=sucursal_id,
        is_active=True
    ).values("id", "nombre")
    return JsonResponse(list(zonas), safe=False)


@login_required
def get_maquinas_ajax(request, zona_id):
    maquinas = Maquina.objects.filter(
        zona_id=zona_id,
        estado="Operativa",
        zona__is_active=True
    ).values("id", "numero_maquina", "nombre_juego")
    return JsonResponse(list(maquinas), safe=False)


# ============================================
# OCR
# ============================================

@csrf_exempt
def ocr_lectura(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    try:
        # 1) cargar imagen
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

        # 2) preproceso
        imagen = imagen.convert("L")
        imagen = ImageOps.autocontrast(imagen)

        w, h = imagen.size
        factor = max(2.0, 1500 / max(w, h))
        imagen = imagen.resize((int(w * factor), int(h * factor)), Image.LANCZOS)
        imagen = imagen.point(lambda x: 0 if x < 150 else 255, "1")

        config = "--oem 3 --psm 6"

        texto_plano = pytesseract.image_to_string(imagen, lang="eng", config=config)
        print("===== OCR RAW =====")
        print(texto_plano)

        data_ocr = pytesseract.image_to_data(imagen, lang="eng", config=config, output_type=Output.DICT)
        filas = agrupar_lineas(data_ocr)

        entrada = None
        salida = None
        entrada_raw = None
        salida_raw = None

        # 3) buscar entradas/salidas por filas
        for f in filas:
            txt_norm = normalizar_texto_label(f["texto"])

            if entrada is None and es_linea_entrada(txt_norm) and f["numeros"]:
                entrada_raw, entrada_str = extraer_monto_desde_tokens(f["numeros"])
                entrada = normalizar_valor(entrada_str)

            if salida is None and es_linea_salida(txt_norm) and f["numeros"]:
                salida_raw, salida_str = extraer_monto_desde_tokens(f["numeros"])
                salida = normalizar_valor(salida_str)

        # 4) fallback: salida en línea siguiente
        if salida is None:
            for i in range(len(filas) - 1):
                txt_norm = normalizar_texto_label(filas[i]["texto"])
                if es_linea_salida(txt_norm):
                    nums_sig = filas[i + 1]["numeros"]
                    if nums_sig:
                        salida_raw, salida_str = extraer_monto_desde_tokens(nums_sig)
                        salida = normalizar_valor(salida_str)
                        break

        # 5) fallback regex plano
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

        # 6) validar
        if entrada is None or salida is None:
            return JsonResponse(
                {"success": False, "error": "No se encontraron ENTRADAS / SALIDAS", "debug": texto_plano},
                status=400,
            )

        total = entrada - salida

        return JsonResponse(
            {
                "success": True,
                "entrada": entrada,
                "salida": salida,
                "total": total,
                "entrada_raw": entrada_raw,
                "salida_raw": salida_raw,
                "mensaje": "OCR procesado correctamente",
            }
        )

    except Exception as e:
        print("Error OCR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)


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
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "/": ""
    }
    for k, v in reemplazos.items():
        s = s.replace(k, v)
    return s


def es_linea_entrada(txt):
    patrones = ["ENTRADA", "ENTRADAS", "NTRADA", "TRADA", "ENTRAD"]
    return any(p in txt for p in patrones)


def es_linea_salida(txt):
    patrones = ["SALIDA", "SALIDAS", "SLIDA", "SALID", "SALD", "SALDA", "ALIDAS", "IDAS"]
    return any(p in txt for p in patrones)


def extraer_monto_desde_tokens(tokens):
    raw = " ".join(tokens)
    solo_digitos = re.sub(r"[^\d]", "", raw)

    if len(solo_digitos) >= 5:
        if len(solo_digitos) > 6:
            solo_digitos = solo_digitos[:6]
        return raw, solo_digitos

    candidato = seleccionar_numero_correcto(tokens)
    return candidato, candidato


def seleccionar_numero_correcto(nums):
    nums_limpios = [(n, len(re.sub(r"[^\d]", "", n))) for n in nums]
    nums_limpios.sort(key=lambda x: x[1], reverse=True)
    return nums_limpios[0][0] if nums_limpios else ""


def normalizar_valor(raw):
    if raw is None:
        return None
    s = re.sub(r"[^\d]", "", str(raw))
    if not s:
        return None
    if s.startswith("5") and len(s) >= 6:
        s = s[1:]
    return int(s)


@login_required
def ia_capturar_dummy(request):
    return JsonResponse({
        "success": True,
        "entrada": 150000,
        "salida": 30000,
        "total": 120000,
        "mensaje": "Datos capturados exitosamente (DEMO)",
    })


# ============================================
# TABLAS Y EXCEL
# ============================================

@login_required
def tablas_view(request):
    lecturas = LecturaMaquina.objects.all()

    if request.user.role == "usuario":
        turno_abierto = Turno.objects.filter(usuario=request.user, estado="Abierto").first()
        if turno_abierto:
            lecturas = lecturas.filter(turno=turno_abierto)
        else:
            hoy = timezone.now().date()
            lecturas = lecturas.filter(usuario=request.user, fecha_registro__date=hoy)

    if request.user.role == "admin":
        sucursal_id = request.GET.get("sucursal")
        zona_id = request.GET.get("zona")
        maquina_id = request.GET.get("maquina")
        usuario_id = request.GET.get("usuario")
        fecha_desde = request.GET.get("fecha_desde")
        fecha_hasta = request.GET.get("fecha_hasta")

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

    fecha = request.GET.get("fecha")
    if fecha and request.user.role == "usuario":
        lecturas = lecturas.filter(fecha_registro__date=fecha)

    lecturas = lecturas.order_by("-fecha_registro")[:200]

    total_entrada = lecturas.aggregate(Sum("entrada"))["entrada__sum"] or 0
    total_salida = lecturas.aggregate(Sum("salida"))["salida__sum"] or 0
    total_total = lecturas.aggregate(Sum("total"))["total__sum"] or 0

    context = {
        "lecturas": lecturas,
        "total_entrada": total_entrada,
        "total_salida": total_salida,
        "total_total": total_total,
        "sucursales": Sucursal.objects.all(),
        "zonas": Zona.objects.all(),
        "maquinas": Maquina.objects.all(),
        "usuarios": Usuario.objects.filter(role="usuario"),
    }

    return render(request, "tablas.html", context)
class LecturaEditView(UpdateView):
    model = LecturaMaquina
    form_class = LecturaMaquinaForm
    template_name = "control/lectura_edit.html"
    success_url = reverse_lazy("control:tablas")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        turno = getattr(self.request.user, "turno_activo", None)
        kwargs["turno"] = turno
        return kwargs
@login_required
def export_excel(request):
    lecturas = LecturaMaquina.objects.all()

    if request.user.role == "usuario":
        turno_abierto = Turno.objects.filter(usuario=request.user, estado="Abierto").first()
        if turno_abierto:
            lecturas = lecturas.filter(turno=turno_abierto)
        else:
            hoy = timezone.now().date()
            lecturas = lecturas.filter(usuario=request.user, fecha_registro__date=hoy)

    if request.user.role == "admin":
        sucursal_id = request.GET.get("sucursal")
        zona_id = request.GET.get("zona")
        maquina_id = request.GET.get("maquina")
        usuario_id = request.GET.get("usuario")
        fecha_desde = request.GET.get("fecha_desde")
        fecha_hasta = request.GET.get("fecha_hasta")

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

    fecha = request.GET.get("fecha")
    if fecha and request.user.role == "usuario":
        lecturas = lecturas.filter(fecha_registro__date=fecha)

    lecturas = lecturas.order_by("-fecha_registro")

    wb = Workbook()
    ws = wb.active
    ws.title = "Lecturas de Máquinas"

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    headers = [
        "Fecha", "Sucursal", "Zona", "Nº Máquina", "Juego",
        "Entrada", "Salida", "Total", "Usuario", "Nota"
    ]

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for row_num, lectura in enumerate(lecturas, 2):
        ws.cell(row=row_num, column=1).value = lectura.fecha_registro.strftime("%d/%m/%Y %H:%M")
        ws.cell(row=row_num, column=2).value = lectura.sucursal.nombre if lectura.sucursal else ""
        ws.cell(row=row_num, column=3).value = lectura.zona.nombre if lectura.zona else ""
        ws.cell(row=row_num, column=4).value = lectura.numero_maquina
        ws.cell(row=row_num, column=5).value = lectura.nombre_juego
        ws.cell(row=row_num, column=6).value = lectura.entrada
        ws.cell(row=row_num, column=7).value = lectura.salida
        ws.cell(row=row_num, column=8).value = lectura.total
        ws.cell(row=row_num, column=9).value = getattr(lectura.usuario, "nombre", lectura.usuario.username)
        ws.cell(row=row_num, column=10).value = lectura.nota

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[column].width = max_length + 2

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename=lecturas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
    wb.save(response)
    return response


# ============================================
# CRUD SUCURSALES (ADMIN)
# ============================================

@login_required
@user_passes_test(is_admin)
def sucursales_list(request):
    query = request.GET.get("q")
    sucursales = Sucursal.objects.filter(is_active=True)
    if query:
        sucursales = sucursales.filter(nombre__icontains=query)

    return render(request, "sucursales/list.html", {"sucursales": sucursales, "query": query})


@login_required
@user_passes_test(is_admin)
def sucursal_create(request):
    if request.method == "POST":
        form = SucursalForm(request.POST)
        if form.is_valid():
            form.save()
            if "guardar_otro" in request.POST:
                messages.success(request, "Sucursal guardada. Puede agregar otra.")
                return redirect("control:sucursal_create")
            messages.success(request, "Sucursal creada exitosamente.")
            return redirect("control:sucursales_list")
    else:
        form = SucursalForm()

    return render(request, "sucursales/form.html", {"form": form, "title": "Crear Sucursal"})


@login_required
@user_passes_test(is_admin)
def sucursal_edit(request, pk):
    sucursal = get_object_or_404(Sucursal, pk=pk)
    if request.method == "POST":
        form = SucursalForm(request.POST, instance=sucursal)
        if form.is_valid():
            form.save()
            messages.success(request, "Sucursal actualizada exitosamente.")
            return redirect("control:sucursales_list")
    else:
        form = SucursalForm(instance=sucursal)

    return render(request, "sucursales/form.html", {"form": form, "title": "Editar Sucursal"})


@login_required
@user_passes_test(is_admin)
@login_required
def sucursal_delete(request, pk):
    sucursal = get_object_or_404(Sucursal, pk=pk)

    if request.method == "POST":
        sucursal.is_active = False
        sucursal.save()
        messages.success(request, "Sucursal desactivada correctamente.")
        return redirect("control:sucursales_list")

    return render(request, "sucursales/delete.html", {
        "sucursal": sucursal
    })


# ============================================
# CRUD ZONAS (ADMIN)
# ============================================

@login_required
@user_passes_test(is_admin)
def zonas_list(request):
    sucursal_id = request.GET.get("sucursal")

    zonas = Zona.objects.filter(is_active=True, sucursal__is_active=True)
    if sucursal_id:
        zonas = zonas.filter(sucursal_id=sucursal_id)

    return render(
        request,
        "zonas/list.html",
        {
            "zonas": zonas,
            "sucursales": Sucursal.objects.filter(is_active=True),
            "sucursal_id": sucursal_id,
        },
    )


@login_required
@user_passes_test(is_admin)
def zona_create(request):
    if request.method == "POST":
        form = ZonaForm(request.POST)
        if form.is_valid():
            form.save()
            if "guardar_otro" in request.POST:
                messages.success(request, "Zona guardada. Puede agregar otra.")
                return redirect("control:zona_create")
            messages.success(request, "Zona creada exitosamente.")
            return redirect("control:zonas_list")
    else:
        form = ZonaForm()

    return render(request, "zonas/form.html", {"form": form, "title": "Crear Zona"})


@login_required
@user_passes_test(is_admin)
def zona_edit(request, pk):
    zona = get_object_or_404(Zona, pk=pk)
    if request.method == "POST":
        form = ZonaForm(request.POST, instance=zona)
        if form.is_valid():
            form.save()
            messages.success(request, "Zona actualizada exitosamente.")
            return redirect("control:zonas_list")
    else:
        form = ZonaForm(instance=zona)

    return render(request, "zonas/form.html", {"form": form, "title": "Editar Zona"})


@login_required
@user_passes_test(is_admin)
def zona_delete(request, pk):
    zona = get_object_or_404(Zona, pk=pk)

    if request.method == "POST":
        zona.is_active = False
        zona.save()
        Maquina.objects.filter(zona=zona).update(is_active=False)

        messages.success(request, "Zona desactivada correctamente. El histórico fue conservado.")
        return redirect("control:zonas_list")

    return render(request, "zonas/delete.html", {"object": zona})


# ============================================
# CRUD MÁQUINAS (ADMIN)
# ============================================

@login_required
@user_passes_test(is_admin)
def maquinas_list(request):
    sucursal_id = request.GET.get("sucursal")
    zona_id = request.GET.get("zona")

    maquinas = Maquina.objects.filter(sucursal__is_active=True, zona__is_active=True)

    if sucursal_id:
        maquinas = maquinas.filter(sucursal_id=sucursal_id)
    if zona_id:
        maquinas = maquinas.filter(zona_id=zona_id)

    return render(
        request,
        "maquinas/list.html",
        {
            "maquinas": maquinas,
            "sucursales": Sucursal.objects.filter(is_active=True),
            "zonas": Zona.objects.filter(is_active=True),
            "sucursal_id": sucursal_id,
            "zona_id": zona_id,
        },
    )


@login_required
@user_passes_test(is_admin)
def maquina_create(request):
    if request.method == "POST":
        form = MaquinaForm(request.POST)
        if form.is_valid():
            form.save()
            if "guardar_otro" in request.POST:
                messages.success(request, "Máquina guardada. Puede agregar otra.")
                return redirect("control:maquina_create")
            messages.success(request, "Máquina creada exitosamente.")
            return redirect("control:maquinas_list")
    else:
        form = MaquinaForm()

    return render(request, "maquinas/form.html", {"form": form, "title": "Crear Máquina"})


@login_required
@user_passes_test(is_admin)
def maquina_edit(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk)
    if request.method == "POST":
        form = MaquinaForm(request.POST, instance=maquina)
        if form.is_valid():
            form.save()
            messages.success(request, "Máquina actualizada exitosamente.")
            return redirect("control:maquinas_list")
    else:
        form = MaquinaForm(instance=maquina)

    return render(request, "maquinas/form.html", {"form": form, "title": "Editar Máquina"})


@login_required
@user_passes_test(is_admin)
def maquina_delete(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk)
    if request.method == "POST":
        maquina.delete()
        messages.success(request, "Máquina eliminada exitosamente.")
        return redirect("control:maquinas_list")
    return render(request, "maquinas/delete.html", {"object": maquina})


@login_required
@user_passes_test(is_admin)
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
# CRUD USUARIOS (ADMIN)
# ============================================

@login_required
@user_passes_test(is_admin)
def usuarios_list(request):
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/list.html", {"usuarios": usuarios})


@login_required
@user_passes_test(is_admin)
def usuario_create(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data["password"])
            usuario.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect("control:usuarios_list")
    else:
        form = UsuarioForm()
    return render(request, "usuarios/form.html", {"form": form, "title": "Crear Usuario"})


@login_required
@user_passes_test(is_admin)
def usuario_edit(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "POST":
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get("password")
            if password:
                usuario.set_password(password)
            usuario.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect("control:usuarios_list")
    else:
        form = UsuarioEditForm(instance=usuario)
    return render(request, "usuarios/form.html", {"form": form, "title": "Editar Usuario"})


@login_required
@user_passes_test(is_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado exitosamente.")
        return redirect("control:usuarios_list")
    return render(request, "usuarios/delete.html", {"object": usuario})

def _seed_cierre_defaults(cierre: CierreTurno):
    # Zonas activas de la sucursal
    zonas = Zona.objects.filter(sucursal=cierre.sucursal, is_active=True).order_by("orden", "nombre")
    for z in zonas:
        CierreTurnoZona.objects.get_or_create(cierre=cierre, zona=z)

    # Movimientos fijos
    for key, _label in CierreTurnoMovimiento.TIPO_CHOICES:
        CierreTurnoMovimiento.objects.get_or_create(cierre=cierre, tipo=key)

    # Pagos fijos
    for key, _label in CierreTurnoPago.TIPO_CHOICES:
        CierreTurnoPago.objects.get_or_create(cierre=cierre, tipo=key)

    # Denominaciones típicas
    billetes = [20000, 10000, 5000, 2000, 1000]
    monedas = [500, 100, 50, 10]
    for d in billetes:
        CierreTurnoDenominacion.objects.get_or_create(cierre=cierre, tipo="BILLETE", denominacion=d)
    for d in monedas:
        CierreTurnoDenominacion.objects.get_or_create(cierre=cierre, tipo="MONEDA", denominacion=d)

from django.db import transaction

# ==========================
# CIERRE TURNO (COLUMNA ROJA)
# ==========================

def _recalcular_totales_cierre(cierre: CierreTurno):
    zonas_qs = cierre.zonas.all()
    movs_qs = cierre.movimientos.all()
    dens_qs = cierre.denominaciones.all()

    total_numeral = sum((x.numeral or 0) for x in zonas_qs)
    total_gastos = sum((m.monto or 0) for m in movs_qs)
    total_efectivo = sum((d.cantidad or 0) for d in dens_qs)
    total_redbank = cierre.pagos.filter(tipo="REDBANK").aggregate(s=Sum("monto"))["s"] or 0

    cierre.total_numeral = int(total_numeral)
    cierre.total_gastos = int(total_gastos)
    cierre.total_efectivo_contado = int(total_efectivo)

    # Si tu modelo tiene campo total_pagos, lo guardas. Si no, lo ignoras.


    cierre.total_esperado = int(
        (cierre.caja_base or 0)
        + total_numeral
        + (cierre.redbank_retiros or 0)      # ✅ se suma
        + (cierre.prestamos_salida or 0)     # ⚠️ por ahora lo sumo; confirma si debe restar
        - (total_gastos + (cierre.retiro_diario or 0))
    )
    cierre.descuadre = int((cierre.total_efectivo_contado or 0) - cierre.total_esperado)

def _autollenar_numerales_por_zona(cierre, turno):
    sums = (
        LecturaMaquina.objects
        .filter(turno=turno)
        .values("zona_id")
        .annotate(total=Sum("total"))
    )

    mapa = {x["zona_id"]: int(x["total"] or 0) for x in sums}

    for cz in cierre.zonas.all():
        nuevo = mapa.get(cz.zona_id, 0)
        if cz.numeral != nuevo:
            cz.numeral = nuevo
            cz.save(update_fields=["numeral"])

def total_entregado_zona(cz):
    return int(
        (cz.billete_20000_monto or 0) +
        (cz.billete_10000_monto or 0) +
        (cz.billete_5000_monto  or 0) +
        (cz.billete_2000_monto  or 0) +
        (cz.billete_1000_monto  or 0) +
        (cz.monedas_monto or 0)
    )

def _recalcular_totales_cierre(cierre: CierreTurno):
    zonas_qs = cierre.zonas.all()
    movs_qs = cierre.movimientos.all()

    total_numeral = sum((z.numeral or 0) for z in zonas_qs)
    total_gastos = sum((m.monto or 0) for m in movs_qs)

    # ✅ AQUÍ estaba el problema: ahora el efectivo viene desde las ZONAS (billetes + monedas)
    total_efectivo = sum(total_entregado_zona(z) for z in zonas_qs)

    cierre.total_numeral = int(total_numeral)
    cierre.total_gastos = int(total_gastos)
    cierre.total_efectivo_contado = int(total_efectivo)

    cierre.total_esperado = int(
        (cierre.caja_base or 0)
        + total_numeral
        + (cierre.redbank_retiros or 0)
        + (cierre.prestamos_salida or 0)
        - (total_gastos + (cierre.retiro_diario or 0))
    )
    cierre.descuadre = int((cierre.total_efectivo_contado or 0) - cierre.total_esperado)


from django.db.models import Sum
from django.utils import timezone

@login_required
def cierre_turno_create_or_edit(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id)

    # solo la atendedora del turno o admin
    if request.user.role == "usuario" and turno.usuario_id != request.user.id:
        return HttpResponse("No autorizado", status=403)

    cierre, _created = CierreTurno.objects.get_or_create(
        turno=turno,
        defaults={
            "sucursal": turno.sucursal,
            "usuario": request.user,
            "fecha": getattr(turno, "fecha", None) or timezone.now().date(),
        },
    )

    # --- coherencia cierre vs turno ---
    changed = False
    if cierre.sucursal_id != turno.sucursal_id:
        cierre.sucursal = turno.sucursal
        changed = True

    if cierre.usuario_id != request.user.id:
        cierre.usuario = request.user
        changed = True

    fecha_turno = getattr(turno, "fecha", None) or timezone.now().date()
    if cierre.fecha != fecha_turno:
        cierre.fecha = fecha_turno
        changed = True

    if changed:
        cierre.save()

    # --- sincronizar filas base ---
    _sync_cierre_zonas_activo(cierre)
    _seed_cierre_defaults(cierre)
    _autollenar_numerales_por_zona(cierre, turno)
    _ensure_billetes(cierre)


    for z in cierre.zonas.all():
        total_zona = (
            LecturaMaquina.objects
            .filter(turno=turno, zona=z.zona)
            .aggregate(s=Sum("total"))["s"]
            or 0
        )

        z.numeral = int(total_zona)
        z.save(update_fields=["numeral"])
    # lecturas (para la tabla del template)
    lecturas = (
        LecturaMaquina.objects
        .filter(turno=turno)
        .select_related("zona", "maquina")
        .order_by("zona__orden", "zona__nombre", "numero_maquina", "nombre_juego", "fecha_registro")
    )

    # ✅ SIEMPRE crea form/formsets (GET y POST)
    if request.method == "POST":
        form = CierreTurnoForm(request.POST, instance=cierre)
        zonas_fs = CierreTurnoZonaFormSet(request.POST, instance=cierre, prefix="zonas")
        mov_fs = CierreTurnoMovimientoFormSet(request.POST, instance=cierre, prefix="movimientos")
        pagos_fs = CierreTurnoPagoFormSet(request.POST, instance=cierre, prefix="pagos")
        den_fs = CierreTurnoDenFormSet(request.POST, instance=cierre, prefix="den")

        if form.is_valid() and zonas_fs.is_valid() and mov_fs.is_valid() and pagos_fs.is_valid() and den_fs.is_valid():
            with transaction.atomic():
                form.save()
                zonas_fs.save()
                mov_fs.save()
                pagos_fs.save()
                den_fs.save()
                
                _autollenar_numerales_por_zona(cierre, turno)


                _recalcular_totales_cierre(cierre)
                cierre.save()
                total_lecturas = LecturaMaquina.objects.filter(turno=turno).aggregate(
                    total_sum=Sum("total")
                )["total_sum"] or 0

                cierre.total_lecturas_turno = int(total_lecturas)
                cierre.save(update_fields=["total_lecturas_turno"])

                # cerrar turno
                total_lecturas = LecturaMaquina.objects.filter(turno=turno).aggregate(
                    total_sum=Sum("total")
                )["total_sum"] or 0

                Turno.objects.filter(id=turno.id).update(
                    estado="Cerrado",
                    total_cierre=Decimal(str(total_lecturas)),
                )

            messages.success(request, "Cierre de turno guardado y turno cerrado.")
            return redirect("control:turno")
        else:
            messages.error(request, "Hay errores en el formulario. Revisa los campos.")

    else:
        form = CierreTurnoForm(instance=cierre)
        zonas_fs = CierreTurnoZonaFormSet(instance=cierre, prefix="zonas")
        mov_fs = CierreTurnoMovimientoFormSet(instance=cierre, prefix="movimientos")
        pagos_fs = CierreTurnoPagoFormSet(instance=cierre, prefix="pagos")
        den_fs = CierreTurnoDenFormSet(instance=cierre, prefix="den")


            # --- construir bloques por zona (para template tipo Excel) ---
        # Usamos las zonas del CIERRE (ya sincronizadas) para asegurar que siempre existan
        cierrezonas = (
            cierre.zonas
            .select_related("zona")
            .all()
            .order_by("zona__orden", "zona__nombre")
        )

        zona_blocks = []
        for cz in cierrezonas:
            z = cz.zona

            lects = list(
                LecturaMaquina.objects
                .filter(turno=turno, zona=z)
                .order_by("numero_maquina", "nombre_juego", "fecha_registro")
            )

            total_zona = sum(int(x.total or 0) for x in lects)

            # buscar el formset form correspondiente a esa fila (por PK del inline)
            fz = None
            for _fz in zonas_fs:
                if _fz.instance.pk == cz.pk:
                    fz = _fz
                    break

            zona_blocks.append({
                "zona": z,
                "lecturas": lects,
                "total_zona": total_zona,
                "fz": fz,
            })

    return render(
        request,
        "cuadratura/create_turno.html",
        {
            "turno": turno,
            "cierre": cierre,
            "form": form,
            "zonas_fs": zonas_fs,
            "mov_fs": mov_fs,
            "pagos_fs": pagos_fs,
            "den_fs": den_fs,
            "lecturas": lecturas,
            "zona_blocks": zona_blocks,
        },
   


    )

@login_required
@user_passes_test(is_admin, login_url="/login/")
def cierre_turno_list(request):
    qs = CierreTurno.objects.select_related("turno", "sucursal", "usuario")

    sucursal_id = request.GET.get("sucursal")
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    if sucursal_id:
        qs = qs.filter(sucursal_id=sucursal_id)
    if fecha_desde:
        qs = qs.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__lte=fecha_hasta)

    qs = qs.order_by("-fecha", "-id")

    return render(
        request,
        "cierre_turno/list.html",
        {
            "cierres": qs,
            "sucursales": Sucursal.objects.filter(is_active=True).order_by("nombre"),
        },
    )


@login_required
def cierre_turno_detail(request, pk):
    cierre = get_object_or_404(CierreTurno, pk=pk)

    if request.user.role == "usuario" and cierre.usuario_id != request.user.id:
        return HttpResponse("No autorizado", status=403)

    return render(request, "cierre_turno/detail.html", {"cierre": cierre})



@login_required
def cierre_turno_edit(request, pk):
    cierre = get_object_or_404(CierreTurno, pk=pk)
    turno = cierre.turno  # ✅ importante: ahora existe siempre

    if request.user.role == "usuario" and cierre.usuario_id != request.user.id:
        return HttpResponse("No autorizado", status=403)

    # sincroniza solo zonas activas en ESTE cierre
    _sync_cierre_zonas_activo(cierre)

    # crea filas base de mov/pagos/denominaciones si faltan
    _seed_cierre_defaults(cierre)

    if request.method == "POST":
        form = CierreTurnoForm(request.POST, instance=cierre)
        zonas_fs = CierreTurnoZonaFormSet(request.POST, instance=cierre, prefix="zonas")
        mov_fs = CierreTurnoMovimientoFormSet(request.POST, instance=cierre, prefix="movimientos")
        pagos_fs = CierreTurnoPagoFormSet(request.POST, instance=cierre, prefix="pagos")
        den_fs = CierreTurnoDenFormSet(request.POST, instance=cierre, prefix="den")

        if form.is_valid() and zonas_fs.is_valid() and mov_fs.is_valid() and pagos_fs.is_valid() and den_fs.is_valid():
            with transaction.atomic():
                form.save()
                zonas_fs.save()
                mov_fs.save()
                pagos_fs.save()
                den_fs.save()

                _recalcular_totales_cierre(cierre)
                cierre.save()

                # ✅ cerrar turno si estaba abierto
                if (turno.estado or "").strip().lower() == "abierto":
                    total_lecturas = LecturaMaquina.objects.filter(turno=turno).aggregate(
                        total_sum=Sum("total")
                    )["total_sum"] or 0

                    turno.estado = "Cerrado"
                    turno.total_cierre = Decimal(str(total_lecturas))
                    turno.save(update_fields=["estado", "total_cierre"])

            messages.success(request, "Cierre de turno guardado y turno cerrado.")
            return redirect("control:turno")
        else:
            messages.error(request, "Hay errores en el formulario.")
    else:
        form = CierreTurnoForm(instance=cierre)
        zonas_fs = CierreTurnoZonaFormSet(instance=cierre, prefix="zonas")
        mov_fs = CierreTurnoMovimientoFormSet(instance=cierre, prefix="movimientos")
        pagos_fs = CierreTurnoPagoFormSet(instance=cierre, prefix="pagos")
        den_fs = CierreTurnoDenFormSet(instance=cierre, prefix="den")

    return render(
        request,
        "cuadratura/create_turno.html",
        {
            "turno": turno,
            "cierre": cierre,
            "form": form,
            "zonas_fs": zonas_fs,
            "mov_fs": mov_fs,
            "pagos_fs": pagos_fs,
            "den_fs": den_fs,
        },
    )


@login_required
@user_passes_test(is_admin, login_url="/login/")
def cierre_turno_delete(request, pk):
    cierre = get_object_or_404(CierreTurno, pk=pk)

    if request.method == "POST":
        cierre.delete()
        messages.success(request, "Cierre eliminado.")
        return redirect("control:cierre_turno_list")

    return render(request, "cierre_turno/delete.html", {"cierre": cierre})


@login_required
@user_passes_test(is_admin, login_url="/login/")
def cierre_turno_export_excel(request):
    qs = CierreTurno.objects.select_related("turno", "sucursal", "usuario").order_by("-fecha", "-creado_el")

    sucursal_id = request.GET.get("sucursal")
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    if sucursal_id:
        qs = qs.filter(sucursal_id=sucursal_id)
    if fecha_desde:
        qs = qs.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__lte=fecha_hasta)

    wb = Workbook()
    ws = wb.active
    ws.title = "Cierres de Turno"

    header_fill = PatternFill(start_color="111827", end_color="111827", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    headers = [
        "Fecha", "Sucursal", "Usuario", "Turno",
        "Caja base", "Retiro", "Total numeral", "Total gastos",
        "Esperado", "Contado", "Descuadre"
    ]

    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center")

    row = 2
    for x in qs:
        ws.cell(row=row, column=1, value=x.fecha.strftime("%d/%m/%Y") if x.fecha else "")
        ws.cell(row=row, column=2, value=x.sucursal.nombre if x.sucursal else "")
        ws.cell(row=row, column=3, value=getattr(x.usuario, "nombre", x.usuario.username) if x.usuario else "")
        ws.cell(row=row, column=4, value=getattr(x.turno, "tipo_turno", "") if x.turno else "")
        ws.cell(row=row, column=5, value=int(x.caja_base or 0))
        ws.cell(row=row, column=6, value=int(x.retiro_diario or 0))
        ws.cell(row=row, column=7, value=int(x.total_numeral or 0))
        ws.cell(row=row, column=8, value=int(x.total_gastos or 0))
        ws.cell(row=row, column=9, value=int(x.total_esperado or 0))
        ws.cell(row=row, column=10, value=int(x.total_efectivo_contado or 0))
        ws.cell(row=row, column=11, value=int(x.descuadre or 0))
        row += 1

    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                max_len = max(max_len, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = max_len + 2

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename=cierres_turno_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
    wb.save(response)
    return response


from .models import Zona, CierreTurnoZona

def _sync_cierre_zonas_activo(cierre):
    zonas_activas = (
        Zona.objects
        .filter(sucursal=cierre.sucursal, is_active=True)
        .order_by("orden", "nombre")
    )

    zonas_ids = {z.id for z in zonas_activas}

    # borrar del cierre las zonas que ya no están activas
    cierre.zonas.exclude(zona_id__in=zonas_ids).delete()

    # crear filas faltantes para zonas activas
    existentes = set(cierre.zonas.values_list("zona_id", flat=True))
    for z in zonas_activas:
        if z.id not in existentes:
            CierreTurnoZona.objects.create(
                cierre=cierre,
                zona=z,
                numeral=0,
                caja=0,
                prestamos=0,
                redbank=0,
                retiros=0,
                detalle_entregado_total=0,
                descuadre=0,
            )

def _ensure_billetes(cierre):
    billetes = [20000, 10000, 5000, 2000, 1000]
    for d in billetes:
        CierreTurnoDenominacion.objects.get_or_create(
            cierre=cierre,
            tipo="BILLETE",
            denominacion=d,
            defaults={"cantidad": 0}  # OJO: aquí "cantidad" la usas como MONTO ($), no cantidad de billetes
        )


@login_required
def generar_control(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id)

    # seguridad: atendedora del turno o admin
    if request.user.role == "usuario" and turno.usuario_id != request.user.id:
        return HttpResponse("No autorizado", status=403)

    lecturas = (LecturaMaquina.objects
        .filter(turno=turno)
        .select_related("maquina", "zona")
        .order_by("zona__orden", "zona__nombre", "numero_maquina")
    )

    total_entrada_dia = lecturas.aggregate(s=Sum("entrada_dia"))["s"] or 0
    total_salida_dia  = lecturas.aggregate(s=Sum("salida_dia"))["s"] or 0
    total_total       = lecturas.aggregate(s=Sum("total"))["s"] or 0

    return render(request, "control/control_generado.html", {
        "turno": turno,
        "lecturas": lecturas,
        "total_entrada_dia": total_entrada_dia,
        "total_salida_dia": total_salida_dia,
        "total_total": total_total,
    })

@login_required
def cerrar_turno_sin_cuadratura(request, turno_id):
    turno = get_object_or_404(Turno, pk=turno_id)

    # si quieres restringir:
    if request.user.role == "usuario" and turno.usuario_id != request.user.id:
        return HttpResponse("No autorizado", status=403)

    total_lecturas = LecturaMaquina.objects.filter(turno=turno).aggregate(
        s=Sum("total")
    )["s"] or 0

    Turno.objects.filter(id=turno.id).update(
        estado="Cerrado",
        total_cierre=Decimal(str(total_lecturas)),
    )

    messages.success(request, "Turno cerrado sin cuadratura.")
    return redirect("control:turno")


from .models import (
    Turno, LecturaMaquina, ControlLecturas, ControlLecturasLinea
)

@login_required
@transaction.atomic
def guardar_control(request, turno_id):
    if request.method != "POST":
        return redirect("control:generar_control", turno_id=turno_id)

    turno = get_object_or_404(Turno, id=turno_id)

    # OJO: ajusta si tu turno tiene estado/usuario
    if turno.usuario != request.user:
        messages.error(request, "No autorizado.")
        return redirect("control:dashboard")

    fecha = turno.fecha
    sucursal = turno.sucursal

    lecturas = (
        LecturaMaquina.objects
        .filter(turno=turno)
        .select_related("maquina", "zona")
        .order_by("zona__nombre", "numero_maquina", "id")
    )

    if not lecturas.exists():
        messages.error(request, "No hay lecturas para guardar control.")
        return redirect("control:generar_control", turno_id=turno_id)

    # upsert (si ya existe control del mismo día, lo reescribimos)
    control, created = ControlLecturas.objects.update_or_create(
        sucursal=sucursal,
        fecha_trabajo=fecha,
        defaults={
            "turno": turno,
            "creado_por": request.user,
        }
    )

    # borrar lineas anteriores (si era update)
    control.lineas.all().delete()

    bulk = []
    for lec in lecturas:
        servidor = ""
        if lec.maquina_id:
            # si agregaste servidor en Maquina
            servidor = getattr(lec.maquina, "servidor", "") or ""

        bulk.append(ControlLecturasLinea(
            control=control,
            zona=lec.zona,
            maquina=lec.maquina,
            numero_maquina=lec.numero_maquina,
            servidor=servidor,
            juego=lec.nombre_juego,
            entrada_historica=int(lec.entrada or 0),
            salida_historica=int(lec.salida or 0),
            entrada_parcial=int(lec.entrada_dia or 0),
            salida_parcial=int(lec.salida_dia or 0),
            total=int(lec.total or 0),
        ))

    ControlLecturasLinea.objects.bulk_create(bulk)

    total_general = control.lineas.aggregate(s=Sum("total"))["s"] or 0
    control.total_general = total_general
    control.save(update_fields=["total_general"])

    messages.success(request, "Control guardado correctamente.")
    return redirect("control:controles_detail", pk=control.pk)

@login_required
def controles_list(request):
    # si quieres filtrar por sucursal del usuario, aquí
    qs = (
        ControlLecturas.objects
        .select_related("sucursal", "turno", "creado_por")
        .order_by("-fecha_trabajo", "-id")
    )
    return render(request, "controles/list.html", {"controles": qs})


@login_required
def controles_detail(request, pk):
    control = (
        ControlLecturas.objects
        .select_related("sucursal", "turno")
        .prefetch_related("lineas")
        .get(pk=pk)
    )
    lineas = control.lineas.select_related("zona", "maquina").all()
    return render(request, "controles/detail.html", {"control": control, "lineas": lineas})