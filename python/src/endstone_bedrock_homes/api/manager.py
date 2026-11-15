import sqlite3
import os
from typing import Optional
from endstone.plugin import Plugin
import threading


class HomesManager:
    def __init__(self, plugin: Plugin) -> None:
        self.plugin = plugin
        self.logger = plugin.logger
        self.data_folder = plugin.data_folder
        self.db_path = os.path.join(self.data_folder, "database.db")
        self.connect: Optional[sqlite3.Connection] = None
        self.lock = threading.RLock()

    def is_database_connected(self) -> bool:
        return self.connect is not None

    def create_home(self, name: str, home: str, position: str, dimension: str) -> bool:
        if home is None or name is None:
            return False
        with self.lock:
            try:
                with self.connect:
                    self.connect.execute(
                        "INSERT OR IGNORE INTO homes (name, home, position, dimension) VALUES (?, ?, ?, ?)",
                        (name, home, position, dimension)
                    )
            except Exception as e:
                self.plugin.logger.error(f"{e}")
                return False
        return True

    def delete_home(self, name: str, home: str) -> bool:
        if not self.is_database_connected():
            return False
        if home is None or name is None:
            return False
        with self.lock:
            try:
                with self.connect:
                    self.connect.execute(
                        "DELETE FROM homes WHERE name = ? AND home = ?",
                        (name, home)
                    )
            except Exception as e:
                self.plugin.logger.error(f"{e}")
                return False
        return True

    def select_home(self, name: str, home: str) -> list[str | None]:
        if not self.is_database_connected():
            return []
        if home is None or name is None:
            return []
        with self.lock:
            try:
                with self.connect:
                    row = self.connect.execute(
                        "SELECT name, home, position, dimension FROM homes WHERE name = ? AND home = ?",
                        (name, home)
                    ).fetchone()
                    return row if row is not None and len(row) == 4 else []
            except Exception as e:
                self.plugin.logger.error(f"{e}")
                return []
        return []

    def database_open(self) -> None:
        try:
            if not os.path.exists(self.data_folder):
                os.makedirs(self.data_folder, exist_ok=True)
            self.connect = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connect.execute("PRAGMA journal_mode=WAL")
            self.connect.execute("PRAGMA synchronous=NORMAL")
            with self.connect:
                self.connect.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS homes (
                        name TEXT,
                        home TEXT, 
                        position TEXT,
                        dimension TEXT
                    )
                    """
                )
            return True
        except Exception as e:
            self.plugin.logger.error(f"{e}")
            if self.is_database_connected():
                try:
                    self.connect.close()
                except Exception:
                    pass
            self.connect = None
            return False

    def database_close(self) -> bool:
        if not self.is_database_connected():
            return False
        with self.lock:
            try:
                self.connect.close()
                return True
            except Exception as e:
                self.plugin.logger.error(f"{e}")
                return False
            finally:
                self.connect = None