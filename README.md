<!-- Cover Icon -->
<p align="center">
  <img src="Cover Icon.png" alt="Simple Code Combiner Icon" width="200" height="200">
</p>

<h1 align="center">Simple Code Combiner</h1>

<p align="center">
  🚀 A straightforward tool to combine multiple code files into a single output.
</p>

---

In a development environment, managing multiple code files can be a cumbersome task. The "Simple Code Combiner" app streamlines your workflow by allowing you to effortlessly combine various code files into a single output while labeling each file with its extension, all with just one click. Whether you're preparing scripts for deployment, consolidating code for testing, Feeding your code to LLMs for retrieval-augmented generation (RAG)., or simply organizing your projects, this free and open-source GUI tool enhances efficiency and reduces the risk of errors associated with manual copying and pasting. With support for a wide range of programming languages and customizable file types, it adapts to your specific needs, making it an essential addition to any developer's toolkit.

---

## Features

- ✅ **Streamlined for AI:** With a single click, all your code is gathered in one location, simplifying the process of providing it to AI.
- ✅ **Simple GUI:** Intuitive drag-and-drop interface for easy file selection.
- ✅ **Automatic Labeling:** Automatically labels each file with its extension for clarity and organization, making it easier for AI to identify each file.
- ✅ **Flexible File Support:** Accepts a wide range of programming languages and code-related file extensions.
- ✅ **Customizable File Types:** Allows users to add or remove supported file extensions, saving preferences to a configuration file.
- ✅ **Copy to Clipboard:** Copies the combined content to the clipboard with one click.
- ✅ **Save Combined Output:** Saves the combined text to a single .txt file.
- ✅ **Always on Top:** Keeps the application window in front of all other windows for easy access to all your code files.

---

## Screenshots

### Simple User Interface

![Code Combiner UI](https://i.imgur.com/iDTrivs.png)

---

## Getting Started

### Prerequisites

To run the program:

- Python 3.8+ installed (if running from source).
- TkinterDnD2 and ttkbootstrap installed as dependencies

### Installation

#### **Run as Executable (Recommended)**

1.  Download the latest release from the [Releases Page](https://github.com/chandrath/Simple-Code-Combiner/releases).
2.  Run the **`CodeCombiner.exe`** file.

**Note Regarding Antivirus:** Some antivirus programs might flag the executable as a potential threat. This is a common occurrence for applications created with tools like PyInstaller. If this happens, you can usually choose to "allow" or "whitelist" the application in your antivirus settings. The source code is available for review in this repository.

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

## Building from Source with PyInstaller

To create a standalone executable for the `CodeCombiner` application (which uses `tkinterdnd2` for drag-and-drop functionality), follow these instructions. It is crucial to complete each step carefully for a successful build.

**Prerequisites:**

1.  **Python and Pip:** Ensure you have Python (version 3.8 or higher) and `pip` installed on your system.
2.  **PyInstaller:** If you don't have it installed, install it using pip:

    ```bash
    pip install pyinstaller
    ```

3.  **`tkinterdnd2`:** Ensure you have `tkinterdnd2` installed:
    ```bash
    pip install tkinterdnd2
    ```

**Steps:**

1.  **Prepare Project Files:** Ensure your main project file (`main.py`) and the hook file (`hook-tkinterdnd2.py`) are in the **same directory**.

2.  **Obtain `hook-tkinterdnd2.py`:** Download `hook-tkinterdnd2.py` and save it in the same directory as your `main.py` file. The original file (under MIT License) can be obtained from:

```
 https://github.com/pmgagne/tkinterdnd2/blob/master/hook-tkinterdnd2.py
```

    *Note: If you are working with an updated version or fork, make sure to use the corresponding hook file (if needed).*

_A modified version of the hook file that resolves certain issues can be used from the project folder_

3. **Build with PyInstaller:** Open a terminal or command prompt in the same directory where your project files are located. Then, execute the following PyInstaller command:

   ```bash
   pyinstaller -F --additional-hooks-dir=. --onefile --windowed --icon=app.ico CodeCombiner.py
   ```

   - **`-F` or `--onefile`**: Creates a single, self-contained executable file.
   - **`--additional-hooks-dir=.`**: Tells PyInstaller to use the `hook-tkinterdnd2.py` file in the current directory to correctly include `tkinterdnd2` files.
   - **`--windowed`**: Creates an executable without a console window, suitable for GUI applications.
   - **`--icon=app.ico`**: For the exe icon.
   - **`CodeCombiner.py`**: Specifies your main Python script file.

4. **Locate the Executable:** After a successful build, the executable file will be located in the `dist` subdirectory within your project directory.

**Explanation of the Process**

- **`tkinterdnd2` Dependency:** The `tkinterdnd2` library is a wrapper for the `tkdnd` extension and requires special handling during PyInstaller builds. The `hook-tkinterdnd2.py` file provides PyInstaller with the necessary information to correctly bundle `tkdnd`.
- **Custom Hook File:** The custom hook file ensures that all platform specific binaries of `tkdnd` library are included in your build. The `additional-hooks-dir=.` tells PyInstaller where to find the custom hook script.
- **One-File Distribution:** Using `-F` or `--onefile` provides a single executable, which simplifies distribution as it does not require additional files or setup on the user's machine.
- **No Console Window:** By using the `--windowed` the end user won't see a console window when launching the executable.

**Important Notes:**

- **License:** The provided `hook-tkinterdnd2.py` file is under the MIT License. Make sure you retain the license notices where appropriate.
- **Error Troubleshooting:** If you encounter errors during the build, carefully check the terminal output and verify that you have followed all the steps.
- **Testing:** Thoroughly test your built executable after building it to make sure all functions work as expected.
- **Alternative Hook File:** If the hook file from the repository does not work properly, use the modified one from project directory.

**Attribution:**

These instructions are partially based on the information available in the `tkinterdnd2` project's page on PyPI ([https://pypi.org/project/tkinterdnd2/](https://pypi.org/project/tkinterdnd2/)) and with thanks to the advice and tips of @Matthias W (https://stackoverflow.com/a/78833056).

## License

- "Simple Code Combiner" uses the GPLv3 license

Feel free to open an issue to suggest more features or report bugs!
