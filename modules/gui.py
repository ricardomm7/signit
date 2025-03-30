# gui.py

import os
import tempfile
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk

import fitz  # PyMuPDF
from PIL import Image, ImageTk

from modules.processor import generate_certificates
from modules.utils import read_names_from_csv


class CertificateSignerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("SIGNIT - Digital Certificate Signer")
        self.master.geometry("1000x700")

        # Template paths
        self.template_path = tk.StringVar()
        self.csv_path = tk.StringVar()

        # Text configuration variables
        self.font_family_var = tk.StringVar(value="Times-Roman")
        self.font_size_var = tk.IntVar(value=24)
        self.is_bold_var = tk.BooleanVar(value=False)
        self.is_italic_var = tk.BooleanVar(value=False)
        self.font_color_var = "#000000"  # Default: black

        # Text position variables (for PDF, origin is bottom-left)
        self.pos_x_var = tk.IntVar(value=300)
        self.pos_y_var = tk.IntVar(value=400)

        # Name format
        self.name_format_var = tk.StringVar(value="{name}")

        # Preview data
        self.preview_img = None
        self.template_pdf = None
        self.preview_temp_file = None
        self.sample_name = "Jane Doe"

        # Create the GUI layout
        self.create_widgets()

    def create_widgets(self):
        # Main container with padding
        main_container = ttk.Frame(self.master, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top frame for file selection
        file_frame = ttk.LabelFrame(main_container, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=5)

        # Template PDF selection
        ttk.Label(file_frame, text="Template PDF:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.template_path, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_template).grid(row=0, column=2, padx=5, pady=5)

        # CSV file selection
        ttk.Label(file_frame, text="Names CSV:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.csv_path, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_csv).grid(row=1, column=2, padx=5, pady=5)

        # Middle section with text settings and preview side by side
        middle_frame = ttk.Frame(main_container)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Left side: Text settings and action buttons
        left_side_frame = ttk.Frame(middle_frame)
        left_side_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Text settings frame
        text_frame = ttk.LabelFrame(left_side_frame, text="Text Settings", padding="10")
        text_frame.pack(fill=tk.X, pady=5)

        # Font family
        font_frame = ttk.Frame(text_frame)
        font_frame.pack(fill=tk.X, pady=5)

        ttk.Label(font_frame, text="Font:").grid(row=0, column=0, sticky=tk.E, padx=5)
        font_options = ["Times-Roman", "Helvetica", "Courier", "Symbol"]
        ttk.Combobox(font_frame, textvariable=self.font_family_var, values=font_options, width=15).grid(
            row=0, column=1, padx=5)

        # Font size
        ttk.Label(font_frame, text="Size:").grid(row=0, column=2, sticky=tk.E, padx=5)
        ttk.Spinbox(font_frame, from_=8, to=72, textvariable=self.font_size_var, width=5).grid(
            row=0, column=3, padx=5)

        # Font style
        style_frame = ttk.Frame(text_frame)
        style_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(style_frame, text="Bold", variable=self.is_bold_var).grid(row=0, column=0, padx=5)
        ttk.Checkbutton(style_frame, text="Italic", variable=self.is_italic_var).grid(row=0, column=1, padx=5)

        # Color picker
        color_frame = ttk.Frame(text_frame)
        color_frame.pack(fill=tk.X, pady=5)

        ttk.Button(color_frame, text="Text Color", command=self.choose_font_color).grid(row=0, column=0, padx=5)
        self.color_indicator = tk.Canvas(color_frame, width=20, height=20, bg=self.font_color_var)
        self.color_indicator.grid(row=0, column=1, padx=5)

        # Text position
        position_frame = ttk.Frame(text_frame)
        position_frame.pack(fill=tk.X, pady=5)

        ttk.Label(position_frame, text="X Position:").grid(row=0, column=0, sticky=tk.E, padx=5)
        ttk.Spinbox(position_frame, from_=0, to=1000, textvariable=self.pos_x_var, width=5,
                    command=lambda: self.update_preview()).grid(row=0, column=1, padx=5)

        ttk.Label(position_frame, text="Y Position:").grid(row=0, column=2, sticky=tk.E, padx=5)
        ttk.Spinbox(position_frame, from_=0, to=1000, textvariable=self.pos_y_var, width=5,
                    command=lambda: self.update_preview()).grid(row=0, column=3, padx=5)

        # Sample name for preview
        sample_frame = ttk.Frame(text_frame)
        sample_frame.pack(fill=tk.X, pady=5)

        ttk.Label(sample_frame, text="Sample Name:").grid(row=0, column=0, sticky=tk.E, padx=5)
        sample_entry = ttk.Entry(sample_frame, width=30)
        sample_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        sample_entry.insert(0, self.sample_name)
        sample_entry.bind("<Return>", lambda e: self.update_sample_name(sample_entry.get()))
        ttk.Button(sample_frame, text="Update",
                   command=lambda: self.update_sample_name(sample_entry.get())).grid(row=0, column=2, padx=5)

        # New action buttons frame below text settings
        action_frame = ttk.LabelFrame(left_side_frame, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Update Preview", command=self.update_preview).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(action_frame, text="Generate Certificates", command=self.generate_certificates).pack(side=tk.RIGHT, padx=5, pady=5)

        # Right side: Preview
        preview_frame = ttk.LabelFrame(middle_frame, text="Preview", padding="10")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Canvas for preview with scrollbars
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)

        self.preview_canvas = tk.Canvas(preview_container, bg="#f0f0f0")
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars for preview
        y_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.preview_canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        # Bind events to update preview when settings change
        self.font_family_var.trace_add("write", lambda *args: self.update_preview())
        self.font_size_var.trace_add("write", lambda *args: self.update_preview())
        self.is_bold_var.trace_add("write", lambda *args: self.update_preview())
        self.is_italic_var.trace_add("write", lambda *args: self.update_preview())
        self.name_format_var.trace_add("write", lambda *args: self.update_preview())

    def browse_template(self):
        file_path = filedialog.askopenfilename(
            title="Select Template PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.template_path.set(file_path)
            self.update_preview()

    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            self.csv_path.set(file_path)
            try:
                names = read_names_from_csv(file_path)
                if names and len(names) > 0:
                    self.update_sample_name(names[0])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")

    def update_sample_name(self, name):
        self.sample_name = name
        self.update_preview()

    def choose_font_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color", initialcolor=self.font_color_var)
        if color_code[1]:
            self.font_color_var = color_code[1]
            self.color_indicator.config(bg=self.font_color_var)
            self.update_preview()

    def get_font_settings(self):
        """Return a dictionary with all font settings"""
        font_name = self.font_family_var.get()

        # Add Bold/Italic suffixes for standard fonts
        if font_name in ["Times-Roman", "Helvetica", "Courier"]:
            if self.is_bold_var.get() and self.is_italic_var.get():
                if font_name == "Times-Roman":
                    font_name = "Times-BoldItalic"
                else:
                    font_name = f"{font_name}-BoldOblique"
            elif self.is_bold_var.get():
                if font_name == "Times-Roman":
                    font_name = "Times-Bold"
                else:
                    font_name = f"{font_name}-Bold"
            elif self.is_italic_var.get():
                if font_name == "Times-Roman":
                    font_name = "Times-Italic"
                else:
                    font_name = f"{font_name}-Oblique"

        return {
            "family": font_name,
            "size": self.font_size_var.get(),
            "bold": self.is_bold_var.get(),
            "italic": self.is_italic_var.get(),
            "color": self.font_color_var
        }

    def pdf_to_image(self, pdf_path, dpi=100):
        """
        Convert the first page of a PDF to a PIL Image using PyMuPDF (fitz).
        PyMuPDF is a pure Python library that doesn't need external dependencies.

        Args:
            pdf_path: Path to the PDF file
            dpi: Resolution of the output image

        Returns:
            PIL Image object
        """
        try:
            # Open the PDF file with PyMuPDF
            pdf_document = fitz.open(pdf_path)

            # Get the first page
            first_page = pdf_document[0]

            # Calculate zoom factor based on DPI
            zoom_factor = dpi / 72.0  # 72 points per inch

            # Get the pixel matrix with the specified zoom
            pixmap = first_page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

            # Close the PDF document
            pdf_document.close()

            return img

        except Exception as e:
            raise Exception(f"Error converting PDF to image: {str(e)}")

    def update_preview(self):
        """Generate and display a preview of the certificate with current settings"""
        template_path = self.template_path.get()
        if not template_path or not os.path.isfile(template_path):
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                text="Please select a template PDF file",
                font=("Helvetica", 14)
            )
            return

        # Clean up previous temp file
        if self.preview_temp_file and os.path.exists(self.preview_temp_file):
            os.unlink(self.preview_temp_file)

        # Format the name using the template
        name_text = self.name_format_var.get().format(name=self.sample_name)

        # Create a temporary preview file
        try:
            # Create a temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                self.preview_temp_file = tmp_file.name

            # Generate a preview certificate
            font_settings = self.get_font_settings()
            position = (self.pos_x_var.get(), self.pos_y_var.get())
            generate_certificates(
                template_path,
                [name_text],
                font_settings,
                position,
                os.path.dirname(self.preview_temp_file),
                os.path.basename(self.preview_temp_file)
            )

            # Convert the PDF to an image using PyMuPDF
            preview_image = self.pdf_to_image(self.preview_temp_file, dpi=100)

            # Convert PIL image to Tkinter PhotoImage
            self.preview_img = ImageTk.PhotoImage(image=preview_image)

            # Update canvas
            self.preview_canvas.delete("all")

            # Configure scrollregion
            self.preview_canvas.config(scrollregion=(0, 0, preview_image.width, preview_image.height))

            # Display the image
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_img)

            # Draw position marker
            marker_size = 10
            x, y = position
            # Convert from PDF coordinates (origin at bottom-left) to image coordinates (origin at top-left)
            y_image = preview_image.height - y * (100 / 72)  # Adjust for DPI

            # Draw crosshair at text position
            self.preview_canvas.create_line(x * (100 / 72) - marker_size, y_image, x * (100 / 72) + marker_size,
                                            y_image, fill="red", width=2)
            self.preview_canvas.create_line(x * (100 / 72), y_image - marker_size, x * (100 / 72),
                                            y_image + marker_size, fill="red", width=2)

        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                text=f"Preview error: {str(e)}",
                font=("Helvetica", 14),
                fill="red"
            )

    def generate_certificates(self):
        """Generate certificates for all names in the CSV file"""
        template_path = self.template_path.get()
        csv_path = self.csv_path.get()

        if not template_path or not os.path.isfile(template_path):
            messagebox.showerror("Error", "Template PDF not found.")
            return

        if not csv_path or not os.path.isfile(csv_path):
            messagebox.showerror("Error", "CSV file not found.")
            return

        try:
            # Read names from CSV
            names = read_names_from_csv(csv_path)
            if not names:
                messagebox.showerror("Error", "No names found in CSV.")
                return

            # Format the names using the template
            formatted_names = [self.name_format_var.get().format(name=name) for name in names]

            # Ask for output directory
            output_dir = filedialog.askdirectory(title="Select Output Folder")
            if not output_dir:
                return

            # Generate certificates
            font_settings = self.get_font_settings()
            position = (self.pos_x_var.get(), self.pos_y_var.get())

            # Show progress bar
            progress_window = tk.Toplevel(self.master)
            progress_window.title("Generating Certificates")
            progress_window.geometry("300x100")
            progress_window.transient(self.master)
            progress_window.grab_set()

            ttk.Label(progress_window, text="Generating certificates...").pack(pady=10)

            progress = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
            progress.pack(pady=10)
            progress["maximum"] = len(names)

            # Update the progress bar
            progress_window.update()

            # Generate the certificates
            generate_certificates(
                template_path,
                formatted_names,
                font_settings,
                position,
                output_dir
            )

            progress_window.destroy()

            messagebox.showinfo("Success", f"Generated {len(names)} certificates in {output_dir}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate certificates: {str(e)}")
