# Wargame Trader - Product Validator Agent

An interactive AI-powered agent for validating and searching wargaming products using web scraping and product code extraction.

## Prerequisites

Before running this application, you need to have the following programs installed:

### Required Software

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version` or `python3 --version`

2. **pip (Python Package Manager)**
   - Usually comes with Python installation
   - Verify installation: `pip --version` or `pip3 --version`

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd agentKit_practice
```

### 2. Install Required Python Packages
```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, install packages manually:
```bash
pip install requests beautifulsoup4 openai python-dotenv
```

### 3. Set Up OpenAI API Key

You need an OpenAI API key to use the AI features of this application.

#### Get an OpenAI API Key:
1. Go to [OpenAI's website](https://platform.openai.com/)
2. Sign up for an account or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (it starts with `sk-`)

#### Configure the API Key:

**Environment Variable**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

## Usage
### Default Mode (precoded array of websites + regex for barcodes/SKU. All you have to do is type the command and then the product you want to find. Results will be printed to the console. This is the function I have been working on, the rest are completely generated. Feel free to add more sites and regex to the arrays.)

```bash
python3 search_with_defaults "product name"
```
                ***Not Tested***
### Interactive Mode
Run the main interactive search program:
```bash
python interactive_search.py
```

### Product Validator
Run the product validator directly:
```bash
python product_validator.py [product_name]
```

### Test the Validator
Run the test script to verify functionality:
```bash
python test_validator.py
```

## Features

- **Interactive Product Search**: Search for wargaming products with AI assistance
- **Product Code Extraction**: Automatically extract product codes from web pages
- **Web Scraping**: Fetch product information from various gaming sites
- **Command Line Support**: Use via command line arguments or interactive prompts
- **Error Handling**: Robust error handling for network and parsing issues

## Configuration

The application uses several configuration options that can be customized:

- **User Agent**: Configurable user agent string for web requests
- **Request Timeout**: Adjustable timeout for web requests
- **API Settings**: OpenAI model and temperature settings

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've installed all required packages with `pip install -r requirements.txt`

2. **OpenAI API errors**: Verify your API key is set correctly and has sufficient credits

3. **Network errors**: Check your internet connection and firewall settings

4. **Permission errors**: On Unix systems, you might need to use `sudo` or install packages in a virtual environment

### Virtual Environment (Recommended)
For better package management, use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## License


## Contributing

Feel free to push changes that are working and documented