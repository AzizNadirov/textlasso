from typing import Literal


def clear_llm_res(text: str, extract_strategy: Literal['json', 'xml']) -> str:
    """ clear text from LLM response based on strategy """
    text = text.strip()
    if text.startswith('```'):
        if text.startswith(f'```{extract_strategy}'):
            text = text.replace(f'```{extract_strategy}', '', 1).strip()    # drop ```xml
            
        else:
            text = text.replace('```', '', 1).strip()    # drop ```
        if text.endswith('```'):    # drop closing ```
            text = text[:-3]
            
    return text.strip()