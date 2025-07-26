# TextLasso 🤠

[![PyPI version](https://badge.fury.io/py/textlasso.svg)](https://badge.fury.io/py/textlasso)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TextLasso** is a simple Python library for extracting structured data from raw text, with special focus on processing LLM (Large Language Model) responses. Whether you're parsing JSON buried in markdown, extracting data from XML, or need to generate structured prompts for AI models, TextLasso has you covered.

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
llm_response = """
Here's the person data you requested:

\```json
{
    "name": "Alice Johnson",
    "age": 30,
    "email": "alice@company.com", 
    "skills": ["Python", "Machine Learning", "Data Science"]
}
\```

Hope this helps!
"""

person = extract(llm_response, Person, extract_strategy='json')
print(f"Extracted: {person.name}, {person.age} years old")
print(person)
# Extracted: Alice Johnson, 30 years old
# Person(name='Alice Johnson', age=30, email='alice@company.com', skills=['Python', 'Machine Learning', 'Data Science'])
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
markdown_json = """
Here's your product data:
```json
{
    "name": "Wireless Headphones",
    "price": 199.99,
    "category": "Electronics", 
    "in_stock": false,
    "tags": ["wireless", "bluetooth", "noise-canceling"]
}
\```
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
from dataclasses import dataclass
from typing import List, Optional
from textlasso import extract

@dataclass 
class Address:
    street: str
    city: str
    country: str
    zip_code: Optional[str] = None
    
@dataclass
class ResponseAddress:
    address: Address

xml_data = """
<address>
    <street>123 Main St</street>
    <city>San Francisco</city>
    <country>USA</country>
    <zip_code>94102</zip_code>
</address>
"""

response_address = extract(xml_data, ResponseAddress, extract_strategy='xml')
print(f"Address: {response_address.address.street}, {response_address.address.city}, {response_address.address.country}")
# Address: 123 Main St, San Francisco, USA
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

# HQ: Austin, USA
# Employees: 2
#   - Sarah Chen (engineering): Python, React, AWS
#   - Mike Rodriguez (marketing): SEO, Content Strategy, Analytics
```

### 3. LLM Response Cleaning

```python
from textlasso.cleaners import clear_llm_res

# Clean various LLM response formats
messy_responses = [
    "\```json\\n{\"key\": \"value\"}\\n\```",
    "\```\\n{\"key\": \"value\"}\\n\```", 
    "Here's the data: {\"key\": \"value\"} hope it helps!",
    "\```xml\\n<root><item>data</item></root>\\n\```"
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
# Output:
# Analyze this customer review and extract structured feedback

# ## OUTPUT FORMAT REQUIREMENTS

# You must respond with a valid JSON object that follows this exact structure:

# ### Schema: UserFeedback
# - **rating**: int (required)
# - **comment**: str (required)
# - **category**: str (required)
# - **recommended**: bool (required)
# - **issues**: Array of str (optional)


# ### JSON Format Rules:
# - Use proper JSON syntax with double quotes for strings
# - Include all required fields
# - Use null for optional fields that are not provided
# - Arrays should contain objects matching the specified structure
# - Numbers should not be quoted
# - Booleans should be true/false (not quoted)


# ## EXAMPLES

# Here are 2 examples of the expected JSON format:

# ### Example 1:
# ```json
# {
#   "rating": 1,
#   "comment": "example_comment_1",
#   "category": "example_category_1",
#   "recommended": true,
#   "issues": [
#     "example_issues_item_1",
#     "example_issues_item_2"
#   ]
# }
# ```

# ### Example 2:
# ```json
# {
#   "rating": 2,
#   "comment": "example_comment_2",
#   "category": "example_category_2",
#   "recommended": false,
#   "issues": [
#     "example_issues_item_1",
#     "example_issues_item_2",
#     "example_issues_item_3"
#   ]
# }
# ```

# Remember: Your response must be valid JSON that matches the specified structure exactly.
```

#### Using the Decorator for Function Enhancement
If you have a prompt returning functions, you can use the `@structured_output` decorator to automatically enhance your prompts with structure requirements.

```python

from dataclasses import dataclass
from typing import Optional, List

from textlasso import structured_output

@dataclass
class NewsArticle:
    title: str
    summary: str
    category: str
    sentiment: str
    key_points: List[str]
    publication_date: Optional[str] = None

# decorate prompt-returning function
@structured_output(schema=NewsArticle, strategy="xml", example_count=1)
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
print("Enhanced prompt: ", enhanced_prompt)

# Enhanced prompt:  
#     Analyze the following news article and extract key information:
    
#     Article: Breaking: New AI breakthrough announced by researchers...
    
#     Please provide a comprehensive analysis focusing on the main themes,
#     sentiment, and key takeaways.
    


# ## OUTPUT FORMAT REQUIREMENTS

# You must respond with a valid XML object that follows this exact structure:

# ### Schema: NewsArticle
# - **title**: str (required)
# - **summary**: str (required)
# - **category**: str (required)
# - **sentiment**: str (required)
# - **key_points**: Array of str (required)
# - **publication_date**: str (optional)


# ### XML Format Rules:
# - Use proper XML syntax with opening and closing tags
# - Root element should match the main dataclass name
# - Use snake_case for element names
# - For arrays, repeat the element name for each item
# - Use self-closing tags for null/empty optional fields
# - Include all required fields as elements
```

### 6. Real-World Use Cases

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
llm_survey_output = """
Based on the survey response, here's the extracted data:

\```json
{
    "respondent_id": "RESP_001",
    "age_group": "25-34", 
    "satisfaction_rating": 4,
    "feedback": "Great service overall, but could improve response time",
    "would_recommend": true,
    "improvement_areas": ["response_time", "pricing"]
}
\```

This response indicates positive sentiment with specific improvement suggestions.
"""

survey = extract(llm_survey_output, SurveyResponse, extract_strategy='json')
print(survey)
# SurveyResponse(respondent_id='RESP_001', age_group='25-34', satisfaction_rating=4, feedback='Great service overall, but could improve response time', would_recommend=True, improvement_areas=['response_time', 'pricing'])
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

@structured_output(schema=ProductReview, strategy="xml")
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
# review = extract(llm_response, ProductReview, extract_strategy='xml')
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

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the AI/LLM community
- Inspired by the need for robust text processing in AI applications
- Special thanks to all contributors and users

## 📞 Support

- 📧 Email: aziznadirov@yahoo.com
- 🐛 Issues: [GitHub Issues](https://github.com/AzizNadirov/textlasso/issues)

---

**TextLasso** - Wrangle your text data with ease! 🤠