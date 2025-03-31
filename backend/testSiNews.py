import time
import pytest
from scrapingNews import get_all_news_and_summarize  # Your scraping module
from siNews import Summarizer  # Your summarization module

# Initialize scraper and summarizer
scraper = get_all_news_and_summarize()
summarizer = Summarizer()

# Sample test inputs
TEST_CATEGORY = "Politics"
TEST_KEYWORD = "ශ්‍රී ලංකාව"
TEST_ARTICLE = "ශ්‍රී ලංකාවේ නවතම ආර්ථික ප්‍රවණතා පිළිබඳ විශ්ලේෂණයකි."

# -------------------- Functional Testing --------------------

def test_scraping_news():
    """Test if news scraping fetches articles successfully."""
    articles = scraper.scrape_latest_news()
    assert len(articles) > 0  # Ensure at least one article is scraped
    assert "title" in articles[0] and "content" in articles[0]  # Check structure

def test_summarization():
    """Test if summarization generates valid summaries."""
    summary = summarizer.summarize_article(TEST_ARTICLE)
    assert isinstance(summary, str)
    assert len(summary) > 10  # Ensure the summary has meaningful content

def test_search_by_category():
    """Test if search by category returns relevant articles."""
    articles = scraper.search_news_by_category(TEST_CATEGORY)
    assert len(articles) > 0
    assert all(TEST_CATEGORY in article["category"] for article in articles)

def test_search_by_keyword():
    """Test if keyword search retrieves relevant articles."""
    articles = scraper.search_news_by_keyword(TEST_KEYWORD)
    assert len(articles) > 0
    assert any(TEST_KEYWORD in article["content"] for article in articles)

# -------------------- Non-Functional Testing --------------------

def test_summarization_speed():
    """Measure how quickly the summarizer generates a summary."""
    start_time = time.time()
    summarizer.summarize_article(TEST_ARTICLE)
    end_time = time.time()
    
    assert (end_time - start_time) < 3  # Ensure response time is < 3 seconds

def test_multiple_requests():
    """Simulate multiple users requesting summaries at once."""
    results = []
    for _ in range(10):  # Simulate 10 users
        summary = summarizer.summarize_article(TEST_ARTICLE)
        results.append(summary)
    
    assert all(len(s) > 10 for s in results)  # Ensure valid summaries

def test_reliability():
    """Check if system recovers after an intentional failure."""
    try:
        scraper.simulate_crash()  # Simulate scraper crash
    except Exception:
        pass  # Expected failure
    
    time.sleep(5)  # Wait for system restart
    
    # Try scraping again
    articles = scraper.scrape_latest_news()
    assert len(articles) > 0  # Ensure it recovers

if __name__ == "__main__":
    pytest.main(["-v", "--tb=short"])  # Run all tests
