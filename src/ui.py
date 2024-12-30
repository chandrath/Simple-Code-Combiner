# ui.py
# ui.py
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES
import ttkbootstrap as ttk
from file_combiner import FileCombinerBackend
from ui_menu import FileCombinerMenu
import logging
from ai_integration import summarize_text

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Combiner")
        self.root.geometry("300x450")

        # Initialize the backend logic
        self.backend = FileCombinerBackend()

        # Initialize the menu
        self.menu = FileCombinerMenu(self.root, self)

        # Set up logging (ensure it's initialized once)
        logging.basicConfig(filename="file_combiner.log", level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("Application started")

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

        # **New: Error/Warning display area**
        self.error_frame = ttk.Frame(self.frame, padding=5)
        self.error_frame.pack(fill=tk.X, pady=(0, 5))
        self.error_label = ttk.Label(self.error_frame, text="", foreground="red", wraplength=280)
        self.error_label.pack(fill=tk.X)
        self.error_label.grid_propagate(False) # Prevent resizing based on content

        # Create a button to summarize text
        self.summarize_button = ttk.Button(self.frame, text="AI Summarize", command=self.summarize_combined_text, state=tk.DISABLED)
        self.summarize_button.pack(pady=5)

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
        self.load_config() # Load config after initializing backend and menu

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
            self.clear_error() # Clear any previous error
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
        self.error_label.config(text=message, foreground="red")
        logging.error(message)

    def clear_error(self):
        self.error_label.config(text="", foreground="red")

    def summarize_combined_text(self):
        combined_content = self.text_area.get(1.0, tk.END).strip()
        if not combined_content:
            messagebox.showwarning("No Content", "There is no combined content to summarize.")
            return
        summarize_text(combined_content, app=self)

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
        self.menu.enable_save()
        self.summarize_button.config(state=tk.NORMAL)

    def copy_to_clipboard(self):
        combined_content = self.text_area.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(combined_content.strip())
        self.error_label.config(text="Combined text copied to clipboard!", foreground="green")
        logging.info("Combined content copied to clipboard.")

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        self.backend.clear_file_paths()
        self.copy_button.config(state=tk.DISABLED)
        self.menu.disable_save()
        self.summarize_button.config(state=tk.DISABLED)
        self.clear_error()
        logging.info("Text area cleared.")

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