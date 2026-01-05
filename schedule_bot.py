import os
import requests
from datetime import datetime

# --- CONFIGURATION ---
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
PROMO_LINK = "https://stake.com/?c=stakesoccer24"

# We only want to list BIG games in the morning (IDs from ESPN)
# Premier League(2300), La Liga(53), Bundesliga(10), Serie A(12), Ligue 1(9), Champions League(2)
TOP_LEAGUE_IDS = ["2300", "53", "10", "12", "9", "2"]

def get_todays_matches():
    url = "http://site.api.espn.com/apis/site/v2/sports/soccer/scorepanel"
    try:
        r = requests.get(url)
        data = r.json()
        
        schedule = []
        leagues = data.get('scores', [])
        
        for league in leagues:
            league_id = league.get('id')
            league_name = league.get('name')
            
            # Filter: Only Top Leagues (Optional - remove if you want all games)
            # if league_id not in TOP_LEAGUE_IDS:
            #    continue
            
            for event in league.get('events', []):
                status = event.get('status', {})
                state = status.get('type', {}).get('state')
                
                # Only "pre" (Scheduled) games
                if state == 'pre':
                    date_str = status.get('type', {}).get('shortDetail') # e.g. "Today, 15:00"
                    
                    competition = event.get('competitions', [])[0]
                    competitors = competition.get('competitors', [])
                    home = next((t for t in competitors if t['homeAway'] == 'home'), {})['team']['name']
                    away = next((t for t in competitors if t['homeAway'] == 'away'), {})['team']['name']
                    
                    schedule.append(f"⏰ {date_str} | {home} 𝐯𝐬 {away} ({league_name})")
        
        return schedule
    except:
        return []

def post_schedule(games):
    if not games: 
        print("No games found.")
        return

    # Header
    today = datetime.utcnow().strftime('%A, %d %B')
    msg = f"📅 𝐌𝐀𝐓𝐂𝐇𝐃𝐀𝐘: {today}\n"
    msg += "Don't miss the action! Here are today's top games:\n\n"
    
    # Body (Limit to 15 games to avoid text limit)
    for game in games[:15]:
        msg += f"{game}\n"
        
    # Footer
    msg += "\n🔮 𝐖𝐡𝐨 𝐚𝐫𝐞 𝐲𝐨𝐮 𝐛𝐚𝐜𝐤𝐢𝐧𝐠?\n"
    msg += f"💰 Bet here & Get Bonus: {PROMO_LINK}\n"
    msg += "━━━━━━━━━━━━━━━━\n"
    msg += "#Matchday #Football #Betting"

    # Post
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/feed"
    payload = {"message": msg, "access_token": FB_ACCESS_TOKEN}
    requests.post(url, data=payload)
    print("✅ Schedule Posted")

if __name__ == "__main__":
    matches = get_todays_matches()
    if matches:
        post_schedule(matches)
