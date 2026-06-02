from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL =  "sqlite:///./McGustavo.db"

engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass

sessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    # importa los modelos para que se registren en Base antes de crear las tablas
    from models import cliente, producto, pedido, detalle_pedido  # noqa: F401
    Base.metadata.create_all(engine)


def guardar_cambios(session):
    # confirma los cambios; si algo falla deshace la transaccion para no dejar
    # la sesion en estado roto (asi el siguiente intento puede funcionar)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

