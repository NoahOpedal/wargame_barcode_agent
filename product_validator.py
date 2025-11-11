import os
import re
import time
import requests
from bs4 import BeautifulSoup
from swarm import Swarm, Agent
from typing import List, Dict, Any
import json
from urllib.parse import quote_plus, urljoin, urlparse

class ProductValidator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ProductValidator/1.0; +https://github.com/)'
        })
        
        # Static links for wargaming/trading sites - left blank for user customization
        self.default_sites = [
            # Add your target websites here
            "https://gateway-games-ltd.mybigcommerce.com/",
            "https://www.alphaomegahobby.com/",
            "https://www.meeplemart.com/"
        ]
        
        # Static regex patterns for your specific SKU formats
        self.default_code_patterns = [
            "regex:[0-9]{2}-[0-9]{2}",              # XX-XX format
            "regex:[0-9]{3}-[0-9]{2}",              # XXX-XX format  
            "regex:[0-9]{2}-[0-9]{3}",              # XX-XXX format
            "regex:[0-9]{3}-[0-9]{3}",              # XXX-XXX format
            "regex:501192191[0-9]{4}"               # 13 digit barcode starting with 501192191
        ]
        
    def search_product_codes_on_sites(self, product_name: str, target_sites: List[str], code_patterns: List[str]) -> Dict[str, Any]:
        """
        Search for product codes on specific sites
        
        Args:
            product_name: Name of the product to search for
            target_sites: List of URLs to search
            code_patterns: List of regex patterns or specific sequences to find
        """
        results = {
            'product_name': product_name,
            'found_codes': [],
            'site_results': {}
        }
        
        for site_url in target_sites:
            try:
                # Search for the product on the site
                site_result = self._search_site_for_product(site_url, product_name, code_patterns)
                results['site_results'][site_url] = site_result
                
                # Add any found codes to the main list
                if site_result['codes_found']:
                    results['found_codes'].extend(site_result['codes_found'])
                    
            except Exception as e:
                results['site_results'][site_url] = {
                    'error': f"Failed to search {site_url}: {str(e)}",
                    'codes_found': []
                }
                
        # Remove duplicate codes
        results['found_codes'] = list(set(results['found_codes']))
        
        return results
    
    def _search_site_for_product(self, site_url: str, product_name: str, code_patterns: List[str]) -> Dict[str, Any]:
        """Search a specific site for product and extract codes"""
        try:
            # Try different search approaches
            search_urls = self._generate_search_urls(site_url, product_name)
            
            all_codes_found = []
            pages_searched = []
            
            for search_url in search_urls[:3]:  # Limit to 3 search attempts per site
                try:
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text()
                    
                    # Search for codes using patterns
                    found_codes = self._extract_codes_from_text(text_content, code_patterns)
                    all_codes_found.extend(found_codes)
                    
                    pages_searched.append(search_url)
                    
                    # Add delay between requests
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error searching {search_url}: {e}")
                    continue
            
            return {
                'codes_found': list(set(all_codes_found)),
                'pages_searched': pages_searched,
                'total_codes': len(set(all_codes_found))
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'codes_found': [],
                'pages_searched': []
            }
    
    def _generate_search_urls(self, site_url: str, product_name: str) -> List[str]:
        """Generate different search URL possibilities for a site"""
        search_urls = []
        encoded_name = quote_plus(product_name)
        
        # Add the base site URL
        search_urls.append(site_url)
        
        # Try common search patterns
        base_domain = f"{urlparse(site_url).scheme}://{urlparse(site_url).netloc}"
        
        search_patterns = [
            f"{site_url}?search={encoded_name}",
            f"{site_url}?q={encoded_name}",
            f"{base_domain}/search?q={encoded_name}",
            f"{base_domain}/search/{encoded_name}",
            f"{site_url}/{encoded_name}",
        ]
        
        search_urls.extend(search_patterns)
        
        return search_urls
    
    def _extract_codes_from_text(self, text: str, code_patterns: List[str]) -> List[str]:
        """Extract codes from text using provided patterns"""
        found_codes = []
        
        for pattern in code_patterns:
            try:
                if pattern.startswith('regex:'):
                    # Use as regex pattern
                    regex_pattern = pattern[6:]  # Remove 'regex:' prefix
                    matches = re.findall(regex_pattern, text, re.IGNORECASE)
                    found_codes.extend(matches)
                else:
                    # Use as literal string search
                    if pattern.lower() in text.lower():
                        # Try to extract the code with some context
                        # Look for alphanumeric codes near the pattern
                        context_pattern = f"{re.escape(pattern)}.{{0,50}}([A-Z0-9]{{4,15}})"
                        matches = re.findall(context_pattern, text, re.IGNORECASE)
                        found_codes.extend(matches)
                        
                        # Also look for codes before the pattern
                        reverse_pattern = f"([A-Z0-9]{{4,15}}).{{0,50}}{re.escape(pattern)}"
                        matches = re.findall(reverse_pattern, text, re.IGNORECASE)
                        found_codes.extend(matches)
            except Exception as e:
                print(f"Error processing pattern '{pattern}': {e}")
                continue
        
        return found_codes
    
    def web_search_validation(self, product_name: str, product_codes: List[str], min_matches: int = 3) -> Dict[str, Any]:
        """
        Search the web to validate product codes by looking for matches
        
        Args:
            product_name: Name of the product
            product_codes: List of codes found for the product
            min_matches: Minimum number of matches required for validation
        """
        validation_results = {
            'product_name': product_name,
            'codes_validated': {},
            'overall_validation': False
        }
        
        validated_codes = []
        
        for code in product_codes:
            search_query = f'"{product_name}" "{code}"'
            matches = self._search_web_for_matches(search_query)
            
            validation_results['codes_validated'][code] = {
                'matches_found': len(matches),
                'is_validated': len(matches) >= min_matches,
                'sample_sources': matches[:5]  # Keep top 5 sources
            }
            
            if len(matches) >= min_matches:
                validated_codes.append(code)
        
        validation_results['overall_validation'] = len(validated_codes) > 0
        validation_results['validated_codes'] = validated_codes
        
        return validation_results
    
    def _search_web_for_matches(self, query: str) -> List[Dict[str, str]]:
        """
        Search the web for matches (using DuckDuckGo as example)
        Note: In production, you'd want to use proper search APIs
        """
        matches = []
        
        try:
            # Using DuckDuckGo for web search
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results
            result_divs = soup.find_all('div', {'class': 'result'})
            
            for div in result_divs[:10]:  # Limit to top 10 results
                title_elem = div.find('a', {'class': 'result__a'})
                snippet_elem = div.find('div', {'class': 'result__snippet'})
                
                if title_elem and snippet_elem:
                    matches.append({
                        'title': title_elem.get_text().strip(),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text().strip()
                    })
            
            time.sleep(2)  # Be respectful with requests
            
        except Exception as e:
            print(f"Web search error: {e}")
        
        return matches
    
    def search_with_defaults(self, product_name: str, target_sites: List[str] = None, code_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Search using default sites and patterns, with optional overrides
        
        Args:
            product_name: Name of the product to search for
            target_sites: Optional list of URLs to search (uses defaults if None)
            code_patterns: Optional list of patterns to search (uses defaults if None)
        """
        sites_to_use = target_sites if target_sites is not None else self.default_sites
        patterns_to_use = code_patterns if code_patterns is not None else self.default_code_patterns
        
        return self.search_product_codes_on_sites(product_name, sites_to_use, patterns_to_use)
        

# Agent Functions
def search_sites_for_codes(product_name: str, target_sites: str, code_patterns: str) -> str:
    """
    Search target sites for product codes
    
    Args:
        product_name: Name of the product to search for
        target_sites: Comma-separated list of URLs to search
        code_patterns: Comma-separated list of patterns to search for
    """
    validator = ProductValidator()
    
    # Parse inputs
    sites_list = [site.strip() for site in target_sites.split(',')]
    patterns_list = [pattern.strip() for pattern in code_patterns.split(',')]
    
    result = validator.search_product_codes_on_sites(product_name, sites_list, patterns_list)
    
    return json.dumps(result, indent=2)

def validate_codes_on_web(product_name: str, product_codes: str, min_matches: int = 3) -> str:
    """
    Validate product codes by searching the web for matches
    
    Args:
        product_name: Name of the product
        product_codes: Comma-separated list of codes to validate
        min_matches: Minimum number of web matches required
    """
    validator = ProductValidator()
    
    # Parse codes
    codes_list = [code.strip() for code in product_codes.split(',')]
    
    result = validator.web_search_validation(product_name, codes_list, min_matches)
    
    return json.dumps(result, indent=2)

def process_product_list(product_list: str, target_sites: str, code_patterns: str, min_matches: int = 3) -> str:
    """
    Process a list of products through the complete validation pipeline
    
    Args:
        product_list: Newline-separated list of product names
        target_sites: Comma-separated list of URLs to search
        code_patterns: Comma-separated list of patterns to search for
        min_matches: Minimum number of web matches required
    """
    validator = ProductValidator()
    
    # Parse inputs
    products = [product.strip() for product in product_list.split('\n') if product.strip()]
    sites_list = [site.strip() for site in target_sites.split(',')]
    patterns_list = [pattern.strip() for pattern in code_patterns.split(',')]
    
    results = []
    
    for product_name in products:
        print(f"Processing: {product_name}")
        
        # Step 1: Search sites for codes
        site_search_result = validator.search_product_codes_on_sites(product_name, sites_list, patterns_list)
        
        # Step 2: Validate found codes on the web
        if site_search_result['found_codes']:
            validation_result = validator.web_search_validation(
                product_name, 
                site_search_result['found_codes'], 
                min_matches
            )
        else:
            validation_result = {
                'product_name': product_name,
                'codes_validated': {},
                'overall_validation': False,
                'message': 'No codes found on target sites'
            }
        
        # Combine results
        combined_result = {
            'product_name': product_name,
            'site_search': site_search_result,
            'web_validation': validation_result
        }
        
        results.append(combined_result)
    
    return json.dumps(results, indent=2)

def search_with_default_settings(product_name: str, additional_sites: str = "", additional_patterns: str = "") -> str:
    """
    Search for product codes using built-in default sites and patterns
    
    Args:
        product_name: Name of the product to search for
        additional_sites: Optional comma-separated additional sites to add to defaults
        additional_patterns: Optional comma-separated additional patterns to add to defaults
    """
    validator = ProductValidator()
    
    # Use defaults, but add any additional sites/patterns if provided
    sites_to_use = validator.default_sites.copy()
    patterns_to_use = validator.default_code_patterns.copy()
    
    # Parse and add additional inputs
    if additional_sites.strip():
        extra_sites = [site.strip() for site in additional_sites.split(',') if site.strip()]
        sites_to_use.extend(extra_sites)
        
    if additional_patterns.strip():
        extra_patterns = [pattern.strip() for pattern in additional_patterns.split(',') if pattern.strip()]
        patterns_to_use.extend(extra_patterns)
    
    result = validator.search_product_codes_on_sites(product_name, sites_to_use, patterns_to_use)
    
    return json.dumps(result, indent=2)

# Create the agents
site_scraper_agent = Agent(
    name="Site Scraper",
    instructions="""You are a site scraping specialist. You search specific websites for products and extract product codes based on provided patterns. You can:
    - Search multiple sites for product information
    - Extract codes using regex patterns or text sequences
    - Handle different site structures and search methods
    - Return structured results with found codes
    - Use built-in default settings for common SKU patterns (XX-XX, XXX-XX, etc.) and barcodes starting with 501192191""",
    functions=[search_sites_for_codes, search_with_default_settings]
)

web_validator_agent = Agent(
    name="Web Validator", 
    instructions="""You validate product codes by searching the web for matches. You can:
    - Search the web for product name + code combinations
    - Count the number of matches found
    - Determine if codes meet minimum validation thresholds
    - Provide source information for validation""",
    functions=[validate_codes_on_web]
)

product_processor_agent = Agent(
    name="Product Processor",
    instructions="""You are a product processing orchestrator. You manage the complete product validation pipeline by:
    - Processing lists of product names
    - Coordinating site scraping and web validation
    - Providing comprehensive reports on product code validation
    - Managing the workflow between different validation steps
    - Using built-in default SKU patterns and barcode formats when no specific patterns are provided""",
    functions=[process_product_list, search_sites_for_codes, search_with_default_settings, validate_codes_on_web]
)

if __name__ == "__main__":
    # Example usage
    client = Swarm()
    
    # Set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    print("Product Code Validation Agent System Ready!")
    print("\nExample usage:")
    print("1. Process a product list with site scraping and web validation")
    print("2. Search specific sites for codes")
    print("3. Validate codes on the web")
    
    # Example interaction
    response = client.run(
        agent=product_processor_agent,
        messages=[{
            "role": "user",
            "content": """I need to validate these products:
iPhone 15 Pro
Samsung Galaxy S24
Google Pixel 8

Please search these sites for product codes:
https://www.apple.com,https://www.samsung.com,https://store.google.com

Look for these patterns:
regex:[A-Z]{2}[0-9]{4,6},regex:MODEL[0-9]+,SKU,Part Number

Then validate any found codes by searching the web for at least 3 matches."""
        }]
    )
    
    print("\nAgent Response:")
    print(response.messages[-1]["content"])
