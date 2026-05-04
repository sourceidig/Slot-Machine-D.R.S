from datetime import timedelta
from .models import (
    ControlLecturas, ControlLecturasLinea,
    LecturaMaquina, CicloRecaudacion, CuadraturaCajaDiaria
)

def get_referencia_anterior(maquina, fecha_trabajo, exclude_turno_id=None):
    ciclo = getattr(maquina.sucursal, "ciclo_recaudacion", None)

    if ciclo and fecha_trabajo == ciclo.inicio_ciclo:
        return maquina.contador_inicial_entrada, maquina.contador_inicial_salida, "contador_inicial"

    # 1. Lectura del mismo día de un turno anterior (tarde toma mañana como ref.)
    #    Esto es correcto: dentro del mismo día sí usamos LecturaMaquina
    qs_same = LecturaMaquina.objects.filter(maquina=maquina, fecha_trabajo=fecha_trabajo)
    if exclude_turno_id:
        qs_same = qs_same.exclude(turno_id=exclude_turno_id)
    same_day = qs_same.order_by("-id").first()
    if same_day:
        return same_day.entrada, same_day.salida, "turno_anterior_mismo_dia"

    # 2. Último ControlLecturas guardado antes de esta fecha
    #    (antes era solo "ayer", ahora busca el más reciente disponible)
    control_anterior = (
        ControlLecturas.objects
        .filter(sucursal=maquina.sucursal, fecha_trabajo__lt=fecha_trabajo)
        .order_by("-fecha_trabajo", "-id")
        .first()
    )
    if control_anterior:
        linea = (
            ControlLecturasLinea.objects
            .filter(control=control_anterior, maquina=maquina)
            .first()
        )
        if linea:
            return linea.entrada_historica, linea.salida_historica, "control_anterior"

    # 3. Fallback: contador inicial de la máquina
    #    (se eliminó el paso que buscaba LecturaMaquina de días anteriores)
    return maquina.contador_inicial_entrada, maquina.contador_inicial_salida, "contador_inicial"


def calcular_numerales_caja(sucursal, fecha):
    # 1) Sumar todos los controles del día (puede haber varios turnos)
    from django.db.models import Sum
    numeral_dia = int(
        ControlLecturas.objects.filter(sucursal=sucursal, fecha_trabajo=fecha)
        .aggregate(s=Sum("total_general"))["s"] or 0
    )

    # 2) Determinar inicio del ciclo actual
    inicio_ciclo = get_inicio_ciclo(sucursal)

    # Si la fecha pedida ES el inicio del ciclo (primer día del nuevo ciclo),
    # no hay acumulado previo: el numeral_acumulado es solo el del día.
    if inicio_ciclo and fecha <= inicio_ciclo:
        return numeral_dia, numeral_dia

    # 3) Buscar la última cuadratura anterior DENTRO del ciclo
    qs = CuadraturaCajaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__lt=fecha
    )
    if inicio_ciclo:
        qs = qs.filter(fecha__gte=inicio_ciclo)

    anterior = qs.order_by("-fecha", "-id").first()

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