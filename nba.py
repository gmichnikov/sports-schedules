import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def parse_game_info(game):
    sport = "basketball"
    level = "pro"
    league = "NBA"
    teams = game['name'].split("@")
    home = teams[1].strip()
    road = teams[0].strip()

    # Extract and format the date
    date_str = game['startDate']
    date_obj = datetime.strptime(date_str, '%a, %b %d, %Y')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    day_of_week = date_obj.strftime('%A')

    return [sport, level, league, formatted_date, day_of_week, home, road]

def scrape_sites(sites):
    games = []
    for site in sites:
        response = requests.get(site)
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if script_tag:
            events = json.loads(script_tag.string)
            for event in events:
                if event["@type"] == "SportsEvent":
                    games.append(parse_game_info(event))
    return games
