import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from networkx.algorithms import community

#paths loading

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Dataset_Football_Players" / "archive"

CLUBS_CLEAN_PATH     = DATA_DIR / "clubs_clean.csv"
TRANSFERS_CLEAN_PATH = DATA_DIR / "transfers_clean.csv"

PLAYERS_CLEAN_PATH = DATA_DIR / "players_clean.csv"
players_clean = pd.read_csv(PLAYERS_CLEAN_PATH)

clubs      = pd.read_csv(CLUBS_CLEAN_PATH)
transfers  = pd.read_csv(TRANSFERS_CLEAN_PATH)

# make sure that we record clubs which exist in clubs_clean file , double check here apart from that one already done in clean_data.py
valid_clubs = set(clubs["club_id"].unique())
transfers = transfers[
    transfers["from_club_id"].isin(valid_clubs)
    & transfers["to_club_id"].isin(valid_clubs)
    & (transfers["from_club_id"] != transfers["to_club_id"])
].copy()

min_year = transfers["year"].min()
max_year = transfers["year"].max()

print(f"Transfers data: {len(transfers)} rows, years {min_year}–{max_year}")

#building the directed club-club weighted network

def build_transfer_network(df, start_year=None, end_year=None):

    # restrict by year if requested
    if start_year is not None:
        df = df[df["year"] >= start_year]
    if end_year is not None:
        df = df[df["year"] <= end_year]

    G = nx.DiGraph()

    # add club nodes with attributes
    for _, row in clubs.iterrows():
        cid = int(row["club_id"])
        if cid not in valid_clubs:
            continue
        node_id = f"club_{cid}"
        G.add_node(
            node_id,
            club_id=cid,
            name=row["name"],
            league=row["domestic_competition_id"],
        )

    # aggregate transfers to get weights
    edge_weights = (
        df.groupby(["from_club_id", "to_club_id"])
          .size()
          .reset_index(name="weight")
    )

    for _, row in edge_weights.iterrows():
        u = f"club_{int(row['from_club_id'])}"
        v = f"club_{int(row['to_club_id'])}"
        w = int(row["weight"])
        if G.has_edge(u, v):
            G[u][v]["weight"] += w
        else:
            G.add_edge(u, v, weight=w)

    return G


G = build_transfer_network(transfers)


# basic info for the network
print("\nDirected club – club transfer network (full period)")
print(f"Nodes (clubs): {G.number_of_nodes()}")
print(f"Edges        : {G.number_of_edges()}")



# degrees and strengths 
out_deg = dict(G.out_degree())                    
in_deg  = dict(G.in_degree())                     
out_str = dict(G.out_degree(weight="weight"))     
in_str  = dict(G.in_degree(weight="weight"))     

out_deg_values = np.array(list(out_deg.values()))
in_deg_values  = np.array(list(in_deg.values()))
out_str_values = np.array(list(out_str.values()))
in_str_values  = np.array(list(in_str.values()))

print("\n Degree statistics")
print(f"Out-degree mean: {out_deg_values.mean():.2f}, median: {np.median(out_deg_values):.2f}")
print(f"In-degree  mean: {in_deg_values.mean():.2f}, median: {np.median(in_deg_values):.2f}")

print("\n Strength statistics (weighted by number of transfer)")
print(f"Out-strength mean: {out_str_values.mean():.2f}, median: {np.median(out_str_values):.2f}")
print(f"In-strength  mean: {in_str_values.mean():.2f}, median: {np.median(in_str_values):.2f}")




#top clubs and sending and receiving transfers
top = 5

def print_top_clubs(metric_dict, title, reverse=True):
    ranking = sorted(metric_dict.items(), key=lambda x: x[1], reverse=reverse)[:top]
    print(f"\nTop {top} clubs by {title}:")
    for node, value in ranking:
        name   = G.nodes[node].get("name", "Unknown")
        league = G.nodes[node].get("league", "Unknown")
        print(f"  {name:30s} | league={league:10s} | {title}={value:.0f}")

print_top_clubs(out_deg, "out-degree (distinct destinations)")
print_top_clubs(in_deg,  "in-degree (distinct sources)")
print_top_clubs(out_str, "out-strength (players sent)")
print_top_clubs(in_str,  "in-strength (players received)")


# players in - players out, computing the balance between them
net_balance = {
    node: in_str.get(node, 0) - out_str.get(node, 0)
    for node in G.nodes()
}
print_top_clubs(net_balance, "net transfer balance (in - out)")





#  we study overall structure ignoring direction, but keeping weights, in a undirected graph view
H = G.to_undirected()

print("\nUndirected view of transfer network")
print(f"Nodes: {H.number_of_nodes()}")
print(f"Edges: {H.number_of_edges()}")


# communities detection
print("\nDetecting communities (greedy modularity on H)")
communities = community.greedy_modularity_communities(H, weight="weight")
print(f"Number of communities found: {len(communities)}")

# largest communities with club names
sorted_comms = sorted(communities, key=len, reverse=True)[:3]
for idx, comm in enumerate(sorted_comms, start=1):
    print(f"\nCommunity {idx} (size {len(comm)}):")
    sample_nodes = list(comm)[:10] 
    for node in sample_nodes:
        name   = H.nodes[node].get("name", "Unknown")
        league = H.nodes[node].get("league", "Unknown")
        print(f"  {name:30s} | league={league:10s}")
    if len(comm) > 10:
        print("")





def build_windows(window_size=5):
    windows = []
    start = min_year
    while start <= max_year:
        end = min(start + window_size - 1, max_year)
        windows.append((start, end))
        start = end + 1
    return windows


def summarize_window(start, end):

    # filter transfers in this window
    df_win = transfers[(transfers["year"] >= start) & (transfers["year"] <= end)]
    if df_win.empty:
        print(f"  {start}-{end}: no transfers recorded.")
        return

    # build directed network for this window
    G_win = build_transfer_network(df_win, start_year=start, end_year=end)

    print(
        f"\nWindow {start}-{end}: "
        f"nodes={G_win.number_of_nodes()}, edges={G_win.number_of_edges()}"
    )

    # top clubs by number of transfers
    out_str_win = dict(G_win.out_degree(weight="weight"))
    in_str_win  = dict(G_win.in_degree(weight="weight"))

    def print_top_clubs_window(metric_dict, title, k=3):
        ranking = sorted(metric_dict.items(), key=lambda x: x[1], reverse=True)[:k]
        print(f"  Top {k} clubs by {title}:")
        for node, value in ranking:
            name   = G_win.nodes[node].get("name", "Unknown")
            league = G_win.nodes[node].get("league", "Unknown")
            print(f"    {name:30s} | league={league:10s} | {title}={value:.0f}")

    print_top_clubs_window(out_str_win, "out-strength (players sent)")
    print_top_clubs_window(in_str_win,  "in-strength (players received)")

    # top players by number of transfers
    player_counts = (
        df_win.groupby("player_id")
              .size()
              .reset_index(name="num_transfers")
              .sort_values("num_transfers", ascending=False)
              .head(5)
    )

    player_counts["player_id"] = player_counts["player_id"].astype(int)
    top_players = player_counts.merge(
        players_clean,
        on="player_id",
        how="left"
    )

    print("Top 5 players by number of transfers:")
    for _, row in top_players.iterrows():
        pid   = row["player_id"]
        name  = row.get("name", "Unknown")
        count = int(row["num_transfers"])
        print(f"    ID={pid:<8d} | {name:30s} | transfers={count}")


if __name__ == "__main__":
    print("\nTemporal windows (5-year ranges):")
    for (start, end) in build_windows(window_size=5):
        summarize_window(start, end)


import matplotlib.pyplot as plt

windows = ["2002–06", "2007–11", "2012–16", "2017–21", "2022–26"]

top_out = [2, 20, 55, 90, 75] 
top_in  = [2, 16, 56, 93, 79]  

plt.figure(figsize=(8, 5))
plt.plot(windows, top_out, marker='o', linewidth=2, label="Top exporter (out-strength)")
plt.plot(windows, top_in,  marker='s', linewidth=2, label="Top importer (in-strength)")
plt.title("Temporal evolution in most active importer and exporer")
plt.xlabel("5 years")
plt.ylabel("Number of players sent/received")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

players = [
    "José Fonte",
    "Aubameyang",
    "Ciro Immobile",
    "José Machín",
    "Roberto Piccoli",
]

transfers_counts = [2, 4, 5, 5, 7]

plt.figure(figsize=(8, 5))
plt.bar(players, transfers_counts)
plt.title("Most transferred player in each time window")
plt.xlabel("Player")
plt.ylabel("Number of transfers in that window")
plt.tight_layout()
plt.show()

