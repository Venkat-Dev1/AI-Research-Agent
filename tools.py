import time

from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from rich import print
from dotenv import load_dotenv
import os
load_dotenv()


# Tavily search client for extracting real time data from the web
tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query:str)->str:
    """Search the web for recent and reliable information about the topic and Returns titles,urls and snippets"""
    response=tavily.search(query=query, num_results=5)
    out=[]
    for result in response.get('results', []):
        out.append(
            f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content']}\n"
            )
    return "\n-----\n".join(out)

#print(web_search.invoke("What is the latest news in telangana"))

# BeautifulSoup web scraping tool for extracting data from a webpage
@tool
def web_scraper(url:str)->str:
    """Scrape the content of a webpage and return the text"""
    try:
        response=requests.get(url,timeout=10,headers={'User-Agent': 'Mozilla/5.0'})
        soup=BeautifulSoup(response.content,'html.parser')
        for tag in soup(['script','style','nav','footer','img']):
            tag.decompose()
        return soup.get_text(separator=" ",strip=True)[:5000]  # Return up to 5000 characters of text
    except Exception as e:
        return f"Error occurred while scraping the webpage: {e}"

#print(web_scraper.invoke("https://www.skysports.com/cricket/news/13613181/ms-dhoni-former-india-captain-retires-from-playing-role-with-ipls-chennai-super-kings-aged-455"))