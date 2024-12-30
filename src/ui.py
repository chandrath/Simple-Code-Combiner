# ui.py
# ui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES
import ttkbootstrap as ttk
from file_combiner import FileCombinerBackend
from ui_menu import FileCombinerMenu
import logging
import os  # Import os for path manipulation
from ai_integration import summarize_text

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Combiner")
        self.root.geometry("300x550")  # Assuming this is your updated geometry

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

        # **New: Token count label**
        self.token_count_label = ttk.Label(self.frame, text="", foreground="grey", font=("Arial", 8))
        self.token_count_label.pack(anchor="nw", padx=1)  # Align top-left

        # Frame to hold the text area and scrollbar
        self.text_area_frame = ttk.Frame(self.frame)
        self.text_area_frame.pack(pady=0, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        self.scrollbar = ttk.Scrollbar(self.text_area_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a text area to show dropped files
        self.text_area = tk.Text(self.text_area_frame, height=10, width=50, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the Scrollbar to control the Text widget
        self.scrollbar.config(command=self.text_area.yview)

        # Frame for buttons at the bottom of the text area
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        # AI Summarize button (moved and styled)
        self.summarize_button = ttk.Button(self.button_frame, text="AI Summarize", command=self.summarize_combined_text, state=tk.DISABLED, style="secondary.Outline.TButton", padding=2)
        self.summarize_button.grid(row=0, column=0, sticky="w")

        # Clear button (moved and styled)
        self.clear_button = ttk.Button(self.button_frame, text="Clear", command=self.clear_text, style="danger.Outline.TButton", padding=2)
        self.clear_button.grid(row=0, column=1, sticky="e")

        # **New: Error/Warning display area**
        self.error_frame = ttk.Frame(self.frame, padding=5)
        self.error_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.error_label = ttk.Label(self.error_frame, text="", foreground="red", wraplength=280)
        self.error_label.pack(fill=tk.X)
        self.error_label.grid_propagate(False) # Prevent resizing based on content

        # Create a button to combine files
        self.combine_button = ttk.Button(self.frame, text="Combine Files", command=self.combine_files)
        self.combine_button.pack(pady=5)

        # Create a button to copy combined text to clipboard
        self.copy_button = ttk.Button(self.frame, text="Copy to Clipboard", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(pady=5)

        # Download button (icon only) - moved
        self.download_button = ttk.Button(self.frame, text="⤓", command=self.save_combined_file, state=tk.DISABLED, width=3)
        self.download_button.pack(pady=5)

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
        if file_path:  # Enable combine button if files were added
            self.combine_button.config(state=tk.NORMAL)

    def import_file(self, file_path):
        if self.backend.is_supported_file(file_path):
            file_name = os.path.basename(file_path)
            self.backend.add_file_path(file_path)

            # Define tags and styles
            self.text_area.tag_config("filename", foreground="green", font=("Arial", 10, "bold"))
            self.text_area.tag_config("filepath", foreground="grey", font=("Arial", 8, "italic"))

            # Insert styled text
            self.text_area.insert(tk.END, f"{file_name} ", "filename")
            self.text_area.insert(tk.END, f"({file_path})\n", "filepath")

            self.clear_error()  # Clear any previous error
            self.combine_button.config(state=tk.NORMAL)  # Enable combine button
        else:
            self.display_error(f"Unsupported extension - {file_path}. If it's a code file, use 'Preferences -> Manage Extensions' to add it.")

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
        token_count = len(combined_content.split())  # Simple word/token count

        # Display token count
        self.token_count_label.config(text=f"Token Count: {token_count}")

        # Display combined content in the text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, combined_content)
        self.text_area.tag_remove("error", "1.0", tk.END)

        # Enable the copy and download buttons
        self.copy_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)
        self.menu.enable_save()
        self.summarize_button.config(state=tk.NORMAL)

        # Show success message
        self.error_label.config(text="Provided files now combined. You can copy to clipboard or save the file.", foreground="green")

        # Disable the combine button
        self.combine_button.config(state=tk.DISABLED)

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
        self.download_button.config(state=tk.DISABLED)
        self.menu.disable_save()
        self.summarize_button.config(state=tk.DISABLED)
        self.clear_error()
        self.combine_button.config(state=tk.NORMAL) # Enable combine button
        self.token_count_label.config(text="") # Clear token count
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

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = FileCombinerApp(root)
    root.mainloop()