"""
TextLasso - Simple text data extractor, specially helpful for extracting data from LLM responses.
"""

from .extract import extract
from .prompting import generate_structured_prompt, structured_output
from ._extractors import extract_from_dict

__version__ = "0.1.0"
__all__ = [
    'extract',
    'extract_from_dict', 
    'generate_structured_prompt',
    'structured_output'
]