MENU = [

    {
        "section": "Principal",
        "items": [
            {
                "label": "Dashboard",
                "icon": "bi-speedometer2",
                "url": "control:dashboard",
                "url_name": "dashboard",
                "roles": ["admin"]
            }
        ]
    },

    {
        "section": "Operaciones",
        "items": [
            {
                "label": "Caja",
                "icon": "bi-calendar2-week",
                "url": "control:cuadratura_diaria_list",
                "url_name": "cuadratura_diaria_list",
                "roles": ["admin", "gerente"]
            },
            {
                "label": "Caja",
                "icon": "bi-calendar2-week",
                "url": "control:cuadratura_diaria_create",
                "url_name": "cuadratura_diaria_create",
                "roles": ["supervisor", "encargado"]
            },
            {
                "label": "Control",
                "icon": "bi-archive",
                "url": "control:controles_list",
                "url_name": "controles_list",
                "roles": ["admin", "gerente", "supervisor"]
            },
            {
                "label": "Cuadratura Zonas",
                "icon": "bi-grid-1x2",
                "url": "control:cuadratura_zona_list",
                "url_name": "cuadratura_zona_list",
                "roles": ["admin", "gerente", "supervisor", "encargado", "asistente"]
            },
            {
                "label": "Turno",
                "icon": "bi-clock-history",
                "url": "control:turno",
                "url_name": "turno",
                "roles": ["admin", "encargado", "asistente"]
            },
            {
                "label": "Registro Numerales",
                "icon": "bi-clipboard-data",
                "url": "control:registro",
                "url_name": "registro",
                "roles": ["admin", "encargado", "asistente"]
            },
            {
                "label": "Sesiones",
                "icon": "bi-person-lines-fill",
                "url": "control:sesiones_admin",
                "url_name": "sesiones_admin",
                "roles": ["admin"]
            },
            {
                "label": "Recaudación",
                "icon": "bi-bar-chart-steps",
                "url": "control:recaudacion",
                "url_name": "recaudacion",
                "roles": ["admin"]
            },
            {
                "label": "Movimientos",
                "icon": "bi-clock-history",
                "url": "control:movimientos_list",
                "url_name": "movimientos_list",
                "roles": ["admin", "gerente"]
            },
        ]
    },

    {
        "section": "Configuración",
        "items": [
            {
                "label": "Máquinas",
                "icon": "bi-cpu",
                "url": "control:maquinas_list",
                "url_name": "maquinas_list",
                "roles": ["admin", "tecnico", "gerente", "supervisor"]
            },
            {
                "label": "Zonas",
                "icon": "bi-grid-3x3",
                "url": "control:zonas_list",
                "url_name": "zonas_list",
                "roles": ["admin", "tecnico", "gerente", "supervisor"]
            },
            {
                "label": "Sucursales",
                "icon": "bi-building",
                "url": "control:sucursales_list",
                "url_name": "sucursales_list",
                "roles": ["admin", "tecnico", "gerente", "supervisor"]
            },
            {
                "label": "Usuarios",
                "icon": "bi-people",
                "url": "control:usuarios_list",
                "url_name": "usuarios_list",
                "roles": ["admin", "gerente", "supervisor"]
            },
        ]
    }

]