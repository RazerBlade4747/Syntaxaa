"""
config.py
---------
Central place for settings that might change between computers
(database credentials) or between students (optional AI key).

All secrets are now read from environment variables (via a local
.env file, loaded with python-dotenv) instead of being hardcoded.
This lets the same code point at a local MySQL install for offline
dev, and at a hosted database (e.g. Aiven MySQL on Render) in
production, without editing this file.

SETUP:
1. Install python-dotenv:  pip install python-dotenv
2. Create a file named ".env" in the project root (same folder as
   this file) - it is already excluded via .gitignore - with:

       DB_HOST=your-service-xxxx.aivencloud.com
       DB_PORT=12345
       DB_USER=avnadmin
       DB_PASSWORD=your-aiven-password
       DB_NAME=syntaxaa
       DB_SSL_CA=ca.pem            # path to Aiven's CA cert (see below)
       GEMINI_API_KEY=your-key-here

3. Download the CA certificate from your Aiven console
   (Service -> Overview -> "CA certificate" download button),
   save it as ca.pem in the project root (or point DB_SSL_CA at
   wherever you saved it).

If DB_HOST is not set at all, this file falls back to a plain
localhost MySQL connection with no SSL, so local development still
works without any .env file.
"""

import os
from dotenv import load_dotenv

# Loads variables from a local .env file into the environment.
# Safe to call even if .env does not exist - it just does nothing.
load_dotenv()

# ---------------------------------------------------------
# MySQL connection settings
# ---------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "syntaxaa")
DB_SSL_CA = os.getenv("DB_SSL_CA")  # e.g. "ca.pem" - only needed for hosted DBs

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "port": DB_PORT,
}

# Aiven (and most hosted MySQL providers) require SSL. Only add the
# SSL options when we're actually pointed at a remote host and a CA
# cert path has been provided, so plain local development is
# unaffected.
if DB_HOST != "localhost" and DB_SSL_CA:
    DB_CONFIG["ssl_ca"] = DB_SSL_CA
    DB_CONFIG["ssl_verify_cert"] = True

# ---------------------------------------------------------
# Optional AI key (Gemini / Claude, depending on module)
# ---------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Backwards-compat: some modules (modules/ai_assist.py) reference
# config.AI_API_KEY / config.AI_MODEL instead of the Gemini-specific
# names used by modules/ai_debugger.py.
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")
