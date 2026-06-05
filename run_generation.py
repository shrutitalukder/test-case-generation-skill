from pathlib import Path

from speckit_generator import generate_from_config, load_yaml_or_json


if __name__ == "__main__":
    config_path = Path("config.yaml")
    config = load_yaml_or_json(config_path)
    output_path = generate_from_config(config)
    print(f"Generated artifacts in {output_path}")
