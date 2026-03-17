import time

class PipelineLogger:
    def __init__(self):
        self.logs = []
        
    def start_step(self, step_name: str, description: str):
        log_entry = {
            "step": step_name,
            "description": description,
            "status": "In Progress",
            "timestamp": time.time(),
            "time_taken": 0
        }
        self.logs.append(log_entry)
        _idx = len(self.logs) - 1
        print(f"[{step_name}] {description}")
        return _idx
        
    def complete_step(self, log_index: int):
        if 0 <= log_index < len(self.logs):
            entry = self.logs[log_index]
            entry["status"] = "Completed"
            entry["time_taken"] = time.time() - entry["timestamp"]
            print(f"[{entry['step']}] Completed in {entry['time_taken']:.2f}s")
            
    def fail_step(self, log_index: int, error_msg: str):
        if 0 <= log_index < len(self.logs):
            entry = self.logs[log_index]
            entry["status"] = "Failed"
            entry["error"] = error_msg
            entry["time_taken"] = time.time() - entry["timestamp"]
            print(f"[{entry['step']}] Failed: {error_msg}")
            
    def get_logs(self):
        return self.logs

pipeline_logger = PipelineLogger()
