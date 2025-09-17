# Sports schedules

One thing that has frustrated me for a while is that there is no place to see a schedule of all sporting events. So if I want to take my kids to a game this weekend, I'd have to check in dozens of places online to cover all the options (in particular college sports, minor leagues, etc.).

Now I have a python script that does this for me.

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```bash
   python main.py
   ```

## Usage

- Run without removing duplicates: `python main.py`
- Run with duplicate removal: `python main.py --delete_dupes`

The resulting CSVs are in the [combined_schedules folder](https://github.com/gmichnikov/sports-schedules/tree/main/combined_schedules) (take the most recent one). I'm also uploading the data to DoltHub: https://www.dolthub.com/repositories/gmichnikov/sports-schedules. You can query the results right from that repo using SQL (you can start by running one of the saved queries in the left side panel).

I'm definitely open to feedback and suggestions.
