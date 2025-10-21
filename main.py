from converter import rgb_to_hsv, load_and_resize_image
from img_to_ascii_printer import (
    generate_bw_ascii_art,
    generate_color_ascii_art,
    generate_border_ascii_art,
    get_border_map_sobel,
    get_pixels_border,
    calculate_otsu_threshold,
    calculate_percentile_threshold,
    borders_and_colours,
)
import sys
import numpy as np
from constants import MAX_WIDTH
import colorama

colorama.init()

# Obtener la ruta de la imagen desde argumentos de línea de comandos
if len(sys.argv) > 1:
    img_path = sys.argv[1]
else:
    img_path = "doc_images/sira.jpg"  # Imagen por defecto

np_image = load_and_resize_image(img_path)

hsv_image_array = rgb_to_hsv(img_array=np_image)


print("-" * MAX_WIDTH)

asscii_image_bw = generate_bw_ascii_art(hsv_image_array)

print(asscii_image_bw)

print()

print("-" * MAX_WIDTH)

print()

asscii_image_color = generate_color_ascii_art(hsv_image_array)

print(asscii_image_color)
print(colorama.Style.RESET_ALL)

print()

print("-" * MAX_WIDTH)

print()

# Ascii art con detección de bordes

magnitude, direction, h_edges, v_edges = get_border_map_sobel(
    v_channel=hsv_image_array[:, :, 2]
)


border_threshold = calculate_otsu_threshold(magnitude)
# border_threshold = calculate_percentile_threshold(magnitude, percentile=90)
borders = get_pixels_border(
    magnitud=magnitude, direction=direction, threshold=border_threshold
)

asscii_image_borders = generate_border_ascii_art(border_pixels=borders)
print(asscii_image_borders)

print()

print("-" * MAX_WIDTH)

print()

# Color con bordes
ascii_image_borders_and_colours = borders_and_colours(
    hsv_image_array=hsv_image_array, border_percentile=95
)
print(ascii_image_borders_and_colours)
