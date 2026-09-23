-- =========================================================
-- SYNTAXAA DATABASE SCHEMA
-- Offline-First Intelligent Debugging & Analysis System
-- =========================================================
-- Run this file once in MySQL to create the database and tables.
-- Command line:  mysql -u root -p < database.sql
-- =========================================================

CREATE DATABASE IF NOT EXISTS syntaxaa;
USE syntaxaa;

-- ---------------------------------------------------------
-- 1. USERS TABLE
-- Stores login credentials and whether the account is a
-- student or a teacher.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,   -- stored as a SHA-256 hash, never plain text
    user_type   ENUM('student', 'teacher') NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- 2. ERRORS TABLE
-- The Error Encyclopedia's core data: one row per known
-- Python error type/category.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS errors (
    error_id            INT AUTO_INCREMENT PRIMARY KEY,
    error_name          VARCHAR(100) NOT NULL,
    category            VARCHAR(50) NOT NULL,      -- e.g. Syntax, Logic, Indentation, Name
    meaning             VARCHAR(255) NOT NULL,
    beginner_explanation TEXT NOT NULL,
    example_code        TEXT
);

-- ---------------------------------------------------------
-- 3. FIXES TABLE
-- Linked to errors: how to fix it and how to avoid it again.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS fixes (
    fix_id          INT AUTO_INCREMENT PRIMARY KEY,
    error_id        INT NOT NULL,
    fix_text        TEXT NOT NULL,
    prevention_tip  TEXT,
    FOREIGN KEY (error_id) REFERENCES errors(error_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 4. USER_HISTORY TABLE
-- Every time a student submits code and an error is found,
-- one row is logged here. This feeds Bug DNA, progress
-- analysis, and the teacher dashboard.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_history (
    history_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    error_id        INT,
    code_snippet    TEXT,
    occurred_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved        BOOLEAN DEFAULT FALSE,
    resolved_at     DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (error_id) REFERENCES errors(error_id) ON DELETE SET NULL
);

-- ---------------------------------------------------------
-- 5. PERFORMANCE_DATA TABLE
-- One row per student per error category, tracking how
-- often it happens and how long it takes to resolve.
-- Updated (not re-inserted) whenever a new matching entry
-- is logged in user_history.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS performance_data (
    record_id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT NOT NULL,
    error_category       VARCHAR(50) NOT NULL,
    frequency            INT DEFAULT 0,
    avg_debug_time_seconds INT DEFAULT 0,
    last_updated         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_category (user_id, error_category)
);

-- ---------------------------------------------------------
-- 6. CLASS_CONNECTIONS TABLE
-- Optional teacher-student link. A teacher generates a
-- class_code; a student who enters that code becomes
-- connected to that teacher.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS class_connections (
    connection_id   INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id      INT NOT NULL,
    student_id      INT NOT NULL,
    class_code      VARCHAR(20) NOT NULL,
    connected_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_connection (teacher_id, student_id)
);

-- ---------------------------------------------------------
-- SEED DATA: a starter set of common Python errors so the
-- Encyclopedia and Error Detection Engine have content
-- immediately after setup.
-- ---------------------------------------------------------
INSERT INTO errors (error_name, category, meaning, beginner_explanation, example_code) VALUES
('SyntaxError', 'Syntax', 'The code breaks Python''s grammar rules.',
 'Python could not understand the structure of your code. This often happens because of a missing colon, bracket, or using = instead of == inside a condition.',
 'if x=5:\n    print(x)'),
('IndentationError', 'Indentation', 'Code is not indented the way Python expects.',
 'Python uses indentation (spaces at the start of a line) to know which lines belong together, for example inside an if block or a loop. Mixing tabs and spaces or forgetting to indent causes this.',
 'if x > 5:\nprint("big")'),
('NameError', 'Name', 'You used a variable or function that does not exist yet.',
 'This usually means you misspelled a variable name, or tried to use it before creating it.',
 'print(total)\ntotal = 10'),
('TypeError', 'Type', 'An operation was used on the wrong type of data.',
 'This happens when you try to combine incompatible types, like adding a number and a piece of text directly.',
 'age = 15\nprint("Age: " + age)'),
('ZeroDivisionError', 'Logic', 'The code tried to divide a number by zero.',
 'Division by zero is mathematically undefined, so Python stops the program to warn you.',
 'result = 10 / 0'),
('IndexError', 'Logic', 'You tried to access a position in a list that does not exist.',
 'Lists are numbered starting from 0. Asking for an index beyond the last item causes this error.',
 'numbers = [1, 2, 3]\nprint(numbers[5])'),
('KeyError', 'Logic', 'You tried to access a dictionary key that does not exist.',
 'Dictionaries store data as key-value pairs. Asking for a key that was never added causes this error.',
 'student = {"name": "Ravi"}\nprint(student["age"])'),
('ValueError', 'Type', 'A function received a value of the right type but an inappropriate value.',
 'This often happens when converting text to a number, but the text is not actually a valid number.',
 'age = int("twelve")');

INSERT INTO fixes (error_id, fix_text, prevention_tip) VALUES
(1, 'Check for a missing colon (:) at the end of if/for/while/def lines, and use == instead of = when comparing values.', 'Read each line slowly and check brackets, colons, and quotation marks before running your code.'),
(2, 'Make sure every line inside a block (if/for/while/def) is indented consistently, using 4 spaces.', 'Stick to either spaces or tabs, never mix them, and let your editor show whitespace characters.'),
(3, 'Check the spelling of the variable name, and make sure it is created (assigned a value) before it is used.', 'Declare and initialise variables before using them, and use consistent naming.'),
(4, 'Convert values to the same type before combining them, for example using str() or int().', 'Think about what type each variable holds before combining them in an expression.'),
(5, 'Add a check to make sure the divisor is not zero before dividing.', 'Validate user input or calculated values before using them as a divisor.'),
(6, 'Check the length of the list with len() before accessing an index, or use a valid index.', 'Remember indexing starts at 0 and the last valid index is len(list) - 1.'),
(7, 'Check whether the key exists using "in" or use .get() with a default value.', 'Print or check the dictionary structure before trying to access a specific key.'),
(8, 'Validate the input before converting it, or use a try/except block around the conversion.', 'Always assume user input could be invalid and check it before converting.');
