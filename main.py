import csv
import nba, ncaab, nhl, nfl, mlb
import os
from datetime import datetime
import pandas as pd

# this happens once per sport and assumes "games" contains an array of arrays where each looks like
# [sport, level, league, formatted_date, day_of_week, time, home, road, location]
# this function then adds the city and state
def write_to_csv(sport, games, location_lookup):
    # Get current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'{sport}_schedule_{current_datetime}.csv'

    # Create folder if it doesn't exist
    folder = f'{sport}_schedule'
    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["sport", "level", "league", "date", "day", "time", "home_team", "road_team", "location", "home_city", "home_state"])
        for game in games:
            league = game[2].lower()  # League
            home_team = game[6].lower()  # Home Team
            city, state = location_lookup.get((league, home_team), ("", ""))
            writer.writerow(game + [city, state])

# this happens once, before any sports are scraped
def create_location_lookup():
    location_lookup = {}
    with open('locations.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            key = (row[0].lower(), row[1].lower())  # League and Team Name
            value = (row[2], row[3])  # City and State
            location_lookup[key] = value
    return location_lookup

def get_most_recent_csv(folder):
    csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    # Sort files based on creation time or filename
    most_recent_file = sorted(csv_files, key=lambda x: os.path.getctime(os.path.join(folder, x)), reverse=True)[0]
    return os.path.join(folder, most_recent_file)

def combine_csv_files():
    schedule_folders = [f for f in os.listdir('.') if os.path.isdir(f) and f.endswith('_schedule')]
    combined_folder = 'combined_schedules'
    if not os.path.exists(combined_folder):
        os.makedirs(combined_folder)

    combined_df = create_combined_df(schedule_folders)
    add_missing_teams_to_locations(combined_df)

    # Creating the primary_key column
    combined_df['primary_key'] = combined_df['league'].fillna('Unknown') + '_' + combined_df['date'].fillna('Unknown') + '_' + combined_df['time'].fillna('NA') + '_' + combined_df['home_team'].fillna('Unknown') + '_' + combined_df['road_team'].fillna('Unknown')

    # Reorder columns to make primary_key the first column
    column_order = ['primary_key'] + [col for col in combined_df.columns if col != 'primary_key']
    combined_df = combined_df[column_order]

    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_filename = f'combined_schedule_{current_datetime}.csv'
    combined_df.to_csv(os.path.join(combined_folder, combined_filename), index=False)

def add_missing_teams_to_locations(combined_df):
    locations_df = pd.read_csv('locations.csv')

    # Extract unique league/team combinations from combined_df
    unique_combinations = combined_df[['league', 'home_team']].drop_duplicates()
    added_locations = 0

    # Check each combination and add missing ones to locations_df
    for index, row in unique_combinations.iterrows():
        if not ((locations_df['league'] == row['league']) & (locations_df['team_name'] == row['home_team'])).any():
            # Add missing combination
            new_row = {'league': row['league'], 'team_name': row['home_team'], 'city': '', 'state': ''}
            locations_df = locations_df.append(new_row, ignore_index=True)
            added_locations += 1

    # Save updated DataFrame back to locations.csv
    locations_df.to_csv('locations.csv', index=False)
    print("Added " + str(added_locations) + " locations")

    # LLM Prompt to fill in the city and state:
    # Great, now I have the following new rows in my locations.csv. Can you please do your best to create a new csv that contains exactly these rows but with the city and state (two letter abbrev) filled in as the third and fourth values, using your vast knowledge to make the best possible guess for each location?

def create_combined_df(folders):
    combined_df = pd.DataFrame()
    for folder in folders:
        csv_file = get_most_recent_csv(folder)
        print("combining csv: " + str(csv_file))
        df = pd.read_csv(csv_file, header=0)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df

def main():
    location_lookup = create_location_lookup()

    # Mapping of sports to their respective modules (assuming similar function names across modules)
    sports_modules = {
        # 'nba': nba,
        # 'nhl': nhl,
        # 'ncaab': ncaab,
        # 'nfl': nfl,
        'mlb': mlb,
    }

    for sport, module in sports_modules.items():
        print("Starting " + sport)
        games = module.scrape_sites()
        write_to_csv(sport, games, location_lookup)

    combine_csv_files()

if __name__ == "__main__":
    main()