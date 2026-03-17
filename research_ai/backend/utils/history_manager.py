import sqlite3
import json
import os
import time
from datetime import datetime

class HistoryManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to db/history.db
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_dir = os.path.join(base_dir, 'db')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'history.db')
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Swarm History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS swarm_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT,
                    result TEXT,
                    timestamp INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            # Explorer/Search History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS explorer_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    results_count INTEGER,
                    timestamp INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            # Paper Reader History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reader_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    summary TEXT,
                    timestamp INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            # Graph History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS graph_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT,
                    ideas TEXT,
                    image_path TEXT,
                    timestamp INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            conn.commit()

    def add_swarm_entry(self, topic, result):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO swarm_history (topic, result, timestamp) VALUES (?, ?, ?)', 
                           (topic, result, int(time.time())))
            conn.commit()

    def add_explorer_entry(self, query, results_count):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO explorer_history (query, results_count, timestamp) VALUES (?, ?, ?)', 
                           (query, results_count, int(time.time())))
            conn.commit()

    def add_reader_entry(self, filename, summary):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO reader_history (filename, summary, timestamp) VALUES (?, ?, ?)', 
                           (filename, summary, int(time.time())))
            conn.commit()

    def add_graph_entry(self, topic, ideas, image_path=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO graph_history (topic, ideas, image_path, timestamp) VALUES (?, ?, ?, ?)', 
                           (topic, json.dumps(ideas), image_path, int(time.time())))
            conn.commit()

    def get_history(self, table_name, limit=6):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

# Singleton instance
history_manager = HistoryManager()
