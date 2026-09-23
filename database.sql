-- =========================================================
-- SYNTAXAA DATABASE SCHEMA
-- Offline-First Intelligent Debugging & Analysis System
-- =========================================================
-- Run this file once in MySQL to create the database and tables.
-- Command line: mysql -u root -p < database.sql
-- =========================================================

CREATE DATABASE IF NOT EXISTS syntaxaa;
USE syntaxaa;

-- ---------------------------------------------------------
-- 1. USERS TABLE
-- Stores login credentials and whether the account is a
-- student or a teacher.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL, -- stored as a SHA-256 hash, never plain text
  user_type ENUM('student', 'teacher') NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- 2. ERRORS TABLE
-- The Error Encyclopedia's core data: one row per known
-- Python error type/category.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS errors (
  error_id INT AUTO_INCREMENT PRIMARY KEY,
  error_name VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL, -- e.g. Syntax, Logic, Indentation, Name
  meaning VARCHAR(255) NOT NULL,
  beginner_explanation TEXT NOT NULL,
  example_code TEXT
);

-- ---------------------------------------------------------
-- 3. FIXES TABLE
-- Linked to errors: how to fix it and how to avoid it again.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS fixes (
  fix_id INT AUTO_INCREMENT PRIMARY KEY,
  error_id INT NOT NULL,
  fix_text TEXT NOT NULL,
  prevention_tip TEXT,
  FOREIGN KEY (error_id) REFERENCES errors(error_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 4. USER_HISTORY TABLE
-- Every time a student submits code and an error is found,
-- one row is logged here. This feeds Bug DNA, progress
-- analysis, and the teacher dashboard.
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS user_history (
  history_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  error_id INT,
  code_snippet TEXT,
  occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  resolved BOOLEAN DEFAULT FALSE,
  resolved_at DATETIME NULL,
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
  record_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  error_category VARCHAR(50) NOT NULL,
  frequency INT DEFAULT 0,
  avg_debug_time_seconds INT DEFAULT 0,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
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
  connection_id INT AUTO_INCREMENT PRIMARY KEY,
  teacher_id INT NOT NULL,
  student_id INT NOT NULL,
  class_code VARCHAR(20) NOT NULL,
  connected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
  UNIQUE KEY unique_connection (teacher_id, student_id)
);

-- ---------------------------------------------------------
-- SEED DATA: a starter set of common Python errors so the
-- Encyclopedia and Error Detection Engine have content
-- immediately after setup.
--
-- Covers core built-in exceptions (Syntax/Name/Type/Logic),
-- plus module-specific ones students hit in a CBSE Class 12
-- project: file handling, pickle, tkinter, imports, and
-- MySQL connectivity (mysql.connector).
-- ---------------------------------------------------------
INSERT INTO errors (error_name, category, meaning, beginner_explanation, example_code) VALUES
('SyntaxError', 'Syntax', 'The code breaks Python''s grammar rules.',
 'Python could not understand the structure of your code. This often happens because of a missing colon, bracket, or using = instead of == inside a condition.',
 'if x=5:\n print(x)'),
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
 'age = int("twelve")'),
('FileNotFoundError', 'File Handling', 'You tried to open a file that does not exist at the given path.',
 'This happens when the file name or its location (path) is wrong, or the file has not been created yet. Python cannot open a file that isn''t where you told it to look.',
 'file = open("marks.txt", "r")'),
('PermissionError', 'File Handling', 'The operating system did not allow this program to open or modify the file.',
 'This can happen if the file is open in another program (like Excel), if it is marked read-only, or if you don''t have the rights to write to that folder.',
 'file = open("C:/Windows/system.ini", "w")'),
('UnicodeDecodeError', 'File Handling', 'Python could not convert the file''s bytes into text using the expected encoding.',
 'Text files are stored as bytes, and Python needs to know which encoding (like UTF-8) to use to read them correctly. This error appears when the file uses a different encoding than Python assumed.',
 'file = open("data.txt", "r")\ncontent = file.read()'),
('EOFError', 'Pickle', 'Python reached the end of the file while still expecting more data.',
 'This very commonly happens with pickle.load() when the file you''re reading from is empty or was never written to properly. Python starts reading a pickled object but runs out of bytes before it finishes.',
 'import pickle\nfile = open("data.dat", "rb")\nrecord = pickle.load(file)'),
('UnpicklingError', 'Pickle', 'The data in the file is not a valid pickle stream, so it cannot be converted back into a Python object.',
 'This happens when you try to unpickle a file that wasn''t created with pickle.dump() at all (for example, a plain text file), or the file has become corrupted.',
 'import pickle\nfile = open("notes.txt", "rb")\ndata = pickle.load(file)'),
('AttributeError', 'Attribute', 'You tried to use a method or property that does not exist for that type of object.',
 'Every object (a list, a string, a widget) only has certain methods available. This error means you called something that object doesn''t have - often because of a typo, or because the object is not the type you thought it was (for example, it is None).',
 'name = None\nprint(name.upper())'),
('ImportError', 'Import', 'Python found the module, but could not find the specific name you tried to import from it.',
 'This is different from a missing module - the module itself exists, but the particular function, class or variable you asked for isn''t inside it (often due to a typo or a version difference).',
 'from tkinter import Buttonn'),
('ModuleNotFoundError', 'Import', 'Python could not find the module you tried to import anywhere on your system.',
 'This usually means the module is not installed (for external libraries like pandas or mysql-connector-python), or you misspelled the module name.',
 'import pandaas'),
('TclError', 'Tkinter', 'Tkinter''s underlying Tcl engine rejected a command, usually because of an invalid widget option or a widget that no longer exists.',
 'This is the most common Tkinter error. It often happens when you pass an option a widget doesn''t support (like a wrong color name), or when you try to update a widget that has already been destroyed.',
 'import tkinter as tk\nroot = tk.Tk()\nlabel = tk.Label(root, text="Hi", colour="red")\nroot.mainloop()'),
('RuntimeError', 'Logic', 'An error occurred that doesn''t fit any more specific category - commonly raised when a collection is changed while it''s being looped over.',
 'A frequent cause is modifying a dictionary or set while iterating over it with a for loop, which Python does not allow because it can''t guarantee which items get visited.',
 'data = {"a": 1, "b": 2}\nfor key in data:\n    del data[key]'),
('StopIteration', 'Logic', 'next() was called on an iterator that has no more items left to give.',
 'Iterators (like the object returned by iter(a_list)) run out eventually. Calling next() one time too many raises this error instead of looping forever.',
 'numbers = iter([1, 2])\nprint(next(numbers))\nprint(next(numbers))\nprint(next(numbers))'),
('OverflowError', 'Logic', 'A calculation produced a result too large for Python to represent as a floating-point number.',
 'This is rare with whole numbers (Python''s int can grow as large as memory allows) but happens with very large floating-point results, for example from math.exp() with a huge input.',
 'import math\nresult = math.exp(1000)'),
('RecursionError', 'Logic', 'A function called itself too many times without stopping, exceeding Python''s maximum recursion depth.',
 'This happens with recursive functions (a function that calls itself) when the base case - the condition that stops the recursion - is missing, wrong, or never reached.',
 'def countdown(n):\n    print(n)\n    countdown(n - 1)\ncountdown(5)'),
('ProgrammingError', 'Database', 'MySQL rejected the SQL command you sent, usually because of a syntax mistake or a reference to something that doesn''t exist.',
 'This covers mistakes like a typo in a table/column name, missing quotes around text values in SQL, or the database/table not existing yet.',
 'cursor.execute("SELECT * FROM studnets")'),
('InterfaceError', 'Database', 'Python could not communicate with the MySQL server at all.',
 'This usually means the MySQL server isn''t running, or the host/port/credentials in your connection settings are wrong.',
 'import mysql.connector\nconn = mysql.connector.connect(host="localhost", user="root", password="wrong", database="syntaxaa")');

INSERT INTO fixes (error_id, fix_text, prevention_tip) VALUES
(1, 'Check for a missing colon (:) at the end of if/for/while/def lines, and use == instead of = when comparing values.', 'Read each line slowly and check brackets, colons, and quotation marks before running your code.'),
(2, 'Make sure every line inside a block (if/for/while/def) is indented consistently, using 4 spaces.', 'Stick to either spaces or tabs, never mix them, and let your editor show whitespace characters.'),
(3, 'Check the spelling of the variable name, and make sure it is created (assigned a value) before it is used.', 'Declare and initialise variables before using them, and use consistent naming.'),
(4, 'Convert values to the same type before combining them, for example using str() or int().', 'Think about what type each variable holds before combining them in an expression.'),
(5, 'Add a check to make sure the divisor is not zero before dividing.', 'Validate user input or calculated values before using them as a divisor.'),
(6, 'Check the length of the list with len() before accessing an index, or use a valid index.', 'Remember indexing starts at 0 and the last valid index is len(list) - 1.'),
(7, 'Check whether the key exists using "in" or use .get() with a default value.', 'Print or check the dictionary structure before trying to access a specific key.'),
(8, 'Validate the input before converting it, or use a try/except block around the conversion.', 'Always assume user input could be invalid and check it before converting.'),
(9, 'Check the file name for typos, and make sure the file is in the same folder as your script (or give the correct full path).', 'Use os.path.exists() to check if a file exists before trying to open it, or wrap the open() call in a try/except.'),
(10, 'Close the file if it is open elsewhere, check the file/folder permissions, or save to a different location you have write access to.', 'Avoid writing directly into protected system folders; use a folder inside your own project or Documents.'),
(11, 'Specify the correct encoding when opening the file, for example open("data.txt", "r", encoding="utf-8").', 'Always open text files with an explicit encoding instead of relying on the system default.'),
(12, 'Check that the file actually has data in it (its size is not 0), and that you used pickle.dump() to write to it before trying to read. Wrap pickle.load() in a try/except EOFError to handle an empty file gracefully.', 'Before looping and calling pickle.load() repeatedly, check the file is not empty, and stop the loop with a try/except EOFError when there is nothing left to read.'),
(13, 'Make sure you are opening a file that was actually written using pickle.dump(), and that the file was not edited by a text editor afterwards.', 'Use a distinct file extension like .dat or .pkl for pickle files so you do not accidentally open a plain text file with pickle.load().'),
(14, 'Check the spelling of the method name, and print(type(your_variable)) to confirm it is actually the type of object you expect.', 'Be careful with functions that can return None - always check for None before calling a method on the result.'),
(15, 'Check the exact spelling and capitalisation of the name you are importing, and confirm it actually exists in that module''s documentation.', 'Use your editor''s autocomplete when importing, so you only import names that actually exist.'),
(16, 'Check the spelling of the module name, and if it is a third-party library, install it first using pip install <module_name>.', 'Keep a requirements.txt file listing every external library your project needs, so you remember to install them on a new computer.'),
(17, 'Check the widget option''s spelling (it is "fg", not "colour", for foreground text color), and make sure you are not configuring a widget after it has been destroyed.', 'Refer to the exact Tkinter option names in the documentation instead of guessing, and double check widget option spellings (bg, fg, font, etc.).'),
(18, 'Loop over a copy of the collection instead, for example using list(data.keys()), so the original can be safely modified.', 'Never add or remove items from a list/dict/set while directly looping over it - build a new collection or loop over a copy instead.'),
(19, 'Use a for loop instead of manually calling next() where possible, since for loops stop automatically. If you must use next(), provide a default value: next(numbers, None).', 'Prefer "for item in iterable:" over manual next() calls unless you specifically need to control iteration step by step.'),
(20, 'Check that the numbers going into the calculation are reasonable, and consider using Python''s built-in int type (which does not overflow) instead of float where possible.', 'Validate input ranges before running calculations that could produce extremely large results.'),
(21, 'Add or fix the base case so the function stops calling itself once a certain condition is met, for example "if n <= 0: return".', 'Every recursive function needs a clear base case - write it first before writing the recursive call.'),
(22, 'Check the SQL syntax carefully, and confirm the table and column names match exactly what is in your database (run SHOW TABLES; to check).', 'Run your SQL query directly in a MySQL client first to confirm it works before putting it inside Python code.'),
(23, 'Make sure the MySQL service is running, and double-check the host, username, password and database name in config.py.', 'Test your database credentials with a MySQL client (like MySQL Workbench) before relying on them in your Python code.');
