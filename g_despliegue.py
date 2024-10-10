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
    
    movie_dum,movies, conn, cur = preprocesar()
    
    ratings=pd.read_sql('select * from ratings_final where userID = 1' ,conn)
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
    list_user=[1,4,6 ]
    main(list_user)
    
