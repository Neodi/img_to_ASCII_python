import numpy as np
from numpy.typing import NDArray


def rgb_to_hsv(img_array: NDArray[np.uint8]) -> NDArray[np.float64]:

    if img_array.ndim != 3:
        raise ValueError(
            "img_array must be a 3-dimensional array (e.g., shape (height, width, 3))"
        )

    # Normalizar los valores
    normalized_img = img_array / 255
    print("Normalized img: ", normalized_img[0][0])

    # Máximo, mínimo y diferencia para cada píxel
    cmax = np.max(normalized_img, axis=2)
    cmin = np.min(normalized_img, axis=2)

    print("Cmax value [0][0]: ", cmax[0][0])
    print("Cmin value [0][0]: ", cmin[0][0])

    diff = cmax - cmin
    print("Diff value [0][0]: ", diff[0][0])
    print("Diff array: ", diff.shape)

    # Calcular hue
    hue_array = hue_calculation(
        diff_array=diff, cmax_array=cmax, cmin_array=cmin, rgb_array=normalized_img
    )
    print("hue_array.shape", hue_array.shape)
    print("hue_array[0][0]", hue_array[0][0])

    # Calcular saturation
    saturation_array = saturation_calculation(diff_array=diff, cmax_array=cmax)
    print("saturation_array.shape", saturation_array.shape)
    print("saturation_array.[0][0]", saturation_array[0][0])

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

    print("diff_array.shape", diff_array.shape)
    print("diff_array[mask_red].shape", diff_array[mask_red].shape)

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
