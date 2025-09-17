import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from urllib.parse import urlparse

def load_inputs():
    with open('inputs.json', 'r') as file:
        data = json.load(file)
        return data

def parse_json_game_info(game, team_code, sport, league):
    level = "college"

    # Extracting home and road teams
    home, road = parse_json_team_names(game['name'])
    
    if game["image"]["url"] == "https://yalebulldogs.com/images/logos/site/site.png":
        if home == "":
            home = "Yale University"
        if road == "":
            road = "Yale University"

    # Extracting and formatting the date and time
    start_date_time = game['startDate']
    date_str, time_str = start_date_time.split('T')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    day_of_week = date_obj.strftime('%A')

    location = game['location']['name']

    return [sport, level, league, formatted_date, day_of_week, time_str, home, road, location, team_code]

def parse_json_team_names(name_field):
    vs_match = re.search(r'(?i)\bvs\b', name_field)
    at_match = re.search(r'(?i)\bat\b|\b@\b', name_field)

    if vs_match:
        home, road = name_field.split(vs_match.group(), 1)
    elif at_match:
        road, home = name_field.split(at_match.group(), 1)
    else:
        home, road = None, None  # Handle case where neither 'Vs' nor 'At'/'@' is present

    return home.strip(), road.strip() if home and road else (None, None)

def scrape_sites(sport, league):
    games = []
    inputs = load_inputs()

    json_sites = inputs[league]['json_sites']

    for site in json_sites:
        if sport == "hockey":
            sport = "ice-hockey"
        url = site + "/sports/mens-" + sport + "/schedule/2025-26"

        parsed_site = urlparse(site)
        domain = parsed_site.netloc
        team_code = domain.split('.')[0] # name to be used in team folder/file

        print("Working on " + site)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', {'type': 'application/ld+json'})
        if script_tag:
            events = json.loads(script_tag.string)
            for event in events:
                if event["@type"] == "SportsEvent":
                    games.append(parse_json_game_info(event, team_code, sport, league))

    txt_sites = inputs[league]['txt_sites']

    for site in txt_sites:
        parsed_site = urlparse(site)
        domain = parsed_site.netloc
        team_code = domain.split('.')[1] # name to be used in team folder/file

        print("Working on " + site)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        response = requests.get(site, headers=headers)

        if response.status_code == 200:
            lines = response.text.split('\n')  # Split the response text into lines

            lines = [line.strip() for line in lines]

            team_name = lines[0]  # Assuming the first line contains the team name

            header_indices = find_txt_column_indices(lines[10])  # Header line is 11th line, index 10

            txt_games = []
            for i in range(11, len(lines), 1):  # Start from line 12, every odd line
                line = lines[i]
                if len(line) > 0:
                    game_info = extract_txt_game_info(line, header_indices)
                    txt_games.append(game_info)

            processed_txt_games = process_txt_games(txt_games, team_name, team_code, sport, league)
            games.extend(processed_txt_games)  # Append processed games to the overall games list

    return games

def process_txt_games(txt_games, team_name, team_code, sport, league):
    processed_games = []
    for game in txt_games:
        date_str = game['Date']
        time_str = game['Time']
        at = game['At']
        opponent = game['Opponent']

        # Parsing the date and day of week
        month_abbr, day, day_abbr = re.match(r'(\w{3}) (\d+) \((\w{3})\)', date_str).groups()
        year = "2025" if month_abbr in ['Oct', 'Nov', 'Dec'] else "2026"
        formatted_date = datetime.strptime(f"{day} {month_abbr} {year}", "%d %b %Y").strftime("%Y-%m-%d")
        date_obj = datetime.strptime(formatted_date, "%Y-%m-%d")
        day_of_week = date_obj.strftime("%A")

        # Determining home and road teams
        if at == 'Home' or at == 'Neutral':
            home = team_name
            road = opponent
        else:
            home = opponent
            road = team_name

        location = game['Location']

        processed_games.append([sport, "college", league, formatted_date, day_of_week, time_str, home, road, location, team_code])

    return processed_games

def find_txt_column_indices(header_line):
    headers = ['Date', 'Time', 'At', 'Opponent', 'Location', 'Tournament', 'Result']
    indices = {header: header_line.index(header) for header in headers}
    return indices

def extract_txt_game_info(game_line, indices):
    game_info = {
        'Date': game_line[indices['Date']:indices['Time']].strip(),
        'Time': game_line[indices['Time']:indices['At']].strip(),
        'At': game_line[indices['At']:indices['Opponent']].strip(),
        'Opponent': game_line[indices['Opponent']:indices['Location']].strip(),
        'Location': game_line[indices['Location']:indices['Tournament']].strip(),
        'Tournament': game_line[indices['Tournament']:indices['Result']].strip(),
        'Result': game_line[indices['Result']:].strip(),
    }

    return game_info