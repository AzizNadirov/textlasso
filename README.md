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

#### Enhancing Prompts

```python
from dataclasses import dataclass
from textlasso import generate_structured_prompt, structured_output

# 1. Response Data Class
@dataclass
class Article:
    title_eng: str
    title_az: str
    content_eng: str
    content_az: str

@dataclass
class ResponseArticle:
    article: Article


original_prompt = "You are a professional copywriter-bot. Generate me an article"
enhanced_prompt = generate_structured_prompt(prompt=original_prompt, 
                                    schema=ResponseArticle, 
                                    strategy="xml")

# prompt
print(enhanced_prompt)   # <Prompt: schema='<class '__main__.ResponseArticle'>', strategy='xml', has_data='False'>
## enhanced prompt:
print(enhanced_prompt.prompt)
# You are a professional copywriter-bot. Generate me an article


# ## OUTPUT FORMAT REQUIREMENTS

# You must respond with a valid XML object that follows this exact structure:

# ### Schema: ResponseArticle
# - **article**: Object (Article) (required)
#   Fields:
#     - **title_eng**: str (required)
#     - **title_az**: str (required)
#     - **content_eng**: str (required)
#     - **content_az**: str (required)


# ### XML Format Rules:
# - Use proper XML syntax with opening and closing tags
# - Root element should match the main dataclass name
# - Use snake_case for element names
# - For arrays, repeat the element name for each item
# - Use self-closing tags for null/empty optional fields
# - Include all required fields as elements


# ## EXAMPLES

# Here are 2 examples of the expected XML format:

# ### Example 1:
# ```xml
# <response_article>
#   <article>
#     <title_eng>example_title_eng_1</title_eng>
#     <title_az>example_title_az_1</title_az>
#     <content_eng>example_content_eng_1</content_eng>
#     <content_az>example_content_az_1</content_az>
#   </article>
# </response_article>

# ```

# ### Example 2:
# ```xml
# <response_article>
#   <article>
#     <title_eng>example_title_eng_2</title_eng>
#     <title_az>example_title_az_2</title_az>
#     <content_eng>example_content_eng_2</content_eng>
#     <content_az>example_content_az_2</content_az>
#   </article>
# </response_article>

# ```

# Remember: Your response must be valid XML that matches the specified structure exactly.
```

If you have a prompt-returning function, you can use the `structured_output` decorator to automatically enhance it with structure requirements:

```python

@structured_output(ResponseArticle, "xml")
def get_prompt(title: str):
    return f"Hi, give me a article about {title}"

prompt = get_prompt("Agile Investing: Profiting from Current Tech Surges and Global Currency Dynamics")
```

Bot `generate_structured_prompt` and `structured_output` returns a `Prompt` object, which has a `prompt` attribute containing the enhanced prompt, `schema` attribute containing the dataclass, and `strategy` attribute containing the extraction strategy. 

**Extraction**: the best part - you can extract data using your `prompt` object, without having to worry about the structure requirements:

```python

# response_txt = some_llm.invoke(prompt.prompt)
response_txt = """Ofcourse here is the article: <response_article>
  <article>
    <title_eng>Agile Investing: Profiting from Current Tech Surges and Global Currency Dynamics</title_eng>
    <title_az>Çevik İnvestisiya: Hazırkı Texnologiya Artımlarından və Qlobal Valyuta Dinamikalarından Faydalanma</title_az>
    <content_eng>
      Hello, aspiring investors! Invesbot here, ready to guide you through the ever-shifting landscape of finance. Today, we're diving into the exciting world of "agile investing," a strategy designed to help you thrive amidst current tech surges and dynamic global currency movements. Remember, investment is dynamic, so stay tuned!

      ## The Power of Agile Investing

      Traditional "buy-and-hold" strategies might be comforting, but in today's fast-paced markets, agility is key. Agile investing emphasizes flexibility and quick decision-making to respond to rapid market changes. It's about actively managing your portfolio and keenly understanding market conditions to capitalize on opportunities and mitigate risks.

      ### Key Principles of Agile Investing:

      *   **Active Management:** Forget setting it and forgetting it. Agile investing requires continuous monitoring of market trends.
      *   **Technical Analysis:** Use tools like moving averages and Bollinger Bands to identify optimal entry and exit points.
      *   **Diversification:** Spread your investments across different asset classes to reduce risk, especially in volatile markets.
      *   **Stop-Loss Orders:** Implement automated instructions to sell a security when it reaches a certain price, limiting potential losses.
      *   **Short Selling:** Profit from declining prices by borrowing shares, selling them high, and repurchasing them low.

      ## Navigating the Tech Surge: Where to Invest

      The technology sector continues its rapid evolution, fueled by advancements in Artificial Intelligence (AI), cybersecurity, climate tech, and more. The investment climate for frontier technologies has stabilized and, in many cases, rebounded in 2024, with levels of equity investment increasing in areas like cloud and edge computing, bioengineering, and space technologies. Worldwide spending on AI is projected to grow significantly, with a compound annual growth rate of 29% from 2024 to 2028.

      ### Hot Tech Sectors and Companies to Watch:

      *   **Artificial Intelligence (AI):** AI is powering innovation across industries, with significant investment in AI infrastructure. Hybrid AI, which combines various AI methodologies for more versatile systems, is moving beyond experimentation. Companies like Innodata are key in providing high-quality training data for generative AI systems.
      *   **Data Centers & Cloud Computing:** The expansion of data centers and public cloud services is a critical trend, driven by AI innovation. Global spending on public cloud services is projected to reach US$805 billion in 2024 and double by 2028.
      *   **Cybersecurity:** With escalating threats and a widening attack surface (IoT, generative AI, cloud computing), cybersecurity is a critical tech priority. The global cost of cybercrime is projected to reach US$10.5 trillion in 2025. The market for security products is also growing rapidly, expected to reach US$200 billion by 2028.
      *   **Quantum Computing:** This sector has seen an explosion of interest and significant rallies in emerging quantum stocks.
      *   **Semiconductors:** This industry has benefited from major corporate investments in AI infrastructure, and the "picks and shovels" phase of generative AI continues to favor semiconductor and hardware companies.
      *   **Sustainable Technologies/Climate Tech:** Solutions from carbon capture to energy-efficient building materials are gaining momentum, fueled by a growing focus on sustainable business and combating climate change.
      *   **Supply Chain Innovation:** Enhancing efficiency and transparency through digital freight-forwarding services and real-time tracking are key.

      For those looking at specific stocks, the "Magnificent Seven" (Apple, Microsoft, Alphabet, Amazon, NVIDIA, Meta Platforms, and either Tesla or Broadcom) continue to lead the market in innovation. Some of the best-performing tech stocks by one-year return as of July 2025 include Palantir Technologies (PLTR), MicroStrategy (MSTR), Fortinet (FTNT), Shopify (SHOP), Broadcom (AVGO), Zscaler (ZS), and Cisco Systems (CSCO).

      ## Understanding Global Currency Dynamics

      Currency fluctuations can significantly impact your investment returns, especially when investing globally. Changes in exchange rates can diminish or enhance your returns when converting foreign asset values back to your home currency. Even if your portfolio consists only of domestic shares, there can be indirect exposure to currency risk if those companies conduct significant international business.

      ### Factors Driving Currency Fluctuations:

      *   **Economic Strength:** Confidence in a country's economic prospects typically leads to increased demand for its currency, pushing its value up.
      *   **Interest Rates:** Higher interest rates can make investments in a country more attractive, drawing foreign capital and potentially increasing the domestic currency's value. However, very high interest rates can also slow economic growth.
      *   **Trade Balances:** A country with more exports than imports may see its currency appreciate due to higher demand for its goods and, consequently, its currency.
      *   **Political Environment and Market Sentiment:** Big global events, political instability, and overall investor attitude can create sudden currency swings.

      ### Strategies for Managing Currency Risk:

      *   **Hedging Techniques:** Use financial tools like forward contracts, currency futures, or options to lock in an exchange rate and reduce uncertainty.
      *   **Diversifying Currency Exposure:** Spread investments across different currencies. This way, the fall of one currency might be balanced by the rise of another.
      *   **Currency-Hedged Investment Vehicles:** Consider mutual funds or ETFs designed to automatically offset currency fluctuations.
      *   **Multi-Currency Accounts:** Holding different currencies can help manage exchange risk.
      *   **Stay Informed:** Use tools and apps to track currency trends and market news to make timely decisions.
      *   **Invest in Strong Economies/Stable Currencies:** Choosing countries with stable currencies and strong economies can reduce the impact of extreme fluctuations. Developed markets generally offer more currency stability.

      Agile investing in a world of tech surges and currency dynamics requires constant vigilance and quick decision-making. By understanding the underlying trends and employing smart strategies, you can position yourself to potentially turn market volatility into profitable opportunities. Stay informed, stay agile, and happy investing!
    </content_eng>
    <content_az>
      Salam, gələcək investorlar! Qarşınızda İnvesbot var, maliyyənin daim dəyişən mənzərəsində sizə yol göstərməyə hazıram. Bu gün biz "çevik investisiya"nın maraqlı dünyasına baş vururuq; bu strategiya sizə mövcud texnoloji inkişaflar və dinamik qlobal valyuta hərəkətləri fonunda uğur qazanmağa kömək etmək üçün nəzərdə tutulub. Unutmayın, investisiya dinamikdir, ona görə də bizi izləyin!

      ## Çevik İnvestisiyanın Gücü

      Ənənəvi "al-saxla" strategiyaları rahat ola bilər, lakin müasir sürətlə inkişaf edən bazarlarda çeviklik əsasdır. Çevik investisiya sürətli bazar dəyişikliklərinə reaksiya vermək üçün çevikliyi və sürətli qərar qəbul etməyi vurğulayır. Bu, fürsətlərdən yararlanmaq və riskləri azaltmaq üçün portfelinizi aktiv şəkildə idarə etmək və bazar şərtlərini dərindən anlamaq deməkdir.

      ### Çevik İnvestisiyanın Əsas Prinsipləri:

      *   **Aktiv İdarəetmə:** Unudun ki, investisiyanı bir dəfə qurub sonra yaddan çıxarmaq olar. Çevik investisiya bazar tendensiyalarının davamlı izlənilməsini tələb edir.
      *   **Texniki Analiz:** Optimal giriş və çıxış nöqtələrini müəyyən etmək üçün hərəkətli ortalamalar və Bollinger Bantları kimi alətlərdən istifadə edin.
      *   **Diversifikasiya:** Xüsusilə dəyişkən bazarlarda riski azaltmaq üçün investisiyalarınızı müxtəlif aktiv siniflərinə yayın.
      *   **Stop-Loss Əmrləri:** Potensial itkiləri məhdudlaşdırmaq üçün qiymət müəyyən bir həddə çatdıqda qiymətli kağızı satmaq üçün avtomatlaşdırılmış təlimatlar tətbiq edin.
      *   **Qısa Satış (Short Selling):** Səhmləri borc götürərək, yüksək qiymətə sataraq və aşağı qiymətə yenidən alaraq qiymət düşmələrindən qazanc əldə edin.

      ## Texnologiya Artımı ilə Naviqasiya: Harada İnvestisiya Etməli

      Texnologiya sektoru Süni İntellekt (AI), kiber təhlükəsizlik, iqlim texnologiyası və digər sahələrdəki irəliləyişlərlə sürətli inkişafını davam etdirir. Öncül texnologiyalar üçün investisiya iqlimi sabitləşib və bir çox hallarda 2024-cü ildə bərpa olunub, bulud və kənar hesablama, bio-mühəndislik və kosmik texnologiyalar kimi sahələrdə səhm investisiyaları artıb. Süni İntellektə qlobal xərclərin 2024-cü ildən 2028-ci ilə qədər 29% illik mürəkkəb artım tempi ilə əhəmiyyətli dərəcədə artacağı proqnozlaşdırılır.

      ### İzlənilməsi Vacib Olan İsti Texnologiya Sektorları və Şirkətlər:

      *   **Süni İntellekt (AI):** AI sənayelər üzrə innovasiyalara təkan verir, AI infrastruktura əhəmiyyətli investisiyalar qoyulur. Daha çox yönlü sistemlər üçün müxtəlif AI metodologiyalarını birləşdirən Hibrid AI, eksperimentlərdən kənara çıxır. Innodata kimi şirkətlər generativ AI sistemləri üçün yüksək keyfiyyətli təlim məlumatları təmin etməkdə əsas rol oynayır.
      *   **Məlumat Mərkəzləri və Bulud Hesablama:** Məlumat mərkəzlərinin və ictimai bulud xidmətlərinin genişlənməsi, AI innovasiyası tərəfindən idarə olunan kritik bir tendensiyadır. İctimai bulud xidmətlərinə qlobal xərclərin 2024-cü ildə 805 milyard ABŞ dollarına çatacağı və 2028-ci ilə qədər ikiqat artacağı proqnozlaşdırılır.
      *   **Kiber Təhlükəsizlik:** Artan təhdidlər və genişlənən hücum səthi (IoT, generativ AI, bulud hesablama) ilə kiber təhlükəsizlik kritik bir texnologiya prioritetidir. Kiber cinayətkarlığın qlobal xərcinin 2025-ci ildə 10.5 trilyon ABŞ dollarına çatacağı proqnozlaşdırılır. Təhlükəsizlik məhsulları bazarı da sürətlə böyüyür, 2028-ci ilə qədər 200 milyard ABŞ dollarına çatacağı gözlənilir.
      *   **Kvant Kompüteri:** Bu sektor maraqda partlayış və ortaya çıxan kvant səhmlərində əhəmiyyətli yüksəlişlər görüb.
      *   **Yarımkeçiricilər:** Bu sənaye AI infrastrukturuna qoyulan əsas korporativ investisiyalardan faydalanıb və generativ AI-nin "kürək və qazma" mərhələsi yarımkeçirici və hardware şirkətlərini dəstəkləməyə davam edir.
      *   **Davamlı Texnologiyalar/İqlim Texnologiyası:** Karbon tutulmasından enerji səmərəli tikinti materiallarına qədər həllər, davamlı biznesə və iqlim dəyişikliyi ilə mübarizəyə artan diqqət sayəsində sürət qazanır.
      *   **Təchizat Zənciri İnnovasiyası:** Rəqəmsal yüklərin ekspeditor xidmətləri və real-vaxt izləmə vasitəsilə səmərəliliyin və şəffaflığın artırılması əsasdır.

      Müəyyən səhmlərə baxanlar üçün "Möhtəşəm Yeddi" (Apple, Microsoft, Alphabet, Amazon, NVIDIA, Meta Platforms və ya Tesla, ya da Broadcom) innovasiya sahəsində bazara rəhbərlik etməyə davam edir. 2025-ci ilin iyul ayına olan məlumata görə, bir illik gəlirlə ən yaxşı nəticə göstərən texnologiya səhmlərindən bəziləri Palantir Technologies (PLTR), MicroStrategy (MSTR), Fortinet (FTNT), Shopify (SHOP), Broadcom (AVGO), Zscaler (ZS) və Cisco Systems (CSCO)-dur.

      ## Qlobal Valyuta Dinamikalarını Anlamaq

      Valyuta dəyişkənliyi, xüsusilə qlobal səviyyədə investisiya edərkən, investisiya gəlirlərinizə əhəmiyyətli dərəcədə təsir göstərə bilər. Valyuta məzənnələrindəki dəyişikliklər xarici aktiv dəyərlərini öz valyutanıza çevirərkən gəlirlərinizi azalda və ya artıra bilər. Portfeliniz yalnız yerli səhmlərdən ibarət olsa belə, həmin şirkətlər əhəmiyyətli beynəlxalq biznes fəaliyyəti göstərirsə, dolayı valyuta riski mövcud ola bilər.

      ### Valyuta Dəyişikliklərinə Təsir Edən Faktorlar:

      *   **İqtisadi Güc:** Bir ölkənin iqtisadi perspektivlərinə inam, adətən valyutasına tələbatın artmasına və dəyərinin yüksəlməsinə səbəb olur.
      *   **Faiz Dərəcələri:** Daha yüksək faiz dərəcələri bir ölkədə investisiyaları daha cəlbedici edə bilər, xarici kapitalı cəlb edərək yerli valyutanın dəyərini potensial olaraq artıra bilər. Bununla belə, çox yüksək faiz dərəcələri iqtisadi artımı da ləngidə bilər.
      *   **Ticarət Balansları:** İxracatı idxalatından çox olan bir ölkə, mallarına və nəticədə valyutasına olan yüksək tələbat səbəbindən valyutasının dəyər qazanmasına səbəb ola bilər.
      *   **Siyasi Mühit və Bazar Duyğusu:** Böyük qlobal hadisələr, siyasi qeyri-sabitlik və ümumi investor münasibəti qəfil valyuta dəyişiklikləri yarada bilər.

      ### Valyuta Riskini İdarə Etmək üçün Strategiyalar:

      *   **Hedcinq Texnikaları:** Mübadilə məzənnəsini kilidləmək və qeyri-müəyyənliyi azaltmaq üçün forvard müqavilələri, valyuta fyuçersləri və ya opsionlar kimi maliyyə alətlərindən istifadə edin.
      *   **Valyuta Ekspozisiyasının Diversifikasiyası:** İnvestisiyaları müxtəlif valyutalara yayın. Bu yolla, bir valyutanın düşməsi başqasının yüksəlməsi ilə tarazlaşdırıla bilər.
      *   **Valyuta Hedcinqli İnvestisiya Vasitələri:** Valyuta dəyişkənliyini avtomatik olaraq kompensasiya etmək üçün nəzərdə tutulmuş qarşılıqlı fondları və ya ETF-ləri nəzərdən keçirin.
      *   **Çox Valyutalı Hesablar:** Fərqli valyutaları saxlamaq mübadilə riskini idarə etməyə kömək edə bilər.
      *   **Məlumatlı Olun:** Vaxtında qərarlar qəbul etmək üçün valyuta tendensiyalarını və bazar xəbərlərini izləmək üçün alətlərdən və proqramlardan istifadə edin.
      *   **Güclü İqtisadiyyatlara/Stabil Valyutalara İnvestisiya Edin:** Stabil valyutaları və güclü iqtisadiyyatları olan ölkələri seçmək, ekstremal dəyişikliklərin təsirini azalda bilər. İnkişaf etmiş bazarlar adətən daha çox valyuta sabitliyi təklif edir.

      Texnologiya inkişafının və valyuta dinamikasının hökm sürdüyü bir dünyada çevik investisiya daimi ayıqlıq və sürətli qərar qəbul etməyi tələb edir. Əsas tendensiyaları başa düşərək və ağıllı strategiyalar tətbiq edərək, bazar dəyişkənliyini gəlirli fürsətlərə çevirmək üçün özünüzü mövqeləndirə bilərsiniz. Məlumatlı qalın, çevik olun və uğurlu investisiyalar!
    </content_az>
  </article>
</response_article>
I hope you liked it!
"""

# Yeah, big text... It is LLM response to our enhanced prompt. We are going to use this text to extract some information about the product.
print(data.article.title_az)
# "Çevik İnvestisiya: Hazırkı Texnologiya Artımlarından və Qlobal Valyuta Dinamikalarından Faydalanma"
# 
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

Prompt Generator(actually - builder) functions return `Prompt` object, which contains expected data structure, prompt and shortcut for data extraction.
- `prompt.prompt` - enhanced prompt;
- `prompt.prompt_original` - original prompt;
- `prompt.schema` - dataclass with expected structure;
- `prompt.strategy` - extraction strategy (json/xml);
- `prompt.extract("<text to extract>")` - extract data from prompt;
- `prompt.data` - initially is `None`, then `.extract()` overwrites it;
- `prompt.has_data()` - returns True if `prompt.prompt` contains data;


**Note:** `prompt.extract()` method is a shortcut for `textlasso.extract()` function.


```python
from textlasso import generate_structured_prompt

@dataclass
class UserFeedback:
    rating: int
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

print(prompt.prompt)
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
print("Enhanced prompt: ", enhanced_prompt.prompt)

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
# llm = some LLM model
llm_response = llm.invoke(extraction_prompt.prompt)
review = extract(llm_response, ProductReview, extract_strategy='xml')
# or
extraction_prompt.extract(llm_response)
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