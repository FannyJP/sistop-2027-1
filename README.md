# FiUnamFS

En este proyecto estoy trabajando con Python para crear un programa que permita realizar algunas operaciones con FiUnamFS.

De acuerdo con lo que pide la práctica, el programa debe poder mostrar los archivos que hay en el disco, copiar archivos hacia la computadora, agregar archivos, eliminarlos y trabajar con varios hilos al mismo tiempo.

Para ir organizando el trabajo, fui separando el código en diferentes archivos, de manera que cada uno se encargue de una parte del programa.

## Archivos y carpetas

- **main.py:** es donde comienza el programa y desde donde se llaman las demás partes.
- **filesystem.py:** aquí estoy trabajando con la imagen del disco. Por ahora permite abrirla y revisar algunos de sus datos para comprobar que sea FiUnamFS.
- **directory.py:** se encarga de leer el directorio para conocer qué archivos hay y obtener información sobre ellos.
- **operations.py:** aquí comencé a trabajar con las operaciones de los archivos. Por el momento tiene una función para copiar archivos desde FiUnamFS a la computadora.
- **threads.py:** este archivo se utilizará más adelante para agregar el trabajo con hilos.
- **disco/:** aquí se guardará la imagen del disco.
- **archivos/:** aquí se guardarán los archivos que se copien a la computadora.

## Lo que llevo

Hasta ahora tengo creada la estructura inicial y he comenzado a trabajar en la lectura del sistema de archivos. Primero agregué la parte para abrir la imagen y obtener los datos principales del superbloque.

Después trabajé en la lectura del directorio, para poder identificar los archivos que contiene y mostrar algunos de sus datos. También comencé con la función para copiar archivos desde el disco hacia la computadora.

## Lo que falta

Todavía falta agregar la copia de archivos desde la computadora hacia FiUnamFS y la opción para eliminarlos. También queda pendiente implementar los hilos y la sincronización que pide la práctica.

Por ahora es un primer avance y todavía faltan varias partes por desarrollar.