from typing import TYPE_CHECKING

from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.pedido import Pedido
    from models.producto import Producto


class DetallePedido(Base):
    __tablename__ = 'detalle_pedidos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey('pedidos.id'))
    producto_id: Mapped[int] = mapped_column(ForeignKey('productos.id'))
    cantidad: Mapped[int]
    subtotal: Mapped[float]

    pedido: Mapped['Pedido'] = relationship(back_populates='detalles')
    producto: Mapped['Producto'] = relationship()
