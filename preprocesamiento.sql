-------------------- Preprocesamiento --------------------

----- Crear tabla con usuarios que han calificado más de 50 películas
DROP TABLE IF EXISTS usuarios_sel;

CREATE TABLE usuarios_sel AS 
SELECT "userID", COUNT(*) AS count_rating
FROM ratings
GROUP BY "userID"
HAVING count_rating > 50 and count_rating<= 1500
ORDER BY count_rating DESC;

------ Crear tabla con películas que han sido calificados por más de 50 usuarios
DROP TABLE IF EXISTS movies_sel;

CREATE TABLE movies_sel AS
SELECT m.movieID, 
       COUNT(r.movieID) AS count_rating
FROM movies m
LEFT JOIN ratings r ON m.movieID = r.movieID
GROUP BY m.movieID, m.title
HAVING count_rating > 50
ORDER BY count_rating DESC;

------- Crear tabla filtradas de películas, usuarios y calificaciones
DROP TABLE IF EXISTS ratings_final;

CREATE TABLE ratings_final AS
SELECT r.userID, r.movieID, r.rating
FROM ratings r
INNER JOIN movies_sel m ON r.movieID = m.movieID
INNER JOIN usuarios_sel u ON u.userID = r.userID;

------- Crear tabla de películas finales
DROP TABLE IF EXISTS movie_final;

CREATE TABLE movie_final AS
SELECT a.movieID, a.title, a.genres
FROM movies a
INNER JOIN movies_sel b ON a.movieID = b.movieID;

----- Crear tabla completa
DROP TABLE IF EXISTS full_ratings;

CREATE TABLE full_ratings AS
SELECT r.*, m.title, m.genres
FROM ratings_final r
INNER JOIN movie_final m ON r.movieID = m.movieID;