from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

# Create Flask application
app = Flask(__name__)
CORS(app)  # This allows our future frontend to talk with our API

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rivenop21",
        database="movie_dashboard"
    )

# Search endpoint
@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    # Get the search query from URL (like /api/movies/search?query=Batman)
    query = request.args.get('query', '')
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Returns results as dictionaries
    
    # Search for movies matching the query
    cursor.execute("SELECT * FROM movies WHERE title LIKE %s", (f'%{query}%',))
    movies = cursor.fetchall()
    
    # Clean up
    cursor.close()
    conn.close()
    
    # Return results as JSON
    return jsonify(movies)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
    