from bs4 import BeautifulSoup
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAITextCompletion, AzureTextCompletion
import json
import re
import requests
import random


kernel = sk.Kernel()

def process_document(url, name,endpoint, api_key):
    
    text = extract_text_url(url)
    cleaned_text = clean_text(text)
    summarised_text = summarise_text_openai(cleaned_text,endpoint, api_key)
    file_name, file_path = save_json(summarised_text, url, name)

    
    return file_name,file_path

def extract_text_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    text = soup.get_text()
    return text

def clean_text(text):
    text = text.replace("\n", " ")
    text = text.replace("\r\n\n ", " ")
    text = re.sub(' +', ' ', text)
    text = re.sub(r'\b\w{1,3}\b', '', text) 
    return text

def summarise_text_openai(text,endpoint, api_key):
   
    kernel.add_text_completion_service("dv", AzureTextCompletion("demo", endpoint, api_key))

    # Wrap your prompt in a function
    prompt = kernel.create_semantic_function("""
    Summarize the following text : {{$INPUT}}""")

    # Run your prompt
    summarised_text = str(prompt(text))
    
    return summarised_text

def save_json(summarised_text, url, name):

    data = {'id:': str(random.randint(0,1000000)),'url': url,'text': summarised_text,'name': name}

    file_name = name + ".json"
    file_path = "./data/" + file_name

    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)

    return file_name, file_path