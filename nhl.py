import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def load_urls():
    with open('inputs.json', 'r') as file:
        data = json.load(file)
        return data

def parse_game_info(game):
    sport = "hockey"
    level = "pro"
    league = "NHL"
    teams = game['name'].split("@")
    home = teams[1].strip()
    road = teams[0].strip()

    # Extract and format the date
    date_str = game['startDate']
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    day_of_week = date_obj.strftime('%A')

    location = game['location']['name']
    time_str = ""

    return [sport, level, league, formatted_date, day_of_week, time_str, home, road, location]

def scrape_sites():
    games = []
    json_content = load_urls()
    sites = json_content["nhl"]['sites']

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