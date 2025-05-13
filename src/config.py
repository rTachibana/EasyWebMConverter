import os
import json
import sys

# Get script root directory
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default configuration
DEFAULT_CONFIG = {
    "output_directory": os.path.join(script_dir, "output"),
    "output_filename_template": "output-{timestamp}",
    "show_output_dir_prompt": True,
    "ask_for_next_file": True,
    "default_format": "1",  # 1 = MP4, 2 = WebM
    "default_size": "1",    # 1 = Original
    "default_bitrate": "1"  # 1 = Auto (Quality-based)
}

# Configuration file path
CONFIG_FILE = os.path.join(script_dir, "config.json")

def load_config():
    """Load configuration from file or return default if file doesn't exist"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with default config to ensure all keys are present
                result = DEFAULT_CONFIG.copy()
                result.update(config)
                return result
        else:
            # Create default config file if it doesn't exist
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False

def get_output_dir():
    """Get output directory from config and ensure it exists"""
    config = load_config()
    output_dir = config.get("output_directory", DEFAULT_CONFIG["output_directory"])
    
    # Use absolute path
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(script_dir, output_dir)
    
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir

def get_output_filename(ext):
    """Generate output filename with timestamp based on template in config"""
    import datetime
    
    config = load_config()
    template = config.get("output_filename_template", DEFAULT_CONFIG["output_filename_template"])
    
    # Replace timestamp placeholder with actual timestamp (including seconds)
    timestamp = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    filename = template.replace("{timestamp}", timestamp) + f".{ext}"
    
    return os.path.join(get_output_dir(), filename)

def should_show_output_dir_prompt():
    """Check if output directory prompt should be shown"""
    config = load_config()
    return config.get("show_output_dir_prompt", DEFAULT_CONFIG["show_output_dir_prompt"])

def should_ask_for_next_file():
    """Check if user should be prompted for next file"""
    config = load_config()
    return config.get("ask_for_next_file", DEFAULT_CONFIG["ask_for_next_file"])

def get_default_format():
    """Get default format from config"""
    config = load_config()
    return config.get("default_format", DEFAULT_CONFIG["default_format"])

def get_default_size():
    """Get default size from config"""
    config = load_config()
    return config.get("default_size", DEFAULT_CONFIG["default_size"])

def get_default_bitrate():
    """Get default bitrate from config"""
    config = load_config()
    return config.get("default_bitrate", DEFAULT_CONFIG["default_bitrate"])

def create_default_config_if_not_exists():
    """Create default config file if it doesn't exist"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        print(f"Created default configuration file at: {CONFIG_FILE}")
        print("You can edit this file to customize application settings.")

if __name__ == "__main__":
    # If run directly, create default config file
    create_default_config_if_not_exists()
    print(f"Configuration file path: {CONFIG_FILE}")
    print("Current settings:")
    for key, value in load_config().items():
        print(f"  {key}: {value}") 