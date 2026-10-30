"""Parse pasted links, retaining order and removing duplicates."""
import re
from urllib.parse import urlsplit


def parse_urls(text: str) -> list[str]:
    result = []
    for token in re.split(r'[\s,，；;]+', text.strip()):
        token = token.strip('"\'<>（）()').rstrip('。')
        if token.startswith('www.'):
            token = 'https://' + token
        try:
            parts = urlsplit(token)
            valid = parts.scheme.lower() in ('http', 'https') and parts.hostname
        except ValueError:
            valid = False
        if valid and token not in result:
            result.append(token)
    return result
