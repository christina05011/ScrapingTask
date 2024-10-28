# Comentarios generales

## Configuración del proyecto
- Se descargaron los datasets: 'Properties.csv' y 'Bookings.csv'.
- Se creó una carpeta para almacenar archivos y nuevos datasets.

## Ejecución de scripts
Ejecutar en el siguiente orden:
```bash
python .\scraping_.py
python .\data_cleaning.py
```

## ETL
### 📂 Archivo 'scraping_.py':
  Este archivo realiza el scraping de una búsqueda en la página oficial de Booking.com para reservar un hotel en Barcelona.
  Se utilizan datos por defecto, como el número de personas, fecha de ingreso, fecha de salida, etc., ya que la búsqueda se realiza con los mismos datos.
  La extracción de los datos se lleva a cabo a partir de los elementos en el HTML, utilizando la función de inspección de la página.
  
  Además, se realiza la limpieza de los datos que se van a guardar:
  - Se elimina la moneda de euros en los montos.
  - Se estandarizan los números, reemplazando comas por puntos.
  - Los elementos 'PropertyId', 'Property_BookingId' y 'Square' se representan como NaN, ya que no se dispone de esos valores.

  Se creó la estructura para seguir las fórmulas de los datasets iniciales y combinar los datos de ambos archivos.
  El archivo resultante se guarda en formato .csv.

### 📂 Archivo 'data_cleaning.py':
  Este archivo se encarga de la limpieza y estandarización de datos, así como de la unión de todos los archivos.
  Para la limpieza de datos:
  - Se filtran por valores como 'RealProperty' y se validan cantidades como el número de personas, capacidad y tamaño, etc.
  - Se eliminan los elementos duplicados.
  - Se estandarizan valores, por ejemplo, se transforma 'Apa' a 'Apartamento'.
  - Se formatean las fechas.
  - Se actualizan los valores de acuerdo a las fórmulas.
  - Se estandarizan algunos datos, como 'nan' y 'Unknown'; por ejemplo, el valor de 'rating' se establece como 'nan' si no existe en los datasets iniciales.

  Los archivos resultantes se guardan en un solo archivo .csv, de acuerdo a cada dataset descargado y al archivo final.
  
## Retos presentados
### 🎯 Duplicación de datos:  
  Al extraer información de la página de Booking.com, el problema que se presentó durante el proceso de 'scraping_.py' fue que al extraer datos se duplicaban los mismos, y no se conseguía el mínimo de 100 elementos.
  Para resolver este problema se utilizó concurrencia y paginación, además de agregar una verificación para evitar duplicar elementos durante la extracción.

### 🎯 Análisis de datos:
  A lo largo del proceso, realicé un análisis exhaustivo de los datasets para asegurarme de que los datos fueran lo más limpios posible.
  Esto me permitió identificar y encontrar relaciones significativas entre ambos conjuntos de datos.
  La limpieza no solo implicó la eliminación de datos erróneos, sino también la estandarización de valores y la identificación de campos que debían ser tratados como NaN para mantener la integridad del análisis.

### 🎯 Estandarización de valores:
  En el archivo de limpieza de datos, tuve que manejar diversos formatos y valores inconsistentes. Esto incluyó la conversión de monedas, la estandarización de nombres de propiedades y fechas, y la transformación de valores no disponibles a NaN.
  Además, aseguré que todos los datos estandarizados cumplieran con las fórmulas detectadas en los datasets iniciales, garantizando así un formato uniforme que facilitara el análisis posterior.
