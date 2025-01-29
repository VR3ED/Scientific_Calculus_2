from PIL import Image
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct
import threading
from mpl_toolkits.mplot3d import Axes3D


def run_compression(image_path, F_size, d_threshold, logger):
    try:
        blocks = generate_blocks(image_path, F_size)
        total_blocks = len(blocks)

        blocks_processed_dct = apply_dct2(blocks, d_threshold, F_size, logger, total_blocks)
        blocks_idct_rounded = apply_idct2(blocks_processed_dct, logger, total_blocks)

        save_compressed_image(blocks_idct_rounded, image_path, F_size)

    except Exception as e:
        print("Error during compression:", str(e))


def apply_dct2(blocks, d_threshold, F_size, logger, total_blocks):
    blocks_processed_threshold = []
    for idx, block in enumerate(blocks):
        block_array = np.array(block)
        block_dct = dct(dct(block_array.T, norm='ortho').T, norm='ortho')

        # Maschera di quantizzazione: crea matrice di booleani                      ####### qui si fa il controllo per vedere se
        # con valore true solo nelle posizioni < del parametro di threshold               # abbiamo i blocchi "gialli"
        mask = np.abs(np.add.outer(range(F_size), range(F_size))) < d_threshold           # ossia i blocchi che sono sopra la 
                                                                                          # diagonale "d"
        # Operazione che permette di mantenere solo i valori che corrispondono            #
        # agli indici degli elementi della matrice                                        # se non sono sopra la diagonale
        # di quantizzazione impostati a true                                              # allora vengono moltiplicati per 0
        block_processed_threshold = block_dct * mask                                      # tagliando quindi le frequenze
                                                                                    ####### 

        blocks_processed_threshold.append(block_processed_threshold)

        log_message(logger, "✅ DCT2 " + str(idx + 1) + "/"+ str(total_blocks) +" processed")

    return blocks_processed_threshold


def apply_idct2(blocks_dct_quantized, logger, total_blocks):
    blocks_idct_rounded = []
    for idx, block_dct_quantized in enumerate(blocks_dct_quantized):
        # Applica l'IDCT (Inverse Discrete Cosine Transform) al blocco quantizzato
        # La trasformazione è eseguita prima sulle colonne e poi sulle righe
        block_idct = idct(idct(block_dct_quantized.T, norm='ortho').T, norm='ortho')

        # Arrotonda i valori del blocco IDCT ai numeri interi più vicini
        block_idct_rounded = np.round(block_idct)
        # Imposta i valori negativi a 0 e i valori superiori a 255
        # a 255 per evitare valori di pixel non validi
        block_idct_rounded[block_idct_rounded < 0] = 0
        block_idct_rounded[block_idct_rounded > 255] = 255

        # Aggiunge il blocco IDCT arrotondato alla lista,
        # convertendolo in tipo uint8
        blocks_idct_rounded.append(block_idct_rounded.astype(np.uint8))

        log_message(logger, "✅ IDCT2 " + str(idx + 1) + "/"+ str(total_blocks) +" processed")

    return blocks_idct_rounded


def save_compressed_image(blocks_idct_rounded, original_image_path, block_size):
    compressed_image_filename = "compressed_image.bmp"

    try:
        with Image.open(original_image_path) as img:
            img_width, img_height = img.size
            compressed_image = Image.new('L', (img_width, img_height))

            # Calcolo del numero di blocchi orizzontali
            num_blocks_horizontal = img_width // block_size
            num_blocks_vertical = img_height // block_size
            # Ciclo attraverso i blocchi verticali dell'immagine
            for j in range(num_blocks_vertical):
                for i in range(num_blocks_horizontal):
                    # Calcolo delle coordinate del blocco
                    x0 = i * block_size
                    y0 = j * block_size
                    x1 = x0 + block_size
                    y1 = y0 + block_size

                    # Estrazione del prossimo blocco IDCT arrotondato dalla lista
                    block = blocks_idct_rounded.pop(0)
                    # Inserimento del blocco nella posizione
                    # corretta nell'immagine compressa
                    compressed_image.paste(Image.fromarray(block), (x0, y0))

            compressed_image.save(compressed_image_filename)

            def display_images(img, compressed_image):
                # stampa l'immagine compressa di fianco all'originale
                pfig, axes = plt.subplots(1, 2, figsize=(10, 5))
                # View original image
                axes[0].imshow(img, cmap='gray')
                axes[0].set_title('Original image')
                # View the reconstructed image
                axes[1].imshow(compressed_image, cmap='gray')
                axes[1].set_title('Reconstructed image')
                plt.tight_layout()
                plt.show()

            display_thread = threading.Thread(target=display_images, args=(np.array(img), np.array(compressed_image)))
            display_thread.start()
            #display_thread.join()

            compressed_image.close()
            print("Compressed image saved successfully.")

    except Exception as e:
        print("Error during saving compressed image:", str(e))


def generate_blocks(image_path, block_size):
    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size

            # Converti in bianco e nero se necessario
            img_gray = img.convert('L') if img.mode != 'L' else img

            # calcola il numero di blocchi orizzontali e verticali
            num_blocks_horizontal = img_width // block_size
            num_blocks_vertical = img_height // block_size

            blocks = []

            # estrai blocchi dall'immagine
            for j in range(num_blocks_vertical):
                for i in range(num_blocks_horizontal):
                    # calcola le coordinate del blocco: 
                    # x0 e y0 alto a sx - x1 e y1 basso a dx
                    x0 = i * block_size
                    y0 = j * block_size
                    x1 = x0 + block_size
                    y1 = y0 + block_size

                    # Estrai il blocco dall'immagine 
                    block = img_gray.crop((x0, y0, x1, y1))
                    blocks.append(block)

            return blocks

    except Exception as e:
        print("Error during image processing:", str(e))
        return []


def log_message(text_log, message):
    text_log.insert(tk.END, message + "\n")
    text_log.see(tk.END)