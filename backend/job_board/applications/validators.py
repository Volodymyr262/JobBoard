# applications/validators.py
from django.core.exceptions import ValidationError

def validate_file_size(file, max_mb=5):
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"File too large. Max size is {max_mb} MB.")
