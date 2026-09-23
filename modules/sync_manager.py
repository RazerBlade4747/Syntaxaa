"""
sync_manager.py
----------------
Manages local CSV storage and synchronization with the MySQL database.
Ensures that all operations can
run locally in CSV mode when offline
"""

import csv
import os
import hashlib
from datetime import datetime
import database

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_data")

# CSV File Paths
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
HISTORY_CSV = os.path.join(DATA_DIR, "user_history.csv")
PERFORMANCE_CSV = os.path.join(DATA_DIR, "performance_data.csv")
CLASSES_CSV = os.path.join(DATA_DIR, "class_connections.csv")


def ensure_local_storage():
    """Ensures that the local_data directory and required CSV files exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    headers = {
        USERS_CSV: ["user_id", "username", "password", "user_type", "created_at", "synced"],
        HISTORY_CSV: ["history_id", "user_id", "error_id", "code_snippet", "occurred_at", "resolved", "resolved_at", "synced"],
        PERFORMANCE_CSV: ["record_id", "user_id", "error_category", "frequency", "avg_debug_time_seconds", "last_updated", "synced"],
        CLASSES_CSV: ["connection_id", "teacher_id", "student_id", "class_code", "connected_at", "synced"]
    }

    for path, header in headers.items():
        if not os.path.exists(path):
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)


def get_next_id(filepath):
    """Calculates the next incremental ID for a given CSV file."""
    if not os.path.exists(filepath):
        return 1
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        if len(reader) <= 1:
            return 1
        try:
            return int(reader[-1][0]) + 1
        except ValueError:
            return 1


# =========================================================
# LOCAL CSV AUTHENTICATION
# =========================================================

def create_user_csv(username, password, user_type):
    """Creates a new user record in local CSV."""
    ensure_local_storage()
    username = username.strip()
    if not username or not password.strip():
        return False, "Please enter both a username and a password."

    # Check for duplicate username
    with open(USERS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"].lower() == username.lower():
                return False, "That username is already taken locally."

    user_id = get_next_id(USERS_CSV)
    pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(USERS_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, pwd_hash, user_type, created_at, "0"])

    return True, "Account created locally in offline mode."


def verify_login_csv(username, password):
    """Verifies login against local CSV storage."""
    ensure_local_storage()
    username = username.strip()
    pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    with open(USERS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and row["password"] == pwd_hash:
                return {
                    "user_id": int(row["user_id"]),
                    "username": row["username"],
                    "user_type": row["user_type"]
                }
    return None


# =========================================================
# LOCAL CSV HISTORY & BUG DNA
# =========================================================

def log_history_csv(user_id, error_name, code_snippet):
    """Logs history and updates performance tracking in CSV."""
    ensure_local_storage()
    history_id = get_next_id(HISTORY_CSV)
    occurred_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine error_id & category from seed/local lookup
    error_info = database.get_error_by_name(error_name) if error_name else None
    error_id = error_info.get("error_id", "") if error_info else ""
    category = error_info.get("category", "Unknown") if error_info else "Unknown"

    # Write to user_history.csv
    with open(HISTORY_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([history_id, user_id, error_id, code_snippet, occurred_at, "False", "", "0"])

    # Update performance_data.csv
    _update_performance_csv(user_id, category, increment_freq=True)
    return history_id


def mark_resolved_csv(history_id, debug_time_seconds):
    """Marks a history record resolved in CSV and updates avg debug time."""
    ensure_local_storage()
    rows = []
    updated = False
    target_user_id = None
    target_error_id = None

    with open(HISTORY_CSV, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        if not reader:
            return False
        header = reader[0]
        for row in reader[1:]:
            if len(row) >= 8 and str(row[0]) == str(history_id):
                row[5] = "True"  # resolved
                row[6] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # resolved_at
                row[7] = "0"  # mark dirty for re-sync
                target_user_id = row[1]
                target_error_id = row[2]
                updated = True
            rows.append(row)

    if updated:
        with open(HISTORY_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

        # Update average debug time in performance_data.csv
        category = "Unknown"
        if target_error_id:
            for err in database.get_all_errors():
                if str(err.get("error_id", "")) == str(target_error_id):
                    category = err.get("category", "Unknown")
                    break
        if target_user_id:
            _update_performance_csv(int(target_user_id), category, debug_time=debug_time_seconds)

    return updated


def _update_performance_csv(user_id, category, increment_freq=False, debug_time=None):
    """Internal helper to insert or update local performance CSV rows."""
    ensure_local_storage()
    rows = []
    found = False

    with open(PERFORMANCE_CSV, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        if not reader:
            return
        header = reader[0]
        for row in reader[1:]:
            if len(row) >= 7 and str(row[1]) == str(user_id) and row[2] == category:
                found = True
                freq = int(row[3]) + (1 if increment_freq else 0)
                avg_time = int(row[4])
                if debug_time is not None:
                    avg_time = int((avg_time + debug_time) / 2) if avg_time > 0 else int(debug_time)
                last_upd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rows.append([row[0], user_id, category, freq, avg_time, last_upd, "0"])
            else:
                rows.append(row)

    if not found:
        rec_id = get_next_id(PERFORMANCE_CSV)
        freq = 1 if increment_freq else 0
        avg_time = int(debug_time) if debug_time else 0
        last_upd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows.append([rec_id, user_id, category, freq, avg_time, last_upd, "0"])

    with open(PERFORMANCE_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def get_user_history_csv(user_id, limit=50):
    """Retrieves user history from local CSV."""
    ensure_local_storage()
    all_errors = {str(e.get("error_id", "")): e for e in database.get_all_errors()}
    results = []

    with open(HISTORY_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row["user_id"]) == str(user_id):
                err_info = all_errors.get(str(row["error_id"]), {})
                results.append({
                    "history_id": int(row["history_id"]),
                    "code_snippet": row["code_snippet"],
                    "occurred_at": row["occurred_at"],
                    "resolved": row["resolved"] == "True",
                    "error_name": err_info.get("error_name", "Unknown Error"),
                    "category": err_info.get("category", "Unknown")
                })

    results.sort(key=lambda x: x["occurred_at"], reverse=True)
    return results[:limit]


def get_bug_dna_csv(user_id):
    """Retrieves performance stats from local CSV."""
    ensure_local_storage()
    results = []

    with open(PERFORMANCE_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row["user_id"]) == str(user_id):
                results.append({
                    "error_category": row["error_category"],
                    "frequency": int(row["frequency"]),
                    "avg_debug_time_seconds": int(row["avg_debug_time_seconds"])
                })

    results.sort(key=lambda x: x["frequency"], reverse=True)
    return results


# =========================================================
# AUTO-SYNC ENGINE (CSV -> MySQL)
# =========================================================

def sync_local_data_to_mysql():
    """
    Scans all local CSV files for records where synced == '0'
    and pushes them into MySQL, updating synced flag to '1'.
    """
    ensure_local_storage()
    conn = database.get_connection()
    if conn is None:
        return False, "Database unreachable. Cannot sync at this time."

    try:
        cursor = conn.cursor()

        # 1. Sync Users
        _sync_table(
            file_path=USERS_CSV,
            cursor=cursor,
            insert_query="""
                INSERT INTO users (user_id, username, password, user_type, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE username=VALUES(username), password=VALUES(password)
            """,
            extractor=lambda r: (r[0], r[1], r[2], r[3], r[4])
        )

        # 2. Sync History
        _sync_table(
            file_path=HISTORY_CSV,
            cursor=cursor,
            insert_query="""
                INSERT INTO user_history (history_id, user_id, error_id, code_snippet, occurred_at, resolved, resolved_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE resolved=VALUES(resolved), resolved_at=VALUES(resolved_at)
            """,
            extractor=lambda r: (
                r[0], r[1], int(r[2]) if r[2] else None, r[3], r[4], r[5] == "True", r[6] if r[6] else None
            )
        )

        # 3. Sync Performance Data
        _sync_table(
            file_path=PERFORMANCE_CSV,
            cursor=cursor,
            insert_query="""
                INSERT INTO performance_data (user_id, error_category, frequency, avg_debug_time_seconds, last_updated)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    frequency=VALUES(frequency), 
                    avg_debug_time_seconds=VALUES(avg_debug_time_seconds),
                    last_updated=VALUES(last_updated)
            """,
            extractor=lambda r: (r[1], r[2], int(r[3]), int(r[4]), r[5])
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Successfully synced local CSV data to MySQL database!"
    except Exception as e:
        return False, f"Sync error encountered: {str(e)}"


def _sync_table(file_path, cursor, insert_query, extractor):
    """Generic table sync helper."""
    if not os.path.exists(file_path):
        return

    rows = []
    updated_rows = []

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        if len(reader) <= 1:
            return
        header = reader[0]
        rows = reader[1:]

    for row in rows:
        # Check if unsynced (last column)
        if len(row) > 0 and row[-1] == "0":
            try:
                params = extractor(row)
                cursor.execute(insert_query, params)
                row[-1] = "1"  # Mark as synced
            except Exception as e:
                print(f"[Sync Error] {file_path}: {e}")
        updated_rows.append(row)

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)