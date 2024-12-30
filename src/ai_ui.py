# ai_ui.py
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
        self.dialog = ttk.Toplevel(self.parent)
        self.dialog.title("LLM or AI Configuration")
        self.dialog.geometry("500x450")

        self.config_file = "llm_config.json"
        self.pref_file = "preferences.json"
        self.all_configs = load_llm_config(self.config_file)
        self.all_prefs = load_preferences(self.pref_file)
        self.models_data = load_models()

        self.available_providers = sorted(list(self.models_data.keys()))
        self.provider_var = tk.StringVar(self.dialog)
        self.current_provider = self.all_prefs.get("current_provider", "Google") # Set default provider to Google
        if not self.current_provider or self.current_provider not in self.available_providers:
            self.current_provider = self.available_providers[0] if self.available_providers else ""
        self.provider_var.set(self.current_provider)

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


        # Save Button
        save_button = ttk.Button(self.dialog, text="Save", command=self.save_configuration)
        save_button.grid(row=3, column=0, pady=5)
        # Default settings Button
        self.default_button = ttk.Button(self.dialog, text="Default Settings", command=self.reset_to_defaults, style="Link.TButton")
        self.default_button.grid(row=4, column=0, pady=5)
        self.default_button.config(padding=0)


    def populate_config_frame(self, provider_name, frame):
        config_widgets = {}
        provider_config = self.all_prefs.get(provider_name, {})
        models_for_provider = self.models_data.get(provider_name, {})

       # Model Selection
        if provider_name in self.models_data:
            model_frame = ttk.Frame(frame)
            ttk.Label(model_frame, text="Model").pack(side="left", padx=5)

            sorted_models = sorted(models_for_provider.get('models', []))
            model_var = tk.StringVar(self.dialog)
            saved_model = provider_config.get("model")
            initial_model = saved_model if saved_model in sorted_models else (sorted_models[0] if sorted_models else "")
            model_var.set(initial_model)

            model_dropdown = ttk.Combobox(model_frame, textvariable=model_var, values=sorted_models, state="readonly", name="model")
            model_dropdown.pack(side="left", fill="x", expand=True, padx=5)
            model_dropdown.bind("<<ComboboxSelected>>", self.update_model_display)
            model_frame.pack(fill="x", padx=10, pady=5)
            config_widgets["model"] = model_dropdown
            config_widgets["model_var"] = model_var

         # Custom Model Input
        custom_model_frame = ttk.Frame(frame)
        config_widgets["custom_model_enabled_var"] = tk.BooleanVar(value=provider_config.get("custom_model_enabled", False))
        custom_checkbox = ttk.Checkbutton(custom_model_frame, text="Custom Model", variable=config_widgets["custom_model_enabled_var"], command=lambda: self.toggle_custom_model(provider_name))
        custom_checkbox.pack(side="left", padx=5)
        custom_model_entry = ttk.Entry(custom_model_frame, name="custom_model")
        custom_model_entry.insert(0, provider_config.get("custom_model", ""))
        custom_model_entry.pack(side="left", fill="x", expand=True, padx=5)
        custom_model_frame.pack(fill="x", padx=10, pady=5)
        config_widgets["custom_model"] = custom_model_entry

        # Input Token Limit
        input_limit_frame = ttk.Frame(frame)
        config_widgets["input_token_limit_enabled_var"] = tk.BooleanVar(value=provider_config.get("input_token_limit_enabled", True)) # Set default to True
        input_checkbox = ttk.Checkbutton(input_limit_frame, text="Enable Input Token Limit", variable=config_widgets["input_token_limit_enabled_var"], command=lambda: self.toggle_limit_entry(provider_name, "input"))
        input_checkbox.pack(side="left", padx=5)
        ttk.Label(input_limit_frame, text="Limit:").pack(side="left", padx=5)
        input_limit_entry = ttk.Entry(input_limit_frame, name="input_token_limit", validate="key")
        input_limit_entry['validatecommand'] = (input_limit_entry.register(self.validate_integer_input), '%S')
        input_limit_entry.insert(0, provider_config.get("input_token_limit", "1024")) # Set default limit to 1024
        input_limit_entry.pack(side="left", fill="x", expand=True, padx=5)
        input_limit_frame.pack(fill="x", padx=10, pady=5)
        config_widgets["input_token_limit"] = input_limit_entry

        # Output Token Limit
        output_limit_frame = ttk.Frame(frame)
        config_widgets["output_token_limit_enabled_var"] = tk.BooleanVar(value=provider_config.get("output_token_limit_enabled", False))
        output_checkbox = ttk.Checkbutton(output_limit_frame, text="Enable Output Token Limit", variable=config_widgets["output_token_limit_enabled_var"], command=lambda: self.toggle_limit_entry(provider_name, "output"))
        output_checkbox.pack(side="left", padx=5)
        ttk.Label(output_limit_frame, text="Limit:").pack(side="left", padx=5)
        output_limit_entry = ttk.Entry(output_limit_frame, name="output_token_limit", validate="key")
        output_limit_entry['validatecommand'] = (output_limit_entry.register(self.validate_integer_input), '%S')
        output_limit_entry.insert(0, provider_config.get("output_token_limit", ""))
        output_limit_entry.pack(side="left", fill="x", expand=True, padx=5)
        output_limit_frame.pack(fill="x", padx=10, pady=5)
        config_widgets["output_token_limit"] = output_limit_entry

        # Additional fields based on models.json
        for key_suffix, needs_field in models_for_provider.items():
            if needs_field is True and (key_suffix.endswith("_field") or key_suffix.endswith("_tokens_field")):
                field_name = key_suffix.replace("_field", "").replace("_tokens", "_token")
                label_text = field_name.replace("_", " ").title()

                entry_frame = ttk.Frame(frame)
                ttk.Label(entry_frame, text=label_text).pack(side="left", padx=5)

                default_value = models_for_provider.get(f"default_{field_name}")
                entry_value = provider_config.get(field_name, default_value if default_value is not None else "")
                entry = ttk.Entry(entry_frame, name=field_name)
                if field_name in ["api_base", "api_organisation"]:
                     entry.insert(0, entry_value)
                     entry.bind("<FocusIn>", lambda event, entry=entry: self.handle_focus_in(event, entry, "leave blank if not applicable"))
                     entry.bind("<FocusOut>", lambda event, entry=entry: self.handle_focus_out(event, entry, "leave blank if not applicable"))
                     self.handle_focus_out(None, entry, "leave blank if not applicable")
                else:
                  entry.insert(0, entry_value)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                entry_frame.pack(fill="x", padx=10, pady=5)
                config_widgets[field_name] = entry


        self.config_widgets[provider_name] = config_widgets

    def handle_focus_in(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def handle_focus_out(self, event, entry, placeholder):
        if not entry.get():
             entry.insert(0, placeholder)
             entry.config(foreground="grey")


    def load_saved_values(self):
        self.on_provider_change()
        for provider_name in self.available_providers:
            self.toggle_custom_model(provider_name)
            self.toggle_limit_entry(provider_name, "input")
            self.toggle_limit_entry(provider_name, "output")
        self.update_model_display()

    def on_provider_change(self, *args):
        selected_provider = self.provider_var.get()
        for provider, frame in self.config_frames.items():
            if provider == selected_provider:
                frame.grid()
            else:
                frame.grid_remove()
        self.update_model_display()

    def toggle_custom_model(self, provider_name):
        if provider_name in self.config_widgets:
            custom_enabled = self.config_widgets[provider_name]["custom_model_enabled_var"].get()
            self.config_widgets[provider_name]["custom_model"].config(state=tk.NORMAL if custom_enabled else tk.DISABLED)
            self.config_widgets[provider_name]["model"].config(state=tk.DISABLED if custom_enabled else "readonly")
            if not custom_enabled:
                self.config_widgets[provider_name]["custom_model"].delete(0, tk.END) # Clear custom input
            self.update_model_display()

    def toggle_limit_entry(self, provider_name, limit_type):
        if provider_name in self.config_widgets:
            if limit_type == "input":
                enabled = self.config_widgets[provider_name]["input_token_limit_enabled_var"].get()
                self.config_widgets[provider_name]["input_token_limit"].config(state=tk.NORMAL if enabled else tk.DISABLED)
            elif limit_type == "output":
                enabled = self.config_widgets[provider_name]["output_token_limit_enabled_var"].get()
                self.config_widgets[provider_name]["output_token_limit"].config(state=tk.NORMAL if enabled else tk.DISABLED)


    def validate_integer_input(self, input_text):
        return input_text.isdigit() or input_text == ""


    def update_model_display(self, event=None):
         provider = self.provider_var.get()
         if provider in self.config_widgets:
            if self.config_widgets[provider]["custom_model_enabled_var"].get():
                 selected_model = self.config_widgets[provider]["custom_model"].get()
            elif "model_var" in self.config_widgets[provider]:
                selected_model = self.config_widgets[provider]["model_var"].get()
            else:
                 selected_model = "No model selected"

            self.current_model_label.config(text=f"Current Model: {selected_model}")

         else:
            self.current_model_label.config(text="No model selected")


    def save_configuration(self):
        selected_provider = self.provider_var.get()
        self.all_prefs["current_provider"] = selected_provider

        if selected_provider in self.config_widgets:
            config = {}
            # Correctly save the model using the model_var
            if  self.config_widgets[selected_provider]["custom_model_enabled_var"].get():
                custom_model = self.config_widgets[selected_provider]["custom_model"].get().strip()
                if not custom_model:
                    messagebox.showwarning("Missing Input", "Please input the custom model name")
                    return
                config["custom_model_enabled"] = True
                config["custom_model"] = custom_model
                config["model"] = custom_model
            elif "model_var" in self.config_widgets[selected_provider]:
                config["custom_model_enabled"] = False
                config["custom_model"] = ""
                config["model"] = self.config_widgets[selected_provider]["model_var"].get()


            config["input_token_limit_enabled"] = self.config_widgets[selected_provider].get("input_token_limit_enabled_var").get()
            config["input_token_limit"] = self.config_widgets[selected_provider].get("input_token_limit").get()
            config["output_token_limit_enabled"] = self.config_widgets[selected_provider].get("output_token_limit_enabled_var").get()
            config["output_token_limit"] = self.config_widgets[selected_provider].get("output_token_limit").get()

            for key, widget in self.config_widgets[selected_provider].items():
                if key not in ["model", "input_token_limit", "output_token_limit", "model_var", "custom_model", "custom_model_enabled_var"] and isinstance(widget, ttk.Entry):
                    config[key] = widget.get()

            self.all_prefs[selected_provider] = config

        save_preferences(self.all_prefs, self.pref_file)
        messagebox.showinfo("Success", "Configuration saved successfully!")
        self.dialog.destroy()

    def reset_to_defaults(self):
        if messagebox.askokcancel("Confirm Reset", "Are you sure you want to reset all AI settings to their defaults?"):
            # Reset Current Provider to Default
            self.all_prefs["current_provider"] = "OpenAI"
            self.provider_var.set("OpenAI")

            for provider_name in self.available_providers:
                if provider_name in self.config_widgets:
                    for key, widget in self.config_widgets[provider_name].items():
                        if isinstance(widget, ttk.Entry):
                            widget.delete(0, tk.END)
                            models_for_provider = self.models_data.get(provider_name, {})
                            default_value = models_for_provider.get(f"default_{key}")
                            if default_value:
                                widget.insert(0, default_value)
                    #Reset to deafult
                    self.config_widgets[provider_name]["input_token_limit_enabled_var"].set(True)
                    self.config_widgets[provider_name]["output_token_limit_enabled_var"].set(False)
                    self.config_widgets[provider_name]["custom_model_enabled_var"].set(False)
                    self.config_widgets[provider_name]["custom_model"].delete(0, tk.END)
                    self.config_widgets[provider_name]["input_token_limit"].insert(0, "1024") # Reset input token limit to 1024
                    if "model_var" in self.config_widgets[provider_name]:
                        sorted_models = sorted(self.models_data[provider_name]['models'])
                        self.config_widgets[provider_name]["model_var"].set(sorted_models[0] if sorted_models else "")
                # Clear the provider settings in all_prefs
            self.all_prefs = {"current_provider": "OpenAI"}  # Reset to only current_provider being OpenAI
            save_preferences(self.all_prefs, self.pref_file)
            self.load_saved_values()
            messagebox.showinfo("Success", "AI settings reset to defaults.")