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


def calcular_numerales_caja(sucursal, fecha, exclude_pk=None):
    from django.db.models import Sum
    
    # 1) Sumar todos los controles del día (puede haber varios turnos)
    numeral_dia = int(
        ControlLecturas.objects.filter(sucursal=sucursal, fecha_trabajo=fecha)
        .aggregate(s=Sum("total_general"))["s"] or 0
    )

    # 2) Determinar inicio del ciclo actual
    inicio_ciclo = get_inicio_ciclo(sucursal)

    # 3) Buscar la última cuadratura anterior DENTRO del ciclo
    # ✅ FIX: Usar __lte para incluir cajas de turnos anteriores del MISMO DÍA
    qs = CuadraturaCajaDiaria.objects.filter(
        sucursal=sucursal,
        fecha__lte=fecha
    ).order_by("-fecha", "-creado_el")
    
    if inicio_ciclo:
        qs = qs.filter(fecha__gte=inicio_ciclo)
        
    # ✅ FIX: Excluir la caja actual para que no se sume a sí misma
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    anterior = qs.first()

    # Si es el primer día del ciclo y no hay nada anterior
    if not anterior and inicio_ciclo and fecha <= inicio_ciclo:
        return numeral_dia, numeral_dia

    numeral_acumulado = numeral_dia
    
    # ✅ FIX: Lógica para sumar sin duplicar si hay varias cajas el mismo día
    if anterior:
        if anterior.fecha == fecha:
            # Si la caja anterior es de HOY, tomamos el acumulado que venía de ayer 
            # y le sumamos el total de hoy.
            acumulado_ayer = int(anterior.numeral_acumulado or 0) - int(anterior.numeral_dia or 0)
            numeral_acumulado = acumulado_ayer + numeral_dia
        else:
            # Si la caja es de ayer o antes, sumamos directo
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