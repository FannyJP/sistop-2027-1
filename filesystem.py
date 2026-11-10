
import os
import struct


class FiUnamFS:

    def __init__(self, ruta):
        self.ruta = ruta
        self.archivo = None

        self.tamano_cluster = 0
        self.clusters_directorio = 0
        self.clusters_totales = 0

    def abrir(self):
        if not os.path.exists(self.ruta):
            raise FileNotFoundError(
                "No se encontro la imagen del disco"
            )

        self.archivo = open(self.ruta, "rb")

        try:
            self.validar_superbloque()
        except Exception:
            self.cerrar()
            raise

    def validar_superbloque(self):
        self.archivo.seek(0)
        superbloque = self.archivo.read(512)

        if len(superbloque) != 512:
            raise ValueError("Superbloque incompleto")

        identificacion = superbloque[0:8].decode("ascii").strip()
        version = superbloque[10:14].decode("ascii").strip()

        if identificacion != "FiUnamFS":
            raise ValueError("El sistema no es FiUnamFS")

        if version != "27-1":
            raise ValueError("Version no compatible")

        self.tamano_cluster = struct.unpack(
            "<I", superbloque[40:44]
        )[0]

        self.clusters_directorio = struct.unpack(
            "<I", superbloque[44:48]
        )[0]

        self.clusters_totales = struct.unpack(
            "<I", superbloque[48:52]
        )[0]

        print("FiUnamFS validado correctamente")
        print("Version:", version)
        print("Tamano del cluster:", self.tamano_cluster)
        print("Clusters del directorio:", self.clusters_directorio)
        print("Clusters totales:", self.clusters_totales)

    def cerrar(self):
        if self.archivo is not None:
            self.archivo.close()
            self.archivo = None
