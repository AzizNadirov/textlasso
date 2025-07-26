# TextLasso 🤠

[![PyPI version](https://badge.fury.io/py/textlasso.svg)](https://badge.fury.io/py/textlasso)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TextLasso** is a powerful Python library for extracting structured data from raw text, with special focus on processing LLM (Large Language Model) responses. Whether you're parsing JSON buried in markdown, extracting data from XML, or need to generate structured prompts for AI models, TextLasso has you covered.

## ✨ Key Features

- 🎯 **Smart Text Extraction**: Extract structured data from messy text with multiple fallback strategies
- 🧹 **LLM Response Cleaning**: Automatically clean code blocks, markdown artifacts, and formatting
- 🏗️ **Dataclass Integration**: Convert raw text directly to Python dataclasses with type validation
- 🤖 **AI Prompt Generation**: Generate structured prompts with schema validation and examples
- 📊 **Multiple Formats**: Support for JSON, XML, and extensible to other formats
- 🔧 **Flexible Configuration**: Configurable error handling, logging, and validation modes
- 🎨 **Decorator Support**: Enhance existing functions with structured output capabilities

## 🚀 Quick Start

### Installation

```bash
pip install textlasso
```

### Basic Usage

```python
from dataclasses import dataclass
from typing import List, Optional
from textlasso import extract

@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None
    skills: List[str] = None

# Extract from messy LLM response
llm_response = r"""
Here's the person data you requested:

```json
{
    "name": "Alice Johnson",
    "age": 30,
    "email": "alice@company.com", 
    "skills": ["Python", "Machine Learning", "Data Science"]
}
```

Hope this helps!
"""

person = extract(llm_response, Person, extract_strategy='json')
print(f"Extracted: {person.name}, {person.age} years old")
# Output: Extracted: Alice Johnson, 30 years old
```

## 📚 Comprehensive Examples

### 1. Basic Text Extraction

#### JSON Extraction with Fallback Strategies

```python
from dataclasses import dataclass
from typing import List, Optional
from textlasso import extract

@dataclass
class Product:
    name: str
    price: float
    category: str
    in_stock: bool
    tags: Optional[List[str]] = None

# Works with clean JSON
clean_json = '{"name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": true}'

# Works with markdown-wrapped JSON
markdown_json = r"""
Here's your product data:
```json
{
    "name": "Wireless Headphones",
    "price": 199.99,
    "category": "Electronics", 
    "in_stock": false,
    "tags": ["wireless", "bluetooth", "noise-canceling"]
}
```
"""

# Works with messy responses
messy_response = """
Let me extract that product information for you...

The product details are: {"name": "Smart Watch", "price": 299.99, "category": "Wearables", "in_stock": true}

Is this what you were looking for?
"""

# All of these work automatically
products = [
    extract(clean_json, Product, extract_strategy='json'),
    extract(markdown_json, Product, extract_strategy='json'), 
    extract(messy_response, Product, extract_strategy='json')
]

for product in products:
    print(f"{product.name}: ${product.price} ({'✅' if product.in_stock else '❌'})")
```

#### XML Extraction

```python
@dataclass 
class Address:
    street: str
    city: str
    country: str
    zip_code: Optional[str] = None

xml_data = """
<address>
    <street>123 Main St</street>
    <city>San Francisco</city>
    <country>USA</country>
    <zip_code>94102</zip_code>
</address>
"""

address = extract(xml_data, Address, extract_strategy='xml')
print(f"Address: {address.street}, {address.city}, {address.country}")
```

### 2. Complex Nested Data Structures

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Department(Enum):
    ENGINEERING = "engineering"
    MARKETING = "marketing" 
    SALES = "sales"
    HR = "hr"

@dataclass
class Employee:
    id: int
    name: str
    department: Department
    salary: float
    skills: List[str]
    manager_id: Optional[int] = None

@dataclass
class Company:
    name: str
    founded_year: int
    employees: List[Employee]
    headquarters: Address

complex_json = """
{
    "name": "TechCorp Inc",
    "founded_year": 2015,
    "headquarters": {
        "street": "100 Tech Plaza",
        "city": "Austin", 
        "country": "USA",
        "zip_code": "78701"
    },
    "employees": [
        {
            "id": 1,
            "name": "Sarah Chen", 
            "department": "engineering",
            "salary": 120000,
            "skills": ["Python", "React", "AWS"],
            "manager_id": null
        },
        {
            "id": 2,
            "name": "Mike Rodriguez",
            "department": "marketing", 
            "salary": 85000,
            "skills": ["SEO", "Content Strategy", "Analytics"],
            "manager_id": 1
        }
    ]
}
"""

company = extract(complex_json, Company, extract_strategy='json')
print(f"Company: {company.name} ({company.founded_year})")
print(f"HQ: {company.headquarters.city}, {company.headquarters.country}")
print(f"Employees: {len(company.employees)}")

for emp in company.employees:
    print(f"  - {emp.name} ({emp.department.value}): {', '.join(emp.skills)}")
```

### 3. LLM Response Cleaning

```python
from textlasso.cleaners import clear_llm_res

# Clean various LLM response formats
messy_responses = [
    r'```json' + '\n{"key": "value"}\n' + r'```',
    r'```' + '\n{"key": "value"}\n' + r'```', 
    'Here\'s the data: {"key": "value"} hope it helps!',
    r'```xml' + '\n<root><item>data</item></root>\n' + r'```'
]

for response in messy_responses:
    clean_json = clear_llm_res(response, extract_strategy='json')
    clean_xml = clear_llm_res(response, extract_strategy='xml')
    print(f"Original: {response}")
    print(f"JSON cleaned: {clean_json}")
    print(f"XML cleaned: {clean_xml}")
    print("---")
```

### 4. Advanced Data Extraction with Configuration

```python
from textlasso import extract_from_dict
import logging

# Configure custom logging
logger = logging.getLogger("my_extractor")
logger.setLevel(logging.DEBUG)

@dataclass
class FlexibleData:
    required_field: str
    optional_field: Optional[str] = None
    number_field: int = 0

# Strict mode - raises errors on type mismatches
data_with_extra = {
    "required_field": "test",
    "optional_field": "optional", 
    "number_field": "123",  # String instead of int
    "extra_field": "ignored"  # Extra field
}

# Strict mode (default)
try:
    result_strict = extract_from_dict(
        data_with_extra, 
        FlexibleData,
        strict_mode=True,
        ignore_extra_fields=True,
        logger=logger
    )
    print("Strict mode result:", result_strict)
except Exception as e:
    print("Strict mode error:", e)

# Flexible mode - attempts conversion
result_flexible = extract_from_dict(
    data_with_extra,
    FlexibleData, 
    strict_mode=False,
    ignore_extra_fields=True,
    logger=logger
)
print("Flexible mode result:", result_flexible)
```

### 5. Structured Prompt Generation

#### Basic Prompt Generation

```python
from textlasso import generate_structured_prompt

@dataclass
class UserFeedback:
    rating: int  # 1-5
    comment: str
    category: str
    recommended: bool
    issues: Optional[List[str]] = None

# Generate a structured prompt
prompt = generate_structured_prompt(
    prompt="Analyze this customer review and extract structured feedback",
    schema=UserFeedback,
    strategy="json",
    include_schema_description=True,
    example_count=2
)

print(prompt)
```

#### Using the Decorator for Function Enhancement

```python
from textlasso import structured_output

@dataclass
class NewsArticle:
    title: str
    summary: str
    category: str
    sentiment: str  # positive, negative, neutral
    key_points: List[str]
    publication_date: Optional[str] = None

@structured_output(schema=NewsArticle, strategy="json", example_count=1)
def create_article_analysis_prompt(article_text: str) -> str:
    return f"""
    Analyze the following news article and extract key information:
    
    Article: {article_text}
    
    Please provide a comprehensive analysis focusing on the main themes,
    sentiment, and key takeaways.
    """

# The decorator automatically enhances your prompt with structure requirements
article_text = "Breaking: New AI breakthrough announced by researchers..."
enhanced_prompt = create_article_analysis_prompt(article_text)

# This prompt now includes schema definitions, examples, and format requirements
print("Enhanced prompt length:", len(enhanced_prompt))
print("First 500 chars:", enhanced_prompt[:500])
```

#### Advanced Prompt Chaining

```python
from textlasso import structured_output, chain_prompts, prompt_cache

def base_instructions() -> str:
    return "You are an expert data analyst. Always be precise and thorough."

def context_setting() -> str:
    return "Focus on extracting actionable insights from the provided data."

@prompt_cache(maxsize=64)  # Cache prompts to avoid regeneration
@chain_prompts(base_instructions, context_setting)
@structured_output(schema=NewsArticle, strategy="xml", example_count=2)
def create_comprehensive_analysis_prompt(text: str, focus_area: str) -> str:
    return f"""
    Analyze the following content with special attention to {focus_area}:
    
    Content: {text}
    """

# This creates a comprehensive prompt with:
# 1. Base instructions
# 2. Context setting  
# 3. Your specific prompt
# 4. Structured output requirements with examples
# 5. Caching for performance

enhanced_prompt = create_comprehensive_analysis_prompt(
    "Sample article text here...", 
    "market trends"
)
```

### 6. Error Handling and Validation

```python
from textlasso import extract
from textlasso._extractors import ConversionError
import json

@dataclass
class StrictData:
    id: int
    name: str
    active: bool

# Handling malformed data
malformed_data = '{"id": "not_a_number", "name": "test"}'  # Missing required field, wrong type

try:
    result = extract(malformed_data, StrictData, extract_strategy='json')
except ConversionError as e:
    print(f"Conversion failed: {e}")
except json.JSONDecodeError as e:
    print(f"JSON parsing failed: {e}")

# Working with partial data using Optional fields
@dataclass  
class PartialData:
    id: Optional[int] = None
    name: Optional[str] = None
    active: bool = False

partial_json = '{"name": "test"}'  # Only partial data
result = extract(partial_json, PartialData, extract_strategy='json')
print(f"Partial result: {result}")
```

### 7. Real-World Use Cases

#### Processing Survey Responses

```python
@dataclass
class SurveyResponse:
    respondent_id: str
    age_group: str
    satisfaction_rating: int
    feedback: str
    would_recommend: bool
    improvement_areas: List[str]

# Simulating LLM processing of survey data
llm_survey_output = r"""
Based on the survey response, here's the extracted data:

```json
{
    "respondent_id": "RESP_001",
    "age_group": "25-34", 
    "satisfaction_rating": 4,
    "feedback": "Great service overall, but could improve response time",
    "would_recommend": true,
    "improvement_areas": ["response_time", "pricing"]
}
```

This response indicates positive sentiment with specific improvement suggestions.
"""

survey = extract(llm_survey_output, SurveyResponse, extract_strategy='json')
print(f"Survey {survey.respondent_id}: {survey.satisfaction_rating}/5 stars")
print(f"Feedback: {survey.feedback}")
print(f"Improvement areas: {', '.join(survey.improvement_areas)}")
```

#### E-commerce Product Extraction

```python
@dataclass
class ProductReview:
    product_id: str
    reviewer_name: str
    rating: int
    review_text: str
    verified_purchase: bool
    helpful_votes: int
    review_date: str

@structured_output(schema=ProductReview, strategy="json")
def create_review_extraction_prompt(raw_review: str) -> str:
    return f"""
    Extract structured information from this product review:
    
    {raw_review}
    
    Pay attention to implicit ratings, sentiment, and any verification indicators.
    """

raw_review = """
★★★★☆ Amazing headphones! by John D. (Verified Purchase) - March 15, 2024
These headphones exceeded my expectations. Great sound quality and comfortable fit.
Battery life could be better but overall very satisfied. Would definitely buy again!
👍 47 people found this helpful
"""

extraction_prompt = create_review_extraction_prompt(raw_review)
# Send this prompt to your LLM, then extract the response:
# review = extract(llm_response, ProductReview, extract_strategy='json')
```

## 🔧 Configuration Options

### Extraction Configuration

```python
from textlasso import extract_from_dict
import logging

# Configure extraction behavior
result = extract_from_dict(
    data_dict=your_data,
    target_class=YourDataClass,
    strict_mode=False,          # Allow type conversions
    ignore_extra_fields=True,   # Ignore unknown fields
    logger=custom_logger,       # Custom logging
    log_level=logging.DEBUG     # Detailed logging
)
```

### Prompt Generation Configuration

```python
from textlasso import generate_structured_prompt

prompt = generate_structured_prompt(
    prompt="Your base prompt",
    schema=YourSchema,
    strategy="json",                    # or "xml"
    include_schema_description=True,    # Include field descriptions
    example_count=3                     # Number of examples (1-3)
)
```

## 📖 API Reference

### Core Functions

#### `extract(text, target_class, extract_strategy='json')`
Extract structured data from text.

**Parameters:**
- `text` (str): Raw text containing data to extract
- `target_class` (type): Dataclass to convert data into
- `extract_strategy` (Literal['json', 'xml']): Extraction strategy

**Returns:** Instance of `target_class`

#### `extract_from_dict(data_dict, target_class, **options)`
Convert dictionary to dataclass with advanced options.

#### `generate_structured_prompt(prompt, schema, strategy, **options)`
Generate enhanced prompts with structure requirements.

### Decorators

#### `@structured_output(schema, strategy='json', **options)`
Enhance prompt functions with structured output requirements.

#### `@chain_prompts(*prompt_funcs, separator='\n\n---\n\n')`
Chain multiple prompt functions together.

#### `@prompt_cache(maxsize=128)`
Cache prompt results for better performance.

### Utilities

#### `clear_llm_res(text, extract_strategy)`
Clean LLM responses by removing code blocks and formatting.

## 🛠️ Advanced Features

### Custom Type Handling

TextLasso automatically handles:
- **Nested dataclasses**: Complex object hierarchies
- **Optional fields**: Fields that may or may not be present
- **Lists and dictionaries**: Collections with proper type conversion
- **Enums**: Automatic enum value conversion
- **Union types**: Multiple possible types for a field
- **Type validation**: Ensure data matches expected types

### Flexible Error Handling

```python
# Configure error behavior
extractor = DataclassConverter(
    strict_mode=False,          # Try conversion instead of failing
    ignore_extra_fields=True,   # Don't error on unexpected fields
    log_level=logging.WARNING   # Control logging verbosity
)
```

### Multiple Parsing Strategies

TextLasso tries multiple strategies to extract JSON:
1. Direct JSON parsing
2. Extract from markdown code blocks
3. Find JSON objects in text
4. Clean and retry with character filtering
5. Extract JSON arrays
6. Custom fallback strategies

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/AzizNadirov/textlasso.git
cd textlasso
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the AI/LLM community
- Inspired by the need for robust text processing in AI applications
- Special thanks to all contributors and users

## 📞 Support

- 📧 Email: aziznadirov@yahoo.com
- 🐛 Issues: [GitHub Issues](https://github.com/AzizNadirov/textlasso/issues)
- 📖 Documentation: [textlasso.readthedocs.io](https://textlasso.readthedocs.io)

---

**TextLasso** - Wrangle your text data with ease! 🤠