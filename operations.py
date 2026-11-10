
import os


class Operaciones:

    def __init__(self, sistema, directorio):
        self.sistema = sistema
        self.directorio = directorio

    def copiar_desde_fiunamfs(self, nombre_archivo):

        # Obtenemos los archivos del directorio
        archivos = self.directorio.listar()

        archivo_encontrado = None

        # Buscamos el archivo por su nombre
        for archivo in archivos:
            nombre = archivo["nombre"].strip()

            if nombre == nombre_archivo.strip():
                archivo_encontrado = archivo
                break

        if archivo_encontrado is None:
            print("El archivo no existe en FiUnamFS")
            print("Archivos encontrados:")

            for archivo in archivos:
                print("-", repr(archivo["nombre"]))

            return

        # Obtenemos los datos del archivo
        tamano = archivo_encontrado["tamano"]
        cluster = archivo_encontrado["cluster_inicial"]

        # Calculamos dónde comienza el archivo
        posicion = cluster * self.sistema.tamano_cluster

        # Creamos la carpeta de destino
        os.makedirs("archivos", exist_ok=True)

        # Leemos el contenido del archivo
        self.sistema.archivo.seek(posicion)
        contenido = self.sistema.archivo.read(tamano)

        # Guardamos el archivo en la computadora
        ruta_destino = os.path.join("archivos", nombre_archivo)

        with open(ruta_destino, "wb") as archivo_salida:
            archivo_salida.write(contenido)

        print("Archivo copiado correctamente:", nombre_archivo)
