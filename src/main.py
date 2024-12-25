# main.py
import tkinterdnd2
from ui import FileCombinerApp

if __name__ == "__main__":
    root = tkinterdnd2.Tk()
    app = FileCombinerApp(root)
    root.mainloop()