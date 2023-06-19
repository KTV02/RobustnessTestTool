import os
import concurrent.futures
import io
import numpy as np
import pygame
from skimage import util, filters, transform
from skimage.util import img_as_ubyte
import skimage.exposure as exposure
from skimage import img_as_float
from skimage.transform import resize
from skimage.io import imread
from PIL import Image, ImageDraw, ImageOps
import skimage.io as io
from skimage.filters import gaussian
from skimage.transform import rescale


class TransformationsHelper:
    def __init__(self, environment):
        self.environment = environment
        self.transformations_file = self.environment.get_transformation_file()
        self.assets = self.environment.get_assets()

    def get_available_transformations(self):
        with open(self.transformations_file, "r") as file:
            transformations = file.read().splitlines()
        return transformations

    def add_noise(self, image, factor):
        # Add noise to the image
        noisy_image = util.random_noise(image, mode='gaussian', var=factor)
        return noisy_image

    def adjust_imagecontrast(self, image, factor):
        # Adjust contrast of the image
        adjusted_image = exposure.adjust_gamma(image, gamma=1 / factor)
        return adjusted_image

    def adjust_imagebrightness(self, image, factor):
        # Adjust brightness of the image
        adjusted_image = exposure.adjust_gamma(image, gamma=factor)
        return adjusted_image

    def adjust_imagesharpness(self, image, factor):
        # Sharpen the image
        sharpened_image = filters.unsharp_mask(image, radius=1.0, amount=factor)
        return sharpened_image

    def add_smoke(self, image, factor):
        # Convert the image to a PIL image if it's a NumPy array
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Load smoke texture
        smoke_texture = Image.open("smoke-texture.jpg")

        # Resize the smoke texture to match the image size
        resized_smoke_texture = smoke_texture.resize(
            (image.width, image.height)
        )

        # Convert images to numpy arrays
        image_array = np.array(image)
        smoke_texture_array = np.array(resized_smoke_texture)

        # Generate random transparency values for the smoke
        smoke_mask = np.random.uniform(0.2, 0.5, (image.height, image.width))

        # Normalize the smoke mask to the range [0, 1]
        smoke_mask = (smoke_mask - np.min(smoke_mask)) / (np.max(smoke_mask) - np.min(smoke_mask))

        # Apply smoke texture with transparency to the image
        smoke_image_array = image_array.copy()
        alpha = factor  # Adjust the transparency level as desired

        for y in range(image.height):
            for x in range(image.width):
                smoke_image_array[y, x] = (
                                                  alpha * smoke_texture_array[y, x] +
                                                  (1 - alpha) * image_array[y, x]
                                          ) * smoke_mask[y, x] + image_array[y, x] * (1 - smoke_mask[y, x])

        # Convert the resulting array back to PIL image
        smoke_image = Image.fromarray(smoke_image_array.astype(np.uint8))

        return smoke_image

    def add_imageglare(self, image):
        # Load the glare pattern
        glare_pattern = imread('glare_pattern.jpg')

        # Resize the glare pattern to match the shape of the image
        resized_glare_pattern = resize(glare_pattern, image.shape[:2], mode='reflect')

        # Convert the image and resized glare pattern to float
        image = img_as_float(image)
        resized_glare_pattern = img_as_float(resized_glare_pattern)

        # Add the glare pattern to the image
        alpha = 0.5  # Adjust this value to control the intensity of the glare
        image_with_glare = image + alpha * resized_glare_pattern

        # Clip the values to the valid range [0, 1]
        image_with_glare = np.clip(image_with_glare, 0, 1)

        # Convert the image back to uint8
        image_with_glare = img_as_ubyte(image_with_glare)

        return image_with_glare

    def add_lens_flare(self, image):
        # Convert the numpy array to PIL Image
        image = Image.fromarray(image).convert("RGBA")

        # Create a blank canvas with the same dimensions as the image
        canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))

        # Create a white circle in the center of the canvas
        center_x = image.width // 2
        center_y = image.height // 2
        radius = min(image.width, image.height) // 4
        draw = ImageDraw.Draw(canvas)
        draw.ellipse([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
                     fill=(255, 255, 255, 255))

        # Apply the lens flare effect by blending the canvas with the image
        result = Image.alpha_composite(image, canvas)

        # Convert the PIL Image back to numpy array
        result = np.array(result)

        # Return the result as numpy array
        return result

    def add_custom_lens_flare(self, image_array, flare_intensity):
        # Convert the NumPy array to a PIL Image
        image_pil = Image.fromarray(image_array)

        # Initialize pygame
        pygame.init()

        # Set the temporary display mode
        display = pygame.display.set_mode((1, 1))

        # Create a surface from the PIL Image
        image_surface = pygame.image.fromstring(image_pil.tobytes(), image_pil.size, image_pil.mode)

        # Load the flare overlays
        flare_path1 = self.assets + 'untitled7.png'
        flare_path2 = self.assets + 'untitled8.png'
        flare1 = pygame.image.load(flare_path1)
        flare2 = pygame.image.load(flare_path2)

        # Resize the flare overlays to match the image dimensions
        flare1 = pygame.transform.scale(flare1, image_surface.get_size())
        flare2 = pygame.transform.scale(flare2,
                                        (int(image_surface.get_width() * 0.4), int(image_surface.get_height() * 0.4)))

        # Adjust the flare intensity by increasing the brightness of the flare images
        flare1_pixels = np.array(pygame.surfarray.pixels3d(flare1))
        flare1_pixels = np.clip(flare1_pixels * flare_intensity, 0, 255).astype(np.uint8)
        flare1 = pygame.surfarray.make_surface(flare1_pixels)
        del flare1_pixels

        flare2_pixels = np.array(pygame.surfarray.pixels3d(flare2))
        flare2_pixels = np.clip(flare2_pixels * flare_intensity, 0, 255).astype(np.uint8)
        flare2 = pygame.surfarray.make_surface(flare2_pixels)
        del flare2_pixels

        # Create a new surface to hold the modified image
        modified_image = pygame.Surface(image_surface.get_size(), pygame.SRCALPHA)

        # Blit the original image onto the new surface
        modified_image.blit(image_surface, (0, 0))

        # Add the first lens flare effect to the new surface
        modified_image.blit(flare1, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Add the second lens flare effect to the new surface
        flare2_pos = (int(image_surface.get_width() * 0.3), int(image_surface.get_height() * 0.2))
        modified_image.blit(flare2, flare2_pos, special_flags=pygame.BLEND_RGB_ADD)

        # Convert the modified image to a numpy array and transpose it
        modified_image_array = np.transpose(pygame.surfarray.array3d(modified_image), axes=(1, 0, 2))

        return modified_image_array

    def lower_resolution(self, image, factor):
        # Convert the image to a PIL image if it's a NumPy array
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Calculate the new dimensions based on the resolution factor
        width, height = image.size
        new_width = int(width / factor)
        new_height = int(height / factor)

        # Resize the image to the lower resolution
        resized_image = image.resize((new_width, new_height), resample=Image.BILINEAR)

        # Convert the resized image back to a NumPy array
        resized_image_array = np.array(resized_image)

        return resized_image_array

    def apply_transformations(self, image_path, transformations, output):
        print(output)
        if not os.path.exists(output):
            os.makedirs(output)

        # Load the image if `image` parameter is a path
        if isinstance(image_path, str):
            print("path:" + image_path)
            image = io.imread(image_path)
        else:
            image = None

        transformed_images = []

        # Define valid value ranges for each transformation
        valid_ranges = {
            'noise': (0, 0.5),  # Example values, adjust as needed
            'contrast': (0.01, 5),  # Example values, adjust as needed
            'brightness': (0, 10),  # Example values, adjust as needed
            'sharpness': (0, 20),  # Example values, adjust as needed
            'smoke': (0, 1),  # Example values, adjust as needed
            'glare': (0, 10),  # Example values, adjust as needed
            'resolution': (1, 5)
        }

        def apply_transformation(transformation):
            nonlocal image
            transformation_label = transformation[0]
            accuracy = int(transformation[1])

            # Check if the transformation is valid
            if transformation_label not in valid_ranges:
                print("Unknown transformation:", transformation_label)
                return None

            transformed_images = []
            min_value, max_value = valid_ranges[transformation_label]
            intensity_values = []
            if accuracy == 1:
                intensity_values.append((min_value + max_value) / 2)
            else:
                intensity_values = np.linspace(min_value, max_value, accuracy).tolist()
            for mapped_intensity in intensity_values:
                print(mapped_intensity)
                # Map the intensity parameter from 1-10 to the valid value range

                transformed_image = image.copy()

                if transformation_label == 'noise':
                    transformed_image = self.add_noise(transformed_image, mapped_intensity)
                elif transformation_label == 'contrast':
                    transformed_image = self.adjust_imagecontrast(transformed_image, mapped_intensity)
                elif transformation_label == 'brightness':
                    transformed_image = self.adjust_imagebrightness(transformed_image, mapped_intensity)
                elif transformation_label == 'sharpness':
                    transformed_image = self.adjust_imagesharpness(transformed_image, mapped_intensity)
                elif transformation_label == 'smoke':
                    transformed_image = self.add_smoke(transformed_image, mapped_intensity)
                elif transformation_label == 'glare':
                    transformed_image = self.add_custom_lens_flare(transformed_image, mapped_intensity)
                elif transformation_label == 'resolution':
                    transformed_image = self.lower_resolution(transformed_image, mapped_intensity)


                transformed_images.append(transformed_image)
                transformed_image_pil = Image.fromarray(img_as_ubyte(transformed_image))

                # Save the transformed image with a formatted filename
                image_name = os.path.basename(image_path)
                image_extension = os.path.splitext(image_path)[1]

                index = intensity_values.index(mapped_intensity)
                transformed_image_name = "{}-{}-{}-{}".format(
                    os.path.splitext(image_name)[0],
                    transformation_label,
                    index,
                    image_extension
                )
                transformed_image_path = os.path.join(output, transformed_image_name)

                transformed_image_pil.save(transformed_image_path)
            return transformed_images

        # Use concurrent.futures.ThreadPoolExecutor to parallelize the transformation application
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the transformation tasks to the executor
            transformation_results = executor.map(apply_transformation, transformations)

            # Collect the results
            for result in transformation_results:
                if result is not None:
                    transformed_images.extend(result)

        return transformed_images

#
# transformations_file = "path/to/transformations.txt"
# image_path = "Assets/website.png"
# output_path = "C:\\Users\\Lennart Kremp\\OneDrive\\Studium\\Bachelorarbeit\\RobustnessTestTool\\output"
# #transformations = ["noise","contrast","brightness","sharpness","smoke","glare"]
# transformations = [["glare",5]]
# helper = TransformationsHelper(transformations_file)
# helper.apply_transformations(image_path, transformations, output_path)
