import os

import numpy as np
import skimage.io as io
from skimage import util, filters, transform
from skimage.util import img_as_ubyte
from skimage.filters import gaussian
from skimage.transform import rescale
from PIL import Image
import skimage.exposure as exposure
from skimage import img_as_float
from skimage.transform import resize
from skimage.io import imread


class TransformationsHelper:
    def __init__(self, transformations_file):
        self.transformations_file = transformations_file

    def get_available_transformations(self):
        with open(self.transformations_file, "r") as file:
            transformations = file.read().splitlines()
        return transformations

    def add_noise(self, image):
        # Add noise to the image
        noisy_image = util.random_noise(image, mode='gaussian',var=0.1)
        return noisy_image

    def adjust_imagecontrast(self, image, factor):
        # Adjust contrast of the image
        adjusted_image = exposure.adjust_gamma(image, gamma=1/factor)
        return adjusted_image

    def adjust_imagebrightness(self, image, factor):
        # Adjust brightness of the image
        adjusted_image = exposure.adjust_gamma(image, gamma=factor)
        return adjusted_image

    def adjust_imagesharpness(self, image):
        # Sharpen the image
        sharpened_image = filters.unsharp_mask(image, radius=1.0, amount=1.5)
        return sharpened_image


    def add_smoke(self, image):
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
        alpha = 0.8  # Adjust the transparency level as desired

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

    def apply_transformations(self, image_path, transformations, output):
        if not os.path.exists(output):
            os.makedirs(output)

        # Load the image if `image` parameter is a path
        if isinstance(image_path, str):
            image = io.imread(image_path)

        transformed_images = []

        for transformation in transformations:
            transformed_image = image.copy()

            if transformation == 'noise':
                transformed_image = self.add_noise(transformed_image)
            elif transformation == 'contrast':
                transformed_image = self.adjust_imagecontrast(transformed_image,1.5)
            elif transformation == 'brightness':
                transformed_image = self.adjust_imagebrightness(transformed_image,3)
            elif transformation == 'sharpness':
                transformed_image = self.adjust_imagesharpness(transformed_image)
            elif transformation == 'smoke':
                transformed_image = self.add_smoke(transformed_image)
            elif transformation == 'glare':
                transformed_image = self.add_imageglare(transformed_image)

            transformed_images.append(transformed_image)
            transformed_image_pil = Image.fromarray(img_as_ubyte(transformed_image))

            # Save the transformed image with a formatted filename
            image_name = os.path.basename(image_path)
            image_extension = os.path.splitext(image_path)[1]

            transformed_image_name = "{}-{}{}".format(os.path.splitext(image_name)[0], transformation, image_extension)
            transformed_image_path = os.path.join(output, transformed_image_name)

            transformed_image_pil.save(transformed_image_path)  
        return transformed_images

# Usage example:
helper = TransformationsHelper(transformations_file='transformations.txt')
helper.apply_transformations("C:\\Users\\Lennart Kremp\\Downloads\\website.jpg", ["noise"], "C:\\Users\\Lennart Kremp\\OneDrive\\Studium\\Bachelorarbeit\\RobustnessTestTool\\output")

transformations_file = "path/to/transformations.txt"
image_path = "C:\\Users\\Lennart Kremp\\Downloads\\website.jpg"
output_path = "C:\\Users\\Lennart Kremp\\OneDrive\\Studium\\Bachelorarbeit\\RobustnessTestTool\\output"
transformations = ["noise","contrast","brightness","sharpness","smoke","glare"]

helper = TransformationsHelper(transformations_file)
helper.apply_transformations(image_path, transformations, output_path)
