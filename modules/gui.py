import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
import os
import pandas as pd

from modules import processor, utils

class CertificateSignerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Digital Certificate Signer")

        # Variáveis para armazenar os caminhos e dados
        self.template_pdf = None
        self.csv_file = None
        self.click_coords = None
        self.csv_data = None

        # Cria os elementos da interface
        self.create_widgets()

    def create_widgets(self):
        self.select_pdf_button = tk.Button(self.master, text="Select PDF Template", command=self.select_pdf)
        self.select_pdf_button.pack(pady=5)

        self.select_csv_button = tk.Button(self.master, text="Select CSV File", command=self.select_csv)
        self.select_csv_button.pack(pady=5)

        # Canvas para exibir a primeira página do PDF
        self.canvas = tk.Canvas(self.master, width=600, height=800, bg="gray")
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.process_button = tk.Button(self.master, text="Generate Certificates", command=self.generate_certificates)
        self.process_button.pack(pady=5)

    def select_pdf(self):
        self.template_pdf = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.template_pdf:
            try:
                # Converter a primeira página do PDF em imagem para exibição
                image = processor.pdf_to_image(self.template_pdf)
                self.tk_image = ImageTk.PhotoImage(image)
                self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load PDF template: {e}")

    def select_csv(self):
        self.csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.csv_file:
            try:
                self.csv_data = utils.read_csv_data(self.csv_file)
                messagebox.showinfo("CSV Loaded", f"{len(self.csv_data)} records loaded.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load CSV file: {e}")

    def on_canvas_click(self, event):
        # Salva as coordenadas clicadas no canvas
        self.click_coords = (event.x, event.y)
        messagebox.showinfo("Coordinates Selected", f"Selected coordinates: {self.click_coords}")

    def generate_certificates(self):
        if not self.template_pdf or self.csv_data is None or self.click_coords is None:
            messagebox.showerror("Error", "Please select a PDF template, CSV file, and click on the position.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        # Para cada registro no CSV, gera um certificado com o texto informado
        for idx, row in self.csv_data.iterrows():
            text_to_add = row['text']
            output_filename = os.path.join(output_dir, f"certificate_{idx+1}.pdf")
            try:
                processor.add_text_to_pdf(self.template_pdf, output_filename, self.click_coords, text_to_add)
            except Exception as e:
                messagebox.showerror("Error", f"Error processing certificate {idx+1}: {e}")
        messagebox.showinfo("Done", "Certificates generated successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateSignerGUI(root)
    root.mainloop()
