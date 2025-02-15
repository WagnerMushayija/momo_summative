-- schema.sql
CREATE DATABASE IF NOT EXISTS transactions_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE transactions_db;

CREATE TABLE IF NOT EXISTS transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    date_time DATETIME NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    sender VARCHAR(100),
    receiver VARCHAR(100),
    transaction_id VARCHAR(50) UNIQUE,
    raw_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_date_time (date_time),
    INDEX idx_amount (amount),
    INDEX idx_sender (sender),
    INDEX idx_receiver (receiver)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;