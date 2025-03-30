# main.py

import tkinter as tk
from modules.gui import CertificateSignerGUI


def main():
    root = tk.Tk()
    app = CertificateSignerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
