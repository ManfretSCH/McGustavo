# Restaurante McGustavo - Sistema de Gestion de Pedidos

Aplicacion de escritorio para gestionar los pedidos de un restaurante de comida
rapida. Permite registrar pedidos, administrar el menu y los clientes, y consultar
el historial de ventas.

Proyecto grupal de **Python II - Optativo II** (Grupo 2).

## Tecnologias

- Python 3.12
- Tkinter (interfaz grafica)
- SQLAlchemy 2.0 + SQLite (base de datos)
- uv (gestor de paquetes y entorno)

## Como ejecutar

```bash
uv run python main.py
```

La primera vez se crea automaticamente la base de datos `McGustavo.db` y se cargan
algunos productos de ejemplo en el menu.

## Funcionalidades

- **Nuevo Pedido:** elegir cliente, agregar productos con cantidad, ver el total y guardar.
- **Historial:** listar pedidos, buscar por cliente o fecha, ver el detalle, cambiar el
  estado (pendiente / entregado / cancelado) y eliminar pedidos.
- **Menu:** agregar, modificar y eliminar productos (comidas y bebidas).
- **Clientes:** registrar, modificar y eliminar clientes.

## Estructura del proyecto

```
.
├── main.py                      # punto de entrada: inicia la BD y abre la ventana
├── database.py                  # conexion, sesion e inicializacion de la BD
├── seed.py                      # productos de ejemplo para el menu
├── models/                      # modelos y operaciones de base de datos (CRUD)
│   ├── cliente.py
│   ├── producto.py
│   ├── pedido.py
│   └── detalle_pedido.py
└── views/                       # interfaz grafica (Tkinter)
    ├── ventana_principal.py     # ventana con las pestañas
    └── frames.py                # contenido de cada pestaña
```
