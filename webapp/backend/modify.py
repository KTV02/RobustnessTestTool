import pygame
import numpy as np

# Initialize pygame
pygame.init()

# Set the temporary display mode
display = pygame.display.set_mode((1, 1))

# Load the original image and flare overlays
image_path = 'Assets/website.png'
flare_path1 = 'Assets/untitled7.png'
flare_path2 = 'Assets/untitled8.png'
image = pygame.image.load(image_path)
flare1 = pygame.image.load(flare_path1)
flare2 = pygame.image.load(flare_path2)

# Resize the flare overlays to match the image dimensions
flare1 = pygame.transform.scale(flare1, image.get_size())
flare2 = pygame.transform.scale(flare2, (int(image.get_width() * 0.4), int(image.get_height() * 0.4)))

# Adjust the flare intensity by increasing the brightness of the flare images
flare_intensity = 3.0  # Increase the intensity for brighter flare

# Increase the brightness of the flare images
flare1_pixels = np.array(pygame.surfarray.pixels3d(flare1))
flare1_pixels = np.clip(flare1_pixels * flare_intensity, 0, 255).astype(np.uint8)
flare1 = pygame.surfarray.make_surface(flare1_pixels)
del flare1_pixels

flare2_pixels = np.array(pygame.surfarray.pixels3d(flare2))
flare2_pixels = np.clip(flare2_pixels * flare_intensity, 0, 255).astype(np.uint8)
flare2 = pygame.surfarray.make_surface(flare2_pixels)
del flare2_pixels

# Create a new surface to hold the modified image
modified_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)

# Blit the original image onto the new surface
modified_image.blit(image, (0, 0))

# Add the first lens flare effect to the new surface
modified_image.blit(flare1, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

# Add the second lens flare effect to the new surface
flare2_pos = (int(image.get_width() * 0.3), int(image.get_height() * 0.2))
modified_image.blit(flare2, flare2_pos, special_flags=pygame.BLEND_RGB_ADD)

# Save the modified image
output_path = 'output.png'
pygame.image.save(modified_image, output_path)