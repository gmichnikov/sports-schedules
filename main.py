import json
import csv
import nba  # Importing the NBA module

def load_urls():
    with open('inputs.json', 'r') as file:
        data = json.load(file)
        return data

def write_to_csv(sport, games, location_lookup):
    with open(f'{sport}_schedule.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Sport", "Level", "League", "Date", "Day", "Home Team", "Road Team", "City", "State"])
        for game in games:
            league = game[2].lower()  # League
            home_team = game[5].lower()  # Home Team
            print("League: ", league)
            print("Home team: ", home_team)
            city, state = location_lookup.get((league, home_team), ("", ""))
            writer.writerow(game + [city, state])

def create_location_lookup():
    location_lookup = {}
    with open('locations.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            key = (row[0].lower(), row[1].lower())  # League and Team Name
            value = (row[2], row[3])  # City and State
            location_lookup[key] = value
    print(str(location_lookup))
    return location_lookup

def main():
    urls = load_urls()
    location_lookup = create_location_lookup()

    # Mapping of sports to their respective modules (assuming similar function names across modules)
    sports_modules = {
        'nba': nba  # Add other sports and their modules here
    }

    for sport, module in sports_modules.items():
        if sport in urls:
            games = module.scrape_sites(urls[sport]['sites'])
            write_to_csv(sport, games, location_lookup)

if __name__ == "__main__":
    main()
