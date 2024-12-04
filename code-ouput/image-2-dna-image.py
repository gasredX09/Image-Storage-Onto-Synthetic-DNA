# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aLw7cJ4JW6RbcAMaZn6AfXNcj3gwracY
"""

import numpy as np
from PIL import Image
import random

# Define DNA nucleotides and codebook
DNA_CODEBOOK = ['AT', 'AC', 'AG', 'TA', 'TC', 'TG', 'CA', 'CT', 'GA', 'GT']
NUCLEOTIDE_PAIRS = {'00': 'AT', '01': 'CG', '10': 'GC', '11': 'TA'}

# Load and preprocess image
def load_image(image_path, size=(256, 256)):
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    image = image.resize(size, Image.LANCZOS)  # Resize to 256x256 with high-quality downsampling
    image_data = np.array(image)
    return image_data

# Quantize image data
def quantize_image(image_data, num_levels=4):
    image_min, image_max = image_data.min(), image_data.max()
    normalized_image = (image_data - image_min) / (image_max - image_min)
    quantized_image = (normalized_image * num_levels).astype(int)
    return quantized_image

# Map quantized values to DNA sequence
def quantized_to_dna(quantized_image):
    dna_sequence = ""
    for value in quantized_image.flatten():
        binary = "{:02b}".format(value & 3)  # Convert to 2-bit binary
        dna_pair = NUCLEOTIDE_PAIRS.get(binary, random.choice(DNA_CODEBOOK))
        dna_sequence += dna_pair
    return dna_sequence

# Save DNA sequence to FASTA file
def save_to_fasta(dna_sequence, output_file, description="Image DNA Sequence"):
    with open(output_file, 'w') as fasta_file:
        fasta_file.write(f">{description}\n")
        for i in range(0, len(dna_sequence), 60):  # Wrap to 60 chars per line
            fasta_file.write(dna_sequence[i:i+60] + "\n")

# Decode DNA sequence back to quantized image values
def dna_to_quantized(dna_sequence, image_shape):
    quantized_values = []
    for i in range(0, len(dna_sequence), 2):
        dna_pair = dna_sequence[i:i+2]
        # Reverse mapping: find key from value
        binary = [key for key, value in NUCLEOTIDE_PAIRS.items() if value == dna_pair]
        if binary:
            quantized_values.append(int(binary[0], 2))
        else:
            quantized_values.append(0)  # Default if not found
    return np.array(quantized_values).reshape(image_shape)

# Reconstruct image from quantized values
def reconstruct_image(quantized_image, original_min, original_max):
    # Scale back to original range
    normalized_image = quantized_image / quantized_image.max()
    reconstructed_image = (normalized_image * (original_max - original_min) + original_min).astype(np.uint8)
    return Image.fromarray(reconstructed_image)

# Encode image to DNA and save as FASTA
def encode_image_to_dna(image_path, fasta_path):
    image_data = load_image(image_path)
    quantized_image = quantize_image(image_data)
    dna_sequence = quantized_to_dna(quantized_image)
    save_to_fasta(dna_sequence, fasta_path)
    print(f"DNA sequence saved to {fasta_path}")
    return quantized_image.shape, image_data.min(), image_data.max()

# Decode DNA back to image and save as .jpg
def decode_dna_to_image(fasta_path, image_shape, original_min, original_max):
    with open(fasta_path, 'r') as fasta_file:
        dna_sequence = ''.join(line.strip() for line in fasta_file if not line.startswith('>'))
    quantized_image = dna_to_quantized(dna_sequence, image_shape)
    reconstructed_image = reconstruct_image(quantized_image, original_min, original_max)

    # Save the reconstructed image as a .jpg file
    reconstructed_image.save('reconstructed_image.jpg')
    print("Reconstructed image saved as reconstructed_image.jpg")

    return reconstructed_image

# Usage example
image_path = 'bbtm.jpg'
fasta_path = 'encoded_image.fasta'

# Encode image to DNA
image_shape, original_min, original_max = encode_image_to_dna(image_path, fasta_path)

# Decode DNA back to image
decoded_image = decode_dna_to_image(fasta_path, image_shape, original_min, original_max)
decoded_image.show()  # Display the reconstructed image