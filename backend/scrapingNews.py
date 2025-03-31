import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re
from deep_translator import GoogleTranslator
from siNews import Summarizer 


def translate_to_sinhala(text):
    try:
        translated_text = GoogleTranslator(source='en', target='si').translate(text)
        return translated_text
    except Exception as e:
        print(f"Translation Error: {e}")
        return text  # Return original text if translation fails


# Function to preprocess the text 
def preprocess_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove special characters like &amp;, &lt;, &gt;, etc.
    text = re.sub(r'&[a-zA-Z]+;', '', text)

    # Remove extra spaces and normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading and trailing spaces
    text = text.strip()

    # Remove any unwanted characters 
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters

    # Fix punctuation spacing (ensure space after commas, periods, etc.)
    text = re.sub(r'([.,;:!?])([^\s])', r'\1 \2', text)

    # Remove duplicate words and phrases
    text = re.sub(r'(\b[\u0D80-\u0DFF]+\b)( \1)+', r'\1', text)

    # Remove excessive newlines
    text = re.sub(r'\n+', '\n', text).strip()

    return text
  
  

# Remove unwanted English characters and concatenate split Sinhala words
def postprocess_text(text):
    # Remove unwanted English characters 
    text = re.sub(r'[A-Za-z0-9\.,!?():;"]', '', text)  # removes English characters and punctuation
    
    text = re.sub(r'ශ්රී', 'ශ්‍රී', text)  # concatenate
    text = re.sub(r'ශ් රී', 'ශ්‍රී', text)  # concatenate

    return text
  
  
  
def remove_repeated_sentences(text):
    sentences = text.split('।')  # Sinhala sentences often end with '।'
    unique_sentences = []
    seen_phrases = set()
    
    for sentence in sentences:
        words = sentence.split()
        for word in words:
            if words.count(word) > 1:
                break  # Remove sentence if a word repeats
        else:
            if sentence not in seen_phrases:
                unique_sentences.append(sentence)
                seen_phrases.add(sentence)
    
    return '। '.join(unique_sentences)
  
  
# Scraping the image URL from the 'news-banner' div
def scrape_image(article_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(article_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the 'news-banner' div and extract the image
        banner_div = soup.find('div', class_='news-banner')
        
        if banner_div:
            image_tag = banner_div.find('img')

            if image_tag and 'src' in image_tag.attrs:
                image_url = image_tag['src']
                if not image_url.startswith('http'):
                    # if image URL is relative, convert it to absolute
                    base_url = article_url.rsplit('/', 1)[0]
                    image_url = base_url + '/' + image_url
                return image_url
            else:
                return "No image found in the 'news-banner'."
        else:
            return "No 'news-banner' div found."
    else:
        return f"Failed to fetch image. Status code: {response.status_code}"
  
  
  
  
  
  
  
  
  
  
  
# Scraping the news article content
def scrape_news(article_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(article_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        article_body = soup.find('div', class_='news-content')
        
        if article_body:
            article_content = article_body.get_text(strip=True, separator="\n")
            print(article_content)
            return article_content
        else:
            return "Article content not found."
    else:
        return "Error", f"Failed to fetch the news. Status code: {response.status_code}"




def scrape_title(article_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(article_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the 'news' div and then look for an 'h1' tag inside it
        title_div = soup.find('article', class_='news')
        
        if title_div:
            # Look for the 'h1' tag inside the 'news' div
            title_tag = title_div.find('h1')
            
            if title_tag:
                article_title = title_tag.get_text(strip=True)  # Get the text inside the 'h1' tag
                return article_title
            else:
                return 'No <h1> tag found inside the "news" article.'
        else:
            return 'No "news" article found.'
    else:
        return f"Failed to fetch title. Status code: {response.status_code}"







# RSS Feed Parsing to extract links
def get_news_links(rss_url, max_articles=5):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(rss_url, headers=headers)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        news_links = []

        # Extract all <link> inside <item> tags
        for item in root.findall('.//item'):
            link = item.find('link')
            if link is not None:
                news_links.append(link.text)

        return news_links[:max_articles] # Limit the number of articles
    else:
        print(f"Failed to fetch RSS feed. HTTP Status: {response.status_code}")
        return []




# Main function to scrape, preprocess, translate, and summarize news
def get_all_news_and_summarize(rss_url, max_articles=5):
    news_links = get_news_links(rss_url, max_articles)
    summarizer = Summarizer()  # Instantiate the Summarizer class
    all_summaries = {}

    for i, link in enumerate(news_links):
        print(f"Scraping article {i + 1}/{len(news_links)}: {link}")
        
        # Get the title and translate it to Sinhala
        article_title = scrape_title(link)
        translated_title = translate_to_sinhala(article_title) if article_title != "No title found" else "No title found"
        
        postprocessed_title = postprocess_text(translated_title)
        
        # Get the full content
        full_text = scrape_news(link)

        if full_text:
          
          print("Preprocessing description...")
          cleaned_text = preprocess_text(full_text)  # Clean the text
            
          print("Translating description to Sinhala...")
          sinhala_text = translate_to_sinhala(cleaned_text)  # Translate the cleaned text
            
          print("Summarizing the article...")
          summary = summarizer.summarize_article(sinhala_text)  # Generate the summary
            
          # Scrape image from the 'news-banner' div
          image_url = scrape_image(link)
          
          # Postprocess the translated text 
          postprocessed_text = postprocess_text(sinhala_text)
          postprocessed_summary = postprocess_text(summary)

          all_summaries[link] = {
              "title": postprocessed_title,
              "original text": postprocessed_text,
              "summary": postprocessed_summary,
              "image_url": image_url
          }

    return all_summaries
  
  