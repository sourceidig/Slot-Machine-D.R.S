import base64
import datetime
import io
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from PIL import Image

from .models import (
    CicloRecaudacion,
    ControlLecturas,
    ControlLecturasLinea,
    CuadraturaCajaDiaria,
    InformeRecaudacion,
    InformeRecaudacionLinea,
    LecturaMaquina,
    Maquina,
    RegistroActividad,
    RegistroSesion,
    Sucursal,
    Turno,
    Usuario,
    Zona,
)
from .utils import (
    calcular_numerales_caja,
    es_dia_1_del_ciclo,
    get_caja_anterior_en_ciclo,
    get_inicio_ciclo,
    get_referencia_anterior,
)
from .forms import (
    CuadraturaCajaDiariaForm,
    LecturaMaquinaForm,
    MaquinaForm,
    UsuarioForm,
)


# ─────────────────────────────────────────────
# Factories
# ─────────────────────────────────────────────

def make_sucursal(nombre="Sucursal Test"):
    return Sucursal.objects.create(nombre=nombre)


def make_zona(sucursal, nombre="Zona A"):
    return Zona.objects.create(sucursal=sucursal, nombre=nombre)


def make_usuario(username="tuser"):
    return Usuario.objects.create_user(
        username=username, password="test1234", nombre="Test User"
    )


def make_maquina(sucursal, zona, numero=1, contador_entrada=0, contador_salida=0):
    return Maquina.objects.create(
        sucursal=sucursal,
        zona=zona,
        numero_maquina=numero,
        nombre_juego="Juego Test",
        contador_inicial_entrada=contador_entrada,
        contador_inicial_salida=contador_salida,
    )


def make_turno(sucursal, usuario, fecha=None, estado="Abierto", tipo="Mañana"):
    if fecha is None:
        fecha = datetime.date(2025, 1, 15)
    return Turno.objects.create(
        sucursal=sucursal,
        usuario=usuario,
        fecha=fecha,
        tipo_turno=tipo,
        estado=estado,
    )


def make_lectura(turno, maquina, usuario, entrada, salida):
    """
    Crea una LecturaMaquina. sucursal, zona, numero_maquina y nombre_juego
    son inyectados por LecturaMaquina.save() desde la máquina; total=0 es
    un placeholder que también sobreescribe save().
    """
    return LecturaMaquina.objects.create(
        turno=turno,
        maquina=maquina,
        usuario=usuario,
        entrada=entrada,
        salida=salida,
        total=0,
    )


# ─────────────────────────────────────────────
# LecturaMaquina.save() — cálculos
# ─────────────────────────────────────────────

class LecturaMaquinaCalculosTest(TestCase):
    """
    Verifica que save() calcule correctamente entrada_dia, salida_dia,
    total y el RTP que se escribe en Maquina.rtp_objetivo.

    Para una máquina sin lecturas previas y sin CicloRecaudacion,
    get_referencia_anterior() devuelve (contador_inicial_entrada,
    contador_inicial_salida), por lo que los valores iniciales son
    predecibles.
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.zona = make_zona(self.sucursal)
        self.usuario = make_usuario()
        self.turno = make_turno(self.sucursal, self.usuario)

    # ------------------------------------------------------------------
    # Parciales (entrada_dia, salida_dia, total)
    # ------------------------------------------------------------------

    def test_parciales_calculados_desde_contador_inicial(self):
        """
        Caso base: máquina sin lecturas previas.
        Los parciales se calculan restando el contador_inicial.
        """
        maquina = make_maquina(
            self.sucursal, self.zona,
            contador_entrada=1_000,
            contador_salida=800,
        )
        lectura = make_lectura(self.turno, maquina, self.usuario,
                               entrada=1_500, salida=1_200)

        self.assertEqual(lectura.entrada_anterior, 1_000)
        self.assertEqual(lectura.salida_anterior, 800)
        self.assertEqual(lectura.entrada_dia, 500)   # 1500 - 1000
        self.assertEqual(lectura.salida_dia, 400)    # 1200 - 800
        self.assertEqual(lectura.total, 100)          # 500  - 400

    def test_total_puede_ser_negativo(self):
        """Si salida_dia > entrada_dia el total es negativo (pérdida)."""
        maquina = make_maquina(self.sucursal, self.zona,
                               contador_entrada=1_000, contador_salida=800)
        lectura = make_lectura(self.turno, maquina, self.usuario,
                               entrada=1_100, salida=1_100)

        self.assertEqual(lectura.entrada_dia, 100)
        self.assertEqual(lectura.salida_dia, 300)
        self.assertEqual(lectura.total, -200)

    def test_parciales_cero_cuando_contadores_no_cambian(self):
        """Entrada y salida igual al contador_inicial → parciales = 0."""
        maquina = make_maquina(self.sucursal, self.zona,
                               contador_entrada=500, contador_salida=300)
        lectura = make_lectura(self.turno, maquina, self.usuario,
                               entrada=500, salida=300)

        self.assertEqual(lectura.entrada_dia, 0)
        self.assertEqual(lectura.salida_dia, 0)
        self.assertEqual(lectura.total, 0)

    # ------------------------------------------------------------------
    # RTP en Maquina.rtp_objetivo
    # ------------------------------------------------------------------

    def test_rtp_actualizado_en_maquina(self):
        """
        Cuando entrada_dia > 0, save() actualiza Maquina.rtp_objetivo
        con (entrada_dia - salida_dia) / entrada_dia * 100 redondeado a 2 decimales.
        """
        maquina = make_maquina(self.sucursal, self.zona,
                               contador_entrada=1_000, contador_salida=800)
        make_lectura(self.turno, maquina, self.usuario,
                     entrada=1_500, salida=1_200)
        # entrada_dia=500, salida_dia=400  →  rtp = (500-400)/500*100 = 20.00

        maquina.refresh_from_db()
        self.assertEqual(maquina.rtp_objetivo, Decimal("20.00"))

    def test_rtp_no_se_actualiza_cuando_entrada_dia_es_cero(self):
        """
        Si entrada == contador_inicial (entrada_dia = 0), no se debe
        actualizar rtp_objetivo (evita división por cero).
        """
        maquina = make_maquina(self.sucursal, self.zona,
                               contador_entrada=1_000, contador_salida=800)
        self.assertIsNone(maquina.rtp_objetivo)

        make_lectura(self.turno, maquina, self.usuario,
                     entrada=1_000, salida=900)
        # entrada_dia = 0  →  skip RTP update

        maquina.refresh_from_db()
        self.assertIsNone(maquina.rtp_objetivo)

    # ------------------------------------------------------------------
    # Edición (update): totales se recalculan sobre los anteriores guardados
    # ------------------------------------------------------------------

    def test_editar_lectura_recalcula_totales_con_anteriores_guardados(self):
        """
        Al editar, entrada_anterior y salida_anterior NO se modifican;
        entrada_dia, salida_dia y total sí se recalculan.
        """
        maquina = make_maquina(self.sucursal, self.zona,
                               contador_entrada=1_000, contador_salida=800)
        lectura = make_lectura(self.turno, maquina, self.usuario,
                               entrada=1_500, salida=1_200)

        # Editar: aumentar entrada y salida
        lectura.entrada = 2_000
        lectura.salida = 1_600
        lectura.save()

        self.assertEqual(lectura.entrada_anterior, 1_000)  # sin cambios
        self.assertEqual(lectura.salida_anterior, 800)     # sin cambios
        self.assertEqual(lectura.entrada_dia, 1_000)       # 2000 - 1000
        self.assertEqual(lectura.salida_dia, 800)          # 1600 - 800
        self.assertEqual(lectura.total, 200)               # 1000 - 800

    # ------------------------------------------------------------------
    # fecha_trabajo se hereda del turno
    # ------------------------------------------------------------------

    def test_fecha_trabajo_se_toma_del_turno(self):
        """Si no se pasa fecha_trabajo, save() la toma de turno.fecha."""
        maquina = make_maquina(self.sucursal, self.zona)
        lectura = make_lectura(self.turno, maquina, self.usuario,
                               entrada=100, salida=80)

        self.assertEqual(lectura.fecha_trabajo, self.turno.fecha)


# ─────────────────────────────────────────────
# LecturaMaquina — unique constraint
# ─────────────────────────────────────────────

class LecturaMaquinaUniqueConstraintTest(TestCase):
    """
    Valida la constraint uniq_lectura_maquina_por_turno:
    solo puede existir una lectura por (turno, maquina).
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.zona = make_zona(self.sucursal)
        self.usuario = make_usuario()
        self.turno = make_turno(self.sucursal, self.usuario)
        self.maquina = make_maquina(self.sucursal, self.zona, numero=1)

    def test_segunda_lectura_misma_maquina_mismo_turno_viola_constraint(self):
        """Duplicado en (turno, maquina) debe lanzar IntegrityError."""
        make_lectura(self.turno, self.maquina, self.usuario,
                     entrada=1_000, salida=800)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_lectura(self.turno, self.maquina, self.usuario,
                             entrada=1_100, salida=900)

    def test_lectura_misma_maquina_diferente_turno_es_valida(self):
        """
        Misma máquina en un turno distinto (con otro usuario para cumplir
        la validación de turno único abierto por usuario) no viola la constraint.
        """
        make_lectura(self.turno, self.maquina, self.usuario,
                     entrada=1_000, salida=800)

        usuario2 = make_usuario(username="tuser2")
        turno2 = make_turno(self.sucursal, usuario2)

        # No debe lanzar ninguna excepción
        lectura2 = make_lectura(turno2, self.maquina, usuario2,
                                entrada=1_100, salida=900)
        self.assertIsNotNone(lectura2.pk)

    def test_lectura_diferente_maquina_mismo_turno_es_valida(self):
        """Diferente máquina en el mismo turno no viola la constraint."""
        make_lectura(self.turno, self.maquina, self.usuario,
                     entrada=1_000, salida=800)

        maquina2 = make_maquina(self.sucursal, self.zona, numero=2)
        lectura2 = make_lectura(self.turno, maquina2, self.usuario,
                                entrada=500, salida=400)
        self.assertIsNotNone(lectura2.pk)


# ─────────────────────────────────────────────
# RegistroSesion.duracion
# ─────────────────────────────────────────────

class RegistroSesionDuracionTest(TestCase):
    """
    La property duracion formatea el tiempo transcurrido como HH:MM:SS,
    o devuelve '—' si la sesión sigue activa (hora_cierre es None).

    Las instancias no necesitan guardarse en BD ya que duracion solo
    accede a hora_inicio y hora_cierre.
    """

    UTC = datetime.timezone.utc
    BASE = datetime.datetime(2025, 1, 15, 10, 0, 0, tzinfo=datetime.timezone.utc)

    def _sesion(self, hora_cierre_offset_segundos=None):
        sesion = RegistroSesion()
        sesion.hora_inicio = self.BASE
        if hora_cierre_offset_segundos is not None:
            sesion.hora_cierre = self.BASE + datetime.timedelta(
                seconds=hora_cierre_offset_segundos
            )
        else:
            sesion.hora_cierre = None
        return sesion

    def test_duracion_sesion_activa_retorna_guion(self):
        """hora_cierre=None → sesión activa → '—'."""
        self.assertEqual(self._sesion().duracion, "—")

    def test_duracion_30_minutos(self):
        self.assertEqual(self._sesion(30 * 60).duracion, "00:30:00")

    def test_duracion_exactamente_1_hora(self):
        self.assertEqual(self._sesion(3600).duracion, "01:00:00")

    def test_duracion_horas_minutos_segundos(self):
        offset = 2 * 3600 + 15 * 60 + 30   # 2h 15m 30s
        self.assertEqual(self._sesion(offset).duracion, "02:15:30")

    def test_duracion_segundos_completos_sin_minutos(self):
        self.assertEqual(self._sesion(45).duracion, "00:00:45")


# ─────────────────────────────────────────────
# Turno — un turno abierto por usuario
# ─────────────────────────────────────────────

class TurnoUnicoAbiertoPorUsuarioTest(TestCase):
    """
    Turno.clean() impide que un usuario tenga más de un turno abierto
    simultáneamente. La validación NO ocurre en save(); hay que llamar
    explícitamente a clean() o full_clean().
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.usuario = make_usuario()

    def test_segundo_turno_abierto_mismo_usuario_lanza_validation_error(self):
        """Abrir un segundo turno para el mismo usuario debe fallar."""
        make_turno(self.sucursal, self.usuario, estado="Abierto")

        turno2 = Turno(
            sucursal=self.sucursal,
            usuario=self.usuario,
            fecha=datetime.date(2025, 1, 16),
            tipo_turno="Tarde",
            estado="Abierto",
        )
        with self.assertRaises(ValidationError):
            turno2.clean()

    def test_turno_cerrado_no_bloquea_nuevo_turno_abierto(self):
        """Un turno previo cerrado no impide abrir uno nuevo."""
        make_turno(self.sucursal, self.usuario, estado="Cerrado")

        turno2 = Turno(
            sucursal=self.sucursal,
            usuario=self.usuario,
            fecha=datetime.date(2025, 1, 16),
            tipo_turno="Tarde",
            estado="Abierto",
        )
        # No debe lanzar excepción
        turno2.clean()

    def test_usuarios_distintos_pueden_tener_turnos_abiertos_simultaneamente(self):
        """Dos usuarios diferentes pueden tener cada uno un turno abierto."""
        usuario2 = make_usuario(username="tuser2")
        make_turno(self.sucursal, self.usuario, estado="Abierto")

        turno2 = Turno(
            sucursal=self.sucursal,
            usuario=usuario2,
            fecha=datetime.date(2025, 1, 15),
            tipo_turno="Mañana",
            estado="Abierto",
        )
        # No debe lanzar excepción
        turno2.clean()

    def test_editar_turno_abierto_no_lanza_error(self):
        """
        Editar el propio turno abierto (mismo pk) no debe detectarse
        como duplicado (clean() excluye self.pk del queryset).
        """
        turno = make_turno(self.sucursal, self.usuario, estado="Abierto")
        turno.observaciones = "editado"
        # No debe lanzar excepción
        turno.clean()


# ─────────────────────────────────────────────
# Fechas fijas usadas en los tests de utils
# ─────────────────────────────────────────────
DATE_CURR  = datetime.date(2025, 6, 15)
DATE_PREV  = datetime.date(2025, 6, 14)   # ayer respecto a DATE_CURR
DATE_PREV2 = datetime.date(2025, 6, 13)   # anteayer


# ─────────────────────────────────────────────
# get_referencia_anterior()
# ─────────────────────────────────────────────

class GetReferenciaAnteriorTest(TestCase):
    """
    get_referencia_anterior(maquina, fecha_trabajo) resuelve de qué fuente
    tomar los contadores de referencia:
      1. Si fecha_trabajo == inicio_ciclo  → contador_inicial
      2. Si hay ControlLecturasLinea de ayer → control_ayer
      3. Si hay LecturaMaquina previa (dentro del ciclo) → lectura_anterior
      4. Fallback → contador_inicial
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.zona = make_zona(self.sucursal)
        self.usuario = make_usuario()
        # Máquina con contadores iniciales conocidos
        self.maquina = make_maquina(
            self.sucursal, self.zona,
            contador_entrada=1_000,
            contador_salida=800,
        )

    # -- caso 1: sin ningún historial ----------------------------------------

    def test_sin_historial_usa_contador_inicial(self):
        """Sin ciclo, sin control, sin lecturas previas → fallback contador_inicial."""
        entrada, salida, fuente = get_referencia_anterior(self.maquina, DATE_CURR)

        self.assertEqual(entrada, 1_000)
        self.assertEqual(salida, 800)
        self.assertEqual(fuente, "contador_inicial")

    # -- caso 2: fecha coincide con inicio del ciclo -------------------------

    def test_fecha_es_inicio_ciclo_usa_contador_inicial(self):
        """
        Si fecha_trabajo == ciclo.inicio_ciclo, la función hace bypass
        inmediato al contador_inicial, sin consultar controles ni lecturas.
        """
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=DATE_CURR,
            creado_por=self.usuario,
        )
        # Crear una lectura previa que debería ser ignorada
        usuario2 = make_usuario(username="setup_user")
        turno_prev = make_turno(self.sucursal, usuario2, fecha=DATE_PREV)
        make_lectura(turno_prev, self.maquina, usuario2, entrada=9_000, salida=8_000)

        entrada, salida, fuente = get_referencia_anterior(self.maquina, DATE_CURR)

        self.assertEqual(entrada, 1_000)
        self.assertEqual(salida, 800)
        self.assertEqual(fuente, "contador_inicial")

    # -- caso 3: control de ayer con línea para la máquina -------------------

    def test_control_de_ayer_con_linea_usa_control_ayer(self):
        """
        Existe ControlLecturas de ayer con ControlLecturasLinea para
        esta máquina → retorna los valores históricos de esa línea.
        """
        control = ControlLecturas.objects.create(
            sucursal=self.sucursal,
            fecha_trabajo=DATE_PREV,   # ayer respecto a DATE_CURR
            total_general=0,
        )
        ControlLecturasLinea.objects.create(
            control=control,
            maquina=self.maquina,
            numero_maquina=self.maquina.numero_maquina,
            entrada_historica=2_000,
            salida_historica=1_500,
        )

        entrada, salida, fuente = get_referencia_anterior(self.maquina, DATE_CURR)

        self.assertEqual(entrada, 2_000)
        self.assertEqual(salida, 1_500)
        self.assertEqual(fuente, "control_ayer")

    # -- caso 4: control de ayer existe pero sin línea → cae a lectura -------

    def test_control_de_ayer_sin_linea_cae_a_lectura_anterior(self):
        """
        Hay ControlLecturas de ayer pero sin ControlLecturasLinea para
        esta máquina. La función cae al siguiente nivel: lectura_anterior.
        """
        # Control de ayer sin línea para self.maquina
        ControlLecturas.objects.create(
            sucursal=self.sucursal,
            fecha_trabajo=DATE_PREV,
            total_general=0,
        )
        # Lectura previa en anteayer
        usuario2 = make_usuario(username="setup_user")
        turno_prev = make_turno(self.sucursal, usuario2, fecha=DATE_PREV2)
        lectura_prev = make_lectura(turno_prev, self.maquina, usuario2,
                                    entrada=3_000, salida=2_500)

        entrada, salida, fuente = get_referencia_anterior(self.maquina, DATE_CURR)

        self.assertEqual(entrada, lectura_prev.entrada)
        self.assertEqual(salida, lectura_prev.salida)
        self.assertEqual(fuente, "lectura_anterior")

    # -- caso 5: lectura anterior sin control --------------------------------

    def test_lectura_anterior_sin_control(self):
        """
        Sin ControlLecturas de ayer, pero existe una LecturaMaquina en
        una fecha anterior → retorna los valores de esa lectura.
        """
        usuario2 = make_usuario(username="setup_user")
        turno_prev = make_turno(self.sucursal, usuario2, fecha=DATE_PREV)
        lectura_prev = make_lectura(turno_prev, self.maquina, usuario2,
                                    entrada=5_000, salida=4_200)

        entrada, salida, fuente = get_referencia_anterior(self.maquina, DATE_CURR)

        self.assertEqual(entrada, lectura_prev.entrada)
        self.assertEqual(salida, lectura_prev.salida)
        self.assertEqual(fuente, "lectura_anterior")

    # -- caso 6: lectura anterior fuera del ciclo → ignorada -----------------

    def test_lectura_fuera_del_ciclo_es_ignorada(self):
        """
        El ciclo empezó hace 5 días. Una lectura de hace 10 días (anterior
        al ciclo) queda fuera del filtro fecha_trabajo__gte=inicio_ciclo
        y la función vuelve al contador_inicial.
        """
        inicio_ciclo = DATE_CURR - datetime.timedelta(days=5)
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=inicio_ciclo,
            creado_por=self.usuario,
        )
        fecha_antes_ciclo = DATE_CURR - datetime.timedelta(days=10)
        usuario2 = make_usuario(username="setup_user")
        turno_prev = make_turno(self.sucursal, usuario2, fecha=fecha_antes_ciclo)
        make_lectura(turno_prev, self.maquina, usuario2, entrada=9_000, salida=7_000)

        entrada, salida, fuente = get_referencia_anterior(self.maquina, DATE_CURR)

        self.assertEqual(entrada, 1_000)
        self.assertEqual(salida, 800)
        self.assertEqual(fuente, "contador_inicial")


# ─────────────────────────────────────────────
# calcular_numerales_caja()
# ─────────────────────────────────────────────

class CalcularNumeralesCajaTest(TestCase):
    """
    calcular_numerales_caja(sucursal, fecha) devuelve (numeral_dia, numeral_acumulado).
    numeral_dia    = total_general del ControlLecturas del día (0 si no existe).
    numeral_acumulado = numeral_dia + numeral_acumulado de la última
                        CuadraturaCajaDiaria anterior dentro del ciclo.
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def _make_control(self, fecha, total):
        return ControlLecturas.objects.create(
            sucursal=self.sucursal,
            fecha_trabajo=fecha,
            total_general=total,
        )

    def _make_cuadratura(self, fecha, numeral_acumulado):
        return CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=fecha,
            numeral_acumulado=numeral_acumulado,
        )

    def test_sin_control_ni_cuadratura_retorna_ceros(self):
        """Sin ningún dato → (0, 0)."""
        dia, acum = calcular_numerales_caja(self.sucursal, DATE_CURR)
        self.assertEqual(dia, 0)
        self.assertEqual(acum, 0)

    def test_solo_control_sin_cuadratura_previa(self):
        """Solo hay control del día, sin cuadratura anterior → acumulado = dia."""
        self._make_control(DATE_CURR, 5_000)

        dia, acum = calcular_numerales_caja(self.sucursal, DATE_CURR)

        self.assertEqual(dia, 5_000)
        self.assertEqual(acum, 5_000)

    def test_control_mas_cuadratura_previa_acumula(self):
        """
        Control del día (5 000) + cuadratura anterior con
        numeral_acumulado=20 000 → acumulado = 25 000.
        """
        self._make_control(DATE_CURR, 5_000)
        self._make_cuadratura(DATE_PREV, numeral_acumulado=20_000)

        dia, acum = calcular_numerales_caja(self.sucursal, DATE_CURR)

        self.assertEqual(dia, 5_000)
        self.assertEqual(acum, 25_000)

    def test_fecha_es_inicio_ciclo_retorna_solo_dia(self):
        """
        Cuando fecha == inicio_ciclo la función cortocircuita y devuelve
        (numeral_dia, numeral_dia), ignorando cualquier cuadratura previa.
        """
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=DATE_CURR,
        )
        self._make_control(DATE_CURR, 3_000)
        # Cuadratura previa que NO debe sumarse
        self._make_cuadratura(DATE_PREV, numeral_acumulado=10_000)

        dia, acum = calcular_numerales_caja(self.sucursal, DATE_CURR)

        self.assertEqual(dia, 3_000)
        self.assertEqual(acum, 3_000)

    def test_cuadratura_antes_del_ciclo_es_ignorada(self):
        """
        El ciclo empezó hace 3 días. Una cuadratura de hace 5 días queda
        fuera del filtro fecha__gte=inicio_ciclo y no se suma al acumulado.
        """
        inicio = DATE_CURR - datetime.timedelta(days=3)
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=inicio,
        )
        self._make_control(DATE_CURR, 4_000)
        # Cuadratura fuera del ciclo (5 días atrás, antes del inicio)
        self._make_cuadratura(DATE_CURR - datetime.timedelta(days=5),
                              numeral_acumulado=99_000)

        dia, acum = calcular_numerales_caja(self.sucursal, DATE_CURR)

        self.assertEqual(dia, 4_000)
        self.assertEqual(acum, 4_000)


# ─────────────────────────────────────────────
# es_dia_1_del_ciclo()
# ─────────────────────────────────────────────

class EsDia1DelCicloTest(TestCase):
    """
    es_dia_1_del_ciclo(sucursal, fecha) devuelve True cuando no existen
    CuadraturaCajaDiaria anteriores a 'fecha' dentro del ciclo activo.
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def _make_cuadratura(self, fecha):
        return CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=fecha,
        )

    def test_sin_cuadraturas_es_dia_1(self):
        """Sin ninguna cuadratura previa → True."""
        self.assertTrue(es_dia_1_del_ciclo(self.sucursal, DATE_CURR))

    def test_con_cuadratura_previa_sin_ciclo_no_es_dia_1(self):
        """Cuadratura en fecha anterior, sin ciclo → False."""
        self._make_cuadratura(DATE_PREV)
        self.assertFalse(es_dia_1_del_ciclo(self.sucursal, DATE_CURR))

    def test_con_ciclo_y_cuadratura_dentro_del_ciclo_no_es_dia_1(self):
        """Ciclo activo + cuadratura después del inicio_ciclo → False."""
        inicio = DATE_CURR - datetime.timedelta(days=10)
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=inicio,
        )
        # Cuadratura dentro del ciclo (hace 2 días, posterior al inicio)
        self._make_cuadratura(DATE_CURR - datetime.timedelta(days=2))

        self.assertFalse(es_dia_1_del_ciclo(self.sucursal, DATE_CURR))

    def test_con_ciclo_y_cuadratura_antes_del_ciclo_es_dia_1(self):
        """
        Ciclo activo + cuadratura ANTES del inicio_ciclo.
        El filtro fecha__gte=inicio_ciclo la excluye → True.
        """
        inicio = DATE_CURR - datetime.timedelta(days=3)
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=inicio,
        )
        # Cuadratura anterior al ciclo (5 días atrás)
        self._make_cuadratura(DATE_CURR - datetime.timedelta(days=5))

        self.assertTrue(es_dia_1_del_ciclo(self.sucursal, DATE_CURR))


# ─────────────────────────────────────────────
# get_inicio_ciclo()
# ─────────────────────────────────────────────

class GetInicioCicloTest(TestCase):
    """
    get_inicio_ciclo(sucursal) devuelve ciclo.inicio_ciclo o None.
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def test_sin_ciclo_retorna_none(self):
        """Sin CicloRecaudacion → None."""
        self.assertIsNone(get_inicio_ciclo(self.sucursal))

    def test_con_ciclo_retorna_fecha_inicio(self):
        """CicloRecaudacion existente → devuelve su inicio_ciclo."""
        fecha_inicio = datetime.date(2025, 1, 1)
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=fecha_inicio,
        )
        self.assertEqual(get_inicio_ciclo(self.sucursal), fecha_inicio)


# ─────────────────────────────────────────────
# Helpers para tests OCR
# ─────────────────────────────────────────────

def _png_b64(width=200, height=100, color=(255, 255, 255)):
    """Crea un PNG mínimo en memoria y devuelve su contenido en base64."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ocr_data vacío compatible con agrupar_lineas (produce filas=[])
_EMPTY_OCR_DATA = {
    "text": [], "block_num": [], "par_num": [],
    "line_num": [], "top": [], "conf": [],
    "left": [], "width": [], "height": [], "word_num": [], "level": [],
    "page_num": [],
}


# ─────────────────────────────────────────────
# normalizar_valor()
# ─────────────────────────────────────────────

class NormalizarValorTest(TestCase):
    """
    normalizar_valor(raw) convierte strings crudos del OCR a enteros,
    aplicando limpieza de símbolo peso, formato chileno de miles y
    correcciones de dígitos erróneos habituales en pantallas slot.
    """

    def setUp(self):
        from control.views import normalizar_valor
        self.fn = normalizar_valor

    def test_formato_chileno_con_puntos(self):
        """'197.000' (separador de miles chileno) → 197000."""
        self.assertEqual(self.fn("197.000"), 197000)

    def test_simbolo_peso_eliminado(self):
        """'$197.000' → 197000 ($ se descarta)."""
        self.assertEqual(self.fn("$197.000"), 197000)

    def test_prefijo_s_como_peso_eliminado(self):
        """'S197.000' → 197000 (S leído como $ se descarta)."""
        self.assertEqual(self.fn("S197.000"), 197000)

    def test_numero_plano_sin_separadores(self):
        """'197000' → 197000."""
        self.assertEqual(self.fn("197000"), 197000)

    def test_cinco_inicial_falso_eliminado(self):
        """
        '5197000' tiene 7 dígitos y empieza por '5' (no por '50').
        El OCR lee '$' como '5' → se elimina el primer dígito.
        """
        self.assertEqual(self.fn("5197000"), 197000)

    def test_ultimo_digito_sospechoso_es_redondeado(self):
        """
        '197006': 6 dígitos, último dígito 6 ∈ {1,2,6,7,8,9},
        diferencia con 197000 = 6 ≤ 15 → se redondea a 197000.
        """
        self.assertEqual(self.fn("197006"), 197000)

    def test_none_retorna_none(self):
        self.assertIsNone(self.fn(None))

    def test_string_vacio_retorna_none(self):
        self.assertIsNone(self.fn(""))


# ─────────────────────────────────────────────
# _extraer_valores_de_texto()
# ─────────────────────────────────────────────

class ExtraerValoresDeTextoTest(TestCase):
    """
    _extraer_valores_de_texto(texto_plano, filas) tiene cuatro estrategias
    de extracción. Los tests cubren las tres primeras y el caso sin match.

    'filas' sigue el formato que devuelve agrupar_lineas():
        {"texto": str, "numeros": [str, ...], "top": int}
    """

    def setUp(self):
        from control.views import _extraer_valores_de_texto
        self.fn = _extraer_valores_de_texto

    # -- Estrategia 1: label + número en la misma fila ----------------------

    def test_extrae_desde_fila_con_label_y_numero(self):
        """
        Caso estándar: cada fila contiene el label y su valor juntos.
        Estrategia 1 resuelve ambos en un solo paso.
        """
        filas = [
            {"texto": " ENTRADAS $197.000", "numeros": ["$197.000"], "top": 100},
            {"texto": " SALIDAS $85.000",   "numeros": ["$85.000"],  "top": 150},
        ]
        entrada, salida, _, _ = self.fn("", filas)

        self.assertEqual(entrada, 197000)
        self.assertEqual(salida, 85000)

    def test_variante_ortografica_saudas_detectada_como_salida(self):
        """
        El OCR confunde L con U: 'SAUDAS' en lugar de 'SALIDAS'.
        es_linea_salida() acepta 'SAUDA' → debe extraerse igualmente.
        """
        filas = [
            {"texto": " ENTRADAS $197.000", "numeros": ["$197.000"], "top": 100},
            {"texto": " SAUDAS $85.000",    "numeros": ["$85.000"],  "top": 150},
        ]
        entrada, salida, _, _ = self.fn("", filas)

        self.assertEqual(entrada, 197000)
        self.assertEqual(salida, 85000)

    # -- Estrategia 2 (fallback): label en fila i, número en fila i+1 -------

    def test_extrae_cuando_numero_esta_en_fila_siguiente(self):
        """
        El OCR separa el label y el valor en filas distintas.
        La estrategia 2 busca el número en la fila inmediatamente siguiente.
        """
        filas = [
            {"texto": " ENTRADAS",  "numeros": [],         "top": 100},
            {"texto": " $197.000",  "numeros": ["$197.000"], "top": 110},
            {"texto": " SALIDAS",   "numeros": [],         "top": 150},
            {"texto": " $85.000",   "numeros": ["$85.000"],  "top": 160},
        ]
        entrada, salida, _, _ = self.fn("", filas)

        self.assertEqual(entrada, 197000)
        self.assertEqual(salida, 85000)

    # -- Estrategia 3: regex sobre texto_plano --------------------------------

    def test_extrae_via_regex_con_texto_plano(self):
        """
        filas vacías → estrategia 1 y 2 no encuentran nada.
        El texto plano contiene los patrones → estrategia 3 (regex) extrae.
        """
        texto = "ENTRADAS 197000\nSALIDAS 85000"
        entrada, salida, _, _ = self.fn(texto, [])

        self.assertEqual(entrada, 197000)
        self.assertEqual(salida, 85000)

    # -- Sin coincidencias ---------------------------------------------------

    def test_retorna_nones_cuando_no_hay_coincidencias(self):
        """
        Texto sin palabras clave y sin números grandes (≥ 5 dígitos).
        Todas las estrategias fallan → (None, None, None, None).
        """
        texto = "pantalla apagada sin datos"
        filas = [{"texto": " info 42", "numeros": ["42"], "top": 10}]
        entrada, salida, er, sr = self.fn(texto, filas)

        self.assertIsNone(entrada)
        self.assertIsNone(salida)
        self.assertIsNone(er)
        self.assertIsNone(sr)


# ─────────────────────────────────────────────
# ocr_lectura() — endpoint HTTP
# ─────────────────────────────────────────────

class OcrLecturaEndpointTest(TestCase):
    """
    Tests de integración para POST /api/ocr-lectura/.

    _preprocesar_imagen() usa solo PIL (sin Tesseract) → se deja correr.
    _ocr_texto() llama a Tesseract → se mockea con patch.
    """

    URL = "/api/ocr-lectura/"

    def _post_json(self, payload):
        import json
        return self.client.post(
            self.URL,
            data=json.dumps(payload),
            content_type="application/json",
        )

    # -- Método incorrecto ---------------------------------------------------

    def test_get_retorna_405(self):
        """GET no está permitido → 405 con success=False."""
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 405)
        self.assertFalse(response.json()["success"])

    # -- Validación de entrada -----------------------------------------------

    def test_body_sin_clave_image_retorna_400(self):
        """JSON sin la clave 'image' → 400 con mensaje claro."""
        response = self._post_json({})

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("imagen", data["error"].lower())

    def test_base64_invalido_retorna_500(self):
        """
        Base64 corrupto → base64.b64decode lanza binascii.Error →
        capturado por el except genérico → 500 con success=False.
        """
        response = self._post_json({"image": "!!!ESTO_NO_ES_BASE64!!!"})

        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.json()["success"])

    # -- Respuesta exitosa ---------------------------------------------------

    def test_respuesta_exitosa_devuelve_entrada_salida_total(self):
        """
        Imagen PNG válida + mock de _ocr_texto que devuelve texto con
        ENTRADAS y SALIDAS → 200 con los campos correctos.
        total = 197000 - 85000 = 112000.
        """
        b64 = _png_b64()

        with patch("control.views._ocr_texto") as mock_ocr:
            mock_ocr.return_value = (
                "ENTRADAS 197000\nSALIDAS 85000",
                _EMPTY_OCR_DATA,
            )
            response = self._post_json({"image": b64})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["entrada"], 197000)
        self.assertEqual(data["salida"], 85000)
        self.assertEqual(data["total"], 112000)
        self.assertIn("mensaje", data)

    # -- OCR sin coincidencias -----------------------------------------------

    def test_ocr_sin_coincidencias_retorna_400_con_debug(self):
        """
        Imagen válida pero el OCR devuelve texto sin ENTRADA/SALIDA → 400.
        La respuesta debe incluir la clave 'debug_texto' para diagnóstico.
        """
        b64 = _png_b64()

        with patch("control.views._ocr_texto") as mock_ocr:
            mock_ocr.return_value = (
                "pantalla sin texto reconocible",
                _EMPTY_OCR_DATA,
            )
            response = self._post_json({"image": b64})

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("debug_texto", data)


# ─────────────────────────────────────────────
# LecturaMaquinaForm
# ─────────────────────────────────────────────

class LecturaMaquinaFormTest(TestCase):
    """
    Tests del clean() de LecturaMaquinaForm:
    - calcula total = entrada - salida
    - rechaza valores negativos en entrada o salida
    - rechaza máquina que no pertenece a la zona seleccionada
    - el campo total no es requerido
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.zona     = make_zona(self.sucursal)
        self.usuario  = make_usuario()
        self.turno    = make_turno(self.sucursal, self.usuario)
        self.maquina  = make_maquina(self.sucursal, self.zona, numero=1)

    def _form(self, data):
        return LecturaMaquinaForm(
            data=data,
            turno=self.turno,
            usuario=self.usuario,
        )

    def test_total_calculado_automaticamente(self):
        """clean() debe asignar total = entrada - salida."""
        form = self._form({
            "zona": self.zona.pk,
            "maquina": self.maquina.pk,
            "entrada": 1500,
            "salida": 1200,
            "total": "",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["total"], 300)

    def test_total_negativo_es_valido(self):
        """total negativo (salida > entrada) es aceptado."""
        form = self._form({
            "zona": self.zona.pk,
            "maquina": self.maquina.pk,
            "entrada": 1000,
            "salida": 1500,
            "total": "",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["total"], -500)

    def test_entrada_negativa_invalida(self):
        """Entrada < 0 debe producir error en el campo entrada."""
        form = self._form({
            "zona": self.zona.pk,
            "maquina": self.maquina.pk,
            "entrada": -1,
            "salida": 0,
            "total": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("entrada", form.errors)

    def test_salida_negativa_invalida(self):
        """Salida < 0 debe producir error en el campo salida."""
        form = self._form({
            "zona": self.zona.pk,
            "maquina": self.maquina.pk,
            "entrada": 1000,
            "salida": -1,
            "total": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("salida", form.errors)

    def test_maquina_de_otra_zona_invalida(self):
        """Máquina cuya zona difiere de la zona seleccionada → error en maquina."""
        zona_b    = make_zona(self.sucursal, nombre="Zona B")
        maquina_b = make_maquina(self.sucursal, zona_b, numero=2)
        form = self._form({
            "zona": self.zona.pk,       # zona A
            "maquina": maquina_b.pk,    # máquina de zona B
            "entrada": 1000,
            "salida": 800,
            "total": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("maquina", form.errors)


# ─────────────────────────────────────────────
# MaquinaForm
# ─────────────────────────────────────────────

class MaquinaFormTest(TestCase):
    """
    Tests de MaquinaForm:
    - clean() fija estado="Operativa" en instancias nuevas
    - el queryset de zona se filtra por sucursal cuando sucursal viene en data
    - campos requeridos correctamente validados
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.zona     = make_zona(self.sucursal)

    def _data(self, **kwargs):
        base = {
            "sucursal": self.sucursal.pk,
            "zona": self.zona.pk,
            "numero_maquina": 99,
            "nombre_juego": "Juego Test",
            "contador_inicial_entrada": 0,
            "contador_inicial_salida": 0,
        }
        base.update(kwargs)
        return base

    def test_nueva_maquina_tiene_estado_operativa(self):
        """clean() debe asignar estado='Operativa' en la instancia nueva."""
        form = MaquinaForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save(commit=False)
        self.assertEqual(instance.estado, "Operativa")

    def test_zona_filtrada_por_sucursal_en_data(self):
        """Cuando sucursal está en data, el queryset de zona excluye zonas de otras sucursales."""
        sucursal_b = make_sucursal(nombre="Sucursal B")
        zona_b     = make_zona(sucursal_b, nombre="Zona B")
        form = MaquinaForm(data=self._data())
        pks = list(form.fields["zona"].queryset.values_list("pk", flat=True))
        self.assertIn(self.zona.pk, pks)
        self.assertNotIn(zona_b.pk, pks)

    def test_formulario_invalido_sin_nombre_juego(self):
        """nombre_juego es requerido; enviarlo vacío debe invalidar el form."""
        form = MaquinaForm(data=self._data(nombre_juego=""))
        self.assertFalse(form.is_valid())
        self.assertIn("nombre_juego", form.errors)


# ─────────────────────────────────────────────
# UsuarioForm
# ─────────────────────────────────────────────

class UsuarioFormTest(TestCase):
    """
    Tests del clean() de UsuarioForm:
    - contraseñas deben coincidir
    - rol es obligatorio
    - roles con sucursal (encargado, supervisor, asistente) requieren al menos una sucursal
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def _data(self, **kwargs):
        base = {
            "username": "nuevo_user",
            "nombre": "Nuevo Usuario",
            "email": "nuevo@test.com",
            "role": "admin",
            "password": "test1234",
            "password_confirm": "test1234",
            "is_active": True,
        }
        base.update(kwargs)
        return base

    def test_formulario_valido_con_datos_correctos(self):
        """Datos completos y coherentes → formulario válido."""
        form = UsuarioForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_contrasenas_distintas_invalidan(self):
        """password ≠ password_confirm → formulario inválido."""
        form = UsuarioForm(data=self._data(password_confirm="otra_clave"))
        self.assertFalse(form.is_valid())

    def test_rol_vacio_invalida(self):
        """role vacío → error en el campo role."""
        form = UsuarioForm(data=self._data(role=""))
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_rol_con_sucursal_sin_sucursal_asignada_invalida(self):
        """encargado sin sucursales asignadas → error en el campo sucursales."""
        form = UsuarioForm(data=self._data(role="encargado"))
        self.assertFalse(form.is_valid())
        self.assertIn("sucursales", form.errors)

    def test_rol_con_sucursal_con_sucursal_asignada_valida(self):
        """encargado con al menos una sucursal asignada → formulario válido."""
        form = UsuarioForm(data=self._data(role="encargado", sucursales=[self.sucursal.pk]))
        self.assertTrue(form.is_valid(), form.errors)


# ─────────────────────────────────────────────
# CuadraturaCajaDiariaForm
# ─────────────────────────────────────────────

class CuadraturaCajaDiariaFormTest(TestCase):
    """
    Tests de CuadraturaCajaDiariaForm:
    - clean() convierte campos numéricos vacíos a 0
    - sucursal y fecha son obligatorios
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def _data(self, **kwargs):
        base = {
            "fecha": "2025-06-15",
            "sucursal": self.sucursal.pk,
        }
        base.update(kwargs)
        return base

    def test_campos_vacios_convertidos_a_cero(self):
        """
        Campos numéricos no enviados (o vacíos) deben quedar como 0
        en cleaned_data después de clean().
        """
        form = CuadraturaCajaDiariaForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data.get("sorteos_dia"), 0)
        self.assertEqual(form.cleaned_data.get("gastos_dia"), 0)
        self.assertEqual(form.cleaned_data.get("caja"), 0)

    def test_sucursal_requerida(self):
        """Omitir sucursal → error en el campo sucursal."""
        data = self._data()
        del data["sucursal"]
        form = CuadraturaCajaDiariaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("sucursal", form.errors)

    def test_fecha_requerida(self):
        """Omitir fecha → error en el campo fecha."""
        data = self._data()
        del data["fecha"]
        form = CuadraturaCajaDiariaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("fecha", form.errors)


# ─────────────────────────────────────────────
# Maquina.clean() — validación sucursal vs zona
# ─────────────────────────────────────────────

class MaquinaCleanTest(TestCase):
    """
    Maquina.clean() valida que la zona pertenezca a la sucursal indicada.
    """

    def setUp(self):
        self.sucursal_a = make_sucursal("Sucursal A")
        self.sucursal_b = make_sucursal("Sucursal B")
        self.zona_a = make_zona(self.sucursal_a)
        self.zona_b = make_zona(self.sucursal_b)

    def test_zona_de_otra_sucursal_lanza_validation_error(self):
        """Zona de sucursal B asignada a máquina de sucursal A → ValidationError."""
        maquina = Maquina(
            sucursal=self.sucursal_a,
            zona=self.zona_b,
            numero_maquina=1,
            nombre_juego="Test",
        )
        with self.assertRaises(ValidationError) as ctx:
            maquina.clean()
        self.assertIn("sucursal", ctx.exception.message_dict)

    def test_zona_de_misma_sucursal_es_valida(self):
        """Zona que pertenece a la sucursal indicada → sin error."""
        maquina = Maquina(
            sucursal=self.sucursal_a,
            zona=self.zona_a,
            numero_maquina=1,
            nombre_juego="Test",
        )
        maquina.clean()  # no debe lanzar excepción


# ─────────────────────────────────────────────
# CuadraturaCajaDiaria — métodos de cálculo
# ─────────────────────────────────────────────

class CuadraturaCajaDiariaCalculosTest(TestCase):
    """
    Verifica total_gastos_dia() y desglose_efectivo_total.
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def test_total_gastos_dia_suma_todos_los_conceptos(self):
        """total_gastos_dia() suma los 12 campos _dia."""
        c = CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=DATE_CURR,
            sorteos_dia=1_000,
            gastos_dia=500,
            sueldo_b_dia=2_000,
            redbank_dia=300,
            regalos_dia=100,
            taxi_dia=50,
            jugados_dia=200,
            transfer_dia=400,
            otros_1_dia=10,
            otros_2_dia=20,
            otros_3_dia=30,
            descuadre_dia=5,
        )
        esperado = 1_000 + 500 + 2_000 + 300 + 100 + 50 + 200 + 400 + 10 + 20 + 30 + 5
        self.assertEqual(c.total_gastos_dia(), esperado)

    def test_total_gastos_dia_sin_datos_es_cero(self):
        """Cuadratura vacía → total_gastos_dia() == 0."""
        c = CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=DATE_CURR,
        )
        self.assertEqual(c.total_gastos_dia(), 0)

    def test_desglose_efectivo_total_suma_todas_las_denominaciones(self):
        """desglose_efectivo_total suma ef_20000..ef_monedas y ef_billetes_malos."""
        c = CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=DATE_CURR,
            ef_20000=40_000,
            ef_10000=30_000,
            ef_5000=15_000,
            ef_2000=4_000,
            ef_1000=3_000,
            ef_monedas=500,
            ef_billetes_malos=10_000,
        )
        self.assertEqual(c.desglose_efectivo_total, 102_500)

    def test_desglose_efectivo_total_vacio_es_cero(self):
        """Sin valores de efectivo → desglose_efectivo_total == 0."""
        c = CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=DATE_CURR,
        )
        self.assertEqual(c.desglose_efectivo_total, 0)


# ─────────────────────────────────────────────
# InformeRecaudacion.rtp e InformeRecaudacionLinea.rtp
# ─────────────────────────────────────────────

class InformeRecaudacionRtpTest(TestCase):
    """
    La propiedad rtp calcula (entrada-salida)/entrada*100 redondeado a 1 decimal.
    Devuelve 0 cuando entrada es 0 (evita división por cero).
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def _informe(self, entrada, salida):
        return InformeRecaudacion(
            sucursal=self.sucursal,
            fecha_inicio=DATE_PREV,
            fecha_cierre=DATE_CURR,
            total_entrada=entrada,
            total_salida=salida,
        )

    def test_rtp_calculado_correctamente(self):
        """(1000 - 850) / 1000 * 100 = 15.0."""
        self.assertEqual(self._informe(1_000, 850).rtp, 15.0)

    def test_rtp_cuando_entrada_es_cero_retorna_cero(self):
        """División por cero evitada → rtp == 0."""
        self.assertEqual(self._informe(0, 500).rtp, 0)

    def test_rtp_redondeado_a_un_decimal(self):
        """(1000 - 333) / 1000 * 100 = 66.7."""
        self.assertEqual(self._informe(1_000, 333).rtp, 66.7)


class InformeRecaudacionLineaRtpTest(TestCase):
    """
    InformeRecaudacionLinea.rtp calcula (parcial_entrada - parcial_salida) / parcial_entrada * 100.
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.informe = InformeRecaudacion.objects.create(
            sucursal=self.sucursal,
            fecha_inicio=DATE_PREV,
            fecha_cierre=DATE_CURR,
        )

    def _linea(self, parcial_entrada, parcial_salida):
        return InformeRecaudacionLinea(
            informe=self.informe,
            numero_maquina=1,
            parcial_entrada=parcial_entrada,
            parcial_salida=parcial_salida,
        )

    def test_rtp_linea_calculado(self):
        """(500 - 400) / 500 * 100 = 20.0."""
        self.assertEqual(self._linea(500, 400).rtp, 20.0)

    def test_rtp_linea_entrada_cero_retorna_cero(self):
        self.assertEqual(self._linea(0, 100).rtp, 0)


# ─────────────────────────────────────────────
# get_caja_anterior_en_ciclo()
# ─────────────────────────────────────────────

class GetCajaAnteriorEnCicloTest(TestCase):
    """
    get_caja_anterior_en_ciclo(sucursal, fecha) devuelve la última
    CuadraturaCajaDiaria anterior a 'fecha' dentro del ciclo, o un
    objeto dummy con ceros si no existe ninguna.
    """

    def setUp(self):
        self.sucursal = make_sucursal()

    def _make_cuadratura(self, fecha, numeral_acumulado=0):
        return CuadraturaCajaDiaria.objects.create(
            sucursal=self.sucursal,
            fecha=fecha,
            numeral_acumulado=numeral_acumulado,
        )

    def test_sin_cuadraturas_retorna_dummy_con_ceros(self):
        """Sin cuadraturas previas → objeto dummy con caja_total = 0."""
        resultado = get_caja_anterior_en_ciclo(self.sucursal, DATE_CURR)
        self.assertEqual(resultado.numeral_dia, 0)
        self.assertEqual(resultado.prestamos, 0)

    def test_retorna_cuadratura_mas_reciente_antes_de_la_fecha(self):
        """Hay cuadraturas previas → retorna la más reciente."""
        c_ayer = self._make_cuadratura(DATE_PREV, numeral_acumulado=5_000)
        self._make_cuadratura(DATE_PREV2, numeral_acumulado=3_000)

        resultado = get_caja_anterior_en_ciclo(self.sucursal, DATE_CURR)
        self.assertEqual(resultado.pk, c_ayer.pk)

    def test_cuadratura_del_mismo_dia_no_cuenta(self):
        """La cuadratura con fecha == fecha_consulta NO es 'anterior'."""
        self._make_cuadratura(DATE_CURR, numeral_acumulado=9_000)
        resultado = get_caja_anterior_en_ciclo(self.sucursal, DATE_CURR)
        # No hay nada antes de DATE_CURR → dummy
        self.assertEqual(resultado.numeral_dia, 0)

    def test_cuadratura_fuera_del_ciclo_es_ignorada(self):
        """Con ciclo activo, las cuadraturas anteriores al inicio_ciclo se ignoran."""
        inicio = DATE_CURR - datetime.timedelta(days=3)
        CicloRecaudacion.objects.create(
            sucursal=self.sucursal,
            inicio_ciclo=inicio,
        )
        # Cuadratura antes del ciclo (5 días atrás)
        self._make_cuadratura(DATE_CURR - datetime.timedelta(days=5), 99_000)

        resultado = get_caja_anterior_en_ciclo(self.sucursal, DATE_CURR)
        self.assertEqual(resultado.numeral_dia, 0)


# ─────────────────────────────────────────────
# Decoradores
# ─────────────────────────────────────────────

class RoleRequiredDecoratorTest(TestCase):
    """
    @role_required(*roles) permite el acceso solo al rol indicado.
    Usuarios no autenticados son redirigidos al login.
    Usuarios con rol incorrecto reciben PermissionDenied.
    """

    def setUp(self):
        self.admin = make_usuario("admin_dec")
        self.admin.role = "admin"
        self.admin.save()

        self.encargado = make_usuario("encarg_dec")
        self.encargado.role = "encargado"
        self.encargado.save()

    def test_rol_correcto_accede_al_dashboard(self):
        """Admin puede acceder al dashboard (solo rol permitido)."""
        self.client.force_login(self.admin)
        response = self.client.get("/dashboard/")
        self.assertNotEqual(response.status_code, 403)

    def test_rol_incorrecto_recibe_403(self):
        """Encargado no puede acceder al dashboard → 403."""
        self.client.force_login(self.encargado)
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 403)

    def test_no_autenticado_redirige_al_login(self):
        """Usuario anónimo → redirect al login (302)."""
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response["Location"])


class ReadonlyForDecoratorTest(TestCase):
    """
    @readonly_for(*roles) bloquea POST para roles de solo lectura.
    GET siempre pasa. POST bloqueado → PermissionDenied.
    """

    def setUp(self):
        self.sucursal = make_sucursal()
        self.supervisor = make_usuario("sup_dec")
        self.supervisor.role = "supervisor"
        self.supervisor.sucursales.add(self.sucursal)
        self.supervisor.save()

        self.admin = make_usuario("admin_dec2")
        self.admin.role = "admin"
        self.admin.save()

    def test_get_permitido_para_rol_readonly(self):
        """Supervisor puede hacer GET en la vista de registro."""
        self.client.force_login(self.supervisor)
        response = self.client.get("/registro/")
        # Solo verificamos que no sea 403 (el GET debe pasar)
        self.assertNotEqual(response.status_code, 403)

    def test_post_bloqueado_para_rol_readonly(self):
        """Supervisor recibe 403 al intentar POST en registro."""
        self.client.force_login(self.supervisor)
        response = self.client.post("/registro/", data={})
        self.assertEqual(response.status_code, 403)

    def test_post_permitido_para_rol_no_readonly(self):
        """Admin puede POST en registro sin restricción de readonly."""
        self.client.force_login(self.admin)
        # Enviamos POST vacío; si falla por validación del form (no por 403) está bien
        response = self.client.post("/registro/", data={})
        self.assertNotEqual(response.status_code, 403)


# ─────────────────────────────────────────────
# SucursalEncargadoMiddleware
# ─────────────────────────────────────────────

class SucursalEncargadoMiddlewareTest(TestCase):
    """
    Si el encargado/asistente tiene más de una sucursal y no ha
    seleccionado una activa en la sesión, el middleware redirige
    a /seleccionar-sucursal/.
    """

    def setUp(self):
        self.suc1 = make_sucursal("Local 1")
        self.suc2 = make_sucursal("Local 2")

        self.encargado = make_usuario("enc_mw")
        self.encargado.role = "encargado"
        self.encargado.sucursales.add(self.suc1, self.suc2)
        self.encargado.save()

        self.enc_una = make_usuario("enc_una")
        self.enc_una.role = "encargado"
        self.enc_una.sucursales.add(self.suc1)
        self.enc_una.save()

    def test_encargado_con_varias_sucursales_sin_sesion_es_redirigido(self):
        """Encargado multi-sucursal sin sucursal_activa_id → redirige a seleccionar."""
        self.client.force_login(self.encargado)
        response = self.client.get("/turno/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("seleccionar-sucursal", response["Location"])

    def test_encargado_con_una_sucursal_no_es_redirigido(self):
        """Encargado con solo una sucursal → no pasa por selección."""
        self.client.force_login(self.enc_una)
        response = self.client.get("/turno/")
        self.assertNotEqual(response.status_code, 302)
        # Cualquier response que no sea redirect al selector está bien

    def test_encargado_con_sucursal_activa_en_sesion_no_es_redirigido(self):
        """Encargado multi-sucursal con sucursal_activa_id en sesión → accede normal."""
        self.client.force_login(self.encargado)
        session = self.client.session
        session["sucursal_activa_id"] = self.suc1.pk
        session.save()
        response = self.client.get("/turno/")
        self.assertNotEqual(response.status_code, 302)


# ─────────────────────────────────────────────
# Login view
# ─────────────────────────────────────────────

class LoginViewTest(TestCase):
    """
    Tests del flujo de autenticación en /login/.
    """

    LOGIN_URL = "/login/"

    def setUp(self):
        self.usuario = make_usuario("login_user")
        self.usuario.set_password("clave_segura")
        self.usuario.save()

    def test_get_retorna_200(self):
        """GET /login/ devuelve el formulario de login."""
        response = self.client.get(self.LOGIN_URL)
        self.assertEqual(response.status_code, 200)

    def test_post_credenciales_correctas_redirige(self):
        """POST con credenciales válidas redirige (302)."""
        response = self.client.post(self.LOGIN_URL, {
            "username": "login_user",
            "password": "clave_segura",
        })
        self.assertEqual(response.status_code, 302)

    def test_post_credenciales_incorrectas_retorna_200_con_error(self):
        """POST con contraseña incorrecta vuelve a mostrar el login."""
        response = self.client.post(self.LOGIN_URL, {
            "username": "login_user",
            "password": "clave_incorrecta",
        })
        self.assertEqual(response.status_code, 200)

    def test_usuario_ya_autenticado_es_redirigido(self):
        """Usuario ya logueado que visita /login/ debe ser redirigido."""
        self.client.force_login(self.usuario)
        response = self.client.get(self.LOGIN_URL)
        self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────
# Control de acceso a vistas por rol
# ─────────────────────────────────────────────

class AccesoVistasRolTest(TestCase):
    """
    Verifica que las vistas restrinjan correctamente el acceso según rol.
    Usa force_login para simular usuarios autenticados.
    """

    def setUp(self):
        self.sucursal = make_sucursal()

        self.admin = make_usuario("adm_acc")
        self.admin.role = "admin"
        self.admin.save()

        self.gerente = make_usuario("ger_acc")
        self.gerente.role = "gerente"
        self.gerente.sucursales.add(self.sucursal)
        self.gerente.save()

        self.tecnico = make_usuario("tec_acc")
        self.tecnico.role = "tecnico"
        self.tecnico.save()

    def test_admin_accede_a_usuarios(self):
        """/usuarios/ es accesible para admin."""
        self.client.force_login(self.admin)
        response = self.client.get("/usuarios/")
        self.assertEqual(response.status_code, 200)

    def test_gerente_puede_ver_usuarios_pero_no_crearlos(self):
        """
        Gerente puede listar usuarios (ROLES_VER_USUARIOS incluye gerente)
        pero no puede acceder al formulario de creación (ROLES_USUARIOS = solo admin).
        """
        self.client.force_login(self.gerente)
        response_list = self.client.get("/usuarios/")
        self.assertEqual(response_list.status_code, 200)

        response_create = self.client.get("/usuarios/create/")
        self.assertEqual(response_create.status_code, 403)

    def test_tecnico_accede_a_maquinas(self):
        """Técnico puede ver la lista de máquinas."""
        self.client.force_login(self.tecnico)
        response = self.client.get("/maquinas/")
        self.assertEqual(response.status_code, 200)

    def test_no_autenticado_en_maquinas_redirige_al_login(self):
        """Visitante anónimo en /maquinas/ → redirect a login."""
        response = self.client.get("/maquinas/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response["Location"])

    def test_admin_accede_a_recaudacion(self):
        """/recaudacion/ solo para admin."""
        self.client.force_login(self.admin)
        response = self.client.get("/recaudacion/")
        self.assertNotEqual(response.status_code, 403)

    def test_gerente_no_accede_a_recaudacion(self):
        """Gerente no puede ver recaudación → 403."""
        self.client.force_login(self.gerente)
        response = self.client.get("/recaudacion/")
        self.assertEqual(response.status_code, 403)


# ─────────────────────────────────────────────
# Signal audit log — RegistroActividad
# ─────────────────────────────────────────────

class RegistroActividadSignalTest(TestCase):
    """
    Los signals post_save y post_delete crean entradas en RegistroActividad
    para los modelos auditados (Sucursal, Maquina, Turno, LecturaMaquina, etc.).
    """

    def test_crear_sucursal_genera_registro_crear(self):
        """Al crear una Sucursal se crea un RegistroActividad de tipo CREAR."""
        antes = RegistroActividad.objects.count()
        make_sucursal("Sucursal Auditada")
        self.assertEqual(RegistroActividad.objects.count(), antes + 1)
        ultimo = RegistroActividad.objects.order_by("-fecha_hora").first()
        self.assertEqual(ultimo.tipo, "CREAR")
        self.assertEqual(ultimo.modulo, "Sucursal")

    def test_editar_sucursal_genera_registro_editar(self):
        """Al modificar una Sucursal se crea un RegistroActividad de tipo EDITAR."""
        suc = make_sucursal("Suc Edit")
        antes = RegistroActividad.objects.count()
        suc.nombre = "Suc Edit Modificada"
        suc.save()
        self.assertEqual(RegistroActividad.objects.count(), antes + 1)
        ultimo = RegistroActividad.objects.order_by("-fecha_hora").first()
        self.assertEqual(ultimo.tipo, "EDITAR")

    def test_eliminar_turno_genera_registro_eliminar(self):
        """Al eliminar un Turno se crea un RegistroActividad de tipo ELIMINAR."""
        suc = make_sucursal()
        usr = make_usuario("audit_usr")
        turno = make_turno(suc, usr)
        antes = RegistroActividad.objects.count()
        turno.delete()
        self.assertEqual(RegistroActividad.objects.count(), antes + 1)
        ultimo = RegistroActividad.objects.order_by("-fecha_hora").first()
        self.assertEqual(ultimo.tipo, "ELIMINAR")
        self.assertEqual(ultimo.modulo, "Turno")

    def test_modelos_no_auditados_no_generan_registro(self):
        """
        EncuadreCajaAdmin NO está en la lista MODELOS de signals.py
        → no debe generar RegistroActividad al crearse.
        """
        from .models import EncuadreCajaAdmin
        suc = make_sucursal()
        turno = make_turno(suc, make_usuario("usr_enc"))
        antes = RegistroActividad.objects.filter(modulo="Encuadre Admin").count()
        EncuadreCajaAdmin.objects.create(
            sucursal=suc,
            turno=turno,
            fecha=DATE_CURR,
        )
        despues = RegistroActividad.objects.filter(modulo="Encuadre Admin").count()
        self.assertEqual(antes, despues)
