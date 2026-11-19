
import os
import struct
import threading


class FiUnamFS:
    """Abre y administra la imagen del sistema de archivos."""

    TAMANO_SECTOR = 512
    TAMANO_CLUSTER_ESPERADO = 2048
    CLUSTERS_DIRECTORIO_ESPERADOS = 4
    CLUSTERS_TOTALES_ESPERADOS = 720
    TAMANO_IMAGEN_ESPERADO = 1440 * 1024

    def __init__(self, ruta):
        self.ruta = ruta
        self.archivo = None

        self.tamano_cluster = 0
        self.clusters_directorio = 0
        self.clusters_totales = 0

        # Evita que dos hilos accedan al disco al mismo tiempo.
        self.lock = threading.RLock()

    def abrir(self):
        if not os.path.isfile(self.ruta):
            raise FileNotFoundError(
                f"No se encontro la imagen del disco: {self.ruta}"
            )

        self.archivo = open(self.ruta, "r+b")

        try:
            if os.path.getsize(self.ruta) != self.TAMANO_IMAGEN_ESPERADO:
                raise ValueError(
                    "La imagen debe medir exactamente 1440 KB"
                )

            self.validar_superbloque()

        except Exception:
            self.cerrar()
            raise

    def validar_superbloque(self):
        with self.lock:
            self.archivo.seek(0)
            superbloque = self.archivo.read(self.TAMANO_SECTOR)

            if len(superbloque) != self.TAMANO_SECTOR:
                raise ValueError("El superbloque esta incompleto")

            identificacion = superbloque[0:8].decode(
                "ascii", errors="replace"
            )

            version = superbloque[10:14].decode(
                "ascii", errors="replace"
            )

            if identificacion != "FiUnamFS":
                raise ValueError(
                    "La imagen no corresponde a FiUnamFS"
                )

            if version != "27-1":
                raise ValueError(
                    f"Version no compatible: {version}"
                )

            self.tamano_cluster = struct.unpack(
                "<I", superbloque[40:44]
            )[0]

            self.clusters_directorio = struct.unpack(
                "<I", superbloque[44:48]
            )[0]

            self.clusters_totales = struct.unpack(
                "<I", superbloque[48:52]
            )[0]

            if self.tamano_cluster != self.TAMANO_CLUSTER_ESPERADO:
                raise ValueError("El tamano de cluster debe ser 2048 bytes")

            if self.clusters_directorio != self.CLUSTERS_DIRECTORIO_ESPERADOS:
                raise ValueError("El directorio debe ocupar 4 clusters")

            if self.clusters_totales != self.CLUSTERS_TOTALES_ESPERADOS:
                raise ValueError("La imagen debe contener 720 clusters")

            print("FiUnamFS validado correctamente")
            print("Version:", version)
            print("Tamano del cluster:", self.tamano_cluster)
            print("Clusters del directorio:", self.clusters_directorio)
            print("Clusters totales:", self.clusters_totales)

    def cerrar(self):
        with self.lock:
            if self.archivo is not None:
                self.archivo.close()
                self.archivo = None
