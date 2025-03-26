import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_modified(self, event):
        if event.src_path.endswith('.json'):
            self.callback()

class ChangeDetector:
    def __init__(self, config_path: str):
        self.observer = Observer()
        self.event_handler = ConfigChangeHandler(self.handle_change)
        self.config_path = config_path
        self.last_hash = self._calculate_hash()
        self.context_sources = {
            "regulatory_feeds": ["OFAC_API_ENDPOINT", "FCA_REGULATIONS"],
            "system_apis": ["PAYMENT_API_SWAGGER", "RISK_MODEL_VERSION"]
        }

    def check_context_changes(self):
        changes = {}
        for category, endpoints in self.context_sources.items():
            for endpoint in endpoints:
                current_hash = self.get_resource_hash(endpoint)
                if current_hash != self.known_hashes.get(endpoint):
                    changes[endpoint] = {"old": self.known_hashes.get(endpoint), "new": current_hash}
        return changes
        
    def start(self):
        self.observer.schedule(
            self.event_handler,
            path=Path(self.config_path).parent,
            recursive=False
        )
        self.observer.start()
        
    def _calculate_hash(self) -> str:
        with open(self.config_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
        
    def handle_change(self):
        current_hash = self._calculate_hash()
        if current_hash != self.last_hash:
            self.last_hash = current_hash
            print("Configuration change detected - updating test cases...")