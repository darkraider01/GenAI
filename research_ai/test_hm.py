import sys
import os
sys.path.append(os.path.abspath('backend'))
from backend.utils.history_manager import HistoryManager

def test_history():
    print("Testing HistoryManager...")
    try:
        hm = HistoryManager()
        print(f"DB Path: {hm.db_path}")
        print("Adding entry...")
        hm.add_explorer_entry("test query", 10)
        print("Entry added successfully.")
        history = hm.get_history("explorer_history")
        print(f"History count: {len(history)}")
        for entry in history:
            print(f" - {entry['query']} at {entry['timestamp']}")
    except Exception as e:
        import traceback
        print(f"Caught Exception: {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_history()
