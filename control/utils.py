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


# control/utils.py

def calcular_numerales_caja(sucursal, fecha, turno_tipo=None, exclude_pk=None):
    from django.db.models import Sum, Q
    
    # 1) Definir el orden lógico de los turnos para cálculos acumulativos dentro del día
    # Asumimos este orden por defecto, si usas otros nombres en BD debes cambiarlos aquí.
    ORDEN_TURNOS = {
        "Mañana": 1,
        "Tarde": 2,
        "Noche": 3,
    }
    
    # Obtener el orden numérico del turno actual que estamos calculando en el formulario
    orden_actual = ORDEN_TURNOS.get(turno_tipo, 1) # Si no se pasa turno, asumimos Mañana

    # 2) Numeral del Día: Es el numeral ESPECÍFICO del control del turno actual.
    # Viendo image_3.png, el usuario quiere el total de SU control (142), no la suma del día.
    numeral_dia_query = ControlLecturas.objects.filter(
        sucursal=sucursal,
        fecha_trabajo=fecha,
        turno__tipo_turno=turno_tipo # Filtramos estrictamente por el turno del formulario
    )
    
    numeral_dia = int(numeral_dia_query.aggregate(s=Sum("total_general"))["s"] or 0)

    # 3) Determinar inicio del ciclo actual de recaudación
    inicio_ciclo = get_inicio_ciclo(sucursal)

    # Si es el primer día del ciclo (Día 0) y el primer turno (Mañana),
    # no hay acumulado previo: el numeral_acumulado es solo el del día actual.
    if inicio_ciclo and fecha <= inicio_ciclo and orden_actual == 1:
        return numeral_dia, numeral_dia

    # 4) Buscar la última cuadratura anterior DENTRO del ciclo para el acumulado
    # Esta búsqueda es compleja porque puede ser del turno anterior de hoy, o de ayer.
    
    # Construimos filtros avanzados para buscar cuadraturas previas en orden cronológico inverso
    query_anterior = Q(sucursal=sucursal)
    
    filtros_fecha = Q(fecha__lt=fecha) # Buscar en días anteriores
    
    if turno_tipo in ORDEN_TURNOS:
        # Si es Tarde o Noche, también buscar en cuadraturas de HOY que tengan turnos anteriores
        turnos_anteriores_hoy = [t for t, ord in ORDEN_TURNOS.items() if ord < orden_actual]
        if turnos_anteriores_hoy:
            filtros_fecha |= Q(fecha=fecha, turno__tipo_turno__in=turnos_anteriores_hoy)

    query_anterior &= filtros_fecha
    
    if inicio_ciclo:
        query_anterior &= Q(fecha__gte=inicio_ciclo) # No buscar antes del inicio del ciclo

    # Realizamos la búsqueda
    qs_anterior = CuadraturaCajaDiaria.objects.filter(query_anterior).order_by("-fecha", "-creado_el")
    
    # Excluimos la propia caja si la estamos editando para evitar cálculos circulares
    if exclude_pk:
        qs_anterior = qs_anterior.exclude(pk=exclude_pk)

    anterior = qs_anterior.first()

    # 5) Calcular Numeral Acumulado
    # Se calcula sumando el Numeral Acumulado de la caja anterior + el Numeral del Día actual.
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