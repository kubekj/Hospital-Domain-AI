import numpy as np
from PIL import Image, ImageEnhance
import os

def image_to_ascii(image_path, target_height=100, background_char='Z'):
    # Load the image and convert to grayscale
    try:
        img = Image.open(image_path).convert('L')  # Convert to grayscale
    except FileNotFoundError:
        print("Image not found in the script's directory.")
        return None, None

    # Resize the image to make it more manageable
    aspect_ratio = img.width / img.height
    new_height = target_height
    new_width = int(int(new_height / aspect_ratio)*0.8)
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Convert image to numpy array
    data = np.array(img)
    min_val = data.min()  # This should be 0 if the background is completely black

    # ASCII characters from E to Y
    ascii_chars = [chr(x) for x in range(ord('E'), ord('Y') + 1)]
    num_chars = len(ascii_chars)

    # Map normalized data to ASCII characters
    ascii_image = []
    for row in data:
        new_row = []
        for value in row:
            if value == min_val:
                new_row.append(background_char)  # Use 'Z' for completely black (background)
            else:
                index = int((value / 255) * num_chars)
                new_row.append(ascii_chars[min(index, num_chars - 1)])
        ascii_image.append(new_row)

    return ascii_image, new_width

def write_lvl_file(level_data, width, level_name, file_path):
    lines = [
        '#domain',
        'hospital',
        '#levelname',
        level_name,
        '#colors'
    ]
    
    # Append initial level configuration
    lines.append('#initial')
    lines.append('+' * (width + 2))
    for row in level_data:
        lines.append('+' + ''.join(row) + '+')
    lines.append('+' * (width + 2))
    
    # Write to file
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f'Level written to {file_path}')

# Setup file paths
directory = os.getcwd()
current_directory = os.path.join(directory, 'grouplevel/images/')
image_filename = os.path.join(current_directory, 'photo_black.png')
level_name = os.path.basename(image_filename).split('.')[0]
lvl_filename = os.path.join(current_directory, f'{level_name}.lvl')

# Process the image and generate the level
ascii_data, ascii_width = image_to_ascii(image_filename, target_height=40, background_char='Z')  # Adjust width as needed
if ascii_data is not None and ascii_width is not None:
    write_lvl_file(ascii_data, ascii_width, level_name, lvl_filename)


# import numpy as np
# from PIL import Image
# import os
# directory = os.getcwd()
# current_directory = os.path.join(directory, 'grouplevel/')

# def closest_color(rgb, color_options):
#     # Find the closest color by Euclidean distance
#     r, g, b = rgb
#     color_diffs = []
#     for color in color_options:
#         cr, cg, cb = color
#         color_diff = (r - cr)**2 + (g - cg)**2 + (b - cb)**2
#         color_diffs.append((color_diff, color_options[color]))
#     return min(color_diffs)[1]

# def process_image_to_level_data(image_path, color_mappings):
#     # Load the image
#     try:
#         img = Image.open(image_path).convert('RGB')
#     except FileNotFoundError:
#         print("Image not found in the script's directory.")
#         return None

#     # Convert image to a numpy array
#     data = np.array(img)
#     height, width, _ = data.shape
#     level_data = []

#     # Process each pixel to the closest color/letter
#     for row in data:
#         level_row = ''.join(closest_color(tuple(pixel), color_mappings) for pixel in row)
#         level_data.append(level_row)
    
#     return level_data, width

# def write_lvl_file(level_data, width, color_groups, level_name, file_path):
#     lines = [
#         '#domain',
#         'hospital',
#         f'#levelname',
#         level_name,
#         '#colors'
#     ]
    
#     # Append color definitions
#     for color, details in color_groups.items():
#         line = f'{color.lower()}: {details["index"]}, ' + ', '.join(details["letters"])
#         lines.append(line)
    
#     # Append initial level configuration
#     lines.append('#initial')
#     lines.append('+' * (width + 2))
#     for row in level_data:
#         lines.append('+' + row + '+')
#     lines.append('+' * (width + 2))
    
#     # Write to file
#     with open(file_path, 'w') as f:
#         f.write('\n'.join(lines))
#     print(f'Level written to {file_path}')

# # Define color groups and mappings
# color_mappings = {
#     (0, 0, 255): 'A',  # Blue
#     (255, 0, 0): 'B',  # Red
#     (0, 255, 255): 'C',  # Cyan
#     (128, 0, 128): 'D',  # Purple
#     (0, 255, 0): 'E',  # Green
#     (255, 165, 0): 'F',  # Orange
#     (255, 192, 203): 'G',  # Pink
#     (128, 128, 128): 'H',  # Grey
#     (173, 216, 230): 'I',  # Lightblue
#     (165, 42, 42): 'J',  # Brown
# }

# color_groups = {
#     'Green': {'index': 0, 'letters': ['A', 'C']},
#     'Brown': {'index': 1, 'letters': ['B', 'D']},
#     'Orange': {'index': 2, 'letters': ['E', 'F']},
#     'Pink': {'index': 3, 'letters': ['G']},
#     'Grey': {'index': 4, 'letters': ['H']},
#     'Lightblue': {'index': 5, 'letters': ['I']},
#     'Red': {'index': 6, 'letters': []},  # Example unused group
#     'Blue': {'index': 7, 'letters': []},  # Example unused group
# }

# # Use the current directory to find the photo.png
# image_filename = os.path.join(current_directory, 'photo.png')
# level_name = os.path.basename(image_filename).split('.')[0]
# lvl_filename = os.path.join(current_directory, f'{level_name}.lvl')

# #Process the image and generate the level
# level_data, level_width = process_image_to_level_data(image_filename, color_mappings)
# if level_data is not None:
#     write_lvl_file(level_data, level_width, color_groups, level_name, lvl_filename)