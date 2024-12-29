# ai_integration.py
# ai_integration.py
# ai_integration.py
import json
import logging
import os
import tkinter as tk
from tkinter import messagebox

class AIProvider:
    def __init__(self, provider_name, settings):
        self.provider_name = provider_name
        self.settings = settings
        self.models_data = self._load_models()

    def _load_models(self, models_file=None):
      if models_file is None:
          models_file = os.path.join(os.path.dirname(__file__), "models.json")
      try:
          with open(models_file, 'r') as f:
              return json.load(f)
      except (FileNotFoundError, json.JSONDecodeError) as e:
          logging.error(f"Error loading models file: {e}")
          return {}

    def summarize(self, text):
        api_key = self.settings.get("api_key")
        if not api_key:
            raise ValueError(f"API Key is not configured for the selected AI provider: {self.provider_name}")

        # Input token limit check
        if self.settings.get("input_token_limit_enabled", False):
            input_token_limit = self.settings.get("input_token_limit")
            if input_token_limit and len(text.split()) > int(input_token_limit):
                raise ValueError(f"Text exceeds the input token limit of {input_token_limit}.")

        # Output token limit
        output_token_limit = None
        if self.settings.get("output_token_limit_enabled", False):
            output_token_limit = self.settings.get("output_token_limit")
            if output_token_limit:
                output_token_limit = int(output_token_limit)

        api_base = self.settings.get("api_base")
        if not api_base:
            provider_data = self.models_data.get(self.provider_name, {})
            api_base = provider_data.get("default_api_base")

        model = self.settings.get("model")
        if not model and self.provider_name in self.models_data and self.models_data[self.provider_name].get('models'):
            model = self.models_data[self.provider_name]['models'][0]
            logging.warning(f"No model selected for {self.provider_name}. Using default model: {model}")
        elif not model:
            raise ValueError(f"No model configured for the selected AI provider: {self.provider_name}")

        if self.provider_name == "OpenAI":
            return self._summarize_with_openai(text, model=model, api_base=api_base, max_tokens=output_token_limit)
        elif self.provider_name == "Groq":
            return self._summarize_with_openai(text, model=model, api_base=api_base, max_tokens=output_token_limit)
        elif self.provider_name == "Mistral AI":
            return self._summarize_with_openai(text, model=model, api_base=api_base, max_tokens=output_token_limit)
        elif self.provider_name == "Anthropic":
            anthropic_max_tokens = self.settings.get("anthropic_max_tokens")
            max_tokens = int(anthropic_max_tokens) if anthropic_max_tokens else output_token_limit
            return self._summarize_with_anthropic(text, model=model, max_tokens=max_tokens)
        elif self.provider_name == "Local LLM":
            return self._summarize_with_local_llm(text)
        elif self.provider_name == "Google":
            return self._summarize_with_gemini(text, model=model)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider_name}")

    def _summarize_with_openai(self, text, model, api_base=None, max_tokens=None):
        import openai
        openai.api_key = self.settings.get("api_key")
        openai.api_base = api_base if api_base else "https://api.openai.com/v1"
        client = openai.OpenAI(api_key=openai.api_key, base_url=openai.api_base)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Summarize the following text:"},
                    {"role": "user", "content": text}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")

    def _summarize_with_anthropic(self, text, model, max_tokens=None):
        import anthropic
        api_key = self.settings.get("api_key")
        client = anthropic.Anthropic(api_key=api_key)
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
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

    def _summarize_with_gemini(self, text, model):
        import google.generativeai as genai
        genai.configure(api_key=self.settings.get("api_key"))
        model_name = model
        model = genai.GenerativeModel(model_name)
        try:
            response = model.generate_content(f"Summarize the following text:\n\n{text}")
            return response.text
        except Exception as e:
            raise Exception(f"Google Gemini API error: {e}")

def load_llm_config(config_file="llm_config.json"):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading LLM config: {e}")
        return {}

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

def summarize_text(text, config_file="llm_config.json", pref_file="preferences.json", app=None):
    all_prefs = load_preferences(pref_file)
    provider_name = all_prefs.get("current_provider", "OpenAI")
    provider_config = all_prefs.get(provider_name, {})
    try:
        provider = AIProvider(provider_name, provider_config)
        summary_text = provider.summarize(text)

        if app:
          # Create and display a popup window
          popup = tk.Toplevel(app.root)
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
          current_model_label = tk.Label(popup, text=f"Current AI Model: {provider_config.get('model', 'No Model Selected')}", foreground="red")
          current_model_label.pack(side="bottom", fill="x", padx=10, pady=5)

        return summary_text
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        if app:
            messagebox.showerror("Summarization Error", str(e))
        return None