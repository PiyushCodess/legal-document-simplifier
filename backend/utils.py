import os
import re
from datetime import datetime


def validate_file_extension(filename, allowed_extensions):
    """
    Validate if file has an allowed extension
    
    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def sanitize_filename(filename):
    """
    Sanitize filename by removing special characters
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = filename.replace(' ', '_')
    return filename


def get_file_size(filepath):
    """
    Get file size in human-readable format
    
    Args:
        filepath (str): Path to file
        
    Returns:
        str: File size in human-readable format
    """
    try:
        size_bytes = os.path.getsize(filepath)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    except Exception as e:
        return "Unknown"


def format_timestamp(timestamp=None):
    """
    Format timestamp for display
    
    Args:
        timestamp (datetime, optional): Timestamp to format. Defaults to now.
        
    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_key_phrases(text, num_phrases=5):
    """
    Extract key phrases from text (simple implementation)
    
    Args:
        text (str): Text to analyze
        num_phrases (int): Number of phrases to extract
        
    Returns:
        list: List of key phrases
    """
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences[:num_phrases]


def count_words(text):
    """
    Count words in text
    
    Args:
        text (str): Text to analyze
        
    Returns:
        int: Word count
    """
    return len(text.split())


def estimate_reading_time(text, words_per_minute=200):
    """
    Estimate reading time for text
    
    Args:
        text (str): Text to analyze
        words_per_minute (int): Average reading speed
        
    Returns:
        str: Estimated reading time
    """
    word_count = count_words(text)
    minutes = word_count / words_per_minute
    
    if minutes < 1:
        return "Less than 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes > 1 else ''}"
    else:
        hours = int(minutes / 60)
        remaining_minutes = int(minutes % 60)
        return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"


def clean_text(text):
    """
    Clean text by removing extra whitespace and special characters
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = text.strip()
    return text


def create_directory_if_not_exists(directory_path):
    """
    Create directory if it doesn't exist
    
    Args:
        directory_path (str): Path to directory
    """
    os.makedirs(directory_path, exist_ok=True)


def get_file_extension(filename):
    """
    Get file extension from filename
    
    Args:
        filename (str): Name of the file
        
    Returns:
        str: File extension (lowercase)
    """
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def format_file_info(filepath):
    """
    Get formatted information about a file
    
    Args:
        filepath (str): Path to file
        
    Returns:
        dict: File information
    """
    try:
        stat_info = os.stat(filepath)
        return {
            'size': get_file_size(filepath),
            'created': format_timestamp(datetime.fromtimestamp(stat_info.st_ctime)),
            'modified': format_timestamp(datetime.fromtimestamp(stat_info.st_mtime)),
            'extension': get_file_extension(filepath)
        }
    except Exception as e:
        return {
            'error': str(e)
        }