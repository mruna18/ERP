import os

# def get_unique_filename(directory, base_filename):
#     name, ext = os.path.splitext(base_filename)
#     counter = 1
#     new_filename = base_filename

#     while os.path.exists(os.path.join(directory, new_filename)):
#         new_filename = f"{name}({counter}){ext}"
#         counter += 1

#     return new_filename


def get_unique_filepath(directory, filename):
    """
    Returns a unique file path by adding (1), (2), etc. if the file already exists.
    """
    filepath = os.path.join(directory, filename)
    file_root, file_ext = os.path.splitext(filepath)
    counter = 1

    while os.path.exists(filepath):
        filepath = f"{file_root} ({counter}){file_ext}"
        counter += 1

    return filepath