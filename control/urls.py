from django.urls import path
from . import views

app_name = 'control'

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Turno
    path('turno/', views.turno_view, name='turno'),
    path('turno/cerrar/<int:turno_id>/', views.cerrar_turno, name='cerrar_turno'),
    
    # Registro
    path('registro/', views.registro_view, name='registro'),
    path('api/zonas/<int:sucursal_id>/', views.get_zonas_ajax, name='get_zonas_ajax'),
    path('api/maquinas/<int:zona_id>/', views.get_maquinas_ajax, name='get_maquinas_ajax'),
    path('api/ia/capturar/', views.ia_capturar_dummy, name='ia_capturar'),
    
    # Tablas
    path('tablas/', views.tablas_view, name='tablas'),
    path('tablas/export-excel/', views.export_excel, name='export_excel'),
    
    # CRUD Sucursales
    path('sucursales/', views.sucursales_list, name='sucursales_list'),
    path('sucursales/create/', views.sucursal_create, name='sucursal_create'),
    path('sucursales/edit/<int:pk>/', views.sucursal_edit, name='sucursal_edit'),
    path('sucursales/delete/<int:pk>/', views.sucursal_delete, name='sucursal_delete'),
    
    # CRUD Zonas
    path('zonas/', views.zonas_list, name='zonas_list'),
    path('zonas/create/', views.zona_create, name='zona_create'),
    path('zonas/edit/<int:pk>/', views.zona_edit, name='zona_edit'),
    path('zonas/delete/<int:pk>/', views.zona_delete, name='zona_delete'),
    
    # CRUD Máquinas
    path('maquinas/', views.maquinas_list, name='maquinas_list'),
    path('maquinas/create/', views.maquina_create, name='maquina_create'),
    path('maquinas/edit/<int:pk>/', views.maquina_edit, name='maquina_edit'),
    path('maquinas/delete/<int:pk>/', views.maquina_delete, name='maquina_delete'),
    
    # CRUD Usuarios
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/create/', views.usuario_create, name='usuario_create'),
    path('usuarios/edit/<int:pk>/', views.usuario_edit, name='usuario_edit'),
    path('usuarios/delete/<int:pk>/', views.usuario_delete, name='usuario_delete'),
]
