from PIL import Image
from converter import rgb_to_hsv
import numpy as np


img = Image.open("jull_img.jpg")

print("PIL: ", img.format)
print("PIL: ", img.size)
print("PIL: ", img.mode)
print()
print("-" * 50)
print()

np_image = np.asarray(img)

print("NP: ", "alto, ancho, canales")
print("NP: ", np_image.shape)

print()

print("NP: ", "pixel ejemplo [0][0]")
print("NP: ", np_image[0][0])

print()

print("-" * 50)

print()

print("Converter: ")
hsv_image_array = rgb_to_hsv(img_array=np_image)

print()

print("-" * 50)
