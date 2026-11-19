# FiUnamFS

**Autor:** Perez Baez Jessica Estefani  
**Lenguaje:** Python  
**Versión utilizada:** Python 3.15.2

## ¿De qué trata el proyecto?

En este proyecto estoy trabajando con Python para crear un programa que permita realizar diferentes operaciones con FiUnamFS.

La idea es poder consultar los archivos que contiene el disco, copiar archivos desde FiUnamFS a la computadora, agregar archivos desde la computadora al disco y también eliminarlos.

Además, como parte de la práctica, estoy trabajando con varios hilos para que las operaciones se puedan ejecutar mediante un hilo trabajador y otro que se encarga de recibir los cambios de estado.

Para organizar mejor el trabajo, fui separando el código en diferentes archivos, de manera que cada uno se encargue de una parte del programa.

Durante el desarrollo también he realizado algunas mejoras para validar mejor la imagen del disco, revisar las entradas del directorio y evitar problemas al momento de copiar o agregar archivos.

## Archivos y carpetas

- **main.py:** es donde comienza el programa. Aquí se muestra el menú y se selecciona la operación que se quiere realizar.
- **filesystem.py:** se encarga de abrir la imagen del disco y revisar sus datos principales para comprobar que corresponda a FiUnamFS. También se agregaron algunas validaciones para comprobar que la información del disco sea correcta.
- **directory.py:** permite leer el directorio, mostrar los archivos que contiene y obtener información sobre ellos. También se mejoró la revisión de las entradas para detectar nombres duplicados y posiciones incorrectas al escribir.
- **operations.py:** contiene las operaciones para copiar archivos desde FiUnamFS a la computadora, agregar archivos al disco y eliminarlos. Se mejoraron algunas comprobaciones para evitar copias incompletas y verificar los datos escritos.
- **threads.py:** contiene la parte relacionada con los hilos. Tiene un hilo trabajador que realiza las operaciones y otro que recibe los cambios de estado.
- **disco/:** aquí se guardan las imágenes del disco que utiliza el programa.
- **archivos/:** aquí se guardan los archivos que se copian desde FiUnamFS a la computadora y los archivos que se utilizan para realizar pruebas.

## Requisitos

Para ejecutar el proyecto se necesita:

- Tener Python instalado.
- Se desarrolló y probó utilizando Python 3.15.2.
- Tener la imagen de FiUnamFS proporcionada para la práctica.
- Contar con una terminal para ejecutar el programa.

No se necesitan instalar librerías externas, ya que se utilizan módulos que vienen incluidos con Python, como `os`, `struct`, `threading`, `queue`, `datetime`, `math` y `tempfile`.

## ¿Cómo ejecutar el programa?

Primero hay que descargar o clonar el repositorio.

Después, abrir la carpeta del proyecto desde VS Code o una terminal.

**1. Preparar la imagen del disco**

Este paso es importante porque las imágenes `.img` no están incluidas en el repositorio.

El archivo `.gitignore` ignora las imágenes que se encuentran dentro de `disco/`, por lo que al clonar el proyecto esa carpeta puede no contener la imagen necesaria.

Se debe conseguir la imagen proporcionada por el profesor y colocarla dentro de la carpeta `disco/`.

El programa utiliza por defecto el siguiente nombre:

`fiunamfs.img`

También se puede utilizar una imagen con otro nombre, indicando su ubicación al ejecutar el programa.

**2. Abrir la terminal**

Hay que asegurarse de estar dentro de la carpeta principal del proyecto, donde se encuentra `main.py`.

**3. Ejecutar el programa**

Si la imagen se llama `fiunamfs.img`, escribir:

`py main.py`

También se puede ejecutar con:

`python main.py`

Si se quiere utilizar una imagen con otro nombre, como la que utilicé para las pruebas, se puede indicar su ruta:

`py main.py "disco/fiunamfs prueba.img"`

Si todo está en su lugar, el programa revisará la imagen del disco y mostrará el menú principal.

## Opciones del programa

Al ejecutar el programa aparece un menú con cinco opciones:

1. **Mostrar contenido del directorio:** permite consultar los archivos que se encuentran dentro de FiUnamFS, mostrando su nombre, tamaño, cluster inicial y fechas.
2. **Copiar archivo de FiUnamFS a la computadora:** permite escribir el nombre de un archivo que se encuentra en el disco para copiarlo a la carpeta `archivos/`.
3. **Copiar archivo de la computadora a FiUnamFS:** permite agregar un archivo que se encuentre en la computadora. Para esto se debe proporcionar su ruta.
4. **Eliminar archivo de FiUnamFS:** permite escribir el nombre de un archivo para eliminarlo del disco.
5. **Salir:** cierra el programa y finaliza los hilos.

## ¿Cómo se utilizan los hilos?

Para cumplir con la parte de concurrencia de la práctica, se agregaron dos hilos.

El primero se llama **hilo trabajador**. Es el encargado de realizar las operaciones que se solicitan desde el menú, como copiar archivos, agregarlos o eliminarlos.

El segundo se llama **hilo supervisor**. Su función es recibir los mensajes que indican cuándo comienza una operación, cuándo termina o si ocurrió algún error.

Para que puedan comunicarse se utilizan colas (`Queue`). El trabajador envía los cambios de estado y el supervisor los recibe.

También se utiliza `threading.Event` para avisar al menú cuando una operación terminó. De esta manera, el menú puede esperar el resultado antes de continuar.

Además, se utiliza un bloqueo compartido (`RLock`) en el acceso al disco para evitar que dos hilos lean o modifiquen la imagen al mismo tiempo de manera incorrecta.

Los mensajes del supervisor se guardan en una cola y después se muestran desde `main.py`. Esto ayuda a que no se mezclen con el contenido del directorio o con las opciones del menú.

## Contenido del disco utilizado en las pruebas

En la imagen que utilicé para realizar las pruebas se encontraron originalmente los siguientes archivos:

| Archivo | Tamaño | Cluster inicial |
|---|---:|---:|
| README.org | 31,126 bytes | 6 |
| logo.png | 126,423 bytes | 22 |
| mensaje.jpg | 254,484 bytes | 84 |

Estos son los archivos que contiene la imagen original utilizada para las pruebas.

Los archivos `prueba.txt` y `vacio.txt` se utilizaron después para comprobar las operaciones de agregar, copiar y eliminar.

## Algunas pruebas que he realizado

Durante el desarrollo he estado probando las diferentes opciones para comprobar que funcionen correctamente.

Entre las pruebas realizadas están:

- Mostrar los archivos que contiene el directorio.
- Copiar archivos desde FiUnamFS a la computadora.
- Agregar archivos desde la computadora al disco.
- Eliminar archivos y comprobar que ya no aparezcan en el directorio.
- Agregar y copiar un archivo vacío.
- Intentar agregar un archivo con un nombre demasiado largo.
- Intentar agregar un archivo que ya existe.
- Intentar eliminar o copiar archivos que no se encuentran en el disco.
- Comprobar que se pueda volver a utilizar el espacio de un archivo eliminado.
- Revisar los mensajes que se envían entre los dos hilos.
- Comprobar que los hilos finalicen correctamente al cerrar el programa.

También realicé nuevas pruebas después de las últimas modificaciones para comprobar que la imagen se valide correctamente, que el directorio se pueda consultar y que los archivos se puedan copiar sin problemas.

Para realizar estas pruebas utilicé una copia de la imagen del disco, para no modificar la imagen original proporcionada.

## Archivos utilizados para las pruebas

Durante el desarrollo se crearon algunos archivos temporales, por ejemplo:

- `prueba.txt`
- `vacio.txt`
- `archivo_demasiado_largo.txt`

Estos archivos se utilizaron para probar las operaciones del programa y no forman parte del contenido original de FiUnamFS.

Los archivos que se extraen del disco se guardan dentro de `archivos/`.

No es necesario incluir estos archivos temporales en el repositorio para ejecutar el proyecto.

## Lo que falta y lo que quiero mejorar

Aunque ya tengo funcionando las operaciones principales, todavía quiero seguir revisando el código y hacer algunas mejoras.

En esta última actualización trabajé principalmente en la validación de la imagen, la revisión del directorio y las operaciones de copia. También agregué comprobaciones para evitar errores al escribir información en el disco.

Todavía queda pendiente volver a probar las operaciones de agregar y eliminar archivos con la última versión del código, además de continuar revisando el comportamiento de los hilos y algunos detalles de la documentación.

Por ahora, este es el avance que llevo del proyecto. Todavía hay cosas que revisar antes de considerarlo terminado.