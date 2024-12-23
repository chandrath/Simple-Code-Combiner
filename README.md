<!-- Cover Icon -->
<p align="center">
  <img src="Cover Icon.png" alt="Simple Code Combiner Icon" width="200" height="200">
</p>

<h1 align="center">Simple Code Combiner</h1>

<p align="center">
  🚀 A straightforward tool to combine multiple code files into a single output.
</p>

---

## Features

- ✅ **Simple GUI:** Intuitive drag-and-drop interface for easy file selection.
- ✅ **Flexible File Support:** Accepts a wide range of programming language and code-related file extensions.
- ✅ **Customizable File Types:** Allows users to add or remove supported file extensions, saving preferences to a config file.
- ✅ **Inline Error Reporting:** Displays clear error messages directly in the text area for unsupported files, guiding the user to configure extensions.
- ✅ **Copy to Clipboard:** Copies the combined content to the clipboard with one click.
- ✅ **Save Combined Output:** Saves the combined text to a single txt file.

---

## Screenshots

### Simple User Interface

[Code Combiner UI](https://i.imgur.com/aMpxral.png)

---

## Getting Started

### Prerequisites

To run the program:

- Python 3.8+ installed (if running from source).
- TkinterDnD2 and ttkbootstrap installed as dependencies

### Installation

#### **Run from Source**

1.  Clone this repository:
    ```bash
    git clone https://github.com/chandrath/Simple-Code-Combiner.git
    cd Simple-Code-Combiner
    ```
2.  Install dependencies:
    ```bash
    pip install tkinterdnd2 ttkbootstrap
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## Usage

### Drag and Drop:

- Drag and drop code files directly into the text area of the application.

### Manage Extensions:

- Use the `Preferences -> Manage Extensions` to view the current list of supported file types.
- Add a new file extension (e.g., `.myext`) into the text entry and click `Add`
- Select an extension in the list and click `Remove` to remove it from the list.

### Combine:

- Click the 'Combine Files' button to merge the content of all listed files into a single output in the text area.

### Copy and Save:

- Click the 'Copy to Clipboard' button to copy the combined content to the clipboard.
- Use the 'File -> Save Combined File' option to save the combined content to a file.

## License

- "Simple Code Combiner" uses the GPLv3 license

Feel free to open an issue to suggest more features or report bugs!
