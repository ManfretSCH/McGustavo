from sqlalchemy import select

from models.producto import Producto

PRODUCTOS_INICIALES = [
    ("Hamburguesa Clasica", "Comida", 25000),
    ("Hamburguesa Doble", "Comida", 35000),
    ("Papas Fritas", "Comida", 12000),
    ("Pollo Crispy", "Comida", 28000),
    ("Hot Dog", "Comida", 18000),
    ("Gaseosa", "Bebida", 8000),
    ("Agua Mineral", "Bebida", 6000),
    ("Cerveza", "Bebida", 15000),
    ("Jugo Natural", "Bebida", 10000),
]


def seed_productos(session):
    # solo carga los productos de ejemplo si la tabla esta vacia
    existe = session.scalars(select(Producto).limit(1)).first()
    if existe:
        return

    for nombre, categoria, precio in PRODUCTOS_INICIALES:
        session.add(Producto(nombre=nombre, categoria=categoria, precio=precio))

    session.commit()
