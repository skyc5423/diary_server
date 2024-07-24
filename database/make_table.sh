#!/bin/bash

# Check if required environment variables are set
if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_DATABASE" ]; then
    echo "Error: MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables must be set."
    exit 1
fi

# SQL commands to create tables
SQL_COMMANDS=$(cat << EOF
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX (id)
);

CREATE TABLE diary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userId INT NOT NULL,
    date DATE NOT NULL,
    rawInput TEXT,
    content TEXT,
    imgUrl VARCHAR(255),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX (id),
    FOREIGN KEY (userId) REFERENCES users(id)
);
EOF
)

# Execute SQL commands
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" << EOF
$SQL_COMMANDS
EOF

echo "Tables created successfully!"