import os
import datetime
import cv2
from PIL import Image, ImageTk
import time
import threading
from ultralytics import YOLO

class Camara:
    def __init__(self, widget):
        self.cap = None
        self.widget = widget
        self.model = YOLO("yolo11n.pt")  # Cargar modelo YOLO
        self.camaras_disponibles = self.detectar_camaras()
        self.indice_camara_actual = 0
        self.capturas = {}
        self.hilos_camaras = {}
        self.running = True

        # Parámetros para detección de movimiento
        self.prev_frames = {}
        self.min_area = 500
        self.diff_threshold = 20
        self.no_movement_duration = 5

        # Diccionarios para manejar datos por cámara
        self.last_movement_time = {}
        self.movimiento_activo = {}
        self.video_writers = {}

        # Inicializar los estados por cámara
        for i in self.camaras_disponibles:
            self.last_movement_time[i] = time.time()
            self.movimiento_activo[i] = False

        # Iniciar todas las cámaras disponibles en hilos separados
        for i in self.camaras_disponibles:
            self.hilos_camaras[i] = threading.Thread(target=self.capturar_video, args=(i,))
            self.hilos_camaras[i].start()

    def actualizar_feed(self):
        """Muestra el feed de la cámara seleccionada."""
        if not self.running:
            return

        if self.indice_camara_actual in self.capturas:
            frame = self.capturas[self.indice_camara_actual]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = Image.fromarray(frame_rgb)
            imagen_tk = ImageTk.PhotoImage(imagen)
            self.widget.config(image=imagen_tk)
            self.widget.image = imagen_tk

        self.widget.after(17, self.actualizar_feed)

    def iniciar_camara(self):
        """Inicia la captura desde la cámara actual."""
        if not self.camaras_disponibles:
            print("No hay cámaras disponibles.")
            return

        self.cap = cv2.VideoCapture(self.camaras_disponibles[self.indice_camara_actual])

        self.running = True
        self.actualizar_feed()

    def detectar_camaras(self):
        """Dectecta todas las camara disponibles desde el ordenador."""
        camaras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print("camaraOptenida")
                    camaras.append(i)
                cap.release()
            else:
                cap.release()
        return camaras

    def cambiar_camara(self, direccion):
        """Cambia a la siguiente cámara activa sin detener las demás."""
        camaras_activas = list(self.capturas.keys())

        if not camaras_activas:
            print("⚠️ No hay cámaras activas con capturas.")
            return

        indice_actual = camaras_activas.index(
            self.indice_camara_actual) if self.indice_camara_actual in camaras_activas else 0
        self.indice_camara_actual = camaras_activas[(indice_actual + direccion) % len(camaras_activas)]

        print(f"🔄 Cámara actual: {self.indice_camara_actual}")

    def capturar_video(self, indice):
        cap = cv2.VideoCapture(indice)
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self.detectar_movimiento(indice, frame)
                self.capturas[indice] = frame

                # Si se está grabando para esta cámara, escribir el frame en el archivo
                if self.movimiento_activo.get(indice, False) and indice in self.video_writers:
                    self.video_writers[indice].write(frame)
        cap.release()

    def detectar_movimiento(self, indice, frame):
        """Detecta movimiento y llama a grabar si es necesario."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if indice not in self.prev_frames:
            self.prev_frames[indice] = gray
            self.last_movement_time[indice] = time.time()
            self.movimiento_activo[indice] = False
            return

        diff = cv2.absdiff(self.prev_frames[indice], gray)
        thresh = cv2.threshold(diff, self.diff_threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contornos, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Si detecta movimiento en los contornos empezamos a analizar si es humano
        if any(cv2.contourArea(c) > self.min_area for c in contornos):
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model(frame_rgb, verbose=False)
            count_personas = sum(1 for r in results[0].boxes if int(r.cls) == 0 and r.conf > 0.6)
            """Si se detecta al menos una persona actualizamos el ultimo tiempo en el que se detectó
            esto lo que hace deja un espacio para volver a detectar un humano para que no salgan muchos videos 
            cortos en donde solo aparece una persona y hace en un video conjunto."""
            if count_personas > 0:
                print(f"📷 Movimiento en cámara {indice} | Personas detectadas: {count_personas}")
                self.last_movement_time[indice] = time.time()

                # Si no se está grabando, se inicia la grabación
                if not self.movimiento_activo[indice]:
                    self.grabar(indice)

        # Si transcurre el tiempo sin detectar movimiento, se detiene la grabación
        if self.movimiento_activo[indice] and time.time() - self.last_movement_time[indice] >= self.no_movement_duration:
            print(f"⏹️ No se detecta movimiento en cámara {indice}, deteniendo grabación...")
            self.grabar(indice)

        self.prev_frames[indice] = gray

    def grabar(self, indice):
        """Inicia o detiene la grabación de la cámara especificada."""
        if self.movimiento_activo.get(indice, False):
            print(f"⏹️ La cámara {indice} ya está grabando. Deteniendo grabación...")
            if indice in self.video_writers and self.video_writers[indice].isOpened():
                self.video_writers[indice].release()
                del self.video_writers[indice]
            self.movimiento_activo[indice] = False
            print(f"⏹️ Grabación detenida para la cámara {indice}.")
        else:
            print(f"▶️ Iniciando grabación para la cámara {indice}...")
            if not os.path.exists("video"):
                os.makedirs("video")

            if indice not in self.capturas or self.capturas[indice] is None:
                print(f"⚠️ No se puede iniciar grabación: no hay frames válidos para la cámara {indice}.")
                return

            frame = self.capturas[indice]
            height, width = frame.shape[:2]

            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            video_filename = f"video/camara{indice}_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.avi"

            # Reducimos los FPS de grabación; esto desacelerará la reproducción del video.
            self.video_writers[indice] = cv2.VideoWriter(video_filename, fourcc, 10.0, (width, height))

            if not self.video_writers[indice].isOpened():
                print(f"⚠️ No se pudo abrir el archivo de video para la cámara {indice}.")
                return

            self.movimiento_activo[indice] = True
            print(f"▶️ Grabación iniciada: {video_filename}")

    def detener_camara(self):
        """Detiene todas las cámaras."""
        self.running = False
        for hilo in self.hilos_camaras.values():
            if hilo.is_alive():
                hilo.join()
        if self.cap:
            self.cap.release()
        self.widget.config(image="")
        print("Cámaras detenidas correctamente.")