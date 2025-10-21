from converter import rgb_to_hsv, load_and_resize_image
import numpy as np
import colorama

colorama.init()

BIG_ASCII_RAMP = (
    r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """
)
SMALL_ASCII_RAMP = " .:-=+*#%@"

MAX_WIDTH = 200

np_image = load_and_resize_image("hue_clock.jpg", max_width=MAX_WIDTH)


hsv_image_array = rgb_to_hsv(img_array=np_image)


print("-" * MAX_WIDTH)

print("Grayscale ASCII ART")

ascii_ramp = SMALL_ASCII_RAMP

# Pintar imagen ASCII blanco y negro
v_channel = hsv_image_array[:, :, 2]

# Aumentar constraste
v_min, v_max = v_channel.min(), v_channel.max()
if v_max > v_min:
    v_channel = (v_channel - v_min) / (v_max - v_min)
else:
    v_channel = np.zeros_like(v_channel)


bins = np.linspace(0, 1, len(ascii_ramp))
v_indices = np.digitize(v_channel, bins)

print(f"Image dimensions {v_indices.shape}")

asscii_image = ""
for row in v_indices:
    for index in row:
        asscii_image += ascii_ramp[index - 1]
    asscii_image += "\n"

print(asscii_image)

print()

print("-" * MAX_WIDTH)

print("COLOUR ASCII ART")

hue_channel = hsv_image_array[:, :, 0]

print("Hue channel shape: ", hue_channel.shape)
print("Max hue value: ", hue_channel.max())
print("Min hue value: ", hue_channel.min())

# [330, 30, 90, 150, 210, 270, 330]
# Usamos estos valores como los límites de los rangos de hue:
hue_bins = np.array([0, 30, 90, 150, 210, 270, 330])
hue_indices = np.digitize(hue_channel, hue_bins)
# Count occurrences of each hue index (1 to 7)
unique, counts = np.unique(hue_indices, return_counts=True)
for idx, count in zip(unique, counts):
    print(f"Hue index {idx}: {count}")

saturation_channel = hsv_image_array[:, :, 1]
print("Saturation channel shape: ", saturation_channel.shape)
print("Max saturation value: ", saturation_channel.max())
print("Min saturation value: ", saturation_channel.min())

# Marca como True los valores de saturación inferiores a un valor específico
# Para considerar como blancos o grises
saturation_threshold = 5
low_saturation_mask = saturation_channel < saturation_threshold
print("Low saturation mask head:", low_saturation_mask[0][:10])


def get_color_code(hue_index: int, low_saturation_mask: bool):

    if low_saturation_mask:
        return colorama.Fore.WHITE

    if hue_index == 1 or hue_index == 7:  # Red
        return colorama.Fore.RED
    elif hue_index == 2:  # Yellow
        return colorama.Fore.YELLOW
    elif hue_index == 3:  # Green
        return colorama.Fore.GREEN
    elif hue_index == 4:  # Cyan
        return colorama.Fore.CYAN
    elif hue_index == 5:  # Blue
        return colorama.Fore.BLUE
    elif hue_index == 6:  # Magenta
        return colorama.Fore.MAGENTA

    return colorama.Fore.RESET


ascii_ramp = SMALL_ASCII_RAMP
# Pintar imagen
asscii_image = ""
for row_idx in range(hue_indices.shape[0]):
    for col_idx in range(hue_indices.shape[1]):

        hue_index = hue_indices[row_idx, col_idx]
        is_low_saturation = low_saturation_mask[row_idx, col_idx]
        color_code = get_color_code(hue_index, is_low_saturation)

        asscii_image += f"{color_code}{ascii_ramp[v_indices[row_idx, col_idx] - 1]}"

    asscii_image += "\n"
print(asscii_image)
print(colorama.Style.RESET_ALL)
