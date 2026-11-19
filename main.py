
import os

from filesystem import FiUnamFS
from directory import Directorio
from operations import Operaciones
from threads import AdministradorHilos


RUTA_DISCO = "disco/fiunamfs prueba.img"


def mostrar_menu():

    print("\n========== FIUNAMFS ==========")
    print("1. Mostrar contenido del directorio")
    print("2. Copiar archivo de FiUnamFS a la computadora")
    print("3. Copiar archivo de la computadora a FiUnamFS")
    print("4. Eliminar archivo de FiUnamFS")
    print("5. Salir")
    print("===============================")


def mostrar_directorio(directorio):

    print("\nCONSULTANDO DIRECTORIO DE FIUNAMFS...")

    try:

        archivos = directorio.listar()

        if not archivos:
            print("\nEl directorio esta vacio.")
            return

        print("\nCONTENIDO DEL DIRECTORIO")
        print("=" * 60)

        for archivo in archivos:

            print("Nombre:", archivo["nombre"])
            print("Tamano:", archivo["tamano"], "bytes")
            print("Cluster inicial:", archivo["cluster_inicial"])
            print("Fecha de creacion:", archivo["fecha_creacion"])
            print("Ultima modificacion:", archivo["fecha_modificacion"])
            print("-" * 60)

        print("Total de archivos:", len(archivos))

    except Exception as error:

        print("\nError al consultar el directorio:")
        print(type(error).__name__, ":", error)


def mostrar_mensajes_hilos(administrador):

    mensajes = administrador.obtener_mensajes()

    for mensaje in mensajes:
        print(f"\n[Supervisor] {mensaje}")


def main():

    sistema = FiUnamFS(RUTA_DISCO)
    administrador = None

    try:

        # Abrir y validar la imagen del sistema de archivos.
        sistema.abrir()

        # Crear los objetos principales.
        directorio = Directorio(sistema)
        operaciones = Operaciones(sistema, directorio)

        # Crear e iniciar los hilos concurrentes.
        administrador = AdministradorHilos(operaciones)
        administrador.iniciar()

        while True:

            mostrar_menu()

            opcion = input(
                "Selecciona una opcion: "
            ).strip()

            print("\nOpcion recibida:", repr(opcion))

            # OPCION 1: MOSTRAR DIRECTORIO
            if opcion == "1":

                mostrar_directorio(directorio)

                input("\nPresiona Enter para volver al menu.")

            # OPCION 2: COPIAR DE FIUNAMFS A LA COMPUTADORA
            elif opcion == "2":

                print("\nCOPIAR DE FIUNAMFS A LA COMPUTADORA")

                nombre = input(
                    "Nombre del archivo que deseas copiar: "
                ).strip()

                if not nombre:
                    print("Debes escribir un nombre.")
                    continue

                try:

                    archivo = directorio.buscar(nombre)

                    if archivo is None:

                        print("El archivo no existe en FiUnamFS.")

                    else:

                        # La solicitud se procesa en el hilo trabajador.
                        administrador.enviar_solicitud(
                            "copiar_desde",
                            nombre
                        )

                        # Mostrar mensajes del supervisor.
                        mostrar_mensajes_hilos(
                            administrador
                        )

                        ruta_destino = os.path.join(
                            "archivos",
                            nombre
                        )

                        if os.path.isfile(ruta_destino):

                            print("\nCopia verificada correctamente.")
                            print("Ubicacion:", ruta_destino)

                except Exception as error:

                    # Recoger mensajes incluso si hubo error.
                    mostrar_mensajes_hilos(
                        administrador
                    )

                    print("\nError durante la copia:")
                    print(type(error).__name__, ":", error)

                input("\nPresiona Enter para volver al menu.")

            # OPCION 3: COPIAR DE LA COMPUTADORA A FIUNAMFS
            elif opcion == "3":

                print("\nCOPIAR DE LA COMPUTADORA A FIUNAMFS")

                ruta = input(
                    "Ruta completa del archivo que deseas agregar: "
                ).strip().strip('"')

                if not ruta:
                    print("Debes escribir una ruta.")
                    continue

                try:

                    # La solicitud se procesa en el hilo trabajador.
                    administrador.enviar_solicitud(
                        "copiar_hacia",
                        os.path.basename(ruta),
                        ruta
                    )

                    # Mostrar mensajes del supervisor.
                    mostrar_mensajes_hilos(
                        administrador
                    )

                    print("\nComprobando el directorio...")
                    mostrar_directorio(directorio)

                except Exception as error:

                    # Recoger mensajes incluso si hubo error.
                    mostrar_mensajes_hilos(
                        administrador
                    )

                    print("\nError al agregar el archivo:")
                    print(type(error).__name__, ":", error)

                input("\nPresiona Enter para volver al menu.")

            # OPCION 4: ELIMINAR ARCHIVO
            elif opcion == "4":

                print("\nELIMINAR ARCHIVO DE FIUNAMFS")

                nombre = input(
                    "Nombre del archivo que deseas eliminar: "
                ).strip()

                if not nombre:
                    print("Debes escribir un nombre.")
                    continue

                try:

                    # La solicitud se procesa en el hilo trabajador.
                    administrador.enviar_solicitud(
                        "eliminar",
                        nombre
                    )

                    # Mostrar mensajes del supervisor.
                    mostrar_mensajes_hilos(
                        administrador
                    )

                    print("\nDirectorio actualizado:")
                    mostrar_directorio(directorio)

                except Exception as error:

                    # Recoger mensajes incluso si hubo error.
                    mostrar_mensajes_hilos(
                        administrador
                    )

                    print("\nError al eliminar el archivo:")
                    print(type(error).__name__, ":", error)

                input("\nPresiona Enter para volver al menu.")

            # OPCION 5: SALIR
            elif opcion == "5":

                print("\nCerrando FiUnamFS...")
                break

            else:

                print("\nOpcion no valida. Selecciona del 1 al 5.")

                input("Presiona Enter para continuar.")

    except KeyboardInterrupt:

        print("\nPrograma interrumpido por el usuario.")

    except Exception as error:

        print("\nError en el sistema:")
        print(type(error).__name__, ":", error)

    finally:

        if administrador is not None:
            administrador.finalizar()

        sistema.cerrar()


if __name__ == "__main__":
    main()
