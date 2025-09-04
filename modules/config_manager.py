import json
import os
import base64

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _get_default_config(self):
        return {
            "provider": "local",
            "openai_api_key": "",
            "perplexity_api_key": ""
        }

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    # Make sure all keys are present
                    data = json.load(f)
                    defaults = self._get_default_config()
                    defaults.update(data)
                    return defaults
            except (json.JSONDecodeError, IOError):
                pass
        
        default_config = self._get_default_config()
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
        except IOError:
            pass
        return default_config

    def save_config(self, provider, openai_key, perplexity_key):
        self.config = {
            "provider": provider,
            "openai_api_key": base64.b64encode(openai_key.encode('utf-8')).decode('utf-8'),
            "perplexity_api_key": base64.b64encode(perplexity_key.encode('utf-8')).decode('utf-8')
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get_provider(self):
        return self.config.get("provider", "local")

    def get_api_key(self, provider_name):
        """Gets the key for a specific provider ('openai' or 'perplexity')."""
        key_name = f"{provider_name}_api_key"
        obfuscated_key = self.config.get(key_name, "")
        if not obfuscated_key: return ""
        try:
            return base64.b64decode(obfuscated_key).decode('utf-8')
        except:
            return ""