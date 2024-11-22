import requests
import json

# DeepL API Key (provided by user)
DEEPL_API_KEY = "rtX-dc65358a-25d6-4b59-b119-735d26f3fa13:fx"
DEEPL_API_URL = "https://api-free.deepl.com/v2/languages"

# Check supported languages by DeepL API
response = requests.get(DEEPL_API_URL, headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"})

# Parse the response and list available languages
if response.status_code == 200:
    deepl_languages = response.json()
else:
    deepl_languages = {"error": "Unable to retrieve languages from DeepL API"}

# Pretty print the response content
print("Response status:", response.status_code)
print("Available languages (formatted):")
print(json.dumps(deepl_languages, indent=4, ensure_ascii=False))

# Or alternatively, output each language in a more readable format
if isinstance(deepl_languages, list):
    for lang in deepl_languages:
        print(f"- {lang['name']} ({lang['language']})")
