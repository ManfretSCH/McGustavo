from typing import TYPE_CHECKING

from database import Base, guardar_cambios
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

if TYPE_CHECKING:
    from models.pedido import Pedido


class Cliente(Base):
    __tablename__ = 'clientes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30))
    ruc: Mapped[int] = mapped_column(unique=True)
    tel: Mapped[str] = mapped_column(String(20))
    direccion: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # sirve para relacionar pedido.cliente, acceder al cliente atravez del pedido
    pedidos: Mapped[list['Pedido']] = relationship(back_populates='cliente')


class ClienteCRUD:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre, ruc, tel, direccion = None):
        cliente = Cliente(nombre=nombre, ruc=ruc, tel=tel, direccion=direccion)
        self.session.add(cliente)
        guardar_cambios(self.session)
        return cliente
    
    def listar(self):
        return self.session.scalars(select(Cliente)).all()
    
    def obtener(self, id):
        return self.session.get(Cliente, id)

    def obtener_por_ruc(self, ruc):
        return self.session.scalars(select(Cliente).where(Cliente.ruc == ruc)).first()

    def modificar(self, id, **datos):
        cliente_db = self.session.get(Cliente, id)

        if cliente_db is None:
            return None
        
        for campo, valor in datos.items():
            setattr(cliente_db, campo, valor)

        guardar_cambios(self.session)
        return cliente_db
    
    def eliminar(self, id):
        cliente_db = self.session.get(Cliente, id)
        if cliente_db:
            self.session.delete(cliente_db)
            guardar_cambios(self.session)
    

