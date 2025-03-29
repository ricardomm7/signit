import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

from PIL import ImageTk

from modules import processor, utils


class CertificateSignerGUI:
    def __init__(self, master):
        self.master = master
        master.title("SIGNIT - Digital Certificate Signer")
        master.geometry("1000x700")  # Redimensiona a janela inicial

        # Variáveis para armazenar os caminhos e dados
        self.template_pdf = None
        self.csv_file = None
        self.click_coords = None
        self.csv_data = None
        self.text_color = "#000000"  # Cor padrão (preto)
        self.text_font = "helv"  # Fonte padrão (Helvetica)
        self.text_size = 12  # Tamanho padrão do texto
        self.text_bold = tk.BooleanVar(value=False)  # Negrito desativado por padrão
        self.text_italic = tk.BooleanVar(value=False)  # Itálico desativado por padrão
        self.preview_text_id = None

        # Cria o menu superior
        self.create_top_menu()

        # Canvas para exibir a primeira página do PDF
        self.canvas = tk.Canvas(self.master, width=600, height=800, bg="gray")
        self.canvas.pack(pady=5)

    def create_top_menu(self):
        top_menu = tk.Frame(self.master, bg="lightgray")
        top_menu.pack(side="top", fill="x")

        # Botões para opções
        tk.Button(top_menu, text="Select PDF Template", command=self.select_pdf).pack(side="left", padx=5, pady=5)
        tk.Button(top_menu, text="Select CSV File", command=self.select_csv).pack(side="left", padx=5, pady=5)
        tk.Button(top_menu, text="Select Text Color", command=self.select_color).pack(side="left", padx=5, pady=5)

        # Checkboxes para estilo do texto
        tk.Checkbutton(top_menu, text="Bold", variable=self.text_bold, command=self.update_preview_text).pack(
            side="left", padx=5, pady=5)
        tk.Checkbutton(top_menu, text="Italic", variable=self.text_italic, command=self.update_preview_text).pack(
            side="left", padx=5, pady=5)

        # Controle para tamanho do texto
        tk.Label(top_menu, text="Text Size:", bg="lightgray").pack(side="left", padx=5)
        self.text_size_spinbox = tk.Spinbox(top_menu, from_=8, to=72, width=5, command=self.update_text_size)
        self.text_size_spinbox.delete(0, "end")
        self.text_size_spinbox.insert(0, self.text_size)
        self.text_size_spinbox.pack(side="left", padx=5)

        # Botão para gerar os certificados (alinhado à direita)
        tk.Button(top_menu, text="Generate Certificates", command=self.generate_certificates).pack(side="right", padx=5,
                                                                                                   pady=5)

    def update_text_size(self):
        # Atualiza o tamanho do texto
        try:
            self.text_size = int(self.text_size_spinbox.get())
            self.update_preview_text()
        except ValueError:
            messagebox.showerror("Error", "Invalid text size.")

    def update_preview_text(self):
        # Atualiza a prévia do texto no canvas
        if self.preview_text_id:
            font_style = self.text_font
            if self.text_bold.get() and self.text_italic.get():
                font_style = "helv-bolditalic"
            elif self.text_bold.get():
                font_style = "helv-bold"
            elif self.text_italic.get():
                font_style = "helv-italic"
            self.canvas.itemconfig(self.preview_text_id, font=(font_style, self.text_size))

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

    def select_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")[1]
        if color_code:
            self.text_color = color_code

    def on_canvas_click(self, event):
        # Salva as coordenadas clicadas no canvas
        self.click_coords = (event.x, event.y)
        messagebox.showinfo("Coordinates Selected", f"Selected coordinates: {self.click_coords}")

        # Atualiza a prévia do texto no canvas
        if self.preview_text_id:
            self.canvas.delete(self.preview_text_id)
        font_style = self.text_font
        if self.text_bold.get() and self.text_italic.get():
            font_style = "helv-bolditalic"
        elif self.text_bold.get():
            font_style = "helv-bold"
        elif self.text_italic.get():
            font_style = "helv-italic"
        self.preview_text_id = self.canvas.create_text(
            event.x, event.y, text="Preview Text", fill=self.text_color, font=(font_style, self.text_size)
        )

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
            # Usa o nome da pessoa para nomear o arquivo, removendo espaços
            person_name = row['text'].replace(" ", "").lower()
            output_filename = os.path.join(output_dir, f"certificate_{person_name}.pdf")
            try:
                processor.add_text_to_pdf(
                    self.template_pdf, output_filename, self.click_coords, text_to_add,
                    font_size=self.text_size, font=self.text_font, color=self.text_color
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error processing certificate for {row['text']}: {e}")
        messagebox.showinfo("Done", "Certificates generated successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateSignerGUI(root)
    root.mainloop()
