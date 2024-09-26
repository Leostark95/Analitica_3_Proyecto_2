-------------------- Preprocesamiento --------------------

----- Crear tabla con usuarios que han calificado más de 50 películas
DROP table if exists usuarios_sel;

CREATE table usuarias_sel as 

    SELECT "userId", COUNT(*) as count_rating
    FROM ratings
    GROUP BY "userID"
    HAVING count_rating >50
    ORDER BY count_rating DESC;


------ Crear tabla con películas que han sido calificados por más de 50 usuarios

DROP table if exists movies_sel;

CREATE table movies_sel as
    SELECT m.movieID, m.title, COUNT(r.movieID) as count_rating
    FROM movies m
    LEFT JOIN ratings r ON m.movieID = r.movieID
    GROUP BY count_rating
    HAVING count_rating > 50
    ORDER BY count_rating DESC;


-------crear tablas filtradas de películas, usuarios y calificaciones ---
DROP table if exists ratings_final;

CREATE table ratings_final as
    SELECT r.userID, r.movieID, r.ratings
    FROM ratings r
    INNER JOIN movies_sel m ON r.movieID = m.movieID
    INNER JOIN usuarias_sel u ON u.userID = r.userID


------- Crear tabla de usuarios finales
DROP table if exists users_final;

CREATE table users_final as
    SELECT 