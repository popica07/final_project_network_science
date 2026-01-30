# Mapping Player Mobility and Club Connectivity in World Football Using Network Science

This repository contains the **Final Project for the Network Science course** at **Maastricht University**.  
The project applies network science techniques to analyze professional football data, focusing on **player mobility**, **club connectivity**, and the **evolution of the transfer market** over more than two decades.

## 👥 Authors
- **Popa Ștefan-Andrei**
- **Eduard Levinschi**

---

## 🧠 Project Overview

Professional football forms a complex system where clubs and players interact through transfers across leagues and countries.  
In this project, we model football as a networked system to uncover **structural, temporal, and economic patterns** that are not visible through traditional analysis.

We construct and analyze **two complementary networks**:

1. **Player–Club Bipartite Network**  
   - Captures the current affiliation between players and clubs  
   - Used to analyze squad size, market value distribution, and inequality between clubs  

2. **Directed Club–Club Transfer Network**  
   - Represents player transfers between clubs over time  
   - Edge direction indicates transfer flow, weight equals number of transfers  
   - Studied both as an aggregated network (2002–2026) and in **5-year temporal windows**

---

## 📂 Repository Structure
├── Code/
│ └── clean_data.py # Data cleaning and preprocessing scripts
│
├── Dataset_Football_Players/
│ └── archive/
│ ├── players.csv
│ ├── clubs.csv
│ ├── transfers.csv
│ ├── players_clean.csv
│ ├── clubs_clean.csv
│ └── transfers_clean.csv
│
├── Final_Project_Report_Popa_Stefan_Levinschi_Eduard.pdf
├── Presentation_Network_Science_Popa_Stefan_Andrei_Levinschi_Eduard.pdf
├── Project_Proposal.pdf
├── .gitignore
└── README.md


---

## 🧹 Data Preprocessing

The original dataset (Kaggle / Transfermarkt) contained multiple CSV files and attributes not relevant to network construction.

Key preprocessing steps:
- Removal of unused tables (games, events, valuations, etc.)
- Attribute selection for players, clubs, and transfers
- Removal of duplicates and invalid records
- Conversion of market values and identifiers to numeric formats
- Temporal filtering to ensure consistency across networks

Only **players with a valid current club** were kept for the bipartite network.

---

## 📊 Network Analysis

### 1️⃣ Player–Club Bipartite Network
- Nodes: players and clubs
- Edges: affiliation between a player and their most recent club
- Size:
  - 32,601 players
  - 439 clubs
  - 32,601 edges

Main findings:
- Strong inequality in squad market values
- Elite clubs maintain **small but highly valuable squads**
- Lower-tier clubs rely on larger rosters with lower average value
- Market value drives network structure more than squad size

---

### 2️⃣ Directed Club–Club Transfer Network
- Nodes: clubs
- Directed edges: transfers between clubs
- Edge weight: number of players transferred

Key statistics (2002–2026):
- 439 clubs
- 12,920 directed edges
- Mean out-degree ≈ 29
- Mean out-strength ≈ 47

Main findings:
- Transfer market becomes significantly **denser over time**
- Certain clubs act as **global hubs** (e.g. SL Benfica, Chelsea)
- Clear **community structure**, largely aligned with leagues and regions
- Transfer ecosystems show strong intra-regional interaction

Temporal analysis (5-year windows) reveals:
- Rapid growth in transfer activity after 2011
- Increasing concentration of transfers around central clubs
- Rising player mobility in recent years

---

## 📈 Why Certain Metrics Were Not Used

- **Clustering coefficient** is not meaningful for bipartite graphs (no triangles by definition)
- Directed transfer networks rarely form triangular motifs in practice
- Focus was placed on degree, strength, community detection, and temporal evolution

---

## ⚠️ Limitations

- Sparse transfer data in early periods (2002–2010)
- Youth academy movements may introduce minor noise
- Retired players excluded, emphasizing modern football structure

These limitations are acknowledged and discussed in the report.

---

## 🔮 Future Work

Potential extensions include:
- Dynamic multilayer networks with yearly snapshots
- Integration of player attributes (age, nationality, position)
- Graph Neural Networks (GNNs) for transfer prediction
- Shock analysis (e.g. COVID-19 impact on transfer dynamics)

---

## 🛠️ Technologies Used

- Python
- pandas
- Network science concepts:
  - bipartite graphs
  - directed weighted networks
  - community detection
  - temporal analysis

---

## 📄 Documentation

- **Final Project Report**: detailed methodology, analysis, and results  
- **Presentation**: summarized findings and visualizations  
- **Project Proposal**: initial motivation and research plan  

---

## 🎓 Course Context

This project was completed as part of the **Network Science** course at  
**Maastricht University**, Faculty of Science and Engineering.
