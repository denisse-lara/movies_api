import sys
sys.path.insert(1, '../technical_challenge')

import psycopg2

import config


# establishing the connection
conn = psycopg2.connect(
    database="postgres",
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
)
conn.autocommit = True

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Preparing query to create a database
sql = f"CREATE database {config.DATABASE_NAME}"

# Creating a database
cursor.execute(sql)
print("Database created successfully........")

# Closing the connection
conn.close()
