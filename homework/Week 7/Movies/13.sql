
    SELECT DISTINCT p2.name
    FROM people AS p1
    JOIN stars AS s1 ON p1.id = s1.person_id
    JOIN movies ON movies.id = s1.movie_id
    JOIN stars AS s2 ON movies.id = s2.movie_id
    JOIN people AS p2 ON p2.id = s2.person_id
    WHERE p1.name = 'Kevin Bacon' AND p1.birth = 1958 AND p2.name != 'Kevin Bacon';
    