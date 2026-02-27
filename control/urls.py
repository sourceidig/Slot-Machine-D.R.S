from django.urls import path
from . import views
from .views import LecturaEditView
app_name = "control"

urlpatterns = [
    # -------------------------
    # Autenticación
    # -------------------------
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # -------------------------
    # Dashboard
    # -------------------------
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # -------------------------
    # Turno
    # -------------------------
    path("turno/", views.turno_view, name="turno"),
    path("turno/cerrar/<int:turno_id>/", views.cerrar_turno, name="cerrar_turno"),

    # -------------------------
    # Registro
    # -------------------------
    path("registro/", views.registro_view, name="registro"),
    path("lectura/<int:pk>/editar/", LecturaEditView.as_view(), name="lectura_edit"),

    # -------------------------
    # Cuadratura Caja Diaria (EXCEL GRANDE - GERENCIA)
    # -------------------------
    path("cuadratura-diaria/", views.cuadratura_diaria_list, name="cuadratura_diaria_list"),
    path("cuadratura-diaria/nueva/", views.cuadratura_diaria_create, name="cuadratura_diaria_create"),
    path("cuadratura-diaria/<int:pk>/", views.cuadratura_diaria_detail, name="cuadratura_diaria_detail"),
    path("cuadratura-diaria/<int:pk>/editar/", views.cuadratura_diaria_edit, name="cuadratura_diaria_edit"),
    path("cuadratura-diaria/<int:pk>/eliminar/", views.cuadratura_diaria_delete, name="cuadratura_diaria_delete"),
    path("cuadratura-diaria/export-excel/", views.cuadratura_diaria_export_excel, name="cuadratura_diaria_export_excel"),

    # -------------------------
    # Cierre Turno (COLUMNA ROJA - ATENDEDORAS)  -> CierreTurno
    # -------------------------
    # crear/editar por turno
    path("cierre-turno/turno/<int:turno_id>/", views.cierre_turno_create_or_edit, name="cierre_turno"),

    # admin: lista/detalle/editar/eliminar/export
    path("cierre-turno/", views.cierre_turno_list, name="cierre_turno_list"),
    path("cierre-turno/<int:pk>/", views.cierre_turno_detail, name="cierre_turno_detail"),
    path("cierre-turno/<int:pk>/editar/", views.cierre_turno_edit, name="cierre_turno_edit"),
    path("cierre-turno/<int:pk>/eliminar/", views.cierre_turno_delete, name="cierre_turno_delete"),
    path("cierre-turno/export-excel/", views.cierre_turno_export_excel, name="cierre_turno_export_excel"),

    # -------------------------
    # Encuadre Caja Admin (SOLO ADMIN / GERENTE)
    # -------------------------
    path("encuadre/", views.encuadre_list, name="encuadre_list"),
    path("encuadre/nuevo/", views.encuadre_create, name="encuadre_create"),
    path("encuadre/<int:pk>/", views.encuadre_detail, name="encuadre_detail"),

    # -------------------------
    # Tablas
    # -------------------------
    path("tablas/", views.tablas_view, name="tablas"),
    path("tablas/export-excel/", views.export_excel, name="export_excel"),

    # -------------------------
    # AJAX / API
    # -------------------------
    path("ajax/maquinas/<int:zona_id>/", views.get_maquinas_ajax, name="get_maquinas_ajax"),
    path("ajax/zonas/<int:sucursal_id>/", views.get_zonas_ajax, name="get_zonas_ajax"),
    path("ajax/cuadratura-mensual-data/", views.ajax_cuadratura_mensual_data, name="ajax_cuadratura_mensual_data"),
    path("ajax/zonas/", views.zonas_por_sucursal, name="ajax_zonas"),
    path("ajax/cuadratura-diaria/numerales/", views.ajax_cuadratura_diaria_numerales, name="ajax_cuadratura_diaria_numerales"),
    path("ajax/cuadratura-detalles/", views.ajax_cuadratura_detalles, name="ajax_cuadratura_detalles"),


    path("api/ocr/procesar/", views.ocr_lectura, name="ocr_procesar"),
    path("api/ia/capturar/", views.ia_capturar_dummy, name="ia_capturar"),
    path("api/ocr-lectura/", views.ocr_lectura, name="ocr_lectura"),

    # -------------------------
    # CRUD Sucursales / Zonas / Máquinas / Usuarios
    # -------------------------
    path("sucursales/", views.sucursales_list, name="sucursales_list"),
    path("sucursales/create/", views.sucursal_create, name="sucursal_create"),
    path("sucursales/edit/<int:pk>/", views.sucursal_edit, name="sucursal_edit"),
    path("sucursales/delete/<int:pk>/", views.sucursal_delete, name="sucursal_delete"),

    path("zonas/", views.zonas_list, name="zonas_list"),
    path("zonas/create/", views.zona_create, name="zona_create"),
    path("zonas/edit/<int:pk>/", views.zona_edit, name="zona_edit"),
    path("zonas/delete/<int:pk>/", views.zona_delete, name="zona_delete"),

    path("maquinas/", views.maquinas_list, name="maquinas_list"),
    path("maquinas/create/", views.maquina_create, name="maquina_create"),
    path("maquinas/edit/<int:pk>/", views.maquina_edit, name="maquina_edit"),
    path("maquinas/delete/<int:pk>/", views.maquina_delete, name="maquina_delete"),
    path("maquinas/<int:pk>/estado/", views.maquina_update_estado, name="maquina_estado"),

    path("usuarios/", views.usuarios_list, name="usuarios_list"),
    path("usuarios/create/", views.usuario_create, name="usuario_create"),
    path("usuarios/edit/<int:pk>/", views.usuario_edit, name="usuario_edit"),
    path("usuarios/delete/<int:pk>/", views.usuario_delete, name="usuario_delete"),

    #-------------------------
    # Recaudacion / Dia 0
    #------------------------

    path("recaudacion/", views.recaudacion_view, name="recaudacion"),
    path("recaudacion/iniciar-dia-0/", views.iniciar_dia_0, name="iniciar_dia_0"),

    path("turnos/<int:turno_id>/control/", views.generar_control, name="generar_control"),
    path("turnos/<int:turno_id>/control/guardar/", views.guardar_control, name="guardar_control"),
    path("controles/", views.controles_list, name="controles_list"),
    path("controles/<int:pk>/", views.controles_detail, name="controles_detail"),

    path("turnos/<int:turno_id>/cerrar-sin-cuadratura/", views.cerrar_turno_sin_cuadratura, name="cerrar_turno_sin_cuadratura"),

    


]
