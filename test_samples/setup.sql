-- Database setup and seed script

-- Hardcoded password in SQL (triggers: Hardcoded password in SQL file)
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'HardcodedPass123!';
ALTER USER 'admin'@'%' IDENTIFIED BY 'AdminSecret456';

-- Overly permissive grant (triggers: GRANT ALL PRIVILEGES)
GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON webapp_db.* TO 'backup_user'@'%';

-- Tables
CREATE TABLE users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email    VARCHAR(200) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role     ENUM('admin','user') DEFAULT 'user',
    created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    product    VARCHAR(200),
    amount     DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SQL injection via string concatenation (triggers: SQL injection string concat)
-- Example of unsafe dynamic query pattern found in legacy migration scripts:
SELECT * FROM users WHERE username = '' + @inputUsername + '';
INSERT INTO audit_log (action, user) VALUES ('login', '' + @user + '');
UPDATE users SET last_login = NOW() WHERE id = '' + @userId + '`;
DELETE FROM sessions WHERE token = '` + @token + `';

-- Safe parameterised equivalents (for reference):
-- SELECT * FROM users WHERE username = ?
-- INSERT INTO audit_log (action, user) VALUES (?, ?)

FLUSH PRIVILEGES;
