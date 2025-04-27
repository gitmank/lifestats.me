import logging
import sqlite3
from datetime import datetime
from pathlib import Path

class SQLiteHandler(logging.Handler):
    """
    Logging handler that writes log records to a SQLite database.
    """
    def __init__(self, db_path: Path):
        super().__init__()
        # Ensure database directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # Connect to SQLite database (thread-safe)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._create_table()

    def _create_table(self):
        """Create logs table if it does not exist."""
        self.conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                logger TEXT,
                message TEXT,
                pathname TEXT,
                funcName TEXT
            )
            '''
        )
        self.conn.commit()

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            timestamp = datetime.utcnow().isoformat()
            level = record.levelname
            logger_name = record.name
            pathname = record.pathname
            func_name = record.funcName
            self.conn.execute(
                'INSERT INTO logs (timestamp, level, logger, message, pathname, funcName) VALUES (?, ?, ?, ?, ?, ?)',
                (timestamp, level, logger_name, msg, pathname, func_name)
            )
            self.conn.commit()
        except Exception:
            self.handleError(record)

# Configure root logger to use SQLiteHandler
_log_db = Path(__file__).parents[1] / "logs.db"
handler = SQLiteHandler(_log_db)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)