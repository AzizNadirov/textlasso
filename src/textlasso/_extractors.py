import logging
from dataclasses import dataclass, fields, is_dataclass
from typing import get_origin, get_args, Union, Optional, List, Dict, Any, Literal
from enum import Enum
from ._parsers import parse_json, parse_xml


class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass


class DataclassConverter:
    """
    A class-based dictionary to dataclass converter with comprehensive logging.
    
    Features:
    - Nested dataclass conversion
    - Type validation and conversion
    - Comprehensive logging
    - Configurable behavior
    - Optional field handling
    """
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 log_level: int = logging.INFO,
                 strict_mode: bool = True,
                 ignore_extra_fields: bool = True):
        """
        Initialize the converter.
        
        Args:
            logger: Custom logger instance. If None, creates a new one.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            strict_mode: If True, raises errors for type mismatches. If False, attempts conversion.
            ignore_extra_fields: If True, ignores fields in data not present in dataclass.
        """
        self.strict_mode = strict_mode
        self.ignore_extra_fields = ignore_extra_fields
        
        # Setup logging
        if logger is None:
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = logger
            
        self.logger.setLevel(log_level)
        self.logger.info(f"DataclassConverter initialized with strict_mode={strict_mode}")
    
    def convert(self, data: Dict[str, Any], target_class: type) -> Any:
        """
        Convert a dictionary to a dataclass instance.
        
        Args:
            data: Dictionary containing the data to convert
            target_class: The dataclass type to convert to
            
        Returns:
            An instance of target_class with fields populated from data
            
        Raises:
            ConversionError: If conversion fails
        """
        self.logger.info(f"Starting conversion to {target_class.__name__}")
        self.logger.debug(f"Input data: {data}")
        
        try:
            result = self._convert_to_dataclass(data, target_class)
            self.logger.info(f"Successfully converted to {target_class.__name__}")
            self.logger.debug(f"Result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            raise ConversionError(f"Failed to convert data to {target_class.__name__}: {str(e)}") from e
    
    def _convert_to_dataclass(self, data: Dict[str, Any], target_class: type) -> Any:
        """Internal method to convert dictionary to dataclass."""
        if not is_dataclass(target_class):
            raise ValueError(f"{target_class} is not a dataclass")
        
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        self.logger.debug(f"Converting dict to {target_class.__name__}")
        
        kwargs = {}
        dataclass_fields = fields(target_class)
        field_names = {f.name for f in dataclass_fields}
        
        # Check for extra fields
        extra_fields = set(data.keys()) - field_names
        if extra_fields:
            if self.ignore_extra_fields:
                self.logger.warning(f"Ignoring extra fields: {extra_fields}")
            else:
                raise ValueError(f"Extra fields found: {extra_fields}")
        
        # Process each field
        for field in dataclass_fields:
            field_name = field.name
            field_type = field.type
            
            self.logger.debug(f"Processing field '{field_name}' of type {field_type}")
            
            if field_name in data:
                field_value = data[field_name]
                self.logger.debug(f"Found value for '{field_name}': {field_value}")
                
                try:
                    converted_value = self._convert_value(field_value, field_type, f"{target_class.__name__}.{field_name}")
                    kwargs[field_name] = converted_value
                    self.logger.debug(f"Successfully converted '{field_name}' to {type(converted_value)}")
                except Exception as e:
                    self.logger.error(f"Failed to convert field '{field_name}': {str(e)}")
                    raise
                    
            elif field.default is not dataclass.MISSING:
                self.logger.debug(f"Using default value for '{field_name}': {field.default}")
                continue
            elif field.default_factory is not dataclass.MISSING:
                self.logger.debug(f"Using default_factory for '{field_name}'")
                continue
            else:
                # Check if field is Optional
                if self._is_optional(field_type):
                    self.logger.debug(f"Setting optional field '{field_name}' to None")
                    kwargs[field_name] = None
                else:
                    error_msg = f"Required field '{field_name}' not found in data"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
        
        return target_class(**kwargs)
    
    def _convert_value(self, value: Any, target_type: type, context: str = "") -> Any:
        """Convert a value to the target type with detailed logging."""
        self.logger.debug(f"Converting value {value} ({type(value)}) to {target_type} in context: {context}")
        
        if value is None:
            if self._is_optional(target_type):
                self.logger.debug("Value is None and target type is Optional")
                return None
            else:
                raise ValueError(f"Cannot convert None to non-optional type {target_type}")
        
        # Handle Optional types
        if self._is_optional(target_type):
            args = get_args(target_type)
            non_none_types = [arg for arg in args if arg is not type(None)]
            if non_none_types:
                target_type = non_none_types[0]
                self.logger.debug(f"Unwrapped Optional type to {target_type}")
        
        # Handle Union types (excluding Optional)
        origin = get_origin(target_type)
        if origin is Union:
            return self._convert_union_value(value, target_type, context)
        
        # Handle List types
        if origin is list or target_type is list:
            return self._convert_list_value(value, target_type, context)
        
        # Handle Dict types
        if origin is dict or target_type is dict:
            return self._convert_dict_value(value, target_type, context)
        
        # Handle Enum types
        if isinstance(target_type, type) and issubclass(target_type, Enum):
            return self._convert_enum_value(value, target_type, context)
        
        # Handle dataclass types
        if is_dataclass(target_type):
            return self._convert_dataclass_value(value, target_type, context)
        
        # Handle basic types
        if target_type in (str, int, float, bool):
            return self._convert_basic_type(value, target_type, context)
        
        # If no specific handling, try direct assignment
        self.logger.debug("No specific conversion handler, using direct assignment")
        return value
    
    def _convert_union_value(self, value: Any, target_type: type, context: str) -> Any:
        """Convert value to Union type."""
        args = get_args(target_type)
        self.logger.debug(f"Trying Union conversion with types: {args}")
        
        for i, arg_type in enumerate(args):
            if arg_type is type(None):
                continue
            try:
                self.logger.debug(f"Trying Union option {i+1}: {arg_type}")
                result = self._convert_value(value, arg_type, f"{context}[Union:{arg_type}]")
                self.logger.debug(f"Successfully converted to Union type {arg_type}")
                return result
            except (ValueError, TypeError, ConversionError) as e:
                self.logger.debug(f"Union option {arg_type} failed: {str(e)}")
                continue
        
        raise ValueError(f"Cannot convert {value} to any type in {target_type}")
    
    def _convert_list_value(self, value: Any, target_type: type, context: str) -> List[Any]:
        """Convert value to List type."""
        if not isinstance(value, list):
            raise ValueError(f"Expected list, got {type(value)}")
        
        origin = get_origin(target_type)
        if origin is list:
            args = get_args(target_type)
            if args:
                list_item_type = args[0]
                self.logger.debug(f"Converting list items to type {list_item_type}")
                result = []
                for i, item in enumerate(value):
                    converted_item = self._convert_value(item, list_item_type, f"{context}[{i}]")
                    result.append(converted_item)
                return result
        
        self.logger.debug("Converting to plain list")
        return list(value)
    
    def _convert_dict_value(self, value: Any, target_type: type, context: str) -> Dict[Any, Any]:
        """Convert value to Dict type."""
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict, got {type(value)}")
        
        origin = get_origin(target_type)
        if origin is dict:
            args = get_args(target_type)
            if len(args) == 2:
                key_type, value_type = args
                self.logger.debug(f"Converting dict with key type {key_type} and value type {value_type}")
                return {
                    self._convert_value(k, key_type, f"{context}[key]"): 
                    self._convert_value(v, value_type, f"{context}[{k}]")
                    for k, v in value.items()
                }
        
        self.logger.debug("Converting to plain dict")
        return dict(value)
    
    def _convert_enum_value(self, value: Any, target_type: type, context: str) -> Enum:
        """Convert value to Enum type."""
        self.logger.debug(f"Converting to Enum {target_type.__name__}")
        
        try:
            if isinstance(value, str):
                # Try by name first
                return target_type[value]
            else:
                # Try by value
                return target_type(value)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Cannot convert {value} to {target_type.__name__}: {str(e)}")
    
    def _convert_dataclass_value(self, value: Any, target_type: type, context: str) -> Any:
        """Convert value to dataclass type."""
        if isinstance(value, dict):
            self.logger.debug(f"Converting nested dict to dataclass {target_type.__name__}")
            return self._convert_to_dataclass(value, target_type)
        else:
            raise ValueError(f"Expected dict for dataclass {target_type}, got {type(value)}")
    
    def _convert_basic_type(self, value: Any, target_type: type, context: str) -> Any:
        """Convert value to basic type (str, int, float, bool)."""
        if isinstance(value, target_type):
            self.logger.debug(f"Value already is {target_type.__name__}")
            return value
        
        self.logger.debug(f"Converting {type(value).__name__} to {target_type.__name__}")
        
        try:
            if target_type is bool:
                return self._convert_to_bool(value)
            else:
                return target_type(value)
        except (ValueError, TypeError) as e:
            if self.strict_mode:
                raise ValueError(f"Cannot convert {value} to {target_type}: {e}")
            else:
                self.logger.warning(f"Conversion failed, returning original value: {e}")
                return value
    
    def _convert_to_bool(self, value: Any) -> bool:
        """Convert value to boolean with smart string handling."""
        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in ('true', '1', 'yes', 'on', 'y'):
                return True
            elif lower_val in ('false', '0', 'no', 'off', 'n', ''):
                return False
            else:
                raise ValueError(f"Cannot convert string '{value}' to bool")
        else:
            return bool(value)
    
    def _is_optional(self, type_hint) -> bool:
        """Check if a type hint represents Optional[T]."""
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            return len(args) == 2 and type(None) in args
        return False



def extract_from_dict(data_dict: dict,
                      target_class: type,
                      strict_mode: bool = True,
                      ignore_extra_fields: bool = True,
                      logger: Optional[logging.Logger] = None,
                      log_level: int = logging.INFO) -> Any:
    """  """
    extractor = DataclassConverter(logger=logger, 
                                   log_level=log_level, 
                                   strict_mode=strict_mode,
                                   ignore_extra_fields=ignore_extra_fields)
    
    return extractor.convert(data=data_dict, target_class=target_class)



def extract(text: str, 
            target_class: type, 
            extract_strategy: Literal['json', 'xml'] = 'xml') -> Any:
    """ Extract data from text using a specified strategy and target dataclass type 
    
    Args:
        text: The text to extract data from
        target_class: The dataclass type to convert to
        extract_strategy: The strategy to use for extraction (default is 'json')
        
    Returns:
        An instance of target_class dataclass with fields populated from data
        
    Raises:
        ValueError: If extract_strategy is invalid
    """
    if extract_strategy == 'json':
        data_dict = parse_json(text)
    elif extract_strategy == 'xml':
        data_dict = parse_xml(text)
    else:
        raise ValueError(f"Invalid extract_strategy: {extract_strategy}")
    
    return extract_from_dict(data_dict, target_class)