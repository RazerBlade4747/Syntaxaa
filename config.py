"""
config.py
---------
Central place for settings that might change between computers
(database credentials) or between students (optional AI key).

"""

# ---------------------------------------------------------
# MySQL connection settings
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234567890",   # <-- CHANGE THIS to your MySQL password
    "database": "syntaxaa"
}



GEMINI_API_KEY = "AQ.Ab8RN6Iu4r9GH6W_S5OucBoBRfMQG_LMm12gpMCI5rOWNYNCGA"


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234567890",
    "database": "syntaxaa",
    "port": 3306
}