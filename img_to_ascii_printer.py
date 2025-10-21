import numpy as np
from scipy import ndimage
import colorama
from constants import SMALL_ASCII_RAMP, MAX_WIDTH, STURATION_THRESHOLD
from PIL import Image


def generate_bw_ascii_art(hsv_image_array, ascii_ramp=SMALL_ASCII_RAMP):
    """
    Genera arte ASCII en blanco y negro a partir de una imagen HSV.

    Args:
        hsv_image_array: Array numpy con imagen en formato HSV
        ascii_ramp: String con caracteres ASCII ordenados por intensidad

    Returns:
        str: Imagen ASCII en blanco y negro
    """
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

    # Crear array de caracteres ASCII usando indexación vectorizada
    ascii_chars = np.array([ascii_ramp[i - 1] for i in v_indices.flatten()]).reshape(
        v_indices.shape
    )

    # Construir imagen usando list comprehension (más rápido que concatenación de strings)
    asscii_image = "\n".join("".join(row) for row in ascii_chars)

    return asscii_image


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


def generate_color_ascii_art(
    hsv_image_array,
    ascii_ramp=SMALL_ASCII_RAMP,
    saturation_threshold=STURATION_THRESHOLD,
):
    """
    Genera arte ASCII en color basado en una imagen HSV.

    Args:
        hsv_image_array: Array NumPy con valores HSV
        ascii_ramp: Rampa de caracteres ASCII a usar
        saturation_threshold: Umbral de saturación para considerar píxeles como blancos/grises

    Returns:
        str: Imagen ASCII coloreada
    """

    hue_channel = hsv_image_array[:, :, 0]

    # [330, 30, 90, 150, 210, 270, 330]
    # Usamos estos valores como los límites de los rangos de hue:
    hue_bins = np.array([0, 30, 90, 150, 210, 270, 330])
    hue_indices = np.digitize(hue_channel, hue_bins)

    saturation_channel = hsv_image_array[:, :, 1]

    # Marca como True los valores de saturación inferiores a un valor específico
    # Para considerar como blancos o grises
    low_saturation_mask = saturation_channel < saturation_threshold

    # Obtener v_channel y normalizarlo igual que en generate_bw_ascii_art
    v_channel = hsv_image_array[:, :, 2]

    # Normalizar el canal V entre 0 y 1
    v_min, v_max = v_channel.min(), v_channel.max()
    if v_max > v_min:
        v_channel = (v_channel - v_min) / (v_max - v_min)
    else:
        v_channel = np.zeros_like(v_channel)

    # Crear bins correctamente para que los índices estén en el rango [0, len(ascii_ramp)-1]
    bins = np.linspace(0, 1, len(ascii_ramp) + 1)
    v_indices = np.digitize(v_channel, bins) - 1

    # Asegurar que los índices están dentro del rango válido
    v_indices = np.clip(v_indices, 0, len(ascii_ramp) - 1)

    # Crear array de caracteres ASCII
    ascii_chars = np.array(
        [
            ascii_ramp[v_indices[i, j]]
            for i in range(v_indices.shape[0])
            for j in range(v_indices.shape[1])
        ]
    ).reshape(v_indices.shape)

    # Crear array de códigos de color usando vectorización
    color_codes = np.vectorize(get_color_code)(hue_indices, low_saturation_mask)

    # Construir imagen usando list comprehension (más rápido que concatenación de strings)
    asscii_image = "\n".join(
        "".join(
            f"{color_codes[i, j]}{ascii_chars[i, j]}"
            for j in range(ascii_chars.shape[1])
        )
        for i in range(ascii_chars.shape[0])
    )

    return asscii_image


def generate_border_ascii_art(border_pixels: np.ndarray):
    """
    Genera arte ASCII basado en los píxeles de borde.

    Args:
        border_pixels: Array NumPy con caracteres ASCII que representan bordes

    Returns:
        str: Imagen ASCII de bordes
    """
    asscii_image = "\n".join("".join(row) for row in border_pixels)

    return asscii_image


def get_border_map_sobel(v_channel: np.ndarray):

    KERNEL_HORIZONTAL = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    KERNEL_VERTICAL = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

    horizontal_edges = ndimage.convolve(v_channel, KERNEL_HORIZONTAL)
    vertical_edges = ndimage.convolve(v_channel, KERNEL_VERTICAL)

    # Magnitud de los bordes (el gradiente de cada píxel)
    magnitud = np.sqrt(horizontal_edges**2 + vertical_edges**2)

    # Ángulo de los bordes
    direction = np.arctan2(vertical_edges, horizontal_edges) * 180 / np.pi
    direction = (direction + 360) % 360  # Convertir a grados positivos

    return magnitud, direction, horizontal_edges, vertical_edges


def get_pixels_border(
    magnitud: np.ndarray, direction: np.ndarray, threshold: float = 30.0
):
    """
    Identifica los píxeles que son bordes basándose en un umbral de magnitud.

    Args:
        magnitud: Array NumPy con la magnitud del gradiente
        direction: Array NumPy con la dirección del gradiente
        threshold: Umbral para considerar un píxel como borde

    Returns:
        list: Lista de diccionarios con información de los píxeles de borde
    """
    border_pixels = np.full(magnitud.shape, " ", dtype="U1")
    rows, cols = magnitud.shape

    for y in range(rows):
        for x in range(cols):
            if magnitud[y, x] > threshold:
                border_pixels[y, x] = get_cardinal_direction(direction[y, x])

    return border_pixels


def get_cardinal_direction(angle: float) -> str:
    """
    Convierte un ángulo en grados a un carácter ASCII que apunta en esa dirección.

    Args:
        angle: Ángulo en grados (0-360)

    Returns:
        str: Carácter ASCII que representa la dirección del gradiente
    """
    # Normalizar ángulo y mapear a 8 direcciones
    angle = angle % 360
    direction_index = int((angle + 22.5) / 45) % 8
    # directions = ["|", "/", "-", "\\", "|", "/", "-", "\\"]
    directions = ["-", "/", "|", "\\", "-", "/", "|", "\\"]
    return directions[direction_index]


def calculate_percentile_threshold(
    magnitude: np.ndarray, percentile: float = 90
) -> float:
    """
    Calcula el threshold basándose en un percentil de la magnitud.

    Args:
        magnitude: Array con la magnitud del gradiente
        percentile: Percentil a usar (por defecto 90 = solo el 10% más fuerte)

    Returns:
        float: Threshold calculado
    """
    return np.percentile(magnitude, percentile)


def calculate_otsu_threshold(magnitude: np.ndarray) -> float:
    """
    Calcula el threshold óptimo usando el método de Otsu.

    Args:
        magnitude: Array con la magnitud del gradiente

    Returns:
        float: Threshold óptimo calculado
    """
    # Normalizar magnitud a rango 0-255 para el cálculo
    mag_normalized = (
        (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min()) * 255
    ).astype(np.uint8)

    # Calcular histograma
    hist, bin_edges = np.histogram(mag_normalized, bins=256, range=(0, 256))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Calcular probabilidades
    weight = hist / hist.sum()

    # Calcular media acumulada
    mean = np.cumsum(weight * bin_centers)

    # Varianza entre clases
    variance_between = np.zeros(256)
    for t in range(256):
        w0 = weight[:t].sum()
        w1 = weight[t:].sum()

        if w0 == 0 or w1 == 0:
            continue

        m0 = mean[t - 1] / w0 if w0 > 0 and t > 0 else 0
        m1 = (mean[-1] - mean[t - 1]) / w1 if w1 > 0 and t > 0 else 0

        variance_between[t] = w0 * w1 * (m0 - m1) ** 2

    # Encontrar threshold óptimo
    optimal_threshold = np.argmax(variance_between)

    # Desnormalizar al rango original
    threshold = (optimal_threshold / 255.0) * (
        magnitude.max() - magnitude.min()
    ) + magnitude.min()

    return threshold


def borders_and_colours(
    hsv_image_array,
    ascii_ramp=SMALL_ASCII_RAMP,
    saturation_threshold=STURATION_THRESHOLD,
    border_percentile=90.0,
):
    """
    Genera arte ASCII en color con detección de bordes.

    Args:
        hsv_image_array: Array NumPy con valores HSV
        ascii_ramp: Rampa de caracteres ASCII a usar
        saturation_threshold: Umbral de saturación para considerar píxeles como blancos/grises
        border_percentile: Percentil para el threshold de detección de bordes

    Returns:
        str: Imagen ASCII coloreada con bordes
    """
    hue_channel = hsv_image_array[:, :, 0]
    hue_bins = np.array([0, 30, 90, 150, 210, 270, 330])
    hue_indices = np.digitize(hue_channel, hue_bins)

    saturation_channel = hsv_image_array[:, :, 1]
    low_saturation_mask = saturation_channel < saturation_threshold

    # Obtener v_channel
    v_channel = hsv_image_array[:, :, 2]

    # Detectar bordes usando Sobel
    magnitud, direction, _, _ = get_border_map_sobel(v_channel)
    border_threshold = calculate_percentile_threshold(magnitud, border_percentile)
    border_pixels = get_pixels_border(magnitud, direction, border_threshold)

    # Obtener caracteres ASCII normales (reutilizando lógica de generate_color_ascii_art)
    v_min, v_max = v_channel.min(), v_channel.max()
    if v_max > v_min:
        v_channel_normalized = (v_channel - v_min) / (v_max - v_min)
    else:
        v_channel_normalized = np.zeros_like(v_channel)

    bins = np.linspace(0, 1, len(ascii_ramp) + 1)
    v_indices = np.digitize(v_channel_normalized, bins) - 1
    v_indices = np.clip(v_indices, 0, len(ascii_ramp) - 1)

    ascii_chars_normal = np.array(
        [
            ascii_ramp[v_indices[i, j]]
            for i in range(v_indices.shape[0])
            for j in range(v_indices.shape[1])
        ]
    ).reshape(v_indices.shape)

    # Combinar bordes con caracteres ASCII normales
    ascii_chars = np.where(border_pixels != " ", border_pixels, ascii_chars_normal)

    # Aplicar colores
    color_codes = np.vectorize(get_color_code)(hue_indices, low_saturation_mask)

    asscii_image = "\n".join(
        "".join(
            f"{color_codes[i, j]}{ascii_chars[i, j]}"
            for j in range(ascii_chars.shape[1])
        )
        for i in range(ascii_chars.shape[0])
    )

    return asscii_image
