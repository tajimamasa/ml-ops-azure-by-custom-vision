def check_extension(file_name: str) -> bool:
    """Check if the file extension is an image

    Args:
        file_name (str): The file name

    Returns:
        bool: True if the file extension is an image
    """
    file_extension = file_name.split(".")[-1].upper()
    image_extensions = ["PNG", "JPEG", "BMP", "GIF", "JPG"]
    return file_extension in image_extensions


def extract_camera_id(file_name: str) -> str:
    """Extract the camera ID from the file name

    Args:
        file_name (str): The file name

    Returns:
        str: The camera ID
    """
    camera_sentence = file_name.split("_")[0]
    if "camera" not in camera_sentence.lower():
        raise ValueError("The file name does not contain the camera ID")
    camera_id = camera_sentence.split("camera")[-1]
    return camera_id
