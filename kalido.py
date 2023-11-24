from PIL import Image, ImageDraw

# Returns the transposed image based on the 'type' parameter
# 'fliplr'   -> flip left to right
# 'fliptb'   -> flip top to bottom
# 'fliptblr' -> flip top to bottom, then left to right
def mirror_image(image, type):
    if type == 'fliplr':
        return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif type == 'fliptb':
        return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    elif type == 'fliptblr':
        return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).transpose(Image.Transpose.FLIP_LEFT_RIGHT)

# Arranges 4 copies of the original image about the origin (2*w, 2*h) such 
# that they are mirrored about both the vertical and horizontal axes, and 
# returns the new image.
def four_pieces(image):
    w, h = image.size
    pic = Image.new('RGB', (2 * w, 2 * h))                           
    pic.paste(image, (0, 0, w, h))                                   # Paste top left copy
    pic.paste(mirror_image(image, 'fliplr'), (w, 0, w * 2, h))       # Paste top right copy 
    pic.paste(mirror_image(image, 'fliptb'), (0, h, w, h * 2))       # Paste bottom left copy
    pic.paste(mirror_image(image, 'fliptblr'), (w, h, w * 2, h * 2)) # Paste bottom right copy

    return pic

# This function takes a square image and splits it diagonally from the top left
# corner to the bottom right corner. It then reflects the chosen triangle 
# (top or bottom based on the 'type' parameter) across the diagonal, creating 
# a mirror image across the diagonal of the square.
def mirror_across_triangle(image, type='bottom'):
    w, h = image.size 

    mask = Image.new('1', (w, h))
    white = Image.new('RGB', (w, h), (255, 255, 255))
    mask_draw = ImageDraw.Draw(mask)

    # Draw a triangle onto the mask based on the 'type' parameter 
    if type == 'bottom':
        mask_draw.polygon([(0, 0), (0, h), (w, h)], fill=255)
    else:
        mask_draw.polygon([(0, 0), (w, 0), (w, h)], fill=255)

    triangle_image = Image.composite(image, white, mask)
    triangle_image.putalpha(mask)

    # Compose the final mirrored image from the triangle image by rotating it 90 degrees and pasting onto itself
    final_image = Image.alpha_composite(triangle_image, mirror_image(triangle_image, 'fliplr').transpose(Image.Transpose.ROTATE_90))
    final = four_pieces(final_image)

    return final


# Takes a square image and adds mirrored images to the sides, making it rectangular
def add_sides(square_image):
    w, h = square_image.size
    side = square_image.crop((0, 0, w // 2, h))                                          # Get half of the square image
    pic = Image.new('RGB', (w + 2 * side.width, h))                                      # Create a new image that we will paste onto
    pic.paste(mirror_image(side, 'fliplr'), (0, 0, side.width, side.height))             # Paste one mirrored half onto the left side of the new image
    pic.paste(square_image, (0 + side.width, 0, side.width + square_image.width, h))     # Paste the original square image into the middle of the new image
    pic.paste(side, (side.width + w, 0, w + 2 * side.width, h))                          # Paste the second mirrored half onto the right side of the new image

    return pic

# Converts an odd number to an even number.
# If the input number is already even, it's simply returned
def to_even(num):
    if (num % 2) == 0:
        return num
    else:
        return num - 1

# Crops a square image out of the center of the input image
def crop_image(image):
    w, h = image.size   

    # Ensure the dimensions are even so that dividing by 2 
    # doesn't cause rounding issues
    w = to_even(w)                                     
    h = to_even(h) 
    image = image.crop((0, 0, w, h))
    w, h = image.size
                            
    if w > h:                                          # If the width > height, we must make crop the image based on the limiting height value
        offset = (w - h) // 2
        image = image.crop((offset, 0, w - offset, h)) # To center, subtract height from width, then divide result by two, and start from that x offset
    else:                                              # Otherwise, we crop based on the width
        offset = (h - w) // 2
        image = image.crop((0, offset, w, h - offset)) # To center, subtract width from height, then divide result by two, and start from that y offset

    return image

# Creates a kaleidoscopic image and saves it to the output folder
def create_and_save_image(name):
    path = './static/images/' + name                              # Create path to the uploaded image
    image = Image.open(path)                                      # Open the image for editing
    image = crop_image(image)                                     # Crop the image
    square_image = mirror_across_triangle(image)
    final_image = add_sides(square_image)
    final_image.save('./static/output/' + name)                   # Save the final image to the output folder
