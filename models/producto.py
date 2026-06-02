from database import Base, guardar_cambios
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, Session


class Producto(Base):
    __tablename__ = 'productos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30))
    categoria: Mapped[str] = mapped_column(String(20))
    precio: Mapped[float]
    disponible: Mapped[bool] = mapped_column(default=True)


class ProductoCRUD:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre, categoria, precio, disponible=True):
        producto = Producto(nombre=nombre, categoria=categoria, precio=precio, disponible=disponible)
        self.session.add(producto)
        guardar_cambios(self.session)
        return producto

    def listar(self):
        return self.session.scalars(select(Producto).order_by(Producto.categoria, Producto.nombre)).all()

    def listar_por_categoria(self, categoria):
        consulta = select(Producto).where(Producto.categoria == categoria).order_by(Producto.nombre)
        return self.session.scalars(consulta).all()

    def obtener(self, id):
        return self.session.get(Producto, id)

    def modificar(self, id, **datos):
        producto_db = self.session.get(Producto, id)

        if producto_db is None:
            return None

        for campo, valor in datos.items():
            setattr(producto_db, campo, valor)

        guardar_cambios(self.session)
        return producto_db

    def eliminar(self, id):
        producto_db = self.session.get(Producto, id)
        if producto_db:
            self.session.delete(producto_db)
            guardar_cambios(self.session)
