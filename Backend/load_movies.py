import pandas as pd
import mysql.connector

dataset_url = "/Users/macbookair/Downloads/IMDB-Movie-Data.csv"
df = pd.read_csv(dataset_url)

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rivenop21",
    database="movie_dashboard"
)
cursor = connection.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    genre VARCHAR(255),
    year INT
)
"""
cursor.execute(create_table_query)

for index, row in df.iterrows():
    insert_query = """
    INSERT INTO movies (title, genre, year)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (row["Title"], row["Genre"], row["Year"]))

connection.commit()
cursor.close()
connection.close()
