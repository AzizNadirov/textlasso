import json
import re
from typing import Any
import xmltodict
from loguru import logger

from textlasso.cleaners import clear_llm_res


def parse_xml(text: str) -> dict[str, Any]:
    text_clrear = clear_llm_res(text, extract_strategy='xml')
    return xmltodict.parse(text_clrear)


def parse_json(text: str) -> dict[str, Any]:
    text = clear_llm_res(text, extract_strategy='json')
    try:
        return json.loads(text)
    
    except json.JSONDecodeError:
        logger.debug("Loading through simple cleaning strategy failed, trying harders...")
    
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

    # Try each parsing strategy
    errors = []
    for i, strategy in enumerate(parsing_strategies):
        try:
            logger.debug(f"Trying JSON parsing strategy {i+1}")
            result = strategy(text)
            if result is not None:
                logger.success(f"Successfully parsed JSON using strategy {i+1}")
                return result
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            errors.append(f"Strategy {i+1} failed: {str(e)}")
            continue

    logger.error("All JSON parsing strategies failed")
    logger.debug(f"Error details: {'; '.join(errors)}")
    logger.debug(f"Text (first 500 chars): {text[:500]}")

    # If we get here, all strategies failed
    raise json.JSONDecodeError(
        "Failed to extract valid JSON using any parsing strategy", text, 0
    )