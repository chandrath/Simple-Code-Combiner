# ui_menu.py
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import webbrowser
import logging
import ttkbootstrap as ttk
import re
from ai_ui import AIConfigurationDialog

class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag, action in self.links.items():
            if tag in self.text.tag_names(tk.CURRENT):
                webbrowser.open(action)
                return

class FileCombinerMenu:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.menu_bar = tk.Menu(parent)
        parent.config(menu=self.menu_bar)

        self.always_on_top_var = tk.BooleanVar()

        self.create_file_menu()
        self.create_preferences_menu()
        self.create_help_menu()

    def create_file_menu(self):
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Files", command=self.app.open_files)
        self.file_menu.add_command(label="Open Folder", command=self.app.open_folder)
        self.file_menu.add_command(label="Save Combined File", command=self.app.save_combined_file, state=tk.DISABLED)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.quit)

    def create_preferences_menu(self):
        self.preferences_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Preferences", menu=self.preferences_menu)
        self.preferences_menu.add_checkbutton(label="Always on Top", variable=self.always_on_top_var, command=self.toggle_always_on_top)
        self.preferences_menu.add_command(label="Manage Extensions", command=self.manage_extensions)
        self.preferences_menu.add_command(label="AI Configuration", command=self.open_ai_configuration)

    def create_help_menu(self):
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About Us", command=self.show_about)

    def enable_save(self):
        self.file_menu.entryconfig("Save Combined File", state=tk.NORMAL)

    def disable_save(self):
        self.file_menu.entryconfig("Save Combined File", state=tk.DISABLED)

    def show_about(self):
        about_window = Toplevel(self.parent)
        about_window.title("About Us")

        text = tk.Text(about_window, wrap=tk.WORD, height=7, width=50)
        text.pack(padx=10, pady=10)
        text.insert(tk.END, "Code Combiner v0.8.1\nA simple tool to combine code files.\n\nDeveloped By: Shree\n")
        text.config(state=tk.DISABLED)
        text.config(state=tk.NORMAL)
        link = HyperlinkManager(text)
        text.insert(tk.END, "https://github.com/chandrath/Simple-Code-Combiner", link.add("https://github.com/chandrath/Simple-Code-Combiner"))
        text.config(state=tk.DISABLED)

    def toggle_always_on_top(self):
        self.parent.attributes('-topmost', self.always_on_top_var.get())
        logging.info(f"Always on top set to {self.always_on_top_var.get()}.")

    def manage_extensions(self):
        extensions_window = tk.Toplevel(self.parent)
        extensions_window.title("Manage Extensions")
        extensions_window.geometry("400x300")

        scrollbar = ttk.Scrollbar(extensions_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(extensions_window, yscrollcommand=scrollbar.set, height=10)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)
        for ext in self.app.backend.supported_extensions:
            listbox.insert(tk.END, ext)

        entry_frame = ttk.Frame(extensions_window)
        entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        extension_entry = ttk.Entry(entry_frame)
        extension_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def remove_selected_extension():
            selected_indices = listbox.curselection()
            if selected_indices:
                selected_extensions = [listbox.get(i) for i in selected_indices]
                self.app.backend.remove_extensions(selected_extensions)
                for i in reversed(selected_indices):
                    listbox.delete(i)
                self.app.save_config()

        remove_button = ttk.Button(entry_frame, text="Remove", command=remove_selected_extension)
        remove_button.pack(side=tk.RIGHT)

        def add_new_extension():
            new_ext = extension_entry.get().strip().lower()
            if new_ext:
                if not new_ext.startswith("."):
                    messagebox.showwarning("Invalid Extension", "Extension must start with a dot")
                    return
                if not re.match(r"^\.[a-zA-Z0-9_]+$", new_ext):
                    messagebox.showwarning("Invalid Extension", "Invalid characters in extension")
                    return
                if self.app.backend.add_extension(new_ext):
                    listbox.insert(tk.END, new_ext)
                    extension_entry.delete(0, tk.END)
                    self.app.save_config()
                    logging.info(f"Added new extension: {new_ext}")
                else:
                    messagebox.showwarning("Duplicate Extension", f"{new_ext} is already supported!")

        add_button = ttk.Button(entry_frame, text="Add", command=add_new_extension)
        add_button.pack(side=tk.RIGHT)

    def open_ai_configuration(self):
        dialog = AIConfigurationDialog(self.parent)