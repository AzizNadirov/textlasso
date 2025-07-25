import json
import xml.etree.ElementTree as ET
import dataclasses
from dataclasses import fields, is_dataclass
from typing import get_origin, get_args, Union, Dict, Any, Callable, Optional, Type, Literal
from enum import Enum
import logging
import functools



class PromptGenerationError(Exception):
    """Custom exception for prompt generation errors."""
    pass


def generate_structured_prompt(
    prompt: str, 
    schema: type, 
    strategy: Literal['json', 'xml'] = 'xml',
    include_schema_description: bool = True,
    example_count: int = 2
) -> str:
    """
    Generate a structured prompt that requires data in a specific format.
    
    Args:
        prompt: The main prompt message
        schema: Dataclass defining the expected data structure
        strategy: Output format strategy ('json' or 'xml')
        include_schema_description: Whether to include detailed schema description
        example_count: Number of examples to generate (1-3)
    
    Returns:
        Enhanced prompt with structure requirements and examples
        
    Raises:
        PromptGenerationError: If schema is invalid or strategy not supported
    """
    if not is_dataclass(schema):
        raise PromptGenerationError(f"Schema must be a dataclass, got {type(schema)}")
    
    strategy = strategy.lower()
    if strategy not in ['json', 'xml']:
        raise PromptGenerationError(f"Strategy must be 'json' or 'xml', got '{strategy}'")
    
    if not 1 <= example_count <= 3:
        raise PromptGenerationError(f"Example count must be between 1 and 3, got {example_count}")
    
    # Generate the structured prompt
    generator = _StructuredPromptGenerator(schema, strategy, include_schema_description)
    structure_requirements = generator.generate_requirements()
    examples = generator.generate_examples(example_count)
    
    # Combine everything
    enhanced_prompt = f"""{prompt}

{structure_requirements}

{examples}

Remember: Your response must be valid {strategy.upper()} that matches the specified structure exactly."""
    
    return enhanced_prompt


class _StructuredPromptGenerator:
    """Helper class for generating structured prompt components."""
    
    def __init__(self, schema: type, strategy: str, include_description: bool = True):
        self.schema = schema
        self.strategy = strategy
        self.include_description = include_description
        self.logger = logging.getLogger(__name__)
    
    def generate_requirements(self) -> str:
        """Generate the structure requirements section."""
        format_name = self.strategy.upper()
        
        requirements = f"""
## OUTPUT FORMAT REQUIREMENTS

You must respond with a valid {format_name} object that follows this exact structure:"""
        
        if self.include_description:
            requirements += f"\n\n### Schema: {self.schema.__name__}\n"
            requirements += self._generate_schema_description(self.schema)
        
        requirements += f"\n\n### {format_name} Format Rules:\n"
        requirements += self._generate_format_rules()
        
        return requirements
    
    def generate_examples(self, count: int) -> str:
        """Generate example outputs."""
        examples_section = f"\n## EXAMPLES\n\nHere are {count} example{'s' if count > 1 else ''} of the expected {self.strategy.upper()} format:\n"
        
        for i in range(count):
            example_data = self._generate_example_data(variation=i)
            formatted_example = self._format_example(example_data)
            examples_section += f"\n### Example {i + 1}:\n```{self.strategy}\n{formatted_example}\n```\n"
        
        return examples_section
    
    def _generate_schema_description(self, dataclass_type: type, indent: int = 0) -> str:
        """Generate human-readable schema description."""
        description = ""
        prefix = "  " * indent
        
        for field in fields(dataclass_type):
            field_type = field.type
            field_name = field.name
            
            # Determine if field is optional
            is_optional = self._is_optional(field_type) or field.default is not dataclasses.MISSING
            optional_marker = " (optional)" if is_optional else " (required)"
            
            # Get the actual type (unwrap Optional)
            actual_type = self._get_actual_type(field_type)
            type_description = self._get_type_description(actual_type)
            
            description += f"{prefix}- **{field_name}**: {type_description}{optional_marker}\n"
            
            # If it's a nested dataclass, add its description
            if is_dataclass(actual_type):
                description += f"{prefix}  Fields:\n"
                description += self._generate_schema_description(actual_type, indent + 2)
        
        return description
    
    def _generate_format_rules(self) -> str:
        """Generate format-specific rules."""
        if self.strategy == 'json':
            return """- Use proper JSON syntax with double quotes for strings
- Include all required fields
- Use null for optional fields that are not provided
- Arrays should contain objects matching the specified structure
- Numbers should not be quoted
- Booleans should be true/false (not quoted)"""
        else:  # xml
            return """- Use proper XML syntax with opening and closing tags
- Root element should match the main dataclass name
- Use snake_case for element names
- For arrays, repeat the element name for each item
- Use self-closing tags for null/empty optional fields
- Include all required fields as elements"""
    
    def _generate_example_data(self, variation: int = 0) -> Dict[str, Any]:
        """Generate realistic example data for the schema."""
        return self._generate_data_for_type(self.schema, variation)
    
    def _generate_data_for_type(self, dataclass_type: type, variation: int = 0) -> Dict[str, Any]:
        """Generate data for a specific dataclass type."""
        data = {}
        
        for field in fields(dataclass_type):
            field_name = field.name
            field_type = field.type
            
            # Check if field is optional
            is_optional = self._is_optional(field_type) or field.default is not dataclasses.MISSING
            
            # Sometimes skip optional fields for variation
            if is_optional and variation % 3 == 2:
                continue
            
            # Generate value based on type
            actual_type = self._get_actual_type(field_type)
            data[field_name] = self._generate_value_for_type(actual_type, field_name, variation)
        
        return data
    
    def _generate_value_for_type(self, field_type: type, field_name: str, variation: int = 0) -> Any:
        """Generate a realistic value for a given type."""
        origin = get_origin(field_type)
        
        # Handle List types
        if origin is list:
            item_type = get_args(field_type)[0]
            list_size = 2 + (variation % 2)  # 2 or 3 items
            return [self._generate_value_for_type(item_type, f"{field_name}_item", i) 
                   for i in range(list_size)]
        
        # Handle Dict types
        if origin is dict:
            args = get_args(field_type)
            if len(args) == 2:
                return {f"key_{variation + 1}": self._generate_value_for_type(args[1], "value", variation)}
            return {"example_key": "example_value"}
        
        # Handle Enum types
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            enum_values = list(field_type)
            return enum_values[variation % len(enum_values)].value
        
        # Handle dataclass types
        if is_dataclass(field_type):
            return self._generate_data_for_type(field_type, variation)
        
        # Handle basic types
        return self._generate_basic_value(field_type, field_name, variation)
    
    def _generate_basic_value(self, field_type: type, field_name: str, variation: int) -> Any:
        """Generate basic type values."""
        field_lower = field_name.lower()
        
        if field_type is str:
            if 'name' in field_lower:
                names = ["Alice Johnson", "Bob Smith", "Carol Davis"]
                return names[variation % len(names)]
            elif 'email' in field_lower:
                emails = ["alice@example.com", "bob@company.org", "carol@domain.net"]
                return emails[variation % len(emails)]
            elif 'id' in field_lower:
                return f"id_{variation + 1:03d}"
            elif 'status' in field_lower:
                statuses = ["active", "pending", "completed"]
                return statuses[variation % len(statuses)]
            else:
                return f"example_{field_name}_{variation + 1}"
        
        elif field_type is int:
            if 'age' in field_lower:
                return 25 + (variation * 5)
            elif 'count' in field_lower or 'total' in field_lower:
                return 10 + (variation * 5)
            elif 'id' in field_lower:
                return 1000 + variation
            else:
                return variation + 1
        
        elif field_type is float:
            if 'price' in field_lower or 'cost' in field_lower:
                return round(19.99 + (variation * 10.5), 2)
            elif 'rating' in field_lower:
                return round(4.0 + (variation * 0.3), 1)
            else:
                return round(1.5 + (variation * 2.3), 2)
        
        elif field_type is bool:
            return variation % 2 == 0
        
        else:
            return f"value_{variation}"
    
    def _format_example(self, data: Dict[str, Any]) -> str:
        """Format the example data according to the strategy."""
        if self.strategy == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:  # xml
            return self._dict_to_xml(data, self.schema.__name__)
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str) -> str:
        """Convert dictionary to XML string."""
        root = ET.Element(self._to_snake_case(root_name))
        self._dict_to_xml_element(data, root)
        
        # Pretty print
        self._indent_xml(root)
        return ET.tostring(root, encoding='unicode')
    
    def _dict_to_xml_element(self, data: Any, parent: ET.Element) -> None:
        """Recursively convert dictionary to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                element = ET.SubElement(parent, self._to_snake_case(str(key)))
                self._dict_to_xml_element(value, element)
        elif isinstance(data, list):
            for item in data:
                # For lists in XML, we create multiple elements with the same name
                item_element = ET.SubElement(parent, "item")
                self._dict_to_xml_element(item, item_element)
        elif data is None:
            parent.text = ""
        else:
            parent.text = str(data)
    
    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add pretty-printing indentation to XML."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    def _is_optional(self, type_hint) -> bool:
        """Check if a type hint represents Optional[T]."""
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            return len(args) == 2 and type(None) in args
        return False
    
    def _get_actual_type(self, type_hint) -> type:
        """Get the actual type from Optional or Union types."""
        if self._is_optional(type_hint):
            args = get_args(type_hint)
            return next(arg for arg in args if arg is not type(None))
        return type_hint
    
    def _get_type_description(self, field_type: type) -> str:
        """Get human-readable type description."""
        origin = get_origin(field_type)
        
        if origin is list:
            item_type = get_args(field_type)[0]
            item_desc = self._get_type_description(item_type)
            return f"Array of {item_desc}"
        
        if origin is dict:
            args = get_args(field_type)
            if len(args) == 2:
                key_desc = self._get_type_description(args[0])
                val_desc = self._get_type_description(args[1])
                return f"Dictionary ({key_desc} -> {val_desc})"
            return "Dictionary"
        
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            values = [e.value for e in field_type]
            return f"Enum (one of: {', '.join(map(str, values))})"
        
        if is_dataclass(field_type):
            return f"Object ({field_type.__name__})"
        
        return field_type.__name__ if hasattr(field_type, '__name__') else str(field_type)


## Decorator tools

class DecoratorError(Exception):
    """Custom exception for decorator errors."""
    pass

def structured_output(
    schema: Type,
    strategy: str = "json",
    include_schema_description: bool = True,
    example_count: int = 2,
    auto_validate: bool = True,
    logger: Optional[logging.Logger] = None
):
    """
    Decorator that enhances prompt-returning functions with structured output requirements.
    
    Args:
        schema: Dataclass defining the expected output structure
        strategy: Output format ('json' or 'xml')
        include_schema_description: Whether to include detailed schema info
        example_count: Number of examples to generate (1-3)
        auto_validate: Whether to validate the schema at decoration time
        logger: Optional logger for debugging
    
    Usage:
        @structured_output(schema=UserResponse, strategy="json")
        def get_user_extraction_prompt(text: str) -> str:
            return f"Extract user information from: {text}"
        
        # The decorated function will return an enhanced prompt with structure requirements
    """
    
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        # Validate at decoration time if requested
        if auto_validate:
            _validate_decorator_params(schema, strategy, example_count)
        
        # Setup logging
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(f"{func.__module__}.{func.__name__}")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> str:
            try:
                # Call the original function to get the base prompt
                logger.debug(f"Calling original function {func.__name__} with args={args}, kwargs={kwargs}")
                base_prompt = func(*args, **kwargs)
                
                if not isinstance(base_prompt, str):
                    raise DecoratorError(f"Function {func.__name__} must return a string, got {type(base_prompt)}")
                
                logger.debug(f"Base prompt generated: {base_prompt[:100]}...")
                
                # Enhance the prompt with structured output requirements
                enhanced_prompt = generate_structured_prompt(
                    prompt=base_prompt,
                    schema=schema,
                    strategy=strategy,
                    include_schema_description=include_schema_description,
                    example_count=example_count
                )
                
                logger.debug("Enhanced prompt generated successfully")
                return enhanced_prompt
                
            except Exception as e:
                logger.error(f"Error in structured_output decorator for {func.__name__}: {str(e)}")
                raise DecoratorError(f"Failed to enhance prompt from {func.__name__}: {str(e)}") from e
        
        # Add metadata to the wrapper function
        wrapper._structured_output_schema = schema
        wrapper._structured_output_strategy = strategy
        wrapper._structured_output_config = {
            'include_schema_description': include_schema_description,
            'example_count': example_count,
            'auto_validate': auto_validate
        }
        
        return wrapper
    
    return decorator


def _validate_decorator_params(schema: Type, strategy: str, example_count: int):
    """Validate decorator parameters."""
    if not is_dataclass(schema):
        raise DecoratorError(f"Schema must be a dataclass, got {type(schema)}")
    
    if strategy.lower() not in ['json', 'xml']:
        raise DecoratorError(f"Strategy must be 'json' or 'xml', got '{strategy}'")
    
    if not 1 <= example_count <= 3:
        raise DecoratorError(f"Example count must be between 1 and 3, got {example_count}")


def chain_prompts(*prompt_funcs: Callable[..., str], separator: str = "\n\n---\n\n"):
    """
    Decorator that chains multiple prompt functions together.
    
    Args:
        *prompt_funcs: Other prompt functions to chain
        separator: String to separate chained prompts
    
    Usage:
        def base_instruction() -> str:
            return "You are a helpful assistant."
        
        @chain_prompts(base_instruction)
        @structured_output(UserResponse, "json")
        def get_user_prompt(text: str) -> str:
            return f"Extract user data from: {text}"
    """
    
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Collect all prompts
            prompts = []
            
            # Add chained prompts first
            for prompt_func in prompt_funcs:
                try:
                    # Try to call with the same args, fallback to no args
                    try:
                        prompt = prompt_func(*args, **kwargs)
                    except TypeError:
                        prompt = prompt_func()
                    prompts.append(prompt)
                except Exception as e:
                    logging.warning(f"Failed to call chained prompt function {prompt_func.__name__}: {e}")
            
            # Add main prompt
            main_prompt = func(*args, **kwargs)
            prompts.append(main_prompt)
            
            # Combine all prompts
            return separator.join(prompts)
        
        # Add metadata
        wrapper._chained_prompts = prompt_funcs
        wrapper._separator = separator
        
        return wrapper
    
    return decorator


def prompt_cache(maxsize: int = 128):
    """
    Decorator that caches prompt results to avoid regenerating identical prompts.
    
    Args:
        maxsize: Maximum number of cached results
    
    Usage:
        @prompt_cache(maxsize=64)
        @structured_output(UserResponse, "json")
        def get_user_prompt(text: str) -> str:
            return f"Extract user data from: {text}"
    """
    
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        cached_func = functools.lru_cache(maxsize=maxsize)(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cached_func(*args, **kwargs)
        
        # Expose cache methods
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        
        return wrapper
    
    return decorator


