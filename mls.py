from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
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
    site = json_content["mls"]['sites'][0]
    start_date = parse_game_date(json_content["mls"]['start_date'])
    end_date = parse_game_date(json_content["mls"]['end_date'])

    # Set up Selenium with headless options
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())

    # Iterate over dates
    current_date = start_date
    while current_date <= end_date:
        driver = webdriver.Chrome(service=service, options=options)

        schedule_date = current_date.strftime('%Y-%m-%d')

        # Use Selenium to get the page content after JavaScript execution
        driver.get(site + schedule_date)

        # Wait for the necessary time for the page to load and JavaScript to execute
        time.sleep(5)

        # Get the page source and close the browser
        page_source = driver.page_source

        # You can continue with BeautifulSoup to parse the page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all games for the day
        game_containers = soup.find_all('div', class_='mls-c-match-list__match-container')

        for game in game_containers:
            try:
                date_div = game.find('div', {'class': 'mls-c-status-stamp__status'})
                date_str = date_div.get_text().strip() if date_div else ''

                # Assume year 2025 and parse the date
                game_date = datetime.strptime(date_str + ' 2025', '%m/%d %Y')
                formatted_date = game_date.strftime('%Y-%m-%d')
                day_of_week = game_date.strftime('%A')

                away_team_div = game.find('div', class_='--away')
                away_team = away_team_div.find('span', class_='mls-c-club__shortname').get_text().strip()

                home_team_div = game.find('div', class_='--home')
                home_team = home_team_div.find('span', class_='mls-c-club__shortname').get_text().strip()

                gametime = game.find('div', class_='mls-c-scorebug').find('span').get_text().strip()

                venue = game.find('p', class_='sc-kgTSHT').get_text().strip()

                game_data = ['soccer', 'pro', 'mls', formatted_date, day_of_week, gametime, home_team, away_team, venue]
                games.append(game_data)
            except Exception as e:
                print(f"Error processing game: {e}")


        current_date += timedelta(days=7)
        driver.quit()
    
    return games