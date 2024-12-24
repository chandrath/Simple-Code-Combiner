import json
import logging
import tkinter as tk
from tkinter import Toplevel, StringVar, Label, Entry, Button, OptionMenu, messagebox


class AIProvider:
    def __init__(self, provider_name, api_key=None, model="gpt-3.5-turbo", token_limit=1000):
        self.provider_name = provider_name
        self.api_key = api_key
        self.model = model
        self.token_limit = token_limit

    def summarize(self, text):
        if not self.api_key:
            raise ValueError("API Key is not configured for the selected AI provider.")

        if len(text.split()) > self.token_limit:
            raise ValueError(f"Text exceeds the token limit of {self.token_limit}.")

        if self.provider_name == "OpenAI Compatible":
            return self._summarize_with_openai(text)
        elif self.provider_name == "Google Gemini":
            return self._summarize_with_gemini(text)
        else:
            raise ValueError("Unsupported AI provider.")

    def _summarize_with_openai(self, text):
        import openai
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Summarize the following text:"},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content']

    def _summarize_with_gemini(self, text):
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.models.get_model(self.model)
        if not model:
            raise ValueError("Model not found. Please check your model configuration.")
        response = model.generate_text(prompt=text)
        return response.result


def load_llm_config(config_file="llm_config.json"):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_llm_config(config, config_file="llm_config.json"):
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save LLM configuration: {e}")


def show_configuration_dialog(app):
    config_file = "llm_config.json"
    config = load_llm_config(config_file)

    dialog = Toplevel(app.root)
    dialog.title("LLM or AI Configuration")

    provider_var = StringVar(value=config.get("provider_name", "OpenAI Compatible"))
    api_key_var = StringVar(value=config.get("api_key", ""))
    model_var = StringVar(value=config.get("model", "gpt-3.5-turbo"))
    token_limit_var = StringVar(value=str(config.get("token_limit", 1000)))

    def save_configuration():
        try:
            config = {
                "provider_name": provider_var.get(),
                "api_key": api_key_var.get(),
                "model": model_var.get(),
                "token_limit": int(token_limit_var.get())
            }
            save_llm_config(config, config_file)
            messagebox.showinfo("Success", "LLM configuration saved successfully!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    Label(dialog, text="Select Provider").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    provider_menu = OptionMenu(dialog, provider_var, "OpenAI Compatible", "Google Gemini", "Local LLM")
    provider_menu.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

    Label(dialog, text="API Key").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    Entry(dialog, textvariable=api_key_var).grid(row=1, column=1, sticky="ew", padx=10, pady=5)

    Label(dialog, text="Model").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    Entry(dialog, textvariable=model_var).grid(row=2, column=1, sticky="ew", padx=10, pady=5)

    Label(dialog, text="Token Limit").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    Entry(dialog, textvariable=token_limit_var).grid(row=3, column=1, sticky="ew", padx=10, pady=5)

    Button(dialog, text="Save", command=save_configuration).grid(row=4, column=0, columnspan=2, pady=10)


def summarize_text(text, config_file="llm_config.json"):
    config = load_llm_config(config_file)

    if not config:
        raise ValueError("AI configuration is missing. Please configure it in Preferences.")

    provider_name = config.get("provider_name")
    api_key = config.get("api_key")
    model = config.get("model")
    token_limit = config.get("token_limit", 1000)

    provider = AIProvider(provider_name, api_key, model, token_limit)
    return provider.summarize(text)
