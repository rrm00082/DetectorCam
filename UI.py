from camara import Camara  # Importar la clase para manejar la cámara
import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import sys  # Para identificar el sistema operativo


class VentanaUsuario:
    def __init__(self, root):
        self.root = root
        self.colorFondo = "#aed6f1"
        self.colorLateral = "#2a3138"
        self.camara = None
        self.video_label = None  # Etiqueta para mostrar la cámara

        # Configurar la ventana principal
        self.configurar_ventana()

        # Configurar Pantalla Principal
        self.mostrar_frame_principal()
        self.agregar_botones_navegacion()
        self.colocar_etiqueta_video()
        self.mostrar_frame_principal()

        # Configurar Barra Lateral
        self.crear_barra_lateral()

    def configurar_ventana(self):
        self.root.title("Detector de movimiento")

        # Evitar redimensionado
        self.root.resizable(False, False)

        # Icono de la ventana (diferente en Windows y Linux)
        if sys.platform == "win32":
            self.root.iconbitmap("logo.ico")
        else:
            icon = tk.PhotoImage(file="logo.png")
            self.root.iconphoto(False, icon)

        # Medidas originales
        alto = int(self.root.winfo_screenheight() / 2)
        ancho = int(self.root.winfo_screenwidth() / 2)
        self.root.geometry(f"{ancho}x{alto}")
        self.root.config(background=self.colorFondo)
        self.root.config(cursor="dotbox")

    def agregar_botones_navegacion(self):
        espacio_entre_botones = 60
        posicion_x_base = int(self.root.winfo_screenwidth() * 0.30)

        btn_izquierda = tk.Button(self.root, text="<", command=lambda: self.camara.cambiar_camara(-1), width=5)
        btn_derecha = tk.Button(self.root, text=">", command=lambda: self.camara.cambiar_camara(1), width=5)

        btn_izquierda.place(x=posicion_x_base - espacio_entre_botones, y=int(self.root.winfo_screenheight() * 0.45))
        btn_derecha.place(x=posicion_x_base + espacio_entre_botones, y=int(self.root.winfo_screenheight() * 0.45))

    def mostrar_frame_principal(self):
        self.recuadroCamara = tk.Frame(
            self.root,
            bg="white",
            width=int(self.root.winfo_screenwidth() * 0.37),
            height=int(self.root.winfo_screenheight() * 0.4)
        )
        self.recuadroCamara.place(
            x=int(self.root.winfo_screenwidth() * 0.12),
            y=int(self.root.winfo_screenheight() * 0.03)
        )

    def colocar_etiqueta_video(self):
        self.video_label = tk.Label(
            self.recuadroCamara,
            bg="black",
            width=int(self.root.winfo_screenwidth() * 0.37),
            height=int(self.root.winfo_screenheight() * 0.4)
        )
        self.video_label.place(x=0, y=0)

    def crear_barra_lateral(self):
        self.root.update_idletasks()

        BarraLateral = tk.Frame(self.root, bg=self.colorLateral, width=int(self.root.winfo_width() / 4.49))
        BarraLateral.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(BarraLateral, text="Usuario:", bg=self.colorLateral, fg="white", font=("Arial", 12)).place(x=10, y=25)
        self.cuadroTexto = tk.Entry(BarraLateral)
        self.cuadroTexto.place(x=10, y=50)

        tk.Label(BarraLateral, text="Contraseña:", bg=self.colorLateral, fg="white", font=("Arial", 12)).place(x=10,
                                                                                                               y=75)
        self.cuadroTexto2 = tk.Entry(BarraLateral, show="*")
        self.cuadroTexto2.place(x=10, y=100)

        self.btn_iniciar = tk.Button(BarraLateral, text="Iniciar", command=self.iniciar)
        self.btn_iniciar.place(x=10, y=130)
        tk.Button(BarraLateral, text="Parar", command=self.detener_camara).place(x=90, y=130)
        tk.Button(BarraLateral, text="Crear Usuario", command=self.ventana_usuario).place(x=10, y=180)

    def detener_camara(self):
        if self.camara:
            self.camara.detener_camara()
            self.camara = None

        if self.btn_iniciar:
            self.btn_iniciar.config(state=tk.NORMAL)

        if self.recuadroCamara:
            self.recuadroCamara.place(
                x=int(self.root.winfo_screenwidth() * 0.12),
                y=int(self.root.winfo_screenheight() * 0.03)
            )

    def iniciar(self):
        nombre2 = self.cuadroTexto.get().strip()
        passwd2 = self.cuadroTexto2.get().strip()
        archivo = "usuarios.txt"

        if not os.path.exists(archivo):
            messagebox.showerror("Error", "El archivo de usuarios no existe.")
            return

        hashed_passwd = hashlib.sha256(passwd2.encode()).hexdigest()

        with open(archivo, "r") as f:
            for linea in f:
                usuario_guardado, contraseña_guardada = linea.strip().split(":")
                if usuario_guardado == nombre2 and contraseña_guardada == hashed_passwd:
                    if self.recuadroCamara:
                        self.recuadroCamara.place_forget()

                    self.camara = Camara(self.video_label)
                    self.camara.iniciar_camara()

                    self.btn_iniciar.config(state=tk.DISABLED)
                    return

        messagebox.showerror("Error", "Usuario o contraseña incorrectos. Intenta de nuevo.")

    def ventana_usuario(self):
        """
        Abre una ventana para crear un nuevo usuario en Linux.
        """
        winUser = tk.Toplevel(self.root)
        winUser.title("Crea Usuario")

        # Cargar icono según sistema operativo
        if sys.platform == "win32":
            winUser.iconbitmap("logo.ico")
        else:
            icon_path = os.path.join(os.getcwd(), "logo.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                winUser.iconphoto(False, icon)

        # Ajustar tamaño según pantalla
        altowinUser = int(self.root.winfo_screenheight() / 4)
        anchowinUser = int(self.root.winfo_screenwidth() / 4)
        winUser.geometry(f"{anchowinUser}x{altowinUser}")
        winUser.config(background=self.colorFondo)

        # Etiquetas y cuadros de texto
        tk.Label(winUser, text="Crear Usuario", fg="Black", bg=self.colorFondo, font=("Arial", 20)).place(x=10, y=20)
        tk.Label(winUser, text="Usuario", bg=self.colorFondo, fg="Black", font=("Arial", 12)).place(x=10, y=75)
        cuadroTexto3 = tk.Entry(winUser)
        cuadroTexto3.place(x=10, y=100)

        tk.Label(winUser, text="Contraseña", bg=self.colorFondo, fg="Black", font=("Arial", 12)).place(x=10, y=125)
        cuadroTexto4 = tk.Entry(winUser, show="*")
        cuadroTexto4.place(x=10, y=150)

        def crea_usuario():
            """Crea un usuario y guarda en 'usuarios.txt' con permisos adecuados."""
            user3 = cuadroTexto3.get().strip()
            passwd3 = cuadroTexto4.get().strip()

            if not user3 or not passwd3:
                messagebox.showerror("Error", "Usuario o contraseña están vacíos. Intenta de nuevo.")
                return

            hashed_passwd = hashlib.sha256(passwd3.encode()).hexdigest()
            archivo = os.path.join(os.getcwd(), "usuarios.txt")

            # Crear el archivo si no existe con permisos adecuados en Linux
            if not os.path.exists(archivo):
                with open(archivo, "w") as f:
                    print(f"Archivo '{archivo}' creado.")
                os.chmod(archivo, 0o600)  # Permisos: solo lectura/escritura para el propietario

            # Verificar si el usuario ya existe
            with open(archivo, "r") as f:
                for linea in f:
                    usuario_guardado, _ = linea.strip().split(":")
                    if usuario_guardado == user3:
                        messagebox.showerror("Error", "El usuario ya existe.")
                        return

            # Guardar el nuevo usuario
            with open(archivo, "a") as f:
                f.write(f"{user3}:{hashed_passwd}\n")
            messagebox.showinfo("Éxito", f"Usuario '{user3}' creado exitosamente.")

        # Botón para crear el usuario
        tk.Button(winUser, text="Crear", command=crea_usuario).place(x=10, y=180)