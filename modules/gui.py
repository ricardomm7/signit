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
        self.click_coords = (500, 500)  # Coordenadas padrão
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
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Frame para exibir os previews
        self.preview_frame = tk.Frame(self.master, bg="white")
        self.preview_frame.pack(side="right", fill="both", expand=True)

        self.preview_canvas = tk.Canvas(self.preview_frame, bg="white")
        self.preview_canvas.pack(side="left", fill="both", expand=True)

        self.preview_scrollbar = tk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_canvas.yview)
        self.preview_scrollbar.pack(side="right", fill="y")

        self.preview_canvas.configure(yscrollcommand=self.preview_scrollbar.set)
        self.preview_inner_frame = tk.Frame(self.preview_canvas, bg="white")
        self.preview_canvas.create_window((0, 0), window=self.preview_inner_frame, anchor="nw")

        self.preview_inner_frame.bind("<Configure>", lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))

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

        # Entrada para coordenadas de posição
        tk.Label(top_menu, text="X:", bg="lightgray").pack(side="left", padx=5)
        self.x_entry = tk.Entry(top_menu, width=5)
        self.x_entry.pack(side="left", padx=5)
        self.x_entry.insert(0, 200)

        tk.Label(top_menu, text="Y:", bg="lightgray").pack(side="left", padx=5)
        self.y_entry = tk.Entry(top_menu, width=5)
        self.y_entry.pack(side="left", padx=5)
        self.y_entry.insert(0, 200)

        tk.Button(top_menu, text="Set Position", command=self.set_position_from_input).pack(side="left", padx=5)

        # Botão para gerar os certificados (alinhado à direita)
        tk.Button(top_menu, text="Generate Certificates", command=self.generate_certificates).pack(side="right", padx=5, pady=5)

    def set_position_from_input(self):
        # Define as coordenadas com base nos valores inseridos manualmente
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            self.click_coords = (x, y)
            messagebox.showinfo("Coordinates Set", f"Coordinates set to: {self.click_coords}")

            # Atualiza a prévia do texto no canvas
            self.update_preview_text_at(x, y)

            # Atualiza os previews
            self.update_previews()
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates. Please enter numeric values.")

    def on_canvas_click(self, event):
        # Define as coordenadas com base no clique no canvas
        self.click_coords = (event.x, event.y)
        messagebox.showinfo("Coordinates Selected", f"Selected coordinates: {self.click_coords}")

        # Atualiza os campos de entrada com as coordenadas clicadas
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, event.x)
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, event.y)

        # Atualiza a prévia do texto no canvas
        self.update_preview_text_at(event.x, event.y)

        # Atualiza os previews
        self.update_previews()

    def update_preview_text_at(self, x, y):
        # Atualiza a prévia do texto no canvas na posição especificada
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
            x, y, text="Preview Text", fill=self.text_color, font=(font_style, self.text_size)
        )

    def update_text_size(self):
        # Atualiza o tamanho do texto
        try:
            self.text_size = int(self.text_size_spinbox.get())
            self.update_preview_text()
        except ValueError:
            messagebox.showerror("Error", "Invalid text size.")

    def update_preview_text(self):
        # Atualiza a prévia do texto no canvas
        if self.click_coords:
            self.update_preview_text_at(*self.click_coords)

    def select_pdf(self):
        self.template_pdf = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.template_pdf:
            try:
                # Converter a primeira página do PDF em imagem para exibição
                image = processor.pdf_to_image(self.template_pdf)
                self.tk_image = ImageTk.PhotoImage(image)
                self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

                # Atualizar os previews se o CSV já estiver carregado
                if self.csv_data is not None:
                    self.update_previews()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load PDF template: {e}")

    def select_csv(self):
        self.csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.csv_file:
            try:
                self.csv_data = utils.read_csv_data(self.csv_file)
                messagebox.showinfo("CSV Loaded", f"{len(self.csv_data)} records loaded.")

                # Atualizar os previews se o template PDF já estiver carregado
                if self.template_pdf is not None:
                    self.update_previews()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load CSV file: {e}")

    def select_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")[1]
        if color_code:
            self.text_color = color_code

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

    def update_previews(self):
        # Limpa os previews existentes
        for widget in self.preview_inner_frame.winfo_children():
            widget.destroy()

        # Gera e exibe os previews
        for idx, row in self.csv_data.iterrows():
            text_to_add = row['text']
            try:
                preview_image = processor.generate_preview_image(
                    self.template_pdf, self.click_coords, text_to_add,
                    font_size=self.text_size, font=self.text_font, color=self.text_color
                )
                tk_image = ImageTk.PhotoImage(preview_image)
                label = tk.Label(self.preview_inner_frame, image=tk_image, bg="white")
                label.image = tk_image  # Keep a reference to avoid garbage collection
                label.pack(pady=(10, 0))  # Espaçamento superior

                # Adiciona uma linha preta abaixo de cada preview
                separator = tk.Frame(self.preview_inner_frame, height=2, bg="black", width=self.preview_canvas.winfo_width())
                separator.pack(fill="x", pady=(10, 10))  # Espaçamento superior e inferior
            except Exception as e:
                tk.Label(self.preview_inner_frame, text=f"Error generating preview for {row['text']}: {e}", fg="red", bg="white").pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateSignerGUI(root)
    root.mainloop()
