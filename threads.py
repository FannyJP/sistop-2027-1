
import threading
import queue


class AdministradorHilos:

    def __init__(self, operaciones):

        self.operaciones = operaciones

        # Cola de solicitudes para el trabajador.
        self.cola = queue.Queue()

        # Cola de estados que procesa el supervisor.
        self.cola_estados = queue.Queue()

        # Cola de mensajes para mostrar posteriormente en el menú.
        self.cola_mensajes = queue.Queue()

        # Evento para detener al supervisor.
        self.detener = threading.Event()

        # Hilo trabajador.
        self.hilo_trabajador = threading.Thread(
            target=self.procesar_solicitudes,
            name="Hilo-Trabajador"
        )

        # Hilo supervisor.
        self.hilo_supervisor = threading.Thread(
            target=self.supervisar,
            name="Hilo-Supervisor"
        )

    def iniciar(self):

        self.hilo_trabajador.start()
        self.hilo_supervisor.start()

        print("Los dos hilos se iniciaron correctamente")

    def enviar_solicitud(self, operacion, nombre, ruta=None):

        solicitud = {
            "operacion": operacion,
            "nombre": nombre,
            "ruta": ruta,
            "evento": threading.Event(),
            "resultado": None,
            "error": None
        }

        # Enviar la solicitud al trabajador.
        self.cola.put(solicitud)

        # Esperar a que termine la operación.
        solicitud["evento"].wait()

        if solicitud["error"] is not None:
            raise RuntimeError(solicitud["error"])

        return solicitud["resultado"]

    def procesar_solicitudes(self):

        while True:

            solicitud = self.cola.get()

            # None indica que el trabajador debe terminar.
            if solicitud is None:
                self.cola.task_done()
                break

            operacion = solicitud["operacion"]
            nombre = solicitud["nombre"]
            ruta = solicitud["ruta"]

            self.cola_estados.put(
                f"Iniciando operacion: {operacion}"
            )

            try:

                if operacion == "copiar_desde":

                    resultado = (
                        self.operaciones.copiar_desde_fiunamfs(
                            nombre
                        )
                    )

                elif operacion == "copiar_hacia":

                    resultado = (
                        self.operaciones.copiar_a_fiunamfs(
                            ruta
                        )
                    )

                elif operacion == "eliminar":

                    resultado = (
                        self.operaciones.eliminar_archivo(
                            nombre
                        )
                    )

                else:

                    raise ValueError(
                        f"Operacion no reconocida: {operacion}"
                    )

                solicitud["resultado"] = resultado

                self.cola_estados.put(
                    f"Operacion completada: {operacion}"
                )

            except Exception as error:

                solicitud["error"] = (
                    f"{type(error).__name__}: {error}"
                )

                self.cola_estados.put(
                    f"Error en operacion: {operacion}"
                )

            finally:

                # Avisar al menú que la solicitud terminó.
                solicitud["evento"].set()

                self.cola.task_done()

    def supervisar(self):

        while (
            not self.detener.is_set()
            or not self.cola_estados.empty()
        ):

            try:

                estado = self.cola_estados.get(
                    timeout=0.5
                )

                # El supervisor almacena el mensaje.
                # No imprime directamente en la consola.
                self.cola_mensajes.put(estado)

                self.cola_estados.task_done()

            except queue.Empty:

                continue

    def obtener_mensajes(self):

        # Esperar a que el supervisor procese todos
        # los estados enviados hasta este momento.
        self.cola_estados.join()

        mensajes = []

        while not self.cola_mensajes.empty():

            try:
                mensajes.append(
                    self.cola_mensajes.get_nowait()
                )

            except queue.Empty:
                break

        return mensajes

    def finalizar(self):

        print("\nFinalizando los hilos...")

        # Esperar las solicitudes pendientes.
        self.cola.join()

        # Enviar señal para terminar al trabajador.
        self.cola.put(None)

        # Esperar al trabajador.
        self.hilo_trabajador.join()

        # Esperar a que el supervisor procese
        # todos los estados restantes.
        self.cola_estados.join()

        # Detener al supervisor.
        self.detener.set()

        # Esperar al supervisor.
        self.hilo_supervisor.join()

        print("Los hilos finalizaron correctamente")
