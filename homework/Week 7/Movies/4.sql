
    SELECT COUNT(*) AS number_of_movies
    FROM movies
    JOIN ratings ON movies.id = ratings.movie_id
    WHERE ratings.rating = 10.0;
    