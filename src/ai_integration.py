# ai_integration.py
import json
import logging
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