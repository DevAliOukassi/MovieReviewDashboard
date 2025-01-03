from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

# Create Flask application
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5000"}}) 

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
    
@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get movie details
        cursor.execute("""
            SELECT m.*, 
                   AVG(r.rating) as average_rating,
                   COUNT(r.id) as review_count
            FROM movies m
            LEFT JOIN reviews r ON m.id = r.movie_id
            WHERE m.id = %s
            GROUP BY m.id
        """, (movie_id,))
        
        movie = cursor.fetchone()
        
        if not movie:
            return jsonify({"error": "Movie not found"}), 404
        
        # Clean up
        cursor.close()
        conn.close()
        
        return jsonify(movie)
        
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500
    
@app.route('/api/movies/<int:movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id):
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all reviews for the movie
        cursor.execute("""
            SELECT id, rating, comment, created_at
            FROM reviews
            WHERE movie_id = %s
            ORDER BY created_at DESC
        """, (movie_id,))
        
        reviews = cursor.fetchall()
        
        # Clean up
        cursor.close()
        conn.close()
        
        return jsonify(reviews)
        
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500

@app.route('/api/movies/<int:movie_id>/recommendations', methods=['GET'])
def get_recommendations(movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get similar movies based on genre
        cursor.execute("""
            SELECT m2.*, 
                   AVG(r.rating) as average_rating,
                   COUNT(r.id) as review_count
            FROM movies m1 
            JOIN movies m2 ON m1.genre LIKE CONCAT('%', SUBSTRING_INDEX(m2.genre, ',', 1), '%')
            LEFT JOIN reviews r ON m2.id = r.movie_id
            WHERE m1.id = %s 
            AND m2.id != %s
            GROUP BY m2.id
            ORDER BY average_rating DESC, review_count DESC
            LIMIT 5
        """, (movie_id, movie_id))
        
        recommendations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(recommendations)
        
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)