
# This code only shows the possibility of updating the database that i created to behave my way.

import sqlite3

# Connect to the database
conn = sqlite3.connect("refugees.db")
cursor = conn.cursor()

# Update all from Uganda to pakistan
cursor.execute("UPDATE refugees SET country_of_origin = 'Pakistan'")

# Commit changes and close connection
conn.commit()
conn.close()

print("All country_of_origin values updated to Pakistan.")
