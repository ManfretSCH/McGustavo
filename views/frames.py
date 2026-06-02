import tkinter as tk
from tkinter import ttk, messagebox

from models.cliente import ClienteCRUD
from models.producto import ProductoCRUD
from models.pedido import PedidoCRUD


def formato_moneda(valor):
    return f"{valor:,.0f}".replace(",", ".")


class NuevoPedidoFrame(ttk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent, padding=10)
        self.cliente_crud = ClienteCRUD(session)
        self.producto_crud = ProductoCRUD(session)
        self.pedido_crud = PedidoCRUD(session)
        self.cliente_id = None    # cliente seleccionado por RUC
        self.productos_map = {}   # texto -> (id, precio, nombre)
        self.items = []           # dicts: producto_id, nombre, cantidad, subtotal
        self._construir()
        self.refrescar()

    def _construir(self):
        sel = ttk.LabelFrame(self, text="Nuevo pedido", padding=10)
        sel.pack(fill="x")

        fila_cliente = ttk.Frame(sel)
        fila_cliente.pack(fill="x", pady=3)
        ttk.Label(fila_cliente, text="RUC cliente", width=10).pack(side="left")
        self.ruc_entry = ttk.Entry(fila_cliente, width=18)
        self.ruc_entry.pack(side="left")
        self.ruc_entry.bind("<Return>", lambda e: self.buscar_cliente())
        ttk.Button(fila_cliente, text="Buscar", command=self.buscar_cliente).pack(side="left", padx=5)
        self.lbl_cliente = ttk.Label(fila_cliente, text="Cliente: (ninguno)")
        self.lbl_cliente.pack(side="left", padx=10)

        fila_prod = ttk.Frame(sel)
        fila_prod.pack(fill="x", pady=3)
        ttk.Label(fila_prod, text="Producto", width=9).pack(side="left")
        self.producto_cb = ttk.Combobox(fila_prod, state="readonly")
        self.producto_cb.pack(side="left", fill="x", expand=True)
        ttk.Label(fila_prod, text="Cantidad").pack(side="left", padx=(10, 3))
        self.cantidad = ttk.Spinbox(fila_prod, from_=1, to=99, width=5)
        self.cantidad.set(1)
        self.cantidad.pack(side="left")
        ttk.Button(fila_prod, text="Agregar al pedido", command=self.agregar_item).pack(side="left", padx=(10, 0))

        columnas = ("producto", "cantidad", "subtotal")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=10)
        for col, txt, ancho in [("producto", "Producto", 260), ("cantidad", "Cantidad", 100), ("subtotal", "Subtotal", 140)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True, pady=8)

        pie = ttk.Frame(self)
        pie.pack(fill="x")
        ttk.Button(pie, text="Quitar item", command=self.quitar_item).pack(side="left", padx=3)
        ttk.Button(pie, text="Guardar pedido", command=self.guardar).pack(side="left", padx=3)
        ttk.Button(pie, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)
        self.lbl_total = ttk.Label(pie, text="TOTAL: 0", font=("TkDefaultFont", 12, "bold"))
        self.lbl_total.pack(side="right", padx=10)

    def refrescar(self):
        self.productos_map = {}
        valores_p = []
        for p in self.producto_crud.listar():
            if not p.disponible:
                continue
            texto = f"{p.nombre} ({formato_moneda(p.precio)})"
            self.productos_map[texto] = (p.id, p.precio, p.nombre)
            valores_p.append(texto)
        self.producto_cb["values"] = valores_p

    def buscar_cliente(self):
        ruc_txt = self.ruc_entry.get().strip()
        if not ruc_txt.isdigit():
            messagebox.showwarning("RUC invalido", "Ingresa un RUC numerico.")
            return
        cliente = self.cliente_crud.obtener_por_ruc(int(ruc_txt))
        if cliente is None:
            self.cliente_id = None
            self.lbl_cliente.config(text="Cliente: no encontrado")
            messagebox.showinfo("Sin resultados", "No hay un cliente con ese RUC.\nPodes registrarlo en la pestaña Clientes.")
            return
        self.cliente_id = cliente.id
        self.lbl_cliente.config(text=f"Cliente: {cliente.nombre}")

    def agregar_item(self):
        texto = self.producto_cb.get()
        if not texto:
            messagebox.showwarning("Sin producto", "Selecciona un producto.")
            return
        try:
            cantidad = int(self.cantidad.get())
        except ValueError:
            cantidad = 0
        if cantidad <= 0:
            messagebox.showwarning("Cantidad invalida", "La cantidad debe ser mayor a 0.")
            return
        producto_id, precio, nombre = self.productos_map[texto]
        subtotal = precio * cantidad
        self.items.append({"producto_id": producto_id, "nombre": nombre, "cantidad": cantidad, "subtotal": subtotal})
        self._render_items()

    def quitar_item(self):
        sel = self.tabla.selection()
        if not sel:
            return
        indice = self.tabla.index(sel[0])
        del self.items[indice]
        self._render_items()

    def _render_items(self):
        self.tabla.delete(*self.tabla.get_children())
        total = 0
        for it in self.items:
            self.tabla.insert("", "end", values=(it["nombre"], it["cantidad"], formato_moneda(it["subtotal"])))
            total += it["subtotal"]
        self.lbl_total.config(text=f"TOTAL: {formato_moneda(total)}")

    def guardar(self):
        if self.cliente_id is None:
            messagebox.showwarning("Sin cliente", "Busca un cliente por su RUC antes de guardar.")
            return
        if not self.items:
            messagebox.showwarning("Sin productos", "Agrega al menos un producto al pedido.")
            return
        items = [(it["producto_id"], it["cantidad"]) for it in self.items]
        pedido = self.pedido_crud.crear(self.cliente_id, items)
        messagebox.showinfo("Pedido guardado", f"Pedido #{pedido.id} guardado.\nTotal: {formato_moneda(pedido.total)}")
        self.limpiar()

    def limpiar(self):
        self.items = []
        self._render_items()
        self.cliente_id = None
        self.ruc_entry.delete(0, "end")
        self.lbl_cliente.config(text="Cliente: (ninguno)")
        self.producto_cb.set("")
        self.cantidad.set(1)


class HistorialFrame(ttk.Frame):
    ESTADOS = ["pendiente", "entregado", "cancelado"]

    def __init__(self, parent, session):
        super().__init__(parent, padding=10)
        self.crud = PedidoCRUD(session)
        self._construir()
        self.refrescar()

    def _construir(self):
        busq = ttk.LabelFrame(self, text="Buscar", padding=10)
        busq.pack(fill="x")
        ttk.Label(busq, text="Cliente").pack(side="left", padx=(0, 3))
        self.b_nombre = ttk.Entry(busq, width=20)
        self.b_nombre.pack(side="left", padx=(0, 10))
        ttk.Label(busq, text="Fecha (AAAA-MM-DD)").pack(side="left", padx=(0, 3))
        self.b_fecha = ttk.Entry(busq, width=14)
        self.b_fecha.pack(side="left", padx=(0, 10))
        ttk.Button(busq, text="Buscar", command=self.buscar).pack(side="left", padx=3)
        ttk.Button(busq, text="Todo", command=self.refrescar).pack(side="left", padx=3)

        cols = ("id", "cliente", "fecha", "total", "estado")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for col, txt, ancho in [("id", "ID", 50), ("cliente", "Cliente", 180), ("fecha", "Fecha", 150), ("total", "Total", 120), ("estado", "Estado", 100)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True, pady=8)
        self.tabla.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        acc = ttk.Frame(self)
        acc.pack(fill="x")
        ttk.Label(acc, text="Estado:").pack(side="left", padx=3)
        self.estado_cb = ttk.Combobox(acc, values=self.ESTADOS, state="readonly", width=12)
        self.estado_cb.pack(side="left", padx=3)
        ttk.Button(acc, text="Cambiar estado", command=self.cambiar_estado).pack(side="left", padx=3)
        ttk.Button(acc, text="Eliminar pedido", command=self.eliminar).pack(side="left", padx=3)

        det = ttk.LabelFrame(self, text="Detalle del pedido", padding=10)
        det.pack(fill="both", expand=True, pady=8)
        cols_d = ("producto", "cantidad", "subtotal")
        self.tabla_det = ttk.Treeview(det, columns=cols_d, show="headings", height=6)
        for col, txt, ancho in [("producto", "Producto", 260), ("cantidad", "Cantidad", 100), ("subtotal", "Subtotal", 140)]:
            self.tabla_det.heading(col, text=txt)
            self.tabla_det.column(col, width=ancho)
        self.tabla_det.pack(fill="both", expand=True)

    def _seleccion_id(self):
        sel = self.tabla.selection()
        if not sel:
            return None
        return int(self.tabla.item(sel[0], "values")[0])

    def _llenar(self, pedidos):
        self.tabla.delete(*self.tabla.get_children())
        for p in pedidos:
            self.tabla.insert("", "end", values=(
                p.id, p.cliente.nombre, p.fecha.strftime("%Y-%m-%d %H:%M"),
                formato_moneda(p.total), p.estado,
            ))
        self.tabla_det.delete(*self.tabla_det.get_children())

    def refrescar(self):
        self.b_nombre.delete(0, "end")
        self.b_fecha.delete(0, "end")
        self._llenar(self.crud.listar())

    def buscar(self):
        nombre = self.b_nombre.get().strip() or None
        fecha = self.b_fecha.get().strip() or None
        self._llenar(self.crud.buscar(nombre=nombre, fecha=fecha))

    def mostrar_detalle(self, event=None):
        pid = self._seleccion_id()
        if pid is None:
            return
        pedido = self.crud.obtener(pid)
        self.tabla_det.delete(*self.tabla_det.get_children())
        if pedido is None:
            return
        for d in pedido.detalles:
            self.tabla_det.insert("", "end", values=(d.producto.nombre, d.cantidad, formato_moneda(d.subtotal)))

    def cambiar_estado(self):
        pid = self._seleccion_id()
        if pid is None:
            messagebox.showwarning("Sin seleccion", "Selecciona un pedido de la tabla.")
            return
        estado = self.estado_cb.get()
        if not estado:
            messagebox.showwarning("Sin estado", "Elegi un estado.")
            return
        self.crud.cambiar_estado(pid, estado)
        self.refrescar()

    def eliminar(self):
        pid = self._seleccion_id()
        if pid is None:
            messagebox.showwarning("Sin seleccion", "Selecciona un pedido de la tabla.")
            return
        if not messagebox.askyesno("Confirmar", f"Eliminar el pedido #{pid}?"):
            return
        self.crud.eliminar(pid)
        self.refrescar()


class MenuFrame(ttk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent, padding=10)
        self.crud = ProductoCRUD(session)
        self.seleccion_id = None
        self._construir()
        self.refrescar()

    def _construir(self):
        form = ttk.LabelFrame(self, text="Producto", padding=10)
        form.pack(fill="x")
        ttk.Label(form, text="Nombre").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.nombre = ttk.Entry(form, width=30) 
        self.nombre.grid(row=0, column=1, padx=5, pady=3)
        ttk.Label(form, text="Categoria").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.categoria = ttk.Combobox(form, values=["Comida", "Bebida"], state="readonly", width=15)
        self.categoria.set("Comida")
        self.categoria.grid(row=0, column=3, padx=5, pady=3)
        ttk.Label(form, text="Precio").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.precio = ttk.Entry(form, width=30)
        self.precio.grid(row=1, column=1, padx=5, pady=3)
        self.disponible = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Disponible", variable=self.disponible).grid(row=1, column=3, sticky="w", padx=5, pady=3)

        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=8)
        ttk.Button(botones, text="Agregar", command=self.agregar).pack(side="left", padx=3)
        ttk.Button(botones, text="Modificar", command=self.modificar).pack(side="left", padx=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)

        cols = ("id", "nombre", "categoria", "precio", "disponible")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for col, txt, ancho in [("id", "ID", 40), ("nombre", "Nombre", 200), ("categoria", "Categoria", 120), ("precio", "Precio", 120), ("disponible", "Disponible", 100)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.crud.listar():
            self.tabla.insert("", "end", values=(p.id, p.nombre, p.categoria, formato_moneda(p.precio), "Si" if p.disponible else "No"))

    def al_seleccionar(self, event=None):
        sel = self.tabla.selection()
        if not sel:
            return
        v = self.tabla.item(sel[0], "values")
        self.seleccion_id = int(v[0])
        self.nombre.delete(0, "end"); self.nombre.insert(0, v[1])
        self.categoria.set(v[2])
        self.precio.delete(0, "end"); self.precio.insert(0, v[3].replace(".", ""))
        self.disponible.set(v[4] == "Si")

    def _leer_form(self):
        nombre = self.nombre.get().strip()
        categoria = self.categoria.get().strip()
        precio_txt = self.precio.get().strip().replace(".", "").replace(",", ".")
        if not nombre or not categoria:
            messagebox.showwarning("Datos incompletos", "Nombre y categoria son obligatorios.")
            return None
        try:
            precio = float(precio_txt)
        except ValueError:
            messagebox.showwarning("Dato invalido", "El precio debe ser numerico.")
            return None
        return nombre, categoria, precio, self.disponible.get()

    def agregar(self):
        datos = self._leer_form()
        if datos is None:
            return
        self.crud.crear(*datos)
        self.limpiar()
        self.refrescar()

    def modificar(self):
        if self.seleccion_id is None:
            messagebox.showwarning("Sin seleccion", "Selecciona un producto de la tabla.")
            return
        datos = self._leer_form()
        if datos is None:
            return
        nombre, categoria, precio, disponible = datos
        try:
            self.crud.modificar(self.seleccion_id, nombre=nombre, categoria=categoria, precio=precio, disponible=disponible)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el producto:\n{e}")
            return
        self.limpiar()
        self.refrescar()

    def eliminar(self):
        if self.seleccion_id is None:
            messagebox.showwarning("Sin seleccion", "Selecciona un producto de la tabla.")
            return
        if not messagebox.askyesno("Confirmar", "Eliminar el producto seleccionado?"):
            return
        try:
            self.crud.eliminar(self.seleccion_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar (puede estar en pedidos):\n{e}")
            return
        self.limpiar()
        self.refrescar()

    def limpiar(self):
        self.seleccion_id = None
        self.nombre.delete(0, "end")
        self.precio.delete(0, "end")
        self.categoria.set("Comida")
        self.disponible.set(True)
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())


class ClientesFrame(ttk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent, padding=10)
        self.crud = ClienteCRUD(session)
        self.seleccion_id = None
        self._construir()
        self.refrescar()

    def _construir(self):
        form = ttk.LabelFrame(self, text="Datos del cliente", padding=10)
        form.pack(fill="x")
        ttk.Label(form, text="Nombre").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.nombre = ttk.Entry(form, width=30)
        self.nombre.grid(row=0, column=1, padx=5, pady=3)
        ttk.Label(form, text="RUC").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.ruc = ttk.Entry(form, width=20)
        self.ruc.grid(row=0, column=3, padx=5, pady=3)
        ttk.Label(form, text="Telefono").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.tel = ttk.Entry(form, width=30)
        self.tel.grid(row=1, column=1, padx=5, pady=3)
        ttk.Label(form, text="Direccion").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self.direccion = ttk.Entry(form, width=20)
        self.direccion.grid(row=1, column=3, padx=5, pady=3)

        botones = ttk.Frame(self)
        botones.pack(fill="x", pady=8)
        ttk.Button(botones, text="Agregar", command=self.agregar).pack(side="left", padx=3)
        ttk.Button(botones, text="Modificar", command=self.modificar).pack(side="left", padx=3)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=3)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)

        cols = ("id", "nombre", "ruc", "tel", "direccion")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for col, txt, ancho in [("id", "ID", 40), ("nombre", "Nombre", 180), ("ruc", "RUC", 120), ("tel", "Telefono", 120), ("direccion", "Direccion", 200)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=ancho)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

    def refrescar(self):
        self.tabla.delete(*self.tabla.get_children())
        for c in self.crud.listar():
            self.tabla.insert("", "end", values=(c.id, c.nombre, c.ruc, c.tel, c.direccion or ""))

    def al_seleccionar(self, event=None):
        sel = self.tabla.selection()
        if not sel:
            return
        v = self.tabla.item(sel[0], "values")
        self.seleccion_id = int(v[0])
        self.nombre.delete(0, "end"); self.nombre.insert(0, v[1])
        self.ruc.delete(0, "end"); self.ruc.insert(0, v[2])
        self.tel.delete(0, "end"); self.tel.insert(0, v[3])
        self.direccion.delete(0, "end"); self.direccion.insert(0, v[4])

    def _leer_form(self):
        nombre = self.nombre.get().strip()
        ruc_txt = self.ruc.get().strip()
        tel = self.tel.get().strip()
        direccion = self.direccion.get().strip() or None
        if not nombre or not ruc_txt:
            messagebox.showwarning("Datos incompletos", "Nombre y RUC son obligatorios.")
            return None
        if not ruc_txt.isdigit():
            messagebox.showwarning("Dato invalido", "El RUC debe ser numerico.")
            return None
        return nombre, int(ruc_txt), tel, direccion

    def agregar(self):
        datos = self._leer_form()
        if datos is None:
            return
        nombre, ruc, tel, direccion = datos
        try:
            self.crud.crear(nombre, ruc, tel, direccion)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el cliente (el RUC ya existe?):\n{e}")
            return
        self.limpiar()
        self.refrescar()

    def modificar(self):
        if self.seleccion_id is None:
            messagebox.showwarning("Sin seleccion", "Selecciona un cliente de la tabla.")
            return
        datos = self._leer_form()
        if datos is None:
            return
        nombre, ruc, tel, direccion = datos
        try:
            self.crud.modificar(self.seleccion_id, nombre=nombre, ruc=ruc, tel=tel, direccion=direccion)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el cliente (el RUC ya existe?):\n{e}")
            return
        self.limpiar()
        self.refrescar()

    def eliminar(self):
        if self.seleccion_id is None:
            messagebox.showwarning("Sin seleccion", "Selecciona un cliente de la tabla.")
            return
        if not messagebox.askyesno("Confirmar", "Eliminar el cliente seleccionado?"):
            return
        try:
            self.crud.eliminar(self.seleccion_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar (puede tener pedidos):\n{e}")
            return
        self.limpiar()
        self.refrescar()

    def limpiar(self):
        self.seleccion_id = None
        for w in (self.nombre, self.ruc, self.tel, self.direccion):
            w.delete(0, "end")
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())
