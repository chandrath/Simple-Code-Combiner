import json
import logging
import tkinter as tk
from tkinter import Toplevel, StringVar, Label, Entry, Button, OptionMenu, messagebox, Frame, Checkbutton
import ttkbootstrap as ttk
import os

class AIProvider:
    def __init__(self, provider_name, settings):
        self.provider_name = provider_name
        self.settings = settings

    def summarize(self, text):
        api_key = self.settings.get("api_key")
        if not api_key:
            raise ValueError(f"API Key is not configured for the selected AI provider: {self.provider_name}")

        input_token_limit = self.settings.get("input_token_limit")
        if self.settings.get("input_token_limit_enabled", False) and input_token_limit and len(text.split()) > int(input_token_limit):
            raise ValueError(f"Text exceeds the input token limit of {input_token_limit}.")
    
        if self.provider_name == "OpenAI":
            return self._summarize_with_openai(text)
        elif self.provider_name == "Groq":
            return self._summarize_with_openai(text, api_base="https://api.groq.com/openai/v1")
        elif self.provider_name == "Mistral AI":
            return self._summarize_with_openai(text)
        elif self.provider_name == "Anthropic":
            return self._summarize_with_anthropic(text)
        elif self.provider_name == "Local LLM":
            return self._summarize_with_local_llm(text)
        elif self.provider_name == "Google":
            return self._summarize_with_gemini(text)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider_name}")

    def _summarize_with_openai(self, text, api_base=None):
        import openai
        openai.api_key = self.settings.get("api_key")
        openai.api_base = api_base if api_base else self.settings.get("api_base", "https://api.openai.com/v1")
        client = openai.OpenAI(api_key=openai.api_key, base_url=openai.api_base)
        try:
            response = client.chat.completions.create(
                model=self.settings.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": "Summarize the following text:"},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

    def _summarize_with_anthropic(self, text):
        import anthropic
        api_key = self.settings.get("api_key")
        client = anthropic.Anthropic(api_key=api_key)
        try:
            response = client.messages.create(
                model=self.settings.get("model", "claude-3-opus-20240229"),
                 max_tokens= int(self.settings.get("anthropic_max_tokens", 1024)) if self.settings.get("anthropic_max_tokens_enabled", False) else None,
                messages=[
                    {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")

    def _summarize_with_local_llm(self, text):
        # Placeholder for local LLM implementation (e.g., using llama.cpp, KoboldCpp, LM Studio APIs)
        raise NotImplementedError("Local LLM integration is not yet implemented.")

    def _summarize_with_gemini(self, text):
        import google.generativeai as genai
        genai.configure(api_key=self.settings.get("api_key"))
        model_name = self.settings.get("model", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([text])
        return response.text

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
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Preferences file not found or invalid. Creating a new one: {e}")
        return {}  # Return empty dict to make sure preference exists and no errors

def save_preferences(config, pref_file="preferences.json"):
    try:
        with open(pref_file, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save preferences: {e}")

def load_models(models_file=None):
    if models_file is None:
       # Construct the correct path
       models_file = os.path.join(os.path.dirname(__file__), "models.json")
    try:
        with open(models_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading models file: {e}")
        return {}

def show_configuration_dialog(app):
    config_file = "llm_config.json"
    pref_file = "preferences.json"
    all_configs = load_llm_config(config_file)
    all_prefs = load_preferences(pref_file)
    models_data = load_models()

    dialog = Toplevel(app.root)
    dialog.title("LLM or AI Configuration")

    available_providers = ["OpenAI", "Groq", "Mistral AI", "Anthropic", "Local LLM", "Google", "Manual"]
    provider_var = StringVar(dialog)
    provider_var.set(all_prefs.get("current_provider", "OpenAI"))

    config_frames = {}
    config_widgets = {}
    current_model_label = Label(dialog, text="", foreground="red")
    
    def save_configuration():
        selected_provider = provider_var.get()
        all_configs["current_provider"] = selected_provider
        all_prefs["current_provider"] = selected_provider
        
        for provider in available_providers:
             if provider in config_widgets:
                config_value = get_current_config(provider)
                all_configs[provider] = config_value
                all_prefs[provider] = config_value
        save_llm_config(all_configs, config_file)
        save_preferences(all_prefs, pref_file)
        messagebox.showinfo("Success", "LLM configuration saved successfully!")
        dialog.destroy()

    def get_current_config(provider):
        config = {}
        if provider in config_widgets:
            for key, widget in config_widgets[provider].items():
                if isinstance(widget, Entry):
                    config[key] = widget.get()
                elif isinstance(widget, ttk.Combobox):
                     config[key] = widget.get()
                elif isinstance(widget, tk.BooleanVar):
                    config[key] = widget.get()
        return config

    def update_fields(provider):
        for p, frame in config_frames.items():
            frame.grid_remove()
        if provider in config_frames:
            config_frames[provider].grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        elif provider == "Manual":
            for frame in config_frames.values():
                frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        show_hide_fields(provider)
        update_model_display()
        
    def load_and_set_model(provider, model_dropdown, models_list):
            initial_model_value = all_prefs.get(provider, {}).get("model", "")
            if initial_model_value in models_list:
                model_dropdown.set(initial_model_value)
            elif models_list:
                model_dropdown.set(models_list[0])
        
    def update_model_display():
        provider = provider_var.get()
        selected_model = None
        if provider in config_widgets and "model" in config_widgets[provider]:
            selected_model = config_widgets[provider]["model"].get()
        if selected_model:
            current_model_label.config(text=f"Current Model: {selected_model}")
        else:
            current_model_label.config(text="No model selected")
    
    def show_hide_fields(provider):
        if provider in config_widgets and provider in models_data:
            for key, widget in config_widgets[provider].items():
                field_setting_key = f"{key.replace('_field','')}_field"
                if key in ["api_key", "api_base", "api_organisation", "input_token_limit", "anthropic_max_tokens" ]:
                    if field_setting_key in models_data[provider]:
                       widget.config(state=tk.NORMAL if models_data[provider].get(field_setting_key, False) else tk.DISABLED)
                    else:
                        widget.config(state=tk.DISABLED)

                if key == "input_token_limit":
                   if  "input_token_limit_enabled" in config_widgets[provider]:
                      input_token_limit_enabled = config_widgets[provider]["input_token_limit_enabled"]
                      widget.config(state=tk.NORMAL if input_token_limit_enabled.get() else tk.DISABLED)
                if key == "anthropic_max_tokens":
                   if  "anthropic_max_tokens_enabled" in config_widgets[provider]:
                     anthropic_max_tokens_enabled = config_widgets[provider]["anthropic_max_tokens_enabled"]
                     widget.config(state=tk.NORMAL if anthropic_max_tokens_enabled.get() else tk.DISABLED)

    # Provider Selection
    Label(dialog, text="Select Provider").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    OptionMenu(dialog, provider_var, *available_providers, command=update_fields).grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    
    # Configuration Frames
    for provider_name in available_providers:
        frame = Frame(dialog)
        config_frames[provider_name] = frame
        current_config = all_configs.get(provider_name, {})
        current_pref = all_prefs.get(provider_name, {})
        widget_holder = {}

        if provider_name in models_data:
            # Model Dropdown Frame
            model_frame = Frame(frame)
            Label(model_frame, text="Model").pack(side="left", padx=5)
            
            # Sort models alphabetically
            sorted_models = sorted(models_data[provider_name]['models'])
            model_dropdown = ttk.Combobox(model_frame, values=sorted_models, name="model")
            model_dropdown.pack(side="left", padx=5, fill="x", expand=True)
            model_dropdown.bind("<<ComboboxSelected>>", lambda event, provider=provider_name: update_model_display())

            # Load and set model
            load_and_set_model(provider_name, model_dropdown, sorted_models)
            
            model_frame.pack(fill="x", padx=10, pady=5)
            widget_holder["model"] = model_dropdown
        
        # Common fields for all models
        api_key_frame = Frame(frame)
        Label(api_key_frame, text="API Key").pack(side="left", padx=5)
        api_key_entry = Entry(api_key_frame, name="api_key")
        api_key_entry.insert(0, current_config.get("api_key", ""))
        api_key_entry.pack(side="left", fill="x", expand=True, padx=5)
        api_key_frame.pack(fill="x", padx=10, pady=5)
        widget_holder["api_key"] = api_key_entry

        # API Base URL Frame
        api_base_frame = Frame(frame)
        Label(api_base_frame, text="API Base URL").pack(side="left", padx=5)
        api_base_value = current_config.get("api_base", "")
        api_base_entry = Entry(api_base_frame, name="api_base")
        if provider_name == "Groq" and not api_base_value:
            api_base_value = "https://api.groq.com/openai/v1"
        api_base_entry.insert(0, api_base_value)
        api_base_entry.pack(side="left", fill="x", expand=True, padx=5)
        api_base_frame.pack(fill="x", padx=10, pady=5)
        widget_holder["api_base"] = api_base_entry

        # API Organisation Entry Frame
        api_organisation_frame = Frame(frame)
        Label(api_organisation_frame, text="API Organisation").pack(side="left", padx=5)
        api_organisation_entry = Entry(api_organisation_frame, name="api_organisation")
        api_organisation_entry.insert(0, current_config.get("api_organisation", ""))
        api_organisation_entry.pack(side="left", fill="x", expand=True, padx=5)
        api_organisation_frame.pack(fill="x", padx=10, pady=5)
        widget_holder["api_organisation"] = api_organisation_entry
        
        # Input Token limit frame
        input_token_limit_frame = Frame(frame)
        input_token_limit_enable_var = tk.BooleanVar(value=current_config.get("input_token_limit_enabled", False))
        Checkbutton(input_token_limit_frame, text="Enable Input Token Limit", variable=input_token_limit_enable_var, command=lambda: show_hide_fields(provider_var.get())).pack(side="left", padx=5)
        Label(input_token_limit_frame, text="Input Token Limit").pack(side="left", padx=5)
        input_token_limit_entry = Entry(input_token_limit_frame, name="input_token_limit")
        input_token_limit_entry.insert(0, current_config.get("input_token_limit", "1000"))
        input_token_limit_entry.pack(side="left", fill="x", expand=True, padx=5)
        input_token_limit_frame.pack(fill="x", padx=10, pady=5)
        widget_holder["input_token_limit"] = input_token_limit_entry
        widget_holder["input_token_limit_enabled"] = input_token_limit_enable_var

        # Anothorpic Max token frame
        anthropic_max_token_frame = Frame(frame)
        anthropic_max_tokens_enable_var = tk.BooleanVar(value=current_config.get("anthropic_max_tokens_enabled", False))
        Checkbutton(anthropic_max_token_frame, text="Enable Max Output Token Limit", variable=anthropic_max_tokens_enable_var, command=lambda: show_hide_fields(provider_var.get())).pack(side="left", padx=5)
        Label(anthropic_max_token_frame, text="Max Output Tokens").pack(side="left", padx=5)
        max_tokens_entry = Entry(anthropic_max_token_frame, name="anthropic_max_tokens")
        max_tokens_entry.insert(0, current_config.get("anthropic_max_tokens", "1024"))
        max_tokens_entry.pack(side="left", fill="x", expand=True, padx=5)
        anthropic_max_token_frame.pack(fill="x", padx=10, pady=5)
        widget_holder["anthropic_max_tokens"] = max_tokens_entry
        widget_holder["anthropic_max_tokens_enabled"] = anthropic_max_tokens_enable_var
        config_widgets[provider_name] = widget_holder
    
    current_model_label.pack(side="bottom", fill="x", padx=10, pady=5)
    update_fields(provider_var.get())
    update_model_display()
    show_hide_fields(provider_var.get())
    Button(dialog, text="Save", command=save_configuration).grid(row=2, column=0, columnspan=2, pady=10)

def summarize_text(text, config_file="llm_config.json", pref_file="preferences.json", app=None):
    all_prefs = load_preferences(pref_file)
    provider_name = all_prefs.get("current_provider", "OpenAI")
    provider_config = all_prefs.get(provider_name, {})
    provider = AIProvider(provider_name, provider_config)
    summary_text = provider.summarize(text)

    if app:
      # Create and display a popup window
      popup = Toplevel(app.root)
      popup.title("AI Summary")
      # Get the main window's position
      app_x = app.root.winfo_x()
      app_y = app.root.winfo_y()
      app_width = app.root.winfo_width()
      app_height = app.root.winfo_height()
      
      # Calculate the popup's position to be centered on main window
      popup_width = 500 # set your desired width
      popup_height = 300 # set your desired height
      x = app_x + (app_width - popup_width) // 2
      y = app_y + (app_height - popup_height) // 2
    
      popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

      text_widget = tk.Text(popup, wrap=tk.WORD, height=10, width=50)
      text_widget.insert(tk.END, summary_text)
      text_widget.pack(padx=10, pady=10)
      text_widget.config(state=tk.DISABLED)
      current_model_label = Label(popup, text=f"Current AI Model: {provider_config.get('model', 'No Model Selected')}", foreground="red")
      current_model_label.pack(side="bottom", fill="x", padx=10, pady=5)


    return summary_text