#!/usr/bin/env python3
"""
Interactive Product Search Tool
"""

import sys
from product_validator import search_with_default_settings

def main():
    """Main function - handles both interactive and command line modes"""
    
    # Check if command line arguments were provided
    if len(sys.argv) > 1:
        # Option 2: Command line arguments
        product_name = " ".join(sys.argv[1:])
        print(f"Searching for: {product_name}")
        print("-" * 50)
        
        try:
            result = search_with_default_settings(product_name)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
    
    else:
        # Option 1: Interactive mode
        print("Wargame Product Code Validator")
        print("Enter product name to search (or 'exit' to quit)")
        print("=" * 40)
        
        while True:
            product_name = input("\nProduct name: ").strip()
            
            if product_name.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
                
            if not product_name:
                print("Please enter a product name!")
                continue
                
            print(f"\nSearching for '{product_name}'...")
            print("-" * 50)
            
            try:
                result = search_with_default_settings(product_name)
                print(result)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
