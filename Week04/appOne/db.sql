-- docker network create mysql-net
-- docker run -d --name mysql-CAA900NBB --network mysql-net -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 mysql:latest
-- docker exec -it mysql-CAA900NBB mysql -u root -p
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS auth_system;

-- Use the database
USE auth_system;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

