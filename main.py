from database import init_db, sessionLocal
from seed import seed_productos
from views.ventana_principal import VentanaPrincipal


def main():
    init_db()
    session = sessionLocal()
    seed_productos(session)

    app = VentanaPrincipal(session)
    app.mainloop()

    session.close()


if __name__ == "__main__":
    main()
