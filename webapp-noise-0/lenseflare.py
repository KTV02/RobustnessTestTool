from PIL import Image, ImageDraw, ImageOps

def add_lens_flare(image_path,output):
    # Load the image
    image = Image.open(image_path).convert("RGBA")

    # Create a blank canvas with the same dimensions as the image
    canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))

    # Create a white circle in the center of the canvas
    center_x = image.width // 2
    center_y = image.height // 2
    radius = min(image.width, image.height) // 4
    draw = ImageDraw.Draw(canvas)
    draw.ellipse([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], fill=(255, 255, 255, 255))

    # Apply the lens flare effect by blending the canvas with the image
    result = Image.alpha_composite(image, canvas)

    # Display the result
    result.save(output)

# Usage example:
add_lens_flare('website.png','output.png')
