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
    query = request.args.get('query', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM movies WHERE title LIKE %s", (f'%{query}%',))
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(movies)

# Add Review endpoint
@app.route('/api/reviews', methods=['POST'])
def add_review():
    # Get the review data from the request
    data = request.json
    
    # Validate the data
    if not data or 'movie_id' not in data or 'rating' not in data:
        return jsonify({"error": "Missing required fields"}), 400
        
    if not (0 <= data['rating'] <= 5):
        return jsonify({"error": "Rating must be between 0 and 5"}), 400
    
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert the review
        cursor.execute("""
            INSERT INTO reviews (movie_id, rating, comment)
            VALUES (%s, %s, %s)
        """, (data['movie_id'], data['rating'], data.get('comment', '')))
        
        # Commit the transaction
        conn.commit()
        
        # Clean up
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": "Review added successfully"}), 201
        
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)