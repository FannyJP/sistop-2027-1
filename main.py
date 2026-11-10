
from filesystem import FiUnamFS
from directory import Directorio
from operations import Operaciones


def main():

    ruta = "disco/fiunamfs.img"

    sistema = FiUnamFS(ruta)

    try:
        # Abrimos y validamos el sistema de archivos
        sistema.abrir()

        # Creamos el objeto encargado del directorio
        directorio = Directorio(sistema)

        # Mostramos los archivos encontrados
        directorio.mostrar()

        # Creamos el objeto para realizar operaciones
        operaciones = Operaciones(sistema, directorio)

        # Copiamos un archivo desde FiUnamFS a la computadora
        operaciones.copiar_desde_fiunamfs("mensaje.jpg")

    except FileNotFoundError as error:
        print("Error:", error)

    except ValueError as error:
        print("Error:", error)

    finally:
        sistema.cerrar()


if __name__ == "__main__":
    main()
