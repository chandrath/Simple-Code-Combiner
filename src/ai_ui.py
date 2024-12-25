# ai_ui.py
import tkinter as tk
from tkinter import Toplevel, StringVar, Label, Entry, Button, OptionMenu, messagebox, Frame, Checkbutton
import ttkbootstrap as ttk
import json
import logging
import os

def load_llm_config(config_file="llm_config.json"):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading LLM config: {e}")
        return {}

def save_llm_config(config, config_file="llm_config.json"):
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save LLM configuration: {e}")

def load_preferences(pref_file="preferences.json"):
    try:
        with open(pref_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_preferences(config, pref_file="preferences.json"):
    try:
        with open(pref_file, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save preferences: {e}")

def load_models(models_file=None):
    if models_file is None:
        models_file = os.path.join(os.path.dirname(__file__), "models.json")
    try:
        with open(models_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading models file: {e}")
        return {}

class AIConfigurationDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = Toplevel(self.parent)
        self.dialog.title("LLM or AI Configuration")
        self.dialog.geometry("500x400")

        # Load configurations
        self.config_file = "llm_config.json"
        self.pref_file = "preferences.json"
        self.all_configs = load_llm_config(self.config_file)
        self.all_prefs = load_preferences(self.pref_file)
        self.models_data = load_models()

        # Setup provider selection
        self.available_providers = sorted(list(self.models_data.keys()))
        self.provider_var = StringVar(self.dialog)
        
        # Set initial provider from saved preferences or default to first available
        self.current_provider = self.all_prefs.get("current_provider")
        if not self.current_provider or self.current_provider not in self.available_providers:
            self.current_provider = self.available_providers[0] if self.available_providers else ""
        self.provider_var.set(self.current_provider)

        # Initialize UI components
        self.config_frames = {}
        self.config_widgets = {}
        self.current_model_label = ttk.Label(self.dialog, text="", foreground="red")
        
        self.create_widgets()
        self.load_saved_values()

    def create_widgets(self):
        # Provider Selection
        provider_frame = ttk.Frame(self.dialog)
        provider_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(provider_frame, text="Select Provider").pack(side="left")
        self.provider_dropdown = ttk.OptionMenu(
            provider_frame, 
            self.provider_var,
            self.current_provider,
            *self.available_providers,
            command=self.on_provider_change
        )
        self.provider_dropdown.pack(side="left", fill="x", expand=True, padx=5)

        # Configuration Frames
        for provider_name in self.available_providers:
            frame = ttk.Frame(self.dialog)
            self.config_frames[provider_name] = frame
            frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
            self.populate_config_frame(provider_name, frame)
            frame.grid_remove()

        self.current_model_label.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        ttk.Button(self.dialog, text="Save", command=self.save_configuration).grid(row=3, column=0, pady=10)

    def populate_config_frame(self, provider_name, frame):
        config_widgets = {}
        provider_config = self.all_prefs.get(provider_name, {})

        if provider_name in self.models_data:
            # Model Selection
            model_frame = ttk.Frame(frame)
            ttk.Label(model_frame, text="Model").pack(side="left", padx=5)
            
            sorted_models = sorted(self.models_data[provider_name]['models'])
            model_var = StringVar(self.dialog)
            
            # Set saved model or default
            saved_model = provider_config.get("model")
            initial_model = saved_model if saved_model in sorted_models else (sorted_models[0] if sorted_models else "")
            model_var.set(initial_model)
            
            model_dropdown = ttk.Combobox(model_frame, textvariable=model_var, values=sorted_models, state="readonly", name="model")
            model_dropdown.pack(side="left", fill="x", expand=True, padx=5)
            model_dropdown.bind("<<ComboboxSelected>>", self.update_model_display)
            model_frame.pack(fill="x", padx=10, pady=5)
            config_widgets["model"] = model_dropdown

        # Additional fields based on models.json
        for key_suffix, needs_field in self.models_data[provider_name].items():
            if needs_field is True and (key_suffix.endswith("_field") or key_suffix.endswith("_tokens_field")):
                field_name = key_suffix.replace("_field", "")
                label_text = field_name.replace("_", " ").title()
                
                entry_frame = ttk.Frame(frame)
                ttk.Label(entry_frame, text=label_text).pack(side="left", padx=5)
                
                # Get saved value
                entry_value = provider_config.get(field_name, "")
                entry = ttk.Entry(entry_frame, name=field_name)
                entry.insert(0, entry_value)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                entry_frame.pack(fill="x", padx=10, pady=5)
                config_widgets[field_name] = entry

        self.config_widgets[provider_name] = config_widgets

    def load_saved_values(self):
        self.on_provider_change()
        self.update_model_display()

    def on_provider_change(self, *args):
        selected_provider = self.provider_var.get()
        
        # Update visibility of configuration frames
        for provider, frame in self.config_frames.items():
            if provider == selected_provider:
                frame.grid()
            else:
                frame.grid_remove()
                
        self.update_model_display()

    def update_model_display(self, event=None):
        provider = self.provider_var.get()
        if provider in self.config_widgets and "model" in self.config_widgets[provider]:
            selected_model = self.config_widgets[provider]["model"].get()
            if selected_model:
                self.current_model_label.config(text=f"Current Model: {selected_model}")
            else:
                self.current_model_label.config(text="No model selected")

    def save_configuration(self):
        selected_provider = self.provider_var.get()
        self.all_configs["current_provider"] = selected_provider
        self.all_prefs["current_provider"] = selected_provider

        if selected_provider in self.config_widgets:
            config = {}
            for key, widget in self.config_widgets[selected_provider].items():
                if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                    config[key] = widget.get()
            
            self.all_configs[selected_provider] = config
            self.all_prefs[selected_provider] = config

        save_llm_config(self.all_configs, self.config_file)
        save_preferences(self.all_prefs, self.pref_file)
        messagebox.showinfo("Success", "Configuration saved successfully!")
        self.dialog.destroy()