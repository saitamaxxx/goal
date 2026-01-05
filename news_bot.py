import os
import requests
import json

# --- CONFIGURATION ---
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
PROMO_LINK = "https://stake.com/?c=stakesoccer24"

# File to store the ID of the last posted news
MEMORY_FILE = "news_memory.txt"

def get_last_posted_id():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return f.read().strip()
    return "0"

def save_last_posted_id(news_id):
    with open(MEMORY_FILE, "w") as f:
        f.write(str(news_id))

def get_espn_news():
    # Official ESPN Soccer News Endpoint
    url = "http://site.api.espn.com/apis/site/v2/sports/soccer/news"
    try:
        r = requests.get(url)
        data = r.json()
        return data.get("articles", [])
    except:
        return []

def post_news_with_photo(headline, description, image_url, news_link):
    # We use the 'photos' endpoint to upload an image via URL
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/photos"
    
    # Construct the Caption
    caption = f"📰 𝐁𝐑𝐄𝐀𝐊𝐈𝐍𝐆 𝐍𝐄𝐖𝐒\n\n"
    caption += f"📌 {headline}\n\n"
    caption += f"{description}\n\n"
    caption += f"👉 Join the action: {PROMO_LINK}\n"
    caption += "━━━━━━━━━━━━━━━━\n"
    caption += "#FootballNews #Soccer #ESPN #ScoreZone"

    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": FB_ACCESS_TOKEN
    }
    
    try:
        r = requests.post(url, data=payload)
        response = r.json()
        if "id" in response:
            print(f"✅ News Posted: {headline}")
            return True
        else:
            print(f"❌ FB Error: {response}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("--- 🗞️ CHECKING FOR NEW SOCCER NEWS ---")
    
    last_id = get_last_posted_id()
    articles = get_espn_news()
    
    if not articles:
        print("No articles found.")
        exit()

    # Get the latest article (Top of the list)
    latest_article = articles[0]
    
    # Extract Data
    try:
        news_id = str(latest_article.get("images", [{}])[0].get("id", "0")) # Use image ID or headlines hash as unique ID
        if news_id == "0":
             # Fallback if no image ID, use headline text hash
             news_id = str(hash(latest_article.get("headline", "")))
             
        headline = latest_article.get("headline", "")
        description = latest_article.get("description", "")
        # Find the image (ESPN usually puts images in a list)
        images = latest_article.get("images", [])
        
        # Logic: We only post if:
        # 1. It is a NEW article (ID is different from memory)
        # 2. It actually HAS an image
        if news_id != last_id and images:
            image_url = images[0].get("url")
            
            # Post it
            success = post_news_with_photo(headline, description, image_url, PROMO_LINK)
            
            if success:
                save_last_posted_id(news_id)
        else:
            print("No new news or news has no image.")
            
    except Exception as e:
        print(f"Error processing news: {e}")
