import sqlite3
import csv

# ELO Rating Functions
def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_rating(current_rating, expected_score, actual_score, k=32):
    return current_rating + k * (actual_score - expected_score)

# Connect to the SQLite database
conn = sqlite3.connect('f1.db')
cursor = conn.cursor()

# Initialize driver ratings. Select drivers who have raced after 1990.
cursor.execute("""
    SELECT DISTINCT d.driverId, d.forename, d.surname
    FROM drivers d
    JOIN results r ON d.driverId = r.driverId
    JOIN races ra ON r.raceId = ra.raceId
    WHERE ra.year >= 1990
""")
drivers = {row[0]: {'rating': 1000, 'name': f"{row[1]} {row[2]}"} for row in cursor.fetchall()}

# Get races from 1990 onwards
cursor.execute("SELECT raceId FROM races WHERE year >= 1990")
races = [race_id for (race_id,) in cursor.fetchall()]

# Process each race
for race_id in races:
    # Get the results of the race
    cursor.execute("""
        SELECT r.driverId, positionOrder FROM results r
        WHERE raceId = ? AND r.driverId IN (SELECT driverId FROM drivers)
        ORDER BY positionOrder ASC
    """, (race_id,))
    
    race_results = cursor.fetchall()

    # Compare each driver with each other driver
    for i in range(len(race_results)):
        for j in range(i + 1, len(race_results)):
            driver_id_a = race_results[i][0]
            driver_id_b = race_results[j][0]
            
            # Calculate expected scores
            expected_score_a = calculate_expected_score(drivers[driver_id_a]['rating'], drivers[driver_id_b]['rating'])
            expected_score_b = calculate_expected_score(drivers[driver_id_b]['rating'], drivers[driver_id_a]['rating'])
            
            # Actual score - 1 if the driver won, 0.5 for draw, 0 if lost
            actual_score_a = 1
            actual_score_b = 0
            
            # Update ratings
            drivers[driver_id_a]['rating'] = update_rating(drivers[driver_id_a]['rating'], expected_score_a, actual_score_a)
            drivers[driver_id_b]['rating'] = update_rating(drivers[driver_id_b]['rating'], expected_score_b, actual_score_b)

# Close the database connection
conn.close()

# Sort drivers by ELO rating
sorted_drivers = sorted(drivers.items(), key=lambda x: x[1]['rating'], reverse=True)

# Write to CSV
with open('driver_ratings.csv', 'w', newline='') as csvfile:
    fieldnames = ['Driver Name', 'ELO Rating']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for driver_id, info in sorted_drivers:
        writer.writerow({'Driver Name': info['name'], 'ELO Rating': info['rating']})

print("Driver ratings have been written to driver_ratings.csv sorted by ELO rating.")
