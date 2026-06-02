from datetime import datetime

from database import Base, guardar_cambios
from models.cliente import Cliente
from models.detalle_pedido import DetallePedido
from models.producto import Producto
from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session


class Pedido(Base):
    __tablename__ = 'pedidos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey('clientes.id'))
    fecha: Mapped[datetime] = mapped_column(default=datetime.now)
    total: Mapped[float]
    estado: Mapped[str]

    cliente: Mapped['Cliente'] = relationship(back_populates='pedidos')
    detalles: Mapped[list["DetallePedido"]] = relationship(back_populates="pedido", cascade="all, delete-orphan")


class PedidoCRUD:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, cliente_id, items, estado='pendiente'):
        # items: lista de tuplas (producto_id, cantidad)
        pedido = Pedido(cliente_id=cliente_id, total=0, estado=estado)
        total = 0

        for producto_id, cantidad in items:
            producto = self.session.get(Producto, producto_id)
            if producto is None:
                continue
            subtotal = producto.precio * cantidad
            total += subtotal
            pedido.detalles.append(
                DetallePedido(producto_id=producto_id, cantidad=cantidad, subtotal=subtotal)
            )

        pedido.total = total
        self.session.add(pedido)
        guardar_cambios(self.session)
        return pedido

    def listar(self):
        return self.session.scalars(select(Pedido).order_by(Pedido.fecha.desc())).all()

    def obtener(self, id):
        return self.session.get(Pedido, id)

    def buscar(self, nombre=None, fecha=None):
        consulta = select(Pedido).join(Cliente).order_by(Pedido.fecha.desc())

        if nombre:
            consulta = consulta.where(Cliente.nombre.ilike(f"%{nombre}%"))
        if fecha:
            # fecha como texto 'YYYY-MM-DD'; compara contra el dia del pedido
            consulta = consulta.where(func.date(Pedido.fecha) == fecha)

        return self.session.scalars(consulta).all()

    def cambiar_estado(self, id, estado):
        pedido_db = self.session.get(Pedido, id)
        if pedido_db is None:
            return None
        pedido_db.estado = estado
        guardar_cambios(self.session)
        return pedido_db

    def eliminar(self, id):
        pedido_db = self.session.get(Pedido, id)
        if pedido_db:
            self.session.delete(pedido_db)
            guardar_cambios(self.session)
