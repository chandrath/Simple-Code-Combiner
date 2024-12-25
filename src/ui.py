# ui.py
import tkinter as tk
from tkinter import filedialog, messagebox, Menu, Toplevel
from tkinterdnd2 import DND_FILES
import ttkbootstrap as ttk
import webbrowser
from file_combiner import FileCombinerBackend
import logging

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

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Combiner")
        self.root.geometry("300x450")

        # Initialize the backend logic
        self.backend = FileCombinerBackend()

        # Set up logging (ensure it's initialized once)
        logging.basicConfig(filename="file_combiner.log", level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("Application started")

        # Create a menu bar
        self.menu_bar = Menu(root)
        self.root.config(menu=self.menu_bar)

        # Create "File" Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Files", command=self.open_files)
        self.file_menu.add_command(label="Open Folder", command=self.open_folder)
        self.file_menu.add_command(label="Save Combined File", command=self.save_combined_file, state=tk.DISABLED)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Create "Preferences" Menu
        self.preferences_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Preferences", menu=self.preferences_menu)
        self.always_on_top_var = tk.BooleanVar()
        self.preferences_menu.add_checkbutton(label="Always on Top", variable=self.always_on_top_var, command=self.toggle_always_on_top)
        self.preferences_menu.add_command(label="Manage Extensions", command=self.manage_extensions)

        # Create "Help" Menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About Us", command=self.show_about)

        # Create a frame for drag and drop
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a label for instructions
        self.label = ttk.Label(self.frame, text="Drag and drop code files here", font=("Arial", 14))
        self.label.pack(pady=10)

        # Add button to open files/folders
        self.open_button = ttk.Button(self.frame, text="Or click here to open files/folder", command=self.open_files_or_folder, style="Link.TButton")
        self.open_button.pack()

        # Create a text area to show dropped files
        self.text_area = tk.Text(self.frame, height=10, width=50, wrap=tk.WORD)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # Create a button to combine files
        self.combine_button = ttk.Button(self.frame, text="Combine Files", command=self.combine_files)
        self.combine_button.pack(pady=5)

        # Create a button to copy combined text to clipboard
        self.copy_button = ttk.Button(self.frame, text="Copy to Clipboard", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(pady=5)

        # Create a clear button
        self.clear_button = ttk.Button(self.frame, text="Clear", command=self.clear_text, style='Danger.TButton')
        self.clear_button.pack(pady=5)

        # Initialize the list to hold file paths (managed by backend)

        # Set up drag and drop
        self.setup_drag_and_drop()
        self.load_config() # Load config after initializing backend

    def load_config(self):
        self.backend.load_config()

    def save_config(self):
        self.backend.save_config()

    def setup_drag_and_drop(self):
        # Register the main window for drag and drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)  # Handles file paths with spaces correctly
        for path in paths:
            if self.backend.is_directory(path):
                self.import_folder(path)
            elif self.backend.is_file(path):
                self.import_file(path)

    def import_folder(self, folder_path):
        for file_path in self.backend.get_files_from_folder(folder_path):
            self.import_file(file_path)

    def import_file(self, file):
        if self.backend.is_supported_file(file):
            self.backend.add_file_path(file)
            self.text_area.insert(tk.END, f"{file}\n")
        else:
            self.display_error(f"Unsupported extension - {file}. If it's a code file, use 'Preferences -> Manage Extensions' to add it.")

    def open_files(self):
        files = filedialog.askopenfilenames(filetypes=[("All files", "*.*")])
        for file in files:
            self.import_file(file)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.import_folder(folder)

    def open_files_or_folder(self):
        if messagebox.askyesno("Open Option", "Would you like to open a folder?\n(Click 'No' to open files instead)"):
            self.open_folder()
        else:
            self.open_files()

    def display_error(self, message):
        self.text_area.insert(tk.END, f"Error: {message}\n", "error")
        self.text_area.tag_config("error", foreground="red")
        logging.error(message)

    def combine_files(self):
        if not self.backend.file_paths:
            messagebox.showwarning("No Files", "Please add files first.")
            return

        combined_content = self.backend.combine_files()

        # Display combined content in the text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, combined_content)
        self.text_area.tag_remove("error", "1.0", tk.END)

        # Enable the copy button and save option after combining files
        self.copy_button.config(state=tk.NORMAL)
        self.file_menu.entryconfig("Save Combined File", state=tk.NORMAL)

    def copy_to_clipboard(self):
        combined_content = self.text_area.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(combined_content.strip())
        messagebox.showinfo("Copied", "Combined text copied to clipboard!")
        logging.info("Combined content copied to clipboard.")

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        self.backend.clear_file_paths()
        self.copy_button.config(state=tk.DISABLED)
        self.file_menu.entryconfig("Save Combined File", state=tk.DISABLED)
        logging.info("Text area cleared.")

    def show_about(self):
        about_window = Toplevel(self.root)
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
        self.root.attributes('-topmost', self.always_on_top_var.get())
        logging.info(f"Always on top set to {self.always_on_top_var.get()}.")

    def save_combined_file(self):
        combined_content = self.text_area.get(1.0, tk.END).strip()
        if not combined_content:
            messagebox.showwarning("No Content", "There is no combined content to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(combined_content)
                messagebox.showinfo("Saved", f"Combined content saved to {file_path}")
                logging.info(f"Combined content saved to {file_path}")
            except Exception as e:
                logging.error(f"Error saving file: {e}")

    def manage_extensions(self):
        extensions_window = tk.Toplevel(self.root)
        extensions_window.title("Manage Extensions")
        extensions_window.geometry("400x300")

        scrollbar = ttk.Scrollbar(extensions_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(extensions_window, yscrollcommand=scrollbar.set, height=10)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)
        for ext in self.backend.supported_extensions:
            listbox.insert(tk.END, ext)

        entry_frame = ttk.Frame(extensions_window)
        entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        extension_entry = ttk.Entry(entry_frame)
        extension_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def remove_selected_extension():
            selected_indices = listbox.curselection()
            if selected_indices:
                selected_extensions = [listbox.get(i) for i in selected_indices]
                self.backend.remove_extensions(selected_extensions)
                for i in reversed(selected_indices):
                    listbox.delete(i)
                self.save_config()

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
                if self.backend.add_extension(new_ext):
                    listbox.insert(tk.END, new_ext)
                    extension_entry.delete(0, tk.END)
                    self.save_config()
                    logging.info(f"Added new extension: {new_ext}")
                else:
                    messagebox.showwarning("Duplicate Extension", f"{new_ext} is already supported!")

        add_button = ttk.Button(entry_frame, text="Add", command=add_new_extension)
        add_button.pack(side=tk.RIGHT)