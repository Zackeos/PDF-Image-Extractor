import fitz
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading

def extract_images_from_pdf(pdf_path, output_dir, log_callback):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        log_callback(f"Error opening {os.path.basename(pdf_path)}: {e}")
        return

    image_count = 0
    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_num)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            try:
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                image_count += 1
            except Exception as e:
                log_callback(f"Error saving image from {os.path.basename(pdf_path)}: {e}")
    
    doc.close()
    
    if image_count > 0:
        log_callback(f"  Extracted {image_count} images to '{output_dir}'")
    else:
        log_callback(f"  No images found in '{os.path.basename(pdf_path)}'.")

def process_pdf_folder(input_dir, main_output_dir, log_callback):
    log_callback(f"Scanning for PDFs in '{input_dir}'...")
    found_pdfs = 0
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                found_pdfs += 1
                pdf_path = os.path.join(root, filename)
                pdf_subfolder_name = os.path.splitext(filename)[0]
                specific_output_path = os.path.join(main_output_dir, pdf_subfolder_name)
                
                log_callback(f"\nProcessing '{filename}'...")
                extract_images_from_pdf(pdf_path, specific_output_path, log_callback)
    
    if found_pdfs == 0:
        log_callback("\nNo PDF files were found.")
    else:
        log_callback(f"\nFinished. Processed {found_pdfs} PDF file(s).")

class PdfExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Image Extractor")
        self.root.geometry("700x500")

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_frame, text="Input Folder:", width=12, anchor='w').pack(side=tk.LEFT)
        tk.Entry(input_frame, textvariable=self.input_dir, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(input_frame, text="Browse...", command=self.select_input_dir).pack(side=tk.LEFT)

        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_frame, text="Output Folder:", width=12, anchor='w').pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(output_frame, text="Browse...", command=self.select_output_dir).pack(side=tk.LEFT)

        self.start_button = tk.Button(main_frame, text="Start Extraction", command=self.start_extraction, bg="#4CAF50", fg="white", height=2)
        self.start_button.pack(fill=tk.X, pady=10)

        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)

    def select_input_dir(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_dir.set(folder_selected)

    def select_output_dir(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_dir.set(folder_selected)

    def log_message(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)

    def start_extraction(self):
        input_path = self.input_dir.get()
        output_path = self.output_dir.get()

        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        self.start_button.config(state='disabled', text="Processing...")
        
        thread = threading.Thread(target=self.run_processing, args=(input_path, output_path))
        thread.daemon = True
        thread.start()

    def run_processing(self, input_path, output_path):
        try:
            process_pdf_folder(input_path, output_path, self.log_message)
        except Exception as e:
            self.log_message(f"An unexpected error occurred: {e}")
        finally:
            self.start_button.config(state='normal', text="Start Extraction")
            messagebox.showinfo("Complete", "Extraction process has finished!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PdfExtractorApp(root)
    root.mainloop()