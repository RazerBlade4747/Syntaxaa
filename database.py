import hashlib
import json
import os
import mysql.connector
from mysql.connector import Error as MySQLError
import config

# Global Force Offline Toggle Flag
FORCE_OFFLINE = False

# Path to local offline error seed fallback
SEED_FILE = os.path.join(os.path.dirname(__file__), "data", "errors_seed.json")


def is_offline():
    """Returns True if user forced offline or MySQL is unreachable."""
    if FORCE_OFFLINE:
        return True
    return get_connection() is None


def get_connection():
    """
    Attempts connection to MySQL using config.py settings.
    Returns None if connection fails.
    """
    if FORCE_OFFLINE:
        return None
    try:
        conn = mysql.connector.connect(**config.DB_CONFIG)
        return conn
    except MySQLError:
        return None


def hash_password(raw_password):
    """Turns a plain-text password into a SHA-256 hash before storage."""
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


# =========================================================
# AUTHENTICATION
# =========================================================

def create_user(username, password, user_type):
    from modules import sync_manager
    if is_offline():
        return sync_manager.create_user_csv(username, password, user_type)

    if not username.strip() or not password.strip():
        return False, "Please enter both a username and a password."

    conn = get_connection()
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute(
            "INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)",
            (username.strip(), hash_password(password), user_type)
        )
        conn.commit()
        return True, "Account created successfully. You can now log in."
    except MySQLError as e:
        if e.errno == 1062:
            return False, "That username is already taken. Please choose another."
        return False, "Something went wrong while creating your account."
    finally:
        cursor.close()
        conn.close()


def verify_login(username, password):
    from modules import sync_manager
    if is_offline():
        return sync_manager.verify_login_csv(username, password)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "SELECT user_id, username, user_type FROM users WHERE username = %s AND password = %s",
            (username.strip(), hash_password(password))
        )
        return cursor.fetchone()
    except MySQLError:
        return sync_manager.verify_login_csv(username, password)
    finally:
        cursor.close()
        conn.close()


# =========================================================
# ERROR ENCYCLOPEDIA
# =========================================================

def get_all_errors():
    conn = get_connection()
    if conn is None:
        return _load_seed_errors()

    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM errors ORDER BY error_name")
        rows = cursor.fetchall()
        return rows if rows else _load_seed_errors()
    except MySQLError:
        return _load_seed_errors()
    finally:
        cursor.close()
        conn.close()


def search_errors(keyword):
    all_errors = get_all_errors()
    keyword = keyword.strip().lower()
    if not keyword:
        return all_errors
    return [
        e for e in all_errors
        if keyword in e["error_name"].lower() or keyword in e["category"].lower()
    ]


def get_error_by_name(error_name):
    conn = get_connection()
    if conn is None:
        for e in _load_seed_errors():
            if e["error_name"] == error_name:
                return e
        return None

    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM errors WHERE error_name = %s", (error_name,))
        error_row = cursor.fetchone()
        if error_row is None:
            return None
        cursor.execute("SELECT * FROM fixes WHERE error_id = %s", (error_row["error_id"],))
        fix_row = cursor.fetchone()
        if fix_row:
            error_row["fix_text"] = fix_row["fix_text"]
            error_row["prevention_tip"] = fix_row["prevention_tip"]
        return error_row
    except MySQLError:
        return None
    finally:
        cursor.close()
        conn.close()


def _load_seed_errors():
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# =========================================================
# USER HISTORY / BUG DNA / PROGRESS
# =========================================================

def log_history(user_id, error_name, code_snippet):
    from modules import sync_manager
    if is_offline():
        return sync_manager.log_history_csv(user_id, error_name, code_snippet)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        error_id = None
        category = "Unknown"
        if error_name:
            cursor.execute("SELECT error_id, category FROM errors WHERE error_name = %s", (error_name,))
            row = cursor.fetchone()
            if row:
                error_id = row["error_id"]
                category = row["category"]

        cursor.execute(
            "INSERT INTO user_history (user_id, error_id, code_snippet) VALUES (%s, %s, %s)",
            (user_id, error_id, code_snippet)
        )

        cursor.execute(
            """INSERT INTO performance_data (user_id, error_category, frequency)
               VALUES (%s, %s, 1)
               ON DUPLICATE KEY UPDATE frequency = frequency + 1, last_updated = NOW()""",
            (user_id, category)
        )

        conn.commit()
        return cursor.lastrowid
    except MySQLError:
        return sync_manager.log_history_csv(user_id, error_name, code_snippet)
    finally:
        cursor.close()
        conn.close()


def mark_resolved(history_id, debug_time_seconds):
    from modules import sync_manager
    if is_offline():
        return sync_manager.mark_resolved_csv(history_id, debug_time_seconds)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            "UPDATE user_history SET resolved = TRUE, resolved_at = NOW() WHERE history_id = %s",
            (history_id,)
        )

        cursor.execute(
            """SELECT e.category, u.user_id FROM user_history u
               LEFT JOIN errors e ON u.error_id = e.error_id
               WHERE u.history_id = %s""",
            (history_id,)
        )
        row = cursor.fetchone()
        if row and row["category"]:
            cursor.execute(
                """UPDATE performance_data
                   SET avg_debug_time_seconds = (avg_debug_time_seconds + %s) / 2
                   WHERE user_id = %s AND error_category = %s""",
                (debug_time_seconds, row["user_id"], row["category"])
            )
        conn.commit()
        return True
    except MySQLError:
        return sync_manager.mark_resolved_csv(history_id, debug_time_seconds)
    finally:
        cursor.close()
        conn.close()


def get_user_history(user_id, limit=50):
    from modules import sync_manager
    if is_offline():
        return sync_manager.get_user_history_csv(user_id, limit)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            """SELECT h.history_id, h.code_snippet, h.occurred_at, h.resolved,
                      e.error_name, e.category
               FROM user_history h
               LEFT JOIN errors e ON h.error_id = e.error_id
               WHERE h.user_id = %s
               ORDER BY h.occurred_at DESC LIMIT %s""",
            (user_id, limit)
        )
        return cursor.fetchall()
    except MySQLError:
        return sync_manager.get_user_history_csv(user_id, limit)
    finally:
        cursor.close()
        conn.close()


def get_bug_dna(user_id):
    from modules import sync_manager
    if is_offline():
        return sync_manager.get_bug_dna_csv(user_id)

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            """SELECT error_category, frequency, avg_debug_time_seconds
               FROM performance_data WHERE user_id = %s
               ORDER BY frequency DESC""",
            (user_id,)
        )
        return cursor.fetchall()
    except MySQLError:
        return sync_manager.get_bug_dna_csv(user_id)
    finally:
        cursor.close()
        conn.close()


# =========================================================
# TEACHER-STUDENT CONNECTIONS
# =========================================================

def generate_class_code(teacher_id):
    import random
    return f"T{teacher_id}-{random.randint(1000, 9999)}"


def connect_student_to_class(student_id, teacher_id, class_code):
    if is_offline():
        return False, "Class connections require an online database connection."

    conn = get_connection()
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute(
            "INSERT INTO class_connections (teacher_id, student_id, class_code) VALUES (%s, %s, %s)",
            (teacher_id, student_id, class_code)
        )
        conn.commit()
        return True, "Successfully connected to your teacher's class."
    except MySQLError as e:
        if e.errno == 1062:
            return False, "You are already connected to this teacher."
        return False, "Could not connect. Please check the class code and try again."
    finally:
        cursor.close()
        conn.close()


def get_connected_students(teacher_id):
    if is_offline():
        return []

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(
            """SELECT u.user_id, u.username
               FROM class_connections c
               JOIN users u ON c.student_id = u.user_id
               WHERE c.teacher_id = %s""",
            (teacher_id,)
        )
        return cursor.fetchall()
    except MySQLError:
        return []
    finally:
        cursor.close()
        conn.close()


def find_user_id_by_username(username):
    if is_offline():
        return None
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        return row["user_id"] if row else None
    except MySQLError:
        return None
    finally:
        cursor.close()
        conn.close()