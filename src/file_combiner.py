import os
import json
import re
import logging

class FileCombinerBackend:
    def __init__(self):
        self.config_file = "config.json"
        self.default_supported_extensions = [
            '.md', '.py', '.js', '.java', '.kt', '.cs', '.cpp', '.h',
            '.php', '.rb', '.go', '.swift', '.html', '.htm', '.css', '.dart',
            '.jsx', '.tsx', '.ts', '.sh', '.sql', '.r', '.m', '.c', '.hpp',
            '.json', '.xml', '.yaml', '.toml', '.ini', '.gradle', '.groovy',
            '.lua', '.scala', '.pl', '.vb', '.vbs', '.asm', '.pas', '.f', '.for',
            '.rs', '.erl', '.hs', '.clj', '.lisp', '.scm', '.ml', '.fs',
            '.cob', '.coffee', '.tcl', '.ex', '.exs', '.vue', '.svelte',
            '.bat', '.ps1', '.powershell', '.gitignore', '.dockerfile', '.txt'
        ]
        self.supported_extensions = []
        self.file_paths = []
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.supported_extensions = config.get('supported_extensions', self.default_supported_extensions)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("Config file not found or invalid. Using default extensions.")
            self.supported_extensions = self.default_supported_extensions

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'supported_extensions': self.supported_extensions}, f, indent=4)
                logging.info("Configuration saved.")
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def is_directory(self, path):
        return os.path.isdir(path)

    def is_file(self, path):
        return os.path.isfile(path)

    def get_files_from_folder(self, folder_path):
        file_paths = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths

    def is_supported_file(self, file_path):
        file_name = os.path.basename(file_path)
        match = re.search(r'\.[a-zA-Z0-9_]+$', file_name)
        if match:
            ext = match.group(0).lower()
            return ext in self.supported_extensions
        return False

    def add_file_path(self, file_path):
        self.file_paths.append(file_path)

    def clear_file_paths(self):
        self.file_paths.clear()

    def combine_files(self):
        combined_content = ""
        for file_path in self.file_paths:
            try:
                file_name = os.path.basename(file_path)
                combined_content += f"# {file_name}\n"
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_content += f.read() + "\n\n"
            except UnicodeDecodeError as e:
                logging.error(f"UnicodeDecodeError reading {file_path}: {e}")
                combined_content += f"Error reading file {file_name}: Could not decode.\n\n"
            except Exception as e:
                logging.error(f"Error reading file - {file_path}: {e}")
                continue
        return combined_content

    def add_extension(self, ext):
        if ext not in self.supported_extensions:
            self.supported_extensions.append(ext)
            return True
        return False

    def remove_extensions(self, extensions):
        for ext in extensions:
            if ext in self.supported_extensions:
                self.supported_extensions.remove(ext)