
    SELECT AVG(ratings.rating) AS average_rating
    FROM movies
    JOIN ratings ON movies.id = ratings.movie_id
    WHERE movies.year = 2012;
    