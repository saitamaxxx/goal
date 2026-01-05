import os
import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
PROMO_LINK = "https://stake.com/?c=stakesoccer24"

# Unicode Bold Numbers
BOLD_NUMS = str.maketrans("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")

def load_history():
    # Load the scores from the previous run
    if os.path.exists("scores.json"):
        with open("scores.json", "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_history(data):
    # Save current scores for the next run
    with open("scores.json", "w") as f:
        json.dump(data, f)

def get_live_data():
    url = "http://site.api.espn.com/apis/site/v2/sports/soccer/scorepanel"
    try:
        r = requests.get(url)
        return r.json()
    except:
        return {}

def post_goal(league, time, home_team, away_team, score_h, score_a, scoring_team):
    # ⚽ FORMATTING THE GOAL POST
    score_str = f"{score_h}-{score_a}".translate(BOLD_NUMS)
    
    msg = f"⚽ 𝐆𝐎𝐀𝐋 𝐀𝐋𝐄𝐑𝐓! 🚨\n\n"
    msg += f"🏆 {league}\n"
    msg += f"⏱️ {time}' | {home_team} {score_str} {away_team}\n\n"
    msg += f"The net is shaking! {scoring_team} just scored!\n\n"
    msg += f"💰 Bet on the next goal here:\n👉 {PROMO_LINK}\n"
    msg += "━━━━━━━━━━━━━━━━\n"
    msg += "#Goal #LiveScore #Football"

    # Post to Facebook
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
    payload = {"message": msg, "access_token": FB_ACCESS_TOKEN}
    try:
        requests.post(url, data=payload)
        print(f"✅ GOAL POSTED: {home_team} vs {away_team}")
    except Exception as e:
        print(f"❌ FB Error: {e}")

if __name__ == "__main__":
    print("--- 🕵️ CHECKING FOR GOALS ---")
    
    # 1. Load Memory
    history = load_history()
    new_history = {}
    
    # 2. Get Real Time Data
    data = get_live_data()
    
    has_updates = False
    
    leagues = data.get('scores', [])
    for league_group in leagues:
        league_name = league_group.get('name')
        
        for event in league_group.get('events', []):
            match_id = event['id']
            status = event.get('status', {})
            state = status.get('type', {}).get('state')
            
            # Only track LIVE matches ('in')
            if state == 'in':
                # Get Scores
                competitions = event.get('competitions', [])[0]
                competitors = competitions.get('competitors', [])
                
                home = next((t for t in competitors if t['homeAway'] == 'home'), {})
                away = next((t for t in competitors if t['homeAway'] == 'away'), {})
                
                h_name = home.get('team', {}).get('name')
                a_name = away.get('team', {}).get('name')
                
                # Current Scores (Int)
                cur_h = int(home.get('score', 0))
                cur_a = int(away.get('score', 0))
                time = status.get('displayClock', 'Live')

                # 3. COMPARE WITH MEMORY
                if match_id in history:
                    old_h = int(history[match_id]['h'])
                    old_a = int(history[match_id]['a'])
                    
                    # DETECT GOAL
                    if cur_h > old_h:
                        post_goal(league_name, time, h_name, a_name, cur_h, cur_a, h_name)
                    elif cur_a > old_a:
                        post_goal(league_name, time, h_name, a_name, cur_h, cur_a, a_name)
                
                # Add to new history
                new_history[match_id] = {'h': cur_h, 'a': cur_a}

    # 4. Save New State
    save_history(new_history)
