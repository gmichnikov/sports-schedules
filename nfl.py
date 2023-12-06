from bs4 import BeautifulSoup
import requests
from datetime import datetime
import json

def load_urls():
    with open('inputs.json', 'r') as file:
        data = json.load(file)
        return data

def scrape_sites():
    games = []
    json_content = load_urls()
    sites = json_content["nfl"]['sites']

    for site in sites:
        response = requests.get(site)
        soup = BeautifulSoup(response.content, 'html.parser')

        table_container = soup.find('div', class_='table_container')
        tbody = table_container.find('tbody') if table_container else None
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                if 'thead' not in row.get('class', []):  # Exclude header rows
                    date_str = row.find('td', {'data-stat': 'game_date'}).text
                    time_str = row.find('td', {'data-stat': 'gametime'}).text
                    winner = row.find('td', {'data-stat': 'winner'}).text.strip()
                    loser = row.find('td', {'data-stat': 'loser'}).text.strip()
                    location_indicator = row.find('td', {'data-stat': 'game_location'}).text.strip()

                    if location_indicator == "@":
                        home, road = loser, winner
                    else:
                        home, road = winner, loser

                    # Formatting date and extracting day of the week
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_of_week = date_obj.strftime('%A')

                    location = ""
                    games.append(["football", "pro", "NFL", date_str, day_of_week, time_str, home, road, location])

    return games
