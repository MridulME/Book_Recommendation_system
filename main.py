from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import connection&query as t

app = Flask(__name__)

book_df = t.df1
user_df = t.df2

# Train the model
def train_model(book_df):
    try:
        all_titles = book_df['Title'].tolist()
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.8, min_df=3, ngram_range=(1, 2))
        tfidf_matrix = tfidf_vectorizer.fit_transform(all_titles)
        knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
        knn_model.fit(tfidf_matrix)
        return tfidf_vectorizer, knn_model, tfidf_matrix
    except KeyError as e:
        return None, None, None
    except Exception as e:
        return None, None, None

tfidf_vectorizer, knn_model, tfidf_matrix = train_model(book_df)

# Recommend books
def recommend_books(interest_area, book_df, tfidf_vectorizer, knn_model, top_n=5, similarity_threshold=0.2):
    try:
        interest_area_tfidf = tfidf_vectorizer.transform([interest_area])
        distances, indices = knn_model.kneighbors(interest_area_tfidf, n_neighbors=top_n)
        matching_books_indices = [indices[0][i] for i in range(len(distances[0])) if distances[0][i] <= (1 - similarity_threshold)]
        if matching_books_indices:
            recommended_books = book_df.iloc[matching_books_indices]
            return recommended_books
        else:
            return "No matching books found"
    except Exception as e:
        return "No matching books found due to an error."

# Flask endpoint
@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        user_id = int(user_id)
        user_interest = user_df.loc[user_df['professor_id'] == user_id, 'interest_area'].values[0]
        recommendations = recommend_books(user_interest, book_df, tfidf_vectorizer, knn_model)
        if isinstance(recommendations, pd.DataFrame):
            recommended_books = recommendations.to_dict(orient='records')
            return jsonify(recommended_books), 200
        else:
            return jsonify({"message": recommendations}), 200
    except IndexError:
        return jsonify({"error": f"No user found with ID {user_id}"}), 404
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
