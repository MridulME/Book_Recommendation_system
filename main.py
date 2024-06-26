from table_reader import connect_to_mysql
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pandas as pd

app = Flask(__name__)

book_df, user_df = connect_to_mysql()


# Train the model
def train_model(book_df):
    try:
        all_titles = book_df['Title'].tolist()
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
#       tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_df=0.8, min_df=3, ngram_range=(1, 2))
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
def recommend_books(interest_areas, book_df, tfidf_vectorizer, knn_model, top_n=5, similarity_threshold=0.1):
    try:
        interest_areas_list = [ia.strip() for ia in interest_areas.split(',')]
        interest_areas_tfidf = tfidf_vectorizer.transform(interest_areas_list)

        matching_books_indices = set()
        for interest_area_tfidf in interest_areas_tfidf:
            distances, indices = knn_model.kneighbors(interest_area_tfidf, n_neighbors=top_n)
            matching_indices = [indices[0][i] for i in range(len(distances[0])) if
                                distances[0][i] <= (1 - similarity_threshold)]
            matching_books_indices.update(matching_indices)

        if matching_books_indices:
            recommended_books = book_df.iloc[list(matching_books_indices)]
            return recommended_books
        else:
            return "No matching books found"
    except Exception as e:
        return "No matching books found due to an error."


# Flask endpoint to recommend books based on user ID
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


# Flask endpoint to recommend books based on interest area
@app.route('/recommend_by_interest', methods=['GET'])
def recommend_by_interest():
    interest_area = request.args.get('interest_area')
    if not interest_area:
        return jsonify({"error": "Interest area is required"}), 400

    try:
        recommendations = recommend_books(interest_area, book_df, tfidf_vectorizer, knn_model)
        if isinstance(recommendations, pd.DataFrame):
            recommended_books = recommendations.to_dict(orient='records')
            return jsonify(recommended_books), 200
        else:
            return jsonify({"message": recommendations}), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
