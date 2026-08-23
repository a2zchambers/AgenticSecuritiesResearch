import os
import sqlite3
from datetime import datetime

class DatabaseManager:
    """Manages SQLite connectivity, table structures, and run logging transactions."""
    
    def __init__(self, db_filename: str = "trading_results.db"):
        # FIXED: Dynamically calculates the parent path to map the DB file 
        # inside the absolute project root, preventing sub-folder duplication.
        storage_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(storage_dir)
        self.db_path = os.path.join(project_root, db_filename)
        
        self._init_database()

    def _init_database(self):
        """Creates the local database file and target schema if they do not exist."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rating TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    sector TEXT DEFAULT 'UNKNOWN',
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    model_used TEXT DEFAULT 'UNKNOWN'
                )
            """)
            
            # Incremental updates check schema parameters securely
            cursor.execute("PRAGMA table_info(trade_ratings)")
            columns = [col[1] for col in cursor.fetchall()]
            if "sector" not in columns:
                cursor.execute("ALTER TABLE trade_ratings ADD COLUMN sector TEXT DEFAULT 'UNKNOWN'")
                
            conn.commit()
        except Exception as e:
            # Safely log errors directly to terminal fallback loops
            print(f"[Database Architecture Fault] Initialization failed: {str(e)}")
        finally:
            if conn:
                conn.close()

    def save_run_result(self, rating: str, ticker: str, sector: str, reason: str, model_used: str):
        """Appends structural output records directly inside the database table."""
        conn = None
        try:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trade_ratings (rating, ticker, sector, date, time, reason, model_used) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (rating, ticker, sector, current_date, current_time, reason, model_used)
            )
            conn.commit()
            print(f"[Database Registry Commit] Archived run ledger trace safely for ticker: {ticker.upper()}")
        except Exception as e:
            print(f"[Database Architecture Fault] Failed to write run results: {str(e)}")
        finally:
            if conn:
                conn.close()
