CREATE DATABASE sugar_prices_db;

USE sugar_prices_db;

CREATE TABLE monthly_rbi_cpi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monthly_date VARCHAR(10),
    rural_index decimal,
    rural_inflation float,
    urban_index decimal,
    urban_inflation float,
    combined_index decimal,
    combined_inflation float
);

CREATE TABLE historical_sugar_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monthly_date date,
    price float
);

CREATE TABLE sugar_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    monthly_date date,
    sugar_production float,
    sugar_export float,
    sugar_import float
);

drop table monthly_rbi_cpi;

select * from historical_sugar_prices;

select * from sugar_stats;