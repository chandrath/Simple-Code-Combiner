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
import time  # Import the time module

try:
    import tiktoken
except ImportError:
    tiktoken = None
    logging.warning("The 'tiktoken' library is not installed. Token counts may be inaccurate. Install it with: pip install tiktoken")

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
        self.button_frame.columnconfigure(1, weight=0)
        self.button_frame.columnconfigure(2, weight=0) # For clear button

        # AI Summarize button (moved and styled)
        self.summarize_button = ttk.Button(self.button_frame, text="AI Summarize", command=self.summarize_combined_text, state=tk.DISABLED, style="dark.Outline.TButton", padding=2)
        self.summarize_button.grid(row=0, column=0, sticky="w")

        # Edit button
        self.edit_button = ttk.Button(self.button_frame, text="Edit", command=self.open_edit_files_popup, state=tk.DISABLED, style="dark.Outline.TButton", padding=2)
        self.edit_button.grid(row=0, column=1, sticky="e", padx=(0,5))

        # Clear button (moved and styled)
        self.clear_button = ttk.Button(self.button_frame, text="Clear", command=self.clear_text, style="danger.Outline.TButton", padding=2)
        self.clear_button.grid(row=0, column=2, sticky="e")

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
        self.download_button = ttk.Button(self.frame, text="⤓ Save", command=self.save_combined_file, state=tk.DISABLED, width=6)  # Changed text and adjusted width
        self.download_button.pack(pady=5)

        # Progress bar at the bottom
        self.progressbar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progressbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 2))
        self.progressbar.lower()  # Ensure progressbar is at the very bottom
        self.initial_loading()

        # Initialize the list to hold file paths (managed by backend)

        # Set up drag and drop
        self.setup_drag_and_drop()
        self.load_config() # Load config after initializing backend and menu

    def initial_loading(self):
        self.start_progress()
        self.root.after(1000, self.stop_initial_progress) # Keep it for 1 second

    def stop_initial_progress(self):
        self.stop_progress()

    def start_progress(self):
        self.progressbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 2))
        self.progressbar.start()
        self.progressbar.lower()

    def stop_progress(self):
        self.progressbar.stop()
        self.root.after(300, self.progressbar.pack_forget) # Keep it visible for 300ms

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
        files_added = False
        for file_path in self.backend.get_files_from_folder(folder_path):
            self.import_file(file_path)
            files_added = True
        if files_added:
            self.combine_button.config(state=tk.NORMAL)
            self.edit_button.config(state=tk.NORMAL)

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
            self.edit_button.config(state=tk.NORMAL)
        else:
            self.display_error(f"Unsupported extension - {file_path}. If it's a code file, use 'Preferences -> Manage Extensions' to add it.")

    def open_files(self):
        files = filedialog.askopenfilenames(filetypes=[("All files", "*.*")])
        if files:
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

    def open_edit_files_popup(self):
        if not self.backend.file_paths:
            messagebox.showinfo("No Files", "No files added yet.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Edit Files")

        frame = ttk.Frame(popup, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        for file_path in list(self.backend.file_paths):  # Iterate over a copy
            file_frame = ttk.Frame(frame)
            file_frame.pack(fill=tk.X, pady=2)

            file_name = os.path.basename(file_path)
            ttk.Label(file_frame, text=file_name).pack(side=tk.LEFT, expand=True, fill=tk.X)

            remove_button = ttk.Button(file_frame, text="❌", width=3, style="danger.TButton", command=lambda path=file_path: self.remove_file(path, popup))
            remove_button.pack(side=tk.RIGHT)

    def remove_file(self, file_path, popup):
        if file_path in self.backend.file_paths:
            self.backend.file_paths.remove(file_path)

            # Update the text area
            self.text_area.delete(1.0, tk.END)
            for path in self.backend.file_paths:
                file_name = os.path.basename(path)
                self.text_area.insert(tk.END, f"{file_name} ", "filename")
                self.text_area.insert(tk.END, f"({path})\n", "filepath")

            # Reopen the popup to refresh the list (simplest way)
            popup.destroy()
            self.open_edit_files_popup()

            if not self.backend.file_paths:
                self.edit_button.config(state=tk.DISABLED)
                self.combine_button.config(state=tk.DISABLED)

    def calculate_token_count(self, text):
        if tiktoken:
            try:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo") # Or another suitable model
                return len(encoding.encode(text))
            except Exception as e:
                logging.warning(f"Error calculating token count with tiktoken: {e}")
                return len(text.split()) # Fallback to simple split
        else:
            return len(text.split()) # Simple split if tiktoken is not available

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

        self.start_progress() # Start progress before a potentially long operation
        self.root.update() # Force UI update to show progress bar immediately
        start_time = time.time() # For measuring execution time

        combined_content = self.backend.combine_files()
        token_count = self.calculate_token_count(combined_content)

        end_time = time.time()
        print(f"combine_files execution time: {end_time - start_time:.4f} seconds")

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
        self.edit_button.config(state=tk.DISABLED)

        # Show success message
        self.error_label.config(text="Provided files now combined. You can copy to clipboard or save the file.", foreground="green")

        # Disable the combine button
        self.combine_button.config(state=tk.DISABLED)
        self.root.after(300, self.stop_progress) # Keep progress bar for a short duration

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
        self.edit_button.config(state=tk.DISABLED)
        self.clear_error()
        self.combine_button.config(state=tk.DISABLED)
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