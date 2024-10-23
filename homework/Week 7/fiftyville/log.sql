-- Initial exploration to understand database structure
-- [RU] Исходное исследование для понимания структуры базы данных
-- [FR] Exploration initiale pour comprendre la structure de la base de données
-- [ES] Exploración inicial para entender la estructura de la base de datos
PRAGMA table_info(crime_scene_reports);

-- Schema details of the interviews table
-- [RU] Схема таблицы интервью
-- [FR] Détails du schéma de la table des interviews
-- [ES] Detalles del esquema de la tabla de entrevistas
PRAGMA table_info(interviews);

-- Schema details of the courthouse_security_logs table
-- [RU] Схема таблицы журналов безопасности суда
-- [FR] Détails du schéma de la table des journaux de sécurité du tribunal
-- [ES] Detalles del esquema de la tabla de registros de seguridad del juzgado
PRAGMA table_info(courthouse_security_logs);

-- Schema details of the atm_transactions table
-- [RU] Схема таблицы транзакций банкомата
-- [FR] Détails du schéma de la table des transactions aux distributeurs automatiques
-- [ES] Detalles del esquema de la tabla de transacciones de cajeros automáticos
PRAGMA table_info(atm_transactions);

-- Schema details of the bank_accounts table
-- [RU] Схема таблицы банковских счетов
-- [FR] Détails du schéma de la table des comptes bancaires
-- [ES] Detalles del esquema de la tabla de cuentas bancarias
PRAGMA table_info(bank_accounts);

-- Schema details of the airports table
-- [RU] Схема таблицы аэропортов
-- [FR] Détails du schéma de la table des aéroports
-- [ES] Detalles del esquema de la tabla de aeropuertos
PRAGMA table_info(airports);

-- Schema details of the flights table
-- [RU] Схема таблицы рейсов
-- [FR] Détails du schéma de la table des vols
-- [ES] Detalles del esquema de la tabla de vuelos
PRAGMA table_info(flights);

-- Schema details of the passengers table
-- [RU] Схема таблицы пассажиров
-- [FR] Détails du schéma de la table des passagers
-- [ES] Detalles del esquema de la tabla de pasajeros
PRAGMA table_info(passengers);

-- Schema details of the phone_calls table
-- [RU] Схема таблицы телефонных звонков
-- [FR] Détails du schéma de la table des appels téléphoniques
-- [ES] Detalles del esquema de la tabla de llamadas telefónicas
PRAGMA table_info(phone_calls);

-- Schema details of the people table
-- [RU] Схема таблицы людей
-- [FR] Détails du schéma de la table des personnes
-- [ES] Detalles del esquema de la tabla de personas
PRAGMA table_info(people);

-- Finding the crime scene report for July 28, 2023 on Humphrey Street
-- [RU] Поиск отчета о месте преступления за 28 июля 2023 года на Хамфри-стрит
-- [FR] Recherche du rapport de scène de crime pour le 28 juillet 2023 sur Humphrey Street
-- [ES] Buscando el informe de la escena del crimen del 28 de julio de 2023 en Humphrey Street
SELECT * FROM crime_scene_reports WHERE year = 2023 AND month = 7 AND day = 28 AND street = 'Humphrey Street';

-- Retrieving interviews related to the bakery
-- [RU] Извлечение интервью, связанных с пекарней
-- [FR] Récupération des interviews liées à la boulangerie
-- [ES] Recuperación de entrevistas relacionadas con la panadería
SELECT * FROM interviews WHERE transcript LIKE '%bakery%' AND year = 2023 AND month = 7 AND day = 28;

-- Retrieving bakery security logs for cars leaving around the time of the theft (10:15am to 10:25am)
-- [RU] Извлечение журналов безопасности пекарни для машин, покидающих место кражи (с 10:15 до 10:25)
-- [FR] Récupération des journaux de sécurité de la boulangerie pour les voitures quittant les lieux autour de l'heure du vol (de 10h15 à 10h25)
-- [ES] Recuperación de los registros de seguridad de la panadería para los coches que salieron alrededor de la hora del robo (de 10:15 a 10:25)
SELECT * FROM bakery_security_logs WHERE year = 2023 AND month = 7 AND day = 28 AND hour = 10 AND minute BETWEEN 15 AND 25;

-- Retrieving ATM transactions from Leggett Street on the day of the theft
-- [RU] Извлечение транзакций в банкомате на улице Леггетт в день кражи
-- [FR] Récupération des transactions aux distributeurs automatiques sur Leggett Street le jour du vol
-- [ES] Recuperación de transacciones del cajero automático en Leggett Street el día del robo
SELECT * FROM atm_transactions WHERE year = 2023 AND month = 7 AND day = 28 AND atm_location = 'Leggett Street' AND transaction_type = 'withdraw';

-- Retrieving phone call records made on July 28, 2023 with duration less than 60 seconds
-- [RU] Извлечение записей телефонных звонков, сделанных 28 июля 2023 года, с продолжительностью менее 60 секунд
-- [FR] Récupération des enregistrements des appels téléphoniques effectués le 28 juillet 2023 d'une durée inférieure à 60 secondes
-- [ES] Recuperación de los registros de llamadas telefónicas realizadas el 28 de julio de 2023 con una duración inferior a 60 segundos
SELECT * FROM phone_calls WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60;

-- Retrieving bank account owners for transactions from the ATM on Leggett Street
-- [RU] Извлечение владельцев банковских счетов для транзакций из банкомата на улице Леггетт
-- [FR] Récupération des propriétaires de comptes bancaires pour les transactions aux distributeurs automatiques sur Leggett Street
-- [ES] Recuperación de los titulares de cuentas bancarias para las transacciones del cajero automático en Leggett Street
SELECT * FROM bank_accounts WHERE account_number IN (28500762,28296815,76054385,49610011,16153065,25506511,81061156,26013199);

-- Finding the earliest flight departing on July 29, 2023
-- [RU] Поиск самого раннего рейса, отправляющегося 29 июля 2023 года
-- [FR] Recherche du premier vol partant le 29 juillet 2023
-- [ES] Buscando el primer vuelo que sale el 29 de julio de 2023
SELECT * FROM flights WHERE year = 2023 AND month = 7 AND day = 29 ORDER BY hour, minute ASC LIMIT 1;

-- Finding passengers on the earliest flight from Fiftyville
-- [RU] Поиск пассажиров на самом раннем рейсе из Фифтивилля
-- [FR] Recherche des passagers sur le premier vol au départ de Fiftyville
-- [ES] Buscando a los pasajeros en el primer vuelo desde Fiftyville
SELECT * FROM passengers WHERE flight_id = 36;

-- Finding the thief by cross-referencing all lists
-- [RU] Поиск вора путем перекрестной проверки всех списков
-- [FR] Recherche du voleur en croisant toutes les listes
-- [ES] Buscando al ladrón cruzando todas las listas
SELECT p.name FROM people p INNER JOIN passengers ps ON p.passport_number = ps.passport_number AND ps.flight_id = 36 INNER JOIN phone_calls pc ON p.phone_number = pc.caller AND pc.day = 28 AND pc.duration < 60 INNER JOIN bakery_security_logs bsl ON p.license_plate = bsl.license_plate AND bsl.day = 28 AND bsl.activity = 'exit' AND bsl.hour = 10 AND bsl.minute > 15 AND bsl.minute < 25 INNER JOIN bank_accounts ba ON p.id = ba.person_id INNER JOIN atm_transactions atm ON ba.account_number = atm.account_number AND atm.transaction_type = 'withdraw' AND atm.day = 28 AND atm.atm_location = 'Leggett Street';

-- Finding the accomplice from Bruce's call history on July 28th
-- [RU] Поиск сообщника по истории звонков Бруса от 28 июля
-- [FR] Recherche du complice à partir de l'historique des appels de Bruce le 28 juillet
-- [ES] Buscando al cómplice a partir del historial de llamadas de Bruce el 28 de julio
SELECT name FROM people WHERE phone_number IN ( SELECT receiver FROM phone_calls WHERE day = 28 AND duration < 60 AND caller = ( SELECT phone_number FROM people WHERE name = 'Bruce' ) );
