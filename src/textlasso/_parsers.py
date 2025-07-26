import json
import re
import logging
from typing import Any
import xmltodict

from .cleaners import clear_llm_res

logger = logging.getLogger(__name__)


def parse_xml(text: str) -> dict[str, Any]:
    """Parse XML text and return as dictionary, handling root element issues."""
    text_clear = clear_llm_res(text, extract_strategy='xml')
    parsed_dict = xmltodict.parse(text_clear)
    if len(parsed_dict) == 1:
        root_key = list(parsed_dict.keys())[0]
        root_value = parsed_dict[root_key]
        if isinstance(root_value, dict):
            logger.debug(f"XML has single root element '{root_key}', checking if it should be unwrapped")
            wrapper_patterns = [
                'response_',
                'result_', 
                'output_',
                'data_',
                'answer_'
            ]
            
            is_likely_wrapper = any(root_key.lower().startswith(pattern) for pattern in wrapper_patterns)
            
            if is_likely_wrapper:
                logger.debug(f"Root element '{root_key}' appears to be a wrapper, unwrapping")
                return root_value
            else:
                logger.debug(f"Keeping root element '{root_key}' in structure")
                return parsed_dict
        else:
            return parsed_dict
    else:
        return parsed_dict


def parse_json(text: str) -> dict[str, Any]:
    """Parse JSON text with multiple fallback strategies."""
    text = clear_llm_res(text, extract_strategy='json')
    try:
        return json.loads(text)
    
    except json.JSONDecodeError:
        logger.debug("Loading through simple cleaning strategy failed, trying harder...")
    
    parsing_strategies = [
        # Strategy 1: Direct JSON parsing
        lambda resp: json.loads(resp),
        # Strategy 2: Extract JSON from markdown code blocks
        lambda resp: (
            json.loads(re.search(r"```json\s*([\s\S]*?)\s*```", resp).group(1))
            if re.search(r"```json\s*([\s\S]*?)\s*```", resp)
            else None
        ),
        # Strategy 3: Extract from any code blocks (assuming JSON)
        lambda resp: (
            json.loads(re.search(r"```\s*([\s\S]*?)\s*```", resp).group(1))
            if re.search(r"```\s*([\s\S]*?)\s*```", resp)
            else None
        ),
        # Strategy 4: Find anything that looks like a JSON object
        lambda resp: (
            json.loads(re.search(r"{[\s\S]*?}", resp).group(0))
            if re.search(r"{[\s\S]*?}", resp)
            else None
        ),
        # Strategy 5: Find anything that looks like a JSON array
        lambda resp: (
            json.loads(re.search(r"\[[\s\S]*?\]", resp).group(0))
            if re.search(r"\[[\s\S]*?\]", resp)
            else None
        ),
        # Strategy 6: Clean and try again (remove non-JSON characters)
        lambda resp: json.loads(re.sub(r"[^\x00-\x7F]+", "", resp)),
    ]

    errors = []
    for i, strategy in enumerate(parsing_strategies):
        try:
            logger.debug(f"Trying JSON parsing strategy {i+1}")
            result = strategy(text)
            if result is not None:
                logger.info(f"Successfully parsed JSON using strategy {i+1}")
                return result
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            errors.append(f"Strategy {i+1} failed: {str(e)}")
            continue

    logger.error("All JSON parsing strategies failed")
    logger.debug(f"Error details: {'; '.join(errors)}")
    logger.debug(f"Text (first 500 chars): {text[:500]}")

    raise json.JSONDecodeError(
        "Failed to extract valid JSON using any parsing strategy", text, 0
    )