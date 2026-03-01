from datetime import timedelta
from .models import (
    ControlLecturas, ControlLecturasLinea,
    LecturaMaquina, CicloRecaudacion, CuadraturaCajaDiaria
)

def get_referencia_anterior(maquina, fecha_trabajo):
    ciclo = getattr(maquina.sucursal, "ciclo_recaudacion", None)

    if ciclo and fecha_trabajo == ciclo.inicio_ciclo:
        return maquina.contador_inicial_entrada, maquina.contador_inicial_salida, "contador_inicial"

    ayer = fecha_trabajo - timedelta(days=1)
    control_ayer = (
        ControlLecturas.objects
        .filter(sucursal=maquina.sucursal, fecha_trabajo=ayer)
        .order_by("-id")
        .first()
    )
    if control_ayer:
        linea = (
            ControlLecturasLinea.objects
            .filter(control=control_ayer, maquina=maquina)
            .first()
        )
        if linea:
            return linea.entrada_historica, linea.salida_historica, "control_ayer"

    qs = LecturaMaquina.objects.filter(maquina=maquina, fecha_trabajo__lt=fecha_trabajo)
    if ciclo:
        qs = qs.filter(fecha_trabajo__gte=ciclo.inicio_ciclo)

    prev = qs.order_by("-fecha_trabajo", "-id").first()
    if prev:
        return prev.entrada, prev.salida, "lectura_anterior"

    return maquina.contador_inicial_entrada, maquina.contador_inicial_salida, "contador_inicial"


def calcular_numerales_caja(sucursal, fecha):
    # 1) Buscar ControlLecturas del día
    control = ControlLecturas.objects.filter(
        sucursal=sucursal,
        fecha_trabajo=fecha
    ).first()

    # Si hay lectura, usa total_general (conversión segura)
    numeral_dia = int(control.total_general or 0) if control else 0

    # 2) Buscar última cuadratura anterior
    anterior = CuadraturaCajaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__lt=fecha
    ).order_by("-fecha", "-id").first()

    numeral_acumulado = numeral_dia
    if anterior:
        numeral_acumulado += int(anterior.numeral_acumulado or 0)

    return numeral_dia, numeral_acumulado


def get_inicio_ciclo(sucursal):
    try:
        ciclo = CicloRecaudacion.objects.get(sucursal=sucursal)
        return ciclo.inicio_ciclo
    except CicloRecaudacion.DoesNotExist:
        return None


def get_caja_anterior_en_ciclo(sucursal, fecha):
    """
    Última CuadraturaCajaDiaria antes de 'fecha' y desde inicio_ciclo (si existe).
    Si no hay ninguna, usar caja_inicial de la sucursal.
    """
    inicio = get_inicio_ciclo(sucursal)

    qs = CuadraturaCajaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__lt=fecha
    ).order_by("-fecha", "-creado_el")

    if inicio:
        qs = qs.filter(fecha__gte=inicio)

    cuadratura = qs.first()

    if cuadratura:
        return cuadratura
    else:
        # Dummy fallback
        class DummyCuadratura:
            caja_total = 0
            desglose_efectivo_total = 0  
            numeral_dia = 0
            redbank_dia = 0
            transfer_dia = 0
            prestamos = 0
            sorteos_dia = 0
            gastos_dia = 0
            sueldo_b_dia = 0
            regalos_dia = 0
            jugados_dia = 0

        return DummyCuadratura()


def es_dia_1_del_ciclo(sucursal, fecha):
    """
    Devuelve True si no hay cuadraturas anteriores en el ciclo.
    """
    inicio = get_inicio_ciclo(sucursal)
    qs = CuadraturaCajaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__lt=fecha
    )
    if inicio:
        qs = qs.filter(fecha__gte=inicio)

    return not qs.exists()