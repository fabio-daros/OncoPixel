import re
from django import template

register = template.Library()


@register.filter
def extract_image_id(message):
    """
    Extract the number after '#' in messages such as:
    'Image #123 analyzed successfully!' ou
    'Low Confidence in Image #456. No Diagnosis Returned. ' To use as a reference ID.
    """
    message_str = str(message)  # transforma em string
    match = re.search(r'#(\d+)', message_str)
    if match:
        return match.group(1)
    return ''
