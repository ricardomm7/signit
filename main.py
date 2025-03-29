from modules import gui
import tkinter as tk

def main():
    root = tk.Tk()
    app = gui.CertificateSignerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
