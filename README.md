

## Instrucciones para Descargar y Procesar los Datos de Kaggle

Para trabajar con los datos de vino disponibles en Kaggle, sigue los pasos a continuación:

## 1. Descargar el Dataset

Visita el siguiente enlace para descargar el dataset:

[Descargar Wine Reviews](https://www.kaggle.com/datasets/zynicide/wine-reviews?select=winemag-data_first150k.csv)

1. Haz clic en el botón **"Download"** para descargar el archivo ZIP que contiene los datos.

## 2. Mover el Archivo Descargado

Una vez que el archivo ZIP se haya descargado, sigue estos pasos:

1. Localiza el archivo ZIP en tu carpeta de descargas.
2. Mueve el archivo ZIP a la carpeta `datasets` de tu proyecto.

## 3. Descomprimir el Archivo

Descomprime el archivo ZIP en la carpeta `datasets`. Esto debería crear un archivo llamado `winemag-data_first150k.csv`.

## 4. Correr el Notebook de Jupyter

Ahora estás listo para procesar los datos:

1. Abre el archivo `preprocess.ipynb`.
2. Ejecuta las celdas del notebook para procesar los datos y generar el archivo `preprocess_data.csv`.

## 5. Archivo Resultante

Después de ejecutar el notebook, deberías obtener el archivo `preprocess_data.csv` en la carpeta de tu proyecto, listo para ser utilizado.
## SPIMI-INVERT

El algoritmo **SPIMIInvert (Single-Pass In-Memory Indexing)** es una técnica popular para construir un **índice invertido** de manera eficiente, especialmente cuando trabajamos con un gran volumen de documentos. Su objetivo es permitir búsquedas rápidas, ayudándonos a identificar en qué documentos aparece una palabra específica.

#### Algoritmo

El proceso comienza con la **lectura secuencial de cada palabra (token)** dentro de los documentos. A medida que se identifican estas palabras, se va construyendo un **diccionario en memoria**.

1. **Agregar términos al diccionario**: 
   - Cuando encontramos una palabra nueva que aún no está en el diccionario, usamos la función `addToDictionary`. Esta función agrega el término junto con su frecuencia inicial (normalmente 1) y crea una **lista vacía de publicaciones** (posting list) que luego almacenará información sobre en qué documentos aparece esta palabra.
   - Si la palabra ya existe en el diccionario, no la volvemos a agregar. En su lugar, usamos la función `addToPostingsList` para actualizar su lista de publicaciones, añadiendo el **ID del documento** donde aparece y aumentando su frecuencia en dicho documento.

2. **Manejo del límite de memoria**: 
   - Dado que la memoria es limitada, establecemos un tamaño máximo para el diccionario. Una vez que alcanzamos este límite, el contenido se guarda en un archivo en disco mediante `writeBlockToDisk`. Esta función utiliza técnicas de **serialización** para asegurarse de que los datos se guarden en un formato que podamos recuperar fácilmente después.
   - Al guardar los datos en disco, liberamos espacio en la memoria para poder seguir procesando más documentos.

3. **Optimización del índice**:
   - Antes de escribir el diccionario en disco, los términos se ordenan alfabéticamente usando la función `sortTerms`. Esto facilita la fase de búsqueda y también hace que la fusión de múltiples bloques sea más eficiente.

4. **Fusión de bloques en disco**:
   - Después de haber procesado todos los documentos y haber creado múltiples bloques en disco, llega el momento de fusionarlos en un solo índice final. Para esto, usamos la función `mergeBlocks`.
   - `mergeBlocks` carga múltiples bloques en memoria, compara los términos y fusiona sus listas de publicaciones con `mergePostingLists`. Este proceso asegura que todas las publicaciones de un mismo término se unifiquen, sin duplicados.
   - La fusión se realiza en varios pasos, combinando bloques de dos en dos, hasta que obtenemos un único archivo maestro que contiene el índice completo.

5. **Lectura y manejo de bloques**:
   - Para leer los bloques desde el disco durante la fusión, se utiliza `readBlockToDict`. Esta función no solo se encarga de cargar el contenido de los bloques, sino que también maneja errores comunes, como archivos dañados o que no existen, asegurando que el proceso no se detenga abruptamente.
   - Para facilitar la búsqueda eficiente durante la fusión, `getPosicion` nos ayuda a navegar entre diferentes términos y sus publicaciones en los distintos bloques.


