from PIL import Image
from converter import rgb_to_hsv
import numpy as np
import cv2


img = Image.open("jull_img.jpg")
np_image = np.asarray(img)

# Your HSV result
hsv_image_array = rgb_to_hsv(img_array=np_image)

# OpenCV reference (convert to float for comparison)
hsv_opencv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV).astype(np.float64)

# Scale your HSV to match OpenCV ranges
hsv_yours_scaled = hsv_image_array.copy()
hsv_yours_scaled[:, :, 0] /= 2  # Hue: 0-360 -> 0-180
hsv_yours_scaled[:, :, 1] *= 2.55  # Sat: 0-100 -> 0-255
hsv_yours_scaled[:, :, 2] *= 2.55  # Val: 0-100 -> 0-255

# Round to nearest int for comparison (OpenCV uses uint8)
hsv_yours_scaled = np.round(hsv_yours_scaled).astype(np.uint8)
hsv_opencv = np.round(hsv_opencv).astype(np.uint8)

# Check a few sample pixels (e.g., top-left corner)
print("Sample pixel [0,0]:")
print("Yours:", hsv_yours_scaled[0, 0])
print("OpenCV:", hsv_opencv[0, 0])
print(
    "Match?", np.allclose(hsv_yours_scaled[0, 0], hsv_opencv[0, 0], atol=1)
)  # Allow small tolerance

# Full image comparison (check if arrays are close)
matches = np.allclose(
    hsv_yours_scaled, hsv_opencv, atol=5
)  # Tolerance for floating-point differences
print("Full image match?", matches)

if not matches:
    diff = np.abs(hsv_yours_scaled - hsv_opencv)
    print("Max difference:", np.max(diff))
    print("Mean difference:", np.mean(diff))
