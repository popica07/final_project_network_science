import pandas as pd
import networkx as nx
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#it gets the path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Dataset_Football_Players" / "archive"

PLAYERS_CLEAN_PATH = DATA_DIR / "players_clean.csv"
CLUBS_CLEAN_PATH   = DATA_DIR / "clubs_clean.csv"

# reading cleaned dataset
players_clean = pd.read_csv(PLAYERS_CLEAN_PATH)
clubs_clean   = pd.read_csv(CLUBS_CLEAN_PATH)


B = nx.Graph()

for _, row in clubs_clean.iterrows():
    cid = int(row["club_id"])
    node_id = f"club_{cid}"

    B.add_node(
        node_id,
        bipartite="club",
        club_id=cid,
        name=row["name"],
        league=row["domestic_competition_id"],
    )

valid_club_ids = set(clubs_clean["club_id"].astype(int))

for _, row in players_clean.iterrows():
    pid = int(row["player_id"])
    cid = int(row["current_club_id"])

    # here, I skipped the players who doesn't have the club in the clubs id
    if cid not in valid_club_ids:
        continue

    player_node = f"player_{pid}"
    club_node   = f"club_{cid}"

    B.add_node(
        player_node,
        bipartite="player",
        player_id=pid,
        name=row["name"],
        nationality=row["country_of_citizenship"],
        position=row["position"],
    )

    B.add_edge(player_node,club_node,weight=row["market_value_in_eur"]) #the graph weighted by market value


# some basic information about player-club bipartite graph

num_players = sum(1 for _, d in B.nodes(data=True) if d.get("bipartite") == "player")
num_clubs   = sum(1 for _, d in B.nodes(data=True) if d.get("bipartite") == "club")
print("\nPlayer – Club Bipartite Network")
print(f"Total nodes :", B.number_of_nodes())
print(f"  players   :", num_players)
print(f"  clubs     :", num_clubs)
print(f"Total edges :", B.number_of_edges())



# identify the layers
players_layer = [n for n, d in B.nodes(data=True) if d.get("bipartite") == "player"]
clubs_layer   = [n for n, d in B.nodes(data=True) if d.get("bipartite") == "club"]


# degree for players and clubs
club_degrees   = dict(B.degree(clubs_layer))
club_deg_values   = np.array(list(club_degrees.values()))

print("\nBasic Bipartite Metrics (unweighted)")
print(f"Number of player nodes: {len(players_layer)}")
print(f"Number of club nodes  : {len(clubs_layer)}")

print("\nClub degree statistics (number of players per club)")
print(f"  max   : {club_deg_values.max()}")
print(f"  mean  : {club_deg_values.mean():.2f}")


#top 10 clubs by size (number of players) in the last 28 years
top = 10
top_clubs_by_degree = sorted(
    club_degrees.items(), key=lambda x: x[1], reverse=True
)[:top]
print(f"\nTop {top} clubs by squad size (degree):")
for node, deg in top_clubs_by_degree:
    club_name = B.nodes[node].get("name", "Unknown")
    league    = B.nodes[node].get("league", "Unknown")
    print(f"  {club_name:30s} | league={league:10s} | players={deg}")



#total clubs market value value using players' market value
club_strength = dict(B.degree(clubs_layer, weight="weight")) 
club_str_values = np.array(list(club_strength.values()))
print("\nTotal squad market value")
print(f"  max   : {club_str_values.max():.2f}")
print(f"  mean  : {club_str_values.mean():.2f}")



# top clubs by total market value of their squad
top_clubs_by_value = sorted(
    club_strength.items(), key=lambda x: x[1], reverse=True
)[:top]
print(f"\nTop {top} clubs by total squad market value:")
for node, strength in top_clubs_by_value:
    club_name = B.nodes[node].get("name", "Unknown")
    league    = B.nodes[node].get("league", "Unknown")
    print(f"  {club_name:30s} | league={league:10s} | total_value={strength:.2f}")


# average market player value per club
avg_value_per_player = {}
for club_node in clubs_layer:
    deg = club_degrees.get(club_node, 0)
    if deg > 0:
        avg_value_per_player[club_node] = club_strength[club_node] / deg

avg_values = np.array(list(avg_value_per_player.values()))
print("\nAverage player market value per club")
print(f"  max   : {avg_values.max():.2f}")
print(f"  mean  : {avg_values.mean():.2f}")


# top clubs by average market value per player
top_clubs_by_avg = sorted(
    avg_value_per_player.items(), key=lambda x: x[1], reverse=True
)[:top]
print(f"\nTop {top} clubs by average player market value:")
for node, avg_val in top_clubs_by_avg:
    club_name = B.nodes[node].get("name", "Unknown")
    league    = B.nodes[node].get("league", "Unknown")
    players   = club_degrees.get(node, 0)
    print(
        f"  {club_name:30s} | league={league:10s} "
        f"| players={players:3d} | avg_value={avg_val:.2f}"
    )


#distribution of total squad market value

plt.figure(figsize=(10,5))
plt.hist(club_str_values, bins=30, edgecolor='black')

plt.title("Distribution of total squad market value")
plt.xlabel("Total market value (€)")
plt.ylabel("Number of clubs")

def billions_millions(x, pos):
    if x >= 1e9:
        return f'€{x/1e9:.1f}B'   # billions
    elif x >= 1e6:
        return f'€{x/1e6:.0f}M'   # millions
    else:
        return f'€{x:,.0f}'       # fallback for small values

plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(billions_millions))

plt.tight_layout()
plt.show()



