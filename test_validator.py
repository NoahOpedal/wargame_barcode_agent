"""
Simple test script for the Product Validation Agent System
"""

import os
from swarm import Swarm
from product_validator import product_processor_agent, site_scraper_agent, web_validator_agent

def main():
    # Initialize the Swarm client
    client = Swarm()
    
    print("=== Product Code Validation Agent System ===\n")
    
    # Example 1: Search specific sites for codes
    print("Example 1: Searching sites for product codes")
    print("-" * 50)
    
    response1 = client.run(
        agent=site_scraper_agent,
        messages=[{
            "role": "user", 
            "content": """Search for product codes for "iPhone 15" on these sites:
            https://www.apple.com,https://www.bestbuy.com
            
            Look for these patterns:
            regex:[A-Z]{2}[0-9]{4,6},Model,SKU"""
        }]
    )
    
    print("Response:", response1.messages[-1]["content"])
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Validate codes on web
    print("Example 2: Validating codes on the web")
    print("-" * 50)
    
    response2 = client.run(
        agent=web_validator_agent,
        messages=[{
            "role": "user",
            "content": """Validate these codes for "iPhone 15 Pro":
            A2848,MLX73LL/A,MPXT3LL/A
            
            Check if each code appears at least 3 times on the web with this product."""
        }]
    )
    
    print("Response:", response2.messages[-1]["content"])
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: Full pipeline processing
    print("Example 3: Complete product validation pipeline")
    print("-" * 50)
    
    product_list = """iPhone 15 Pro
Samsung Galaxy S24 Ultra
MacBook Pro M3"""

    target_sites = "https://www.apple.com,https://www.samsung.com,https://www.bestbuy.com"
    code_patterns = "regex:[A-Z]{1,3}[0-9]{3,6},Model,SKU,Part"
    
    response3 = client.run(
        agent=product_processor_agent,
        messages=[{
            "role": "user",
            "content": f"""Process this product list through the complete validation pipeline:

Products:
{product_list}

Target Sites: {target_sites}
Code Patterns: {code_patterns}
Minimum Web Matches: 3

Please search the sites for codes, then validate any found codes on the web."""
        }]
    )
    
    print("Response:", response3.messages[-1]["content"])

def quick_test():
    """Quick test with user input product name"""
    print("=== Quick Product Search Test ===")
    
    from product_validator import search_with_default_settings
    
    # Get product name from user input
    product_name = input("Enter product name to search: ").strip()
    
    if not product_name:
        product_name = "Warhammer 40K"  # fallback default
        print(f"No input provided, using default: {product_name}")
    
    print(f"\n🔍 Searching for: {product_name}")
    
    # Test with user-provided product name
    result = search_with_default_settings(product_name)
    print("Search Result:")
    print(result)

if __name__ == "__main__":
    # Run quick test first
    quick_test()
    
    # Then run full tests if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("Or add it to your .zshrc file")
        print("\nYou can still test the scraping functions directly though!")
        
        # Test direct function call
        print("\n🧪 Testing direct function call:")
        from product_validator import ProductValidator
        
        validator = ProductValidator()
        result = validator.search_product_codes_on_sites(
            "iPhone 15",
            ["https://www.apple.com"],
            ["regex:[A-Z]{2}[0-9]{4}", "Model"]
        )
        print("Direct test result:", result)
    else:
        main()
