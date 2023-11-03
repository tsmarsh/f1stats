import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('f1.db')
query = """
SELECT results.*, drivers.* FROM results 
INNER JOIN drivers ON results.driverId = drivers.driverId
INNER JOIN races ON results.raceId = races.raceId
WHERE results.positionText != 'NULL' 
AND races.year > '1990' 
ORDER BY results.raceId ASC, results.positionOrder;
"""

results = pd.read_sql_query(query, conn)
conn.close()

# Initial ELO settings
initial_elo = 1000
k_factor = 32

# Initialize ELO ratings for drivers
drivers_elo = {driver: initial_elo for driver in results['driverRef'].unique()}

# Function to calculate the probability of winning
def calculate_probability(ra, rb):
    return 1 / (1 + 10 ** ((rb - ra) / 400))

# Update ELO ratings after each race
for _, race in results.groupby('raceId'):
    # Sort drivers by their finishing position
    race_sorted = race.sort_values(by='positionOrder', ascending=False)
    for i in range(len(race_sorted)):
        for j in range(i + 1, len(race_sorted)):
            driver_b = race_sorted.iloc[i]['driverRef']
            driver_a = race_sorted.iloc[j]['driverRef']
            
            
            # Calculate ELO win probability
            pa = calculate_probability(drivers_elo[driver_a], drivers_elo[driver_b])
            pb = calculate_probability(drivers_elo[driver_b], drivers_elo[driver_a])
            
            # Update ELO - if both drivers DNF, it's a draw
            sa = 1
            sb = 0
            
            drivers_elo[driver_a] += k_factor * (sa - pa)
            drivers_elo[driver_b] += k_factor * (sb - pb)

# Convert the ELO ratings to a DataFrame
elo_df = pd.DataFrame(drivers_elo.items(), columns=['Driver', 'ELO'])

# Sort the DataFrame by ELO in descending order
elo_df_sorted = elo_df.sort_values(by='ELO', ascending=False)

# Save to CSV
elo_df_sorted.to_csv('f1_elo_ratings.csv', index=False)

print(elo_df_sorted)
