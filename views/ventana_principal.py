import tkinter as tk
from tkinter import ttk

from views.frames import NuevoPedidoFrame, HistorialFrame, MenuFrame, ClientesFrame


class VentanaPrincipal(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("McGustavo - Gestion de Pedidos")
        self.geometry("840x640")
        self.minsize(720, 520)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.f_pedido = NuevoPedidoFrame(notebook, session)
        self.f_historial = HistorialFrame(notebook, session)
        self.f_menu = MenuFrame(notebook, session)
        self.f_clientes = ClientesFrame(notebook, session)

        notebook.add(self.f_pedido, text="Nuevo Pedido")
        notebook.add(self.f_historial, text="Historial")
        notebook.add(self.f_menu, text="Menu")
        notebook.add(self.f_clientes, text="Clientes")

        notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_tab)
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _al_cambiar_tab(self, event):
        frame = event.widget.nametowidget(event.widget.select())
        if hasattr(frame, "refrescar"):
            frame.refrescar()

    def _al_cerrar(self):
        self.session.close()
        self.destroy()
