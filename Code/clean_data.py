#first step is to clean and preprocess data in order to fit on what we need to do
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Dataset_Football_Players" / "archive"

PLAYERS_PATH = DATA_DIR / "players.csv"
CLUBS_PATH = DATA_DIR / "clubs.csv"           #this is where paths are defined
TRANSFERS_PATH = DATA_DIR / "transfers.csv"

#loading data in the non-cleaned format
players   = pd.read_csv(PLAYERS_PATH) 
clubs     = pd.read_csv(CLUBS_PATH)
transfers = pd.read_csv(TRANSFERS_PATH)

players.columns   = players.columns.str.strip()
clubs.columns     = clubs.columns.str.strip()  #stripping the spaces
transfers.columns = transfers.columns.str.strip()


# FIRST ONE: clean data for players.csv which contains players and their attributes
player_keep = [
    "player_id",
    "name",
    "country_of_citizenship",
    "position",
    "current_club_id",
    "market_value_in_eur",
]

players_clean = players[player_keep].copy()

# types and duplicates
players_clean["player_id"] = players_clean["player_id"].astype(int)
players_clean["current_club_id"] = players_clean["current_club_id"].astype("Int64")

# convert market value into numeric
players_clean["market_value_in_eur"] = (
    players_clean["market_value_in_eur"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.replace("m", "", regex=False)
    .str.replace("k", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip() 
)
# Nan becomes 0
players_clean["market_value_in_eur"] = pd.to_numeric(players_clean["market_value_in_eur"], errors="coerce").fillna(0)


players_clean = (
    players_clean
    .sort_values("player_id")
    .drop_duplicates(subset="player_id", keep="first")
)

players_clean = players_clean.dropna(subset=["current_club_id"])
print("players_clean shape:", players_clean.shape)
print(players_clean.head())

# SECOND ONE: clean data for clubs.csv which contains clubs and their attributes

club_keep = [
    "club_id",
    "name",
    "domestic_competition_id"
]

# keep only the columns that exist
club_keep = [c for c in club_keep if c in clubs.columns]

clubs_clean = clubs[club_keep].copy()
clubs_clean["club_id"] = clubs_clean["club_id"].astype(int)

clubs_clean = (
    clubs_clean
    .sort_values("club_id")
    .drop_duplicates(subset="club_id", keep="first")
)

print("clubs_clean shape:", clubs_clean.shape)
print(clubs_clean.head())

# THIRD ONE: clean data for transfers.csv which contains transfer over the past 28 years

trans_keep = [
    "player_id",
    "from_club_id",
    "to_club_id",
    "transfer_date"
]

trans_keep = [c for c in trans_keep if c in transfers.columns]

transfers_clean = transfers[trans_keep].copy()

# parse ids and date 
transfers_clean["player_id"]    = transfers_clean["player_id"].astype(int)
transfers_clean["from_club_id"] = transfers_clean["from_club_id"].astype("Int64")
transfers_clean["to_club_id"]   = transfers_clean["to_club_id"].astype("Int64")

transfers_clean["transfer_date"] = pd.to_datetime(
    transfers_clean["transfer_date"], errors="coerce"
)

# drop invalid rows
transfers_clean = transfers_clean.dropna(
    subset=["transfer_date", "from_club_id", "to_club_id"]
)

# remove transfer which didn't happen
transfers_clean = transfers_clean[
    transfers_clean["from_club_id"] != transfers_clean["to_club_id"]
]

# assuring the fact that I kept only the transfers that exists between in the clubs kept in clubs_clean
valid_clubs = set(clubs_clean["club_id"].unique())
transfers_clean = transfers_clean[
    transfers_clean["from_club_id"].isin(valid_clubs)
    & transfers_clean["to_club_id"].isin(valid_clubs)
]

transfers_clean["year"] = transfers_clean["transfer_date"].dt.year

print("transfers_clean shape:", transfers_clean.shape)
print(transfers_clean.head())


# saving cleaned dataset in the folder to use for the next steps in my project


OUTPUT_DIR = DATA_DIR  # basically is the same folder like with that one from where I got dataset non-cleaned
players_clean_path   = OUTPUT_DIR / "players_clean.csv"
clubs_clean_path     = OUTPUT_DIR / "clubs_clean.csv"
transfers_clean_path = OUTPUT_DIR / "transfers_clean.csv"

players_clean.to_csv(players_clean_path, index=False)
clubs_clean.to_csv(clubs_clean_path, index=False)
transfers_clean.to_csv(transfers_clean_path, index=False)


