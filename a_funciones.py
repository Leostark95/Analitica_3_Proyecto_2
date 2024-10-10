#Librerias
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3 as sql


####Paquete para sistema basado en contenido ####
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors

#Función para ejecutar sql
def ejecutar_sql (nombre_archivo, cur):
    """
    
    """
    sql_file=open(nombre_archivo)
    sql_as_string=sql_file.read()
    sql_file.close
    cur.executescript(sql_as_string)

#Función para crear gráficos de histograma
def plot_histogram(db, title, xlabel, ylabel, bins=10, rotate_xticks=False):
    """
    Esta función tiene como objetivo graficar un histograma, y este sea personalizado
    con los parámetros que recibe. Estos se describen a continuación:

    Parámetros:
    - db: , dataframe, datos a graficar.
    - title: str, título del gráfico.
    - xlabel: str, etiqueta del eje x.
    - ylabel: str, etiqueta del eje y.
    - bins: int, número de bins para el histograma.
    - rotate_xticks: bool, si se debe rotar las etiquetas del eje x.
    """

    #Tamaño de la figura
    plt.figure(figsize=(7, 5)) 

    # Crear el histograma
    plt.hist(db, bins=bins, color='blue', edgecolor='black')

    # Anexar titulos y etiquetas
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Ajustar los ticks del eje x
    plt.xticks(np.arange(0, max(db) + (max(db) // bins), (max(db) // bins)), rotation=45 if rotate_xticks else 0)

    # Ajustar el diseño para evitar solapamientos
    plt.tight_layout() 
    
    #Mostrar el gráfico 
    plt.show()

#Función para separar el año del title, escalado y duminización de la variable genre
def year(db):
    """
    Esta función tiene como objetivo separar el año del title y realizar la duminización a las variable genre.
    Para ello recibe el argumento db que es un dataframe con los datos.
    """
    db['year'] = db['title'].str.extract(r'\((\d{4})\)').astype(int)
    db['title'] = db['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
    
    #Escalar el year
    sc=MinMaxScaler()
    db[["year_sc"]]=sc.fit_transform(db[['year']])
    
    #Hacer dumis el genero.
    db['genres'] = db['genres'].str.lower()  # Normalizar a minúsculas
    db_dum = pd.concat([db, db['genres'].str.get_dummies(sep='|')], axis=1)  # Separar por "|" y crear columnas dummizadas
    
    #Eliminar columna genres
    db_dum = db_dum.drop(columns=['genres'])
    
    return db_dum

