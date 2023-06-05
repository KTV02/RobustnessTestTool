import numpy as np
from PIL import Image

# Define the image size and glare intensity
image_size = (1024, 768)  # Adjust the size as desired
glare_intensity = 0.5  # Adjust the intensity of glare as desired

# Create the glare pattern image
glare_pattern = np.ones(image_size, dtype=np.uint8) * 255
glare_pattern = (1 - glare_intensity) * glare_pattern  # Adjust the intensity based on the glare intensity

# Convert the image to grayscale
glare_pattern = Image.fromarray(glare_pattern).convert("L")

# Save the glare pattern image
glare_pattern.save("glare_pattern.jpg")