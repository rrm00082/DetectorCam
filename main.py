
from UI import VentanaUsuario # Importar la clase desde el archivo separado
import tkinter as tk  # Para crear la ventana principal

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaUsuario(root)
    root.mainloop()