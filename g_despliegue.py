###Librerías####

import numpy as np
import pandas as pd
import sqlite3 as sql
import a_funciones as fn ## para procesamiento
import openpyxl
import os

####Paquete para sistema basado en contenido ####
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors

### Función para procesar datos
def preprocesar():
    
    """ 
    Esta función tiene como objetivo procesar y transformar datos de movies y ratings almacenados en una base de datos.
    La principal función de ella es separar el año del titulo y realizar la duminización de los géneros.
    
    La función devuelve:
    - `movie_dum`: Un dataframe que contiene la información de las movies con columnas dummizadas para los géneros y la columna `year_sc` escalada.
    - `movies`: El dataframe original de movies con el año separado.
    - `conn`: La conexión a la base de datos.
    - `cur`: El cursor de la base de datos para realizar futuras consultas.

    Esta función es esencial para preparar los datos antes de realizar las recomendaciones a los usuarios em base a las películas y sus calificaciones.
    """

    #### conectar_base_de_Datos#################
    conn=sql.connect('data/db_movies')
    cur=conn.cursor()
    

    ######## convertir datos crudos a bases filtradas por usuarios que tengan cierto número de calificaciones
    fn.ejecutar_sql('preprocesamiento.sql', cur)

    ##### llevar datos que cambian constantemente a python ######
    movies=pd.read_sql('select * from movie_final', conn )
    ratings=pd.read_sql('select * from ratings_final', conn)
    usuarios=pd.read_sql('select distinct (userid) from ratings_final',conn)

    #Separar year de title.
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(int)
    movies['title'] = movies['title'].str.replace(r'\(\d{4}\)', '', regex=True).str.strip()
    
    #Escalar el year
    sc=MinMaxScaler()
    movies[["year_sc"]]=sc.fit_transform(movies[['year']])
    
    #Hacer dumis el genero.
    movies['genres'] = movies['genres'].str.lower()  # Normalizar a minúsculas
    movie_dum = pd.concat([movies, movies['genres'].str.get_dummies(sep='|')], axis=1)  # Separar por "|" y crear columnas dummizadas
    
    #Eliminar columna genres
    movie_dum = movie_dum.drop(columns=['genres', 'year'])
    
    return movie_dum,movies, conn, cur

##########################################################################
###############Función para entrenar modelo por cada usuario ##########
###############Basado en contenido todo lo visto por el usuario Knn#############################
def recomendar(user_id):
    
    """
    Esta función tiene como objetivo realizar las recomendaciones de las películas por medio de un
    algorítmo KNN, para ello tiene como argumento el user_id que recibe un id de un usuario y un entero
    k para conocer la cantidad de películas a recomendar.
    Este modelo tiene en cuenta las películas vistas por el usuario y las elimina para recomendar únicamente
    películas que no haya visto.
    
    La función devuelve las k películas recomendadas.
    """
    movie_dum,movies, conn, cur = preprocesar()
    
    ratings=pd.read_sql('select * from ratings_final WHERE userId=:user',conn, params={'user':user_id})
    l_movie_r=ratings['movieId'].to_numpy()
    movie_dum[['movieId','title']]=movies[['movieId','title']]
    movie_r=movie_dum[movie_dum['movieId'].isin(l_movie_r)]
    movie_r=movie_r.drop(columns=['movieId','title'])
    movie_r["indice"]=1 ### para usar group by y que quede en formato pandas tabla de centroide
    centroide=movie_r.groupby("indice").mean()
    
    
    movie_r=movie_dum[~movie_dum['movieId'].isin(l_movie_r)]
    movie_r=movie_r.drop(columns=['movieId','title'])
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(movie_r)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0]
    recomend_b=movies.loc[ids][['movieId','title']]
    
    
    return recomend_b

##### Generar recomendaciones para usuario lista de usuarios ####
##### No se hace para todos porque es muy pesado #############
def main(list_user):
    """
    Esta función tiene como objetivo generar recomendaciones de películas para una lista de usuarios. Para ello, 
    recibe como argumento list_user, que es una lista de id de usuarios. La función itera sobre cada usuario en la lista, 
    llama a la función recomendar para obtener las recomendaciones de películas y las almacena
    en un dataframe. Luego, guarda todas las recomendaciones en dos formatos: un archivo Excel y un archivo CSV, 
    ubicándolos en el directorio salidas/reco.
    """
    
    recomendaciones_todos=pd.DataFrame()
    for userID in list_user:
            
        recomendaciones=recomendar(userID)
        recomendaciones["userID"]=userID
        recomendaciones.reset_index(inplace=True,drop=True)
        
        recomendaciones_todos=pd.concat([recomendaciones_todos, recomendaciones])

        # Crear directorios si no existen
    output_directory = 'salidas/reco'
    os.makedirs(output_directory, exist_ok=True)
    
    recomendaciones_todos.to_excel('salidas\\reco\\recomendaciones.xlsx')
    recomendaciones_todos.to_csv('salidas\\reco\\recomendaciones.csv')


if __name__=="__main__":
    list_user=[504, 486, 608 ]
    main(list_user)
    
import sys
sys.executable
