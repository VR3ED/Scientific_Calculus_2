import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import os
import ProcessImages


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("COMPRESSIONE DI IMMAGINI TRAMITE DCT2")
        self.root.geometry("800x780")  # Dimensione della finestra

        self.image_path = None  # Variabile per memorizzare il percorso dell'immagine
        self.max_F = None  # Variabile per memorizzare la grandezza massima di F

        self.create_widgets()

    def create_widgets(self):
        # Frame for image selection
        self.image_frame = tk.Frame(self.root, padx=10, pady=10)
        self.image_frame.pack(fill=tk.X)

        # Button to choose .bmp image
        self.choose_image_button = tk.Button(self.image_frame, text="Scegli immagine .bmp", command=self.choose_image, bg="darkgray")
        self.choose_image_button.pack(side=tk.LEFT, padx=(0, 10))

        # Label to show selected image path
        self.image_path_label = tk.Label(self.image_frame, text="", width=50, anchor="w", relief=tk.SUNKEN)
        self.image_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Frame for process button and inputs
        self.process_frame = tk.Frame(self.root, padx=10, pady=10)
        self.process_frame.pack(fill=tk.BOTH, expand=True)
        # Frame for process button
        self.process_button_frame = tk.Frame(self.process_frame, padx=10, pady=10, relief=tk.SUNKEN)
        self.process_button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Button to validate and process inputs
        self.process_button = tk.Button(self.process_button_frame, text="Esegui compressione", command=self.process_inputs, bg="yellow")
        self.process_button.pack(fill=tk.BOTH, expand=True)
        # Frame for inputs        
        self.input_frame = tk.Frame(self.process_frame, padx=10, pady=10, relief=tk.SUNKEN)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        # InputBox for Ampiezza finestrelle (F)
        self.label_F = tk.Label(self.input_frame, text="Ampiezza finestrelle (F):")
        self.label_F.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_F = tk.Entry(self.input_frame)
        self.entry_F.grid(row=0, column=1, pady=5)

        # InputBox for Soglia taglio frequenze
        self.label_threshold = tk.Label(self.input_frame, text="Soglia taglio frequenze (d):")
        self.label_threshold.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_threshold = tk.Entry(self.input_frame)
        self.entry_threshold.grid(row=1, column=1, pady=5)

        # Frame for images
        self.image_display_frame = tk.Frame(self.root, padx=10, pady=10)
        self.image_display_frame.pack(fill=tk.BOTH, expand=True)
        # Labels for original images
        self.original_image_label_frame = tk.Frame(self.image_display_frame, padx=10, pady=10, relief=tk.SUNKEN, bd=1)
        self.original_image_label_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.original_image_label = tk.Label(self.original_image_label_frame, text="Immagine Originale")
        self.original_image_label.pack(fill=tk.BOTH, expand=True)
        # Frame for compression matrix visualization
        self.matrix_frame = tk.Frame(self.image_display_frame, padx=10, pady=10, relief=tk.SUNKEN, bd=1)
        self.matrix_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.matrix_label = tk.Label(self.matrix_frame, text="Visualizzazione matrice di compressione:")
        self.matrix_label.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.matrix_frame, width=300, height=300)
        self.canvas.pack()

        # Frame per i log
        self.frame_log = ttk.LabelFrame(self.root, text="Log", padding=10)
        self.frame_log.pack(pady=10, padx=10, fill="both", expand="yes")
        self.text_log = tk.Text(self.frame_log, wrap="word", height=10)
        self.text_log.pack(pady=5, fill="both", expand="yes")

    # apre file dialog per selezionare un'immagine .bmp
    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if file_path:
            self.image_path = file_path  # Salva il percorso dell'immagine selezionata
            self.image_path_label.config(text=file_path)  # Aggiorna la Label con il percorso dell'immagine
            self.display_image(file_path, self.original_image_label)  # Mostra l'immagine originale

            # Calcola la grandezza massima di F
            self.max_F = self.calculate_max_F(file_path)

            # Aggiorna il peso dell'immagine originale
            self.log_message("Selected image: " + file_path)
            if self.image_path:
                file_size_bytes = os.path.getsize(self.image_path)
                file_size_kb = file_size_bytes / 1024.0  # Converti da byte a kilobyte
            self.log_message("Original image size: " + str(file_size_kb) + " KB")
            self.log_message("Original image shape: " + str(Image.open(file_path).size))
        else:
            self.image_path = None  # Resetta il percorso dell'immagine se nessuna immagine è selezionata
            self.image_path_label.config(text="")
            self.max_F = None
            self.image_size_label.config(text="")
            self.compressed_image_size_label.config(text="")

    # Calcola la grandezza massima di F data immagine selezionata
    def calculate_max_F(self, image_path):
        with Image.open(image_path) as img:
            width, height = img.size
        return min(width, height)

    # Mostra l'immagine caricata nell'interfaccia utente
    def display_image(self, image_path, label):
        image = Image.open(image_path)
        image.thumbnail((300, 300))  # Ridimensiona l'immagine per adattarla alla UI
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo  # Mantiene un riferimento all'immagine per evitare che venga eliminata dal garbage collector

    # Verifica gli input "F" e "d" ed avvia la compressione
    def process_inputs(self):
        try:
            # Recupero la grandezza delle finestrelle
            F = int(self.entry_F.get())
            # Controllo che la grandezza delle finestrelle sia valida
            if not self.max_F:
                raise ValueError("Per favore seleziona un'immagine prima di procedere")
            # Controllo che un'immagine sia stata selezionata
            if not self.image_path:
                raise ValueError("Per favore seleziona un'immagine .bmp prima di procedere")

            # Controllo che la grandezza delle finestrelle sia compresa tra 1 e max_F
            if F <= 0 or F > self.max_F:
                raise ValueError(f"La grandezza delle finestrelle deve essere compresa tra 1 e {self.max_F}")

            # Recupero la soglia di compressione (d)
            d = int(self.entry_threshold.get())
            # Controllo che la soglia sia compresa tra 1 e 2F-2
            if not (0 <= d <= (2 * F - 2)):
                raise ValueError(f"La soglia di compressione deve essere compresa tra 0 e {2 * F - 2}")

            # Visualizza la matrice di compressione
            self.visualize_matrix()

            # Esegui la compressione in un thread separato
            threading.Thread(target=self.run_compression, args=(self.image_path, F, d)).start()
        except ValueError as e:
            messagebox.showerror("Errore di input", str(e))

    # Esegui la compressione dell'immagine
    def run_compression(self, image_path, F, d):
        ProcessImages.run_compression(image_path, F, d, self.text_log)
        compressed_image_path = "compressed_image.bmp"
        if os.path.exists(compressed_image_path):
            file_size_bytes = os.path.getsize(compressed_image_path)
            file_size_kb = file_size_bytes / 1024.0  # Converti da byte a kilobyte
        self.log_message("✅ Compression completated")
        self.log_message("New compressed image size: " + str(file_size_kb) + " KB")

    # Visualizza la matrice di compressione 
    def visualize_matrix(self):
        try:
            f = int(self.entry_F.get())
            d = int(self.entry_threshold.get())

            self.canvas.delete("all")
            cell_size = 300 // f
            for i in range(f):
                for j in range(f):
                    color = "red" if (f - (i + j)) <= f-d else "yellow"
                    x0, y0 = i * cell_size, j * cell_size
                    x1, y1 = x0 + cell_size, y0 + cell_size
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

        except ValueError:
            messagebox.showerror("Errore", "Inserisci valori validi per F e D.")

    # Print di una stringa sul LOG
    def log_message(self,message):
        self.text_log.insert(tk.END, message + "\n")
        self.text_log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
