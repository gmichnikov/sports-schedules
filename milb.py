import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def load_urls():
    with open('inputs.json', 'r') as file:
        data = json.load(file)
        return data

def parse_game_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

def scrape_sites():
    games = []
    json_content = load_urls()
    site = json_content["milb"]['sites'][0]
    start_date = parse_game_date(json_content["milb"]['start_date'])
    end_date = parse_game_date(json_content["milb"]['end_date'])

    # Load league information
    milb_levels = pd.read_csv('milb_levels.csv').set_index('team')

    # Set up Selenium with headless options
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Iterate over dates
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y-%m-%d')
        day_of_week = current_date.strftime('%A')

        # response = requests.get(site + formatted_date)
        # soup = BeautifulSoup(response.content, 'html.parser')

        # Use Selenium to get the page content after JavaScript execution
        driver.get(site + formatted_date)

        # Wait for the necessary time for the page to load and JavaScript to execute
        time.sleep(5)  # Adjust this time as needed

        # Get the page source and close the browser
        page_source = driver.page_source

        # You can continue with BeautifulSoup to parse the page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all games for the day
        game_containers = soup.find_all('div', {'data-mlb-test': 'individualGameContainerDesktop'})

        for game in game_containers:
            try:
                # away_team = game.find('div', {'class': 'TeamMatchupLayerstyle__AwayWrapper-sc-ouprud-1'}).get_text().strip()
                # home_team = game.find('div', {'class': 'TeamMatchupLayerstyle__HomeWrapper-sc-ouprud-2'}).get_text().strip()

                away_team_div = game.find('div', {'class': 'TeamMatchupLayerstyle__AwayWrapper-sc-ouprud-1'})
                away_team_name_div = away_team_div.find('div', {'class': 'TeamWrappersstyle__DesktopTeamWrapper-sc-uqs6qh-0'})
                away_team = away_team_name_div.get_text().strip() if away_team_name_div else None

                home_team_div = game.find('div', {'class': 'TeamMatchupLayerstyle__HomeWrapper-sc-ouprud-2'})
                home_team_name_div = home_team_div.find('div', {'class': 'TeamWrappersstyle__DesktopTeamWrapper-sc-uqs6qh-0'})
                home_team = home_team_name_div.get_text().strip() if home_team_name_div else None

                gametime = game.find('a', {'class': 'gameinfo-gamedaylink'}).get_text().strip()
                location = game.find('div', {'class': 'PlayerMatchupLayerstyle__PlayerMatchupLayerWrapper-sc-6brgar-0'}).get_text().strip()
                
                location_parts = location.split(" - ")
                venue = location_parts[0]
                city_state = location_parts[1].split(", ")
                city = city_state[0]
                state = city_state[1]

                # Lookup league
                league = milb_levels.loc[home_team, 'league'] if home_team in milb_levels.index else ''

                game_data = ['baseball', 'minors', league, formatted_date, day_of_week, gametime, home_team, away_team, venue, city, state]
                games.append(game_data)
            except Exception as e:
                print(f"Error processing game: {e}")

        current_date += timedelta(days=1)
    driver.quit()
    
    return games