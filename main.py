from PIL import Image
from converter import rgb_to_hsv
import numpy as np

BIG_ASCII_RAMP = (
    r"""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """
)
SMALL_ASCII_RAMP = " .:-=+*#%@"

img = Image.open("sira.jpg")


def resize_image_maintain_aspect(img, max_width):
    """
    Resize image to a maximum width while maintaining aspect ratio.
    """
    width, height = img.size
    aspect_ratio = height / width
    new_width = min(width, max_width)
    new_height = int(new_width * aspect_ratio)
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


img = resize_image_maintain_aspect(img, 100)
width, height = img.size
img = img.resize((width, height // 2), Image.Resampling.LANCZOS)


np_image = np.asarray(img)


hsv_image_array = rgb_to_hsv(img_array=np_image)


print("-" * 50)

print("Grayscale ASCII ART")

ascii_ramp = SMALL_ASCII_RAMP

# Pintar imagen ASCII blanco y negro
v_channel = hsv_image_array[:, :, 2]  # .astype(float)  # Valor channel for brightness

# Aumentar constraste
v_min, v_max = v_channel.min(), v_channel.max()
if v_max > v_min:
    v_channel = (v_channel - v_min) / (v_max - v_min)
else:
    v_channel = np.zeros_like(v_channel)


bins = np.linspace(0, 1, len(ascii_ramp))
v_indices = np.digitize(v_channel, bins)

print(v_indices.shape)

asscii_image = ""
for row in v_indices:
    for index in row:
        asscii_image += ascii_ramp[index - 1]
    asscii_image += "\n"

print(asscii_image)
