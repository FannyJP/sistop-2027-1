
class Directorio:

    def __init__(self, sistema):
        self.sistema = sistema

    def listar(self):

        archivo = self.sistema.archivo

        tamano_cluster = self.sistema.tamano_cluster
        clusters_directorio = self.sistema.clusters_directorio

        # El directorio comienza en el cluster 1
        inicio_directorio = tamano_cluster

        # Calculamos el tamano del directorio
        tamano_directorio = (
            tamano_cluster * clusters_directorio
        )

        archivo.seek(inicio_directorio)

        datos = archivo.read(tamano_directorio)

        if len(datos) != tamano_directorio:
            raise ValueError("No se pudo leer todo el directorio")

        archivos = []

        # Cada entrada del directorio mide 64 bytes
        for posicion in range(0, tamano_directorio, 64):

            entrada = datos[posicion:posicion + 64]

            tipo = entrada[0:1].decode("ascii")

            # Quitamos espacios y bytes nulos del nombre
            nombre = entrada[1:16].decode("ascii").rstrip(" \x00")

            # Ignoramos las entradas vacias
            if tipo == "-" or nombre.startswith("#"):
                continue

            if tipo != "F":
                continue

            tamano = int.from_bytes(
                entrada[16:20], "little"
            )

            cluster_inicial = int.from_bytes(
                entrada[20:24], "little"
            )

            fecha_creacion = entrada[24:38].decode("ascii")

            fecha_modificacion = entrada[38:52].decode("ascii")

            informacion = {
                "nombre": nombre,
                "tamano": tamano,
                "cluster_inicial": cluster_inicial,
                "fecha_creacion": fecha_creacion,
                "fecha_modificacion": fecha_modificacion
            }

            archivos.append(informacion)

        return archivos

    def mostrar(self):

        archivos = self.listar()

        print("\nCONTENIDO DE FIUNAMFS")
        print("-" * 60)

        if not archivos:
            print("El directorio esta vacio")

        for archivo in archivos:

            print("Nombre:", archivo["nombre"])
            print("Tamano:", archivo["tamano"], "bytes")
            print("Cluster inicial:", archivo["cluster_inicial"])
            print("Fecha de creacion:", archivo["fecha_creacion"])
            print("Ultima modificacion:", archivo["fecha_modificacion"])

            print("-" * 60)
