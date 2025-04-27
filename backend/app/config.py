import yaml
import logging
from pathlib import Path

class Config:
    def __init__(self):
        config_path = Path(__file__).parent / "metrics_config.yaml"
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        self.metrics = data.get("metrics", [])
        # Log loaded metrics configuration
        logging.info(f"Loaded metrics config: {self.metrics}")

    def get_metrics(self):
        return self.metrics

config = Config()