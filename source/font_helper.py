from fontTools.ttLib import TTFont
import os


def find_font_path(font_name, font_dir="C:\\Windows\\Fonts"):
    """
    Searches for the path of the specified font in the given directory.

    Args:
        font_name (str): The name of the font to search for.
        font_dir (str): The directory to search in (default is Windows Fonts directory).

    Returns:
        str: The full path to the font if found, otherwise None.
    """
    for root, _, files in os.walk(font_dir):
        for file in files:
            if file.lower().endswith(('.ttf', '.otf')):  # Common font file extensions
                try:
                    font_path = os.path.join(root, file)
                    font = TTFont(font_path)
                    name_records = font.get('name').names
                    for record in name_records:
                        try:
                            # Decode the font name based on the platform ID and encoding ID
                            platform_id = record.platformID
                            encoding_id = record.platEncID
                            name_id = record.nameID
                            if platform_id == 3 and encoding_id == 1:  # Windows Unicode
                                font_full_name = record.string.decode('utf-16-be')
                            elif platform_id == 1 and encoding_id == 0:  # Macintosh Roman
                                font_full_name = record.string.decode('mac_roman')
                            else:
                                font_full_name = record.string.decode('utf-8')  # Fallback to UTF-8

                            if font_name.lower() in font_full_name.lower():
                                return font_path
                        except UnicodeDecodeError:
                            try:
                                font_full_name = record.string.decode('latin1')
                                if font_name.lower() in font_full_name.lower():
                                    return font_path
                            except Exception as e:
                                print(f"Error decoding font name from {file}: {e}")
                except Exception as e:
                    print(f"Error reading font file {file}: {e}")
    return None
