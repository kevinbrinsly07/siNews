from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS, cross_origin
from scrapingNews import get_all_news_and_summarize  # Import the updated function

# Initialize the Flask app
app = Flask(__name__)

CORS(app)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            original_content TEXT,
            abstractive_summary TEXT,
            link TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to save data to the database
def save_to_db(title, original_content, abstractive_summary, link, image_url):
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO summaries (title, original_content, abstractive_summary, link, image_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, original_content, abstractive_summary, link, image_url))
    conn.commit()
    conn.close()

# Function to fetch and store news data
def fetch_and_store_news_data():
    rss_feed_url = "http://www.adaderana.lk/rss.php"  # RSS Feed URL
    news_data = get_all_news_and_summarize(rss_feed_url)

    # Loop through the scraped data and save it to the database
    for link, data in news_data.items():
        
      
        title = data.get("title", "No title found")  # Get translated title if exists 
        
        # The summary is the abstractive_summary after scraping
        abstractive_summary = data["summary"]  
        
        # The original text is the original_content after scraping
        original_content = data["original text"]  
        
        # Extract the image URL
        image_url = data["image_url"]  

        # Save to the database
        save_to_db(title, original_content, abstractive_summary, link, image_url)

# Endpoint to return stored summaries
@app.route('/summarize', methods=['GET'])
@cross_origin()
def display_scraped_data():
    try:
        conn = sqlite3.connect("summaries.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM summaries')
        rows = cursor.fetchall()
        
        summaries = []
        for row in rows:
            summaries.append({
                'title': row[1],
                'original_content': row[2],
                'abstractive_summary': row[3],
                'link': row[4],
                'image_url': row[5]  # Include image URL in the response
            })
        
        conn.close()
        
        return jsonify(summaries)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_db()  # Initialize the database if it doesn't exist
    fetch_and_store_news_data()  # Fetch and store the data when the server starts
    app.run(debug=True)