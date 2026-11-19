
class Directorio:

    TAMANO_ENTRADA = 64
    CLUSTER_INICIAL_DIRECTORIO = 1

    def __init__(self, sistema):
        self.sistema = sistema

    def _leer_directorio_completo(self):

        sistema = self.sistema

        inicio = (
            self.CLUSTER_INICIAL_DIRECTORIO
            * sistema.tamano_cluster
        )

        tamano = (
            sistema.clusters_directorio
            * sistema.tamano_cluster
        )

        with sistema.lock:
            sistema.archivo.seek(inicio)
            datos = sistema.archivo.read(tamano)

        if len(datos) != tamano:
            raise ValueError("No se pudo leer todo el directorio")

        return datos

    def listar(self):

        datos = self._leer_directorio_completo()
        archivos = []

        for posicion in range(0, len(datos), self.TAMANO_ENTRADA):

            entrada = datos[posicion:posicion + self.TAMANO_ENTRADA]

            tipo = entrada[0:1].decode(
                "ascii", errors="replace"
            )

            nombre = entrada[1:16].decode(
                "ascii", errors="replace"
            ).rstrip(" \x00")

            if tipo != "F" or not nombre or nombre.startswith("#"):
                continue

            tamano = int.from_bytes(
                entrada[16:20], "little"
            )

            cluster = int.from_bytes(
                entrada[20:24], "little"
            )

            fecha_creacion = entrada[24:38].decode(
                "ascii", errors="replace"
            )

            fecha_modificacion = entrada[38:52].decode(
                "ascii", errors="replace"
            )

            informacion = {
                "nombre": nombre,
                "tamano": tamano,
                "cluster_inicial": cluster,
                "fecha_creacion": fecha_creacion,
                "fecha_modificacion": fecha_modificacion,
                "posicion": posicion
            }

            archivos.append(informacion)

        return archivos

    def mostrar(self):

        archivos = self.listar()

        print("\nCONTENIDO DE FIUNAMFS")
        print("-" * 60)

        if not archivos:
            print("El directorio esta vacio")
            return

        for archivo in archivos:

            print("Nombre:", archivo["nombre"])
            print("Tamano:", archivo["tamano"], "bytes")
            print("Cluster inicial:", archivo["cluster_inicial"])
            print("Fecha de creacion:", archivo["fecha_creacion"])
            print("Ultima modificacion:", archivo["fecha_modificacion"])

            print("-" * 60)

    def buscar(self, nombre):

        for archivo in self.listar():

            if archivo["nombre"] == nombre:
                return archivo

        return None

    def entrada_libre(self):

        datos = self._leer_directorio_completo()

        for posicion in range(0, len(datos), self.TAMANO_ENTRADA):

            entrada = datos[posicion:posicion + self.TAMANO_ENTRADA]

            tipo = entrada[0:1]
            nombre = entrada[1:16]

            if tipo == b"-" or nombre.startswith(b"#"):
                return posicion

        raise ValueError("El directorio esta lleno")

    def escribir_entrada(self, posicion, datos):

        if len(datos) != self.TAMANO_ENTRADA:
            raise ValueError("La entrada debe medir 64 bytes")

        inicio = (
            self.CLUSTER_INICIAL_DIRECTORIO
            * self.sistema.tamano_cluster
        )

        with self.sistema.lock:

            self.sistema.archivo.seek(inicio + posicion)
            self.sistema.archivo.write(datos)
            self.sistema.archivo.flush()

    def liberar_entrada(self, posicion):

        nombre_libre = b"#" + b"." * 14

        entrada = (
            b"-" + nombre_libre + bytes(48)
        )

        self.escribir_entrada(posicion, entrada)
