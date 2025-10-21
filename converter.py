import numpy as np
from numpy.typing import NDArray
from PIL import Image
from constants import MAX_WIDTH


def load_and_resize_image(image_path, max_width=MAX_WIDTH):
    """
    Load an image from the given path and resize it while maintaining aspect ratio,
    then adjust the height to half for better ASCII representation.
    """
    img = Image.open(image_path)

    def resize_image_maintain_aspect(img, max_width):
        """
        Resize image to a maximum width while maintaining aspect ratio.
        """
        width, height = img.size
        aspect_ratio = height / width
        new_width = min(width, max_width)
        new_height = int(new_width * aspect_ratio)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    img = resize_image_maintain_aspect(img, max_width)
    width, height = img.size
    img = img.resize((width, height // 2), Image.Resampling.LANCZOS)
    return np.asarray(img)


def rgb_to_hsv(img_array: NDArray[np.uint8]) -> NDArray[np.float64]:

    if img_array.ndim != 3:
        raise ValueError(
            "img_array must be a 3-dimensional array (e.g., shape (height, width, 3))"
        )

    # Normalizar los valores
    normalized_img = img_array / 255

    # Máximo, mínimo y diferencia para cada píxel
    cmax = np.max(normalized_img, axis=2)
    cmin = np.min(normalized_img, axis=2)

    diff = cmax - cmin

    # Calcular hue
    hue_array = hue_calculation(
        diff_array=diff, cmax_array=cmax, cmin_array=cmin, rgb_array=normalized_img
    )

    # Calcular saturation
    saturation_array = saturation_calculation(diff_array=diff, cmax_array=cmax)

    # Calcular Value
    value_array = cmax * 100

    assert hue_array.size == saturation_array.size
    assert hue_array.size == value_array.size

    # Reconstruir la imagen array (hue, saturation, value)
    hsv_image_array = np.stack([hue_array, saturation_array, value_array], axis=2)
    return hsv_image_array


def hue_calculation(
    diff_array: NDArray[np.uint8],
    cmax_array: NDArray[np.uint8],
    cmin_array: NDArray[np.uint8],
    rgb_array: NDArray[np.uint8],
) -> NDArray[np.uint8]:

    hue_array = np.zeros(diff_array.shape, dtype=np.float64)

    # mascara de 0s
    mask_zeros = diff_array == 0
    hue_array[mask_zeros] = 0

    # mascaras para R G B
    mask_red = (diff_array != 0) & (cmax_array == rgb_array[:, :, 0])
    mask_green = (diff_array != 0) & (cmax_array == rgb_array[:, :, 1])
    mask_blue = (diff_array != 0) & (cmax_array == rgb_array[:, :, 2])

    # aplicar mascaras y calcular
    hue_array[mask_red] = (
        60
        * ((rgb_array[:, :, 1] - rgb_array[:, :, 2])[mask_red] / diff_array[mask_red])
        + 360
    ) % 360
    hue_array[mask_green] = (
        60
        * (
            (rgb_array[:, :, 2] - rgb_array[:, :, 0])[mask_green]
            / diff_array[mask_green]
        )
        + 120
    ) % 360
    hue_array[mask_blue] = (
        60
        * ((rgb_array[:, :, 0] - rgb_array[:, :, 1])[mask_blue] / diff_array[mask_blue])
        + 240
    ) % 360

    return hue_array


def saturation_calculation(
    cmax_array: NDArray[np.uint8], diff_array: NDArray[np.uint8]
) -> NDArray[np.uint8]:

    saturation_array = np.zeros(diff_array.shape, np.float64)

    # Cmax == 0 -> saturacion = 0
    mask_zero = cmax_array == 0
    saturation_array[mask_zero] = 0

    # Cmax != 0 -> saturacion = (diff/cmax)*100
    mask_no_zero = cmax_array != 0
    saturation_array[mask_no_zero] = ((diff_array / cmax_array) * 100)[mask_no_zero]

    return saturation_array
