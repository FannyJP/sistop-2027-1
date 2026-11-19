import os
import math
from datetime import datetime


class Operaciones:

    CLUSTER_INICIAL_DATOS = 5

    def __init__(self, sistema, directorio):
        self.sistema = sistema
        self.directorio = directorio

    def validar_nombre(self, nombre):

        if not nombre:
            raise ValueError("El nombre del archivo esta vacio")

        if nombre in (".", ".."):
            raise ValueError("Nombre de archivo no valido")

        if nombre.startswith("#"):
            raise ValueError("El nombre no puede comenzar con #")

        if nombre != nombre.strip():
            raise ValueError(
                "El nombre no puede comenzar ni terminar con espacios"
            )

        if "/" in nombre or "\\" in nombre:
            raise ValueError(
                "El nombre no debe contener rutas"
            )

        try:
            nombre_bytes = nombre.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError(
                "El nombre debe contener solamente caracteres ASCII"
            )

        if len(nombre_bytes) > 15:
            raise ValueError(
                "El nombre del archivo no puede superar 15 bytes"
            )

        if any(byte < 32 or byte > 126 for byte in nombre_bytes):
            raise ValueError(
                "El nombre contiene caracteres no permitidos"
            )

        return nombre_bytes

    def calcular_clusters(self, tamano):

        tamano_cluster = self.sistema.tamano_cluster

        cantidad = math.ceil(tamano / tamano_cluster)

        # Los archivos vacíos también reservan un cluster.
        return max(cantidad, 1)

    def obtener_clusters_ocupados(self):

        archivos = self.directorio.listar()
        ocupados = set()

        for archivo in archivos:

            inicio = archivo["cluster_inicial"]
            cantidad = self.calcular_clusters(
                archivo["tamano"]
            )

            final = inicio + cantidad

            if inicio < self.CLUSTER_INICIAL_DATOS:
                raise ValueError(
                    f"Cluster inicial invalido en {archivo['nombre']}"
                )

            if final > self.sistema.clusters_totales:
                raise ValueError(
                    f"El archivo {archivo['nombre']} excede el disco"
                )

            for cluster in range(inicio, final):
                ocupados.add(cluster)

        return ocupados

    def buscar_espacio_contiguo(self, clusters_necesarios):

        ocupados = self.obtener_clusters_ocupados()

        limite = self.sistema.clusters_totales

        for posible in range(
            self.CLUSTER_INICIAL_DATOS,
            limite - clusters_necesarios + 1
        ):

            candidatos = range(
                posible,
                posible + clusters_necesarios
            )

            if all(
                cluster not in ocupados
                for cluster in candidatos
            ):
                return posible

        raise ValueError(
            "No hay espacio contiguo suficiente en FiUnamFS"
        )

    def copiar_desde_fiunamfs(
        self,
        nombre,
        carpeta_destino="archivos"
    ):

        self.validar_nombre(nombre)

        archivo = self.directorio.buscar(nombre)

        if archivo is None:
            raise FileNotFoundError(
                f"No existe el archivo {nombre} en FiUnamFS"
            )

        os.makedirs(carpeta_destino, exist_ok=True)

        inicio = (
            archivo["cluster_inicial"]
            * self.sistema.tamano_cluster
        )

        with self.sistema.lock:

            self.sistema.archivo.seek(inicio)

            contenido = self.sistema.archivo.read(
                archivo["tamano"]
            )

        if len(contenido) != archivo["tamano"]:
            raise ValueError(
                "No se pudo leer el archivo completo"
            )

        ruta_destino = os.path.join(
            carpeta_destino,
            nombre
        )

        with open(ruta_destino, "wb") as destino:
            destino.write(contenido)

        print(
            f"Archivo copiado correctamente: {ruta_destino}"
        )

        return ruta_destino

    def copiar_a_fiunamfs(self, ruta_origen):

        if not os.path.isfile(ruta_origen):
            raise FileNotFoundError(
                "El archivo de origen no existe"
            )

        nombre = os.path.basename(ruta_origen)

        nombre_bytes = self.validar_nombre(nombre)

        with open(ruta_origen, "rb") as origen:
            contenido = origen.read()

        tamano = len(contenido)

        tamano_cluster = self.sistema.tamano_cluster

        clusters_necesarios = self.calcular_clusters(
            tamano
        )

        # No permitir archivos que excedan la capacidad de datos.
        capacidad_maxima = (
            self.sistema.clusters_totales
            - self.CLUSTER_INICIAL_DATOS
        )

        if clusters_necesarios > capacidad_maxima:
            raise ValueError(
                "El archivo es demasiado grande para FiUnamFS"
            )

        with self.sistema.lock:

            # Comprobar duplicados dentro del bloqueo.
            if self.directorio.buscar(nombre) is not None:
                raise ValueError(
                    "Ya existe un archivo con ese nombre"
                )

            # Buscar espacio y entrada libre.
            cluster_inicial = self.buscar_espacio_contiguo(
                clusters_necesarios
            )

            posicion = self.directorio.entrada_libre()

            fecha = datetime.now().strftime(
                "%Y%m%d%H%M%S"
            ).encode("ascii")

            entrada = (
                b"F"
                + nombre_bytes.ljust(15, b" ")
                + tamano.to_bytes(4, "little")
                + cluster_inicial.to_bytes(4, "little")
                + fecha
                + fecha
                + bytes(12)
            )

            inicio_datos = (
                cluster_inicial * tamano_cluster
            )

            contenido_relleno = contenido.ljust(
                clusters_necesarios * tamano_cluster,
                b"\x00"
            )

            # Escribir datos antes de registrar el archivo.
            try:

                self.sistema.archivo.seek(inicio_datos)

                self.sistema.archivo.write(
                    contenido_relleno
                )

                self.sistema.archivo.flush()

                # Verificar los datos escritos.
                self.sistema.archivo.seek(inicio_datos)

                verificacion = self.sistema.archivo.read(
                    len(contenido_relleno)
                )

                if verificacion != contenido_relleno:
                    raise IOError(
                        "La verificacion de escritura fallo"
                    )

                # Registrar el archivo al final.
                self.directorio.escribir_entrada(
                    posicion,
                    entrada
                )

            except Exception:

                # Intentar limpiar el espacio si la operación falla.
                try:

                    self.sistema.archivo.seek(inicio_datos)

                    self.sistema.archivo.write(
                        bytes(
                            clusters_necesarios
                            * tamano_cluster
                        )
                    )

                    self.sistema.archivo.flush()

                except Exception:
                    pass

                raise

        print(
            f"Archivo agregado correctamente: {nombre}"
        )

        return nombre

    def eliminar_archivo(self, nombre):

        self.validar_nombre(nombre)

        with self.sistema.lock:

            archivo = self.directorio.buscar(nombre)

            if archivo is None:
                raise FileNotFoundError(
                    f"No existe el archivo {nombre} en FiUnamFS"
                )

            tamano_cluster = self.sistema.tamano_cluster

            cantidad = self.calcular_clusters(
                archivo["tamano"]
            )

            inicio = (
                archivo["cluster_inicial"]
                * tamano_cluster
            )

            # Validar que el archivo no invada el superbloque
            # ni el directorio.
            if archivo["cluster_inicial"] < self.CLUSTER_INICIAL_DATOS:
                raise ValueError(
                    "El archivo tiene un cluster inicial invalido"
                )

            if archivo["cluster_inicial"] + cantidad > (
                self.sistema.clusters_totales
            ):
                raise ValueError(
                    "Los clusters del archivo exceden el disco"
                )

            # Primero liberar la entrada del directorio.
            self.directorio.liberar_entrada(
                archivo["posicion"]
            )

            # Después limpiar el contenido de sus clusters.
            self.sistema.archivo.seek(inicio)

            self.sistema.archivo.write(
                bytes(cantidad * tamano_cluster)
            )

            self.sistema.archivo.flush()

        print(
            f"Archivo eliminado correctamente: {nombre}"
        )

        return nombre