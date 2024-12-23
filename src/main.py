import os
import tkinter as tk
from tkinter import filedialog, messagebox, Menu
from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as ttk

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Combiner")
        self.root.geometry("400x400")
        
        # Create a menu bar
        self.menu_bar = Menu(root)
        self.root.config(menu=self.menu_bar)

        # Create a "File" menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Add "Always on Top" option
        self.always_on_top_var = tk.BooleanVar()
        self.file_menu.add_checkbutton(label="Always on Top", variable=self.always_on_top_var, command=self.toggle_always_on_top)

        # Add "About Us" option
        self.file_menu.add_command(label="About Us", command=self.show_about)

        # Create a frame for drag and drop
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a label for instructions
        self.label = ttk.Label(self.frame, text="Drag and drop files here", font=("Arial", 14))
        self.label.pack(pady=20)

        # Create a text area to show dropped files
        self.text_area = tk.Text(self.frame, height=10, width=50)
        self.text_area.pack(pady=10)

        # Create a button to combine files
        self.combine_button = ttk.Button(self.frame, text="Combine Files", command=self.combine_files)
        self.combine_button.pack(pady=5)

        # Create a button to copy combined text to clipboard
        self.copy_button = ttk.Button(self.frame, text="Copy to Clipboard", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(pady=5)

        # Create a clear button
        self.clear_button = ttk.Button(self.frame, text="Clear", command=self.clear_text, style='Danger.TButton')
        self.clear_button.pack(pady=5)

        # Initialize the list to hold file paths
        self.file_paths = []

        # Set up drag and drop
        self.setup_drag_and_drop()

    def setup_drag_and_drop(self):
        # Register the main window for drag and drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        files = event.data.split()
        for file in files:
            if os.path.isfile(file):
                self.file_paths.append(file)
                self.text_area.insert(tk.END, f"{file}\n")

    def combine_files(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please drag and drop files first.")
            return

        combined_content = ""
        for file_path in self.file_paths:
            file_name = os.path.basename(file_path)
            combined_content += f"# {file_name}\n"
            with open(file_path, 'r') as f:
                combined_content += f.read() + "\n\n"

        # Display combined content in the text area
        self.text_area.delete(1.0, tk.END)  # Clear previous content
        self.text_area.insert(tk.END, combined_content)

        # Enable the copy button after combining files
        self.copy_button.config(state=tk.NORMAL)

    def copy_to_clipboard(self):
        combined_content = self.text_area.get(1.0, tk.END)
        self.root.clipboard_clear()  # Clear the clipboard
        self.root.clipboard_append(combined_content.strip())  # Append the combined content
        messagebox.showinfo("Copied", "Combined text copied to clipboard!")

    def clear_text(self):
        self.text_area.delete(1.0, tk.END)  # Clear the text area
        self.file_paths.clear()  # Clear the file paths
        self.copy_button.config(state=tk.DISABLED)  # Disable the copy button

    def show_about(self):
        messagebox.showinfo("About Us", "File Combiner v1.0\nA simple tool to combine code files.")

    def toggle_always_on_top(self):
        if self.always_on_top_var.get():
            self.root.attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False)

if __name__ == "__main__":
    # Create the main TkinterDnD window
    root = TkinterDnD.Tk()
    app = FileCombinerApp(root)
    root.mainloop()