from django.shortcuts import render
from pyexpat.errors import messages
from django.shortcuts import render
import os
from django.conf import settings
from django.contrib import messages
import pandas as pd
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# def home(request):
#     return render(request, 'home.html')

def movie(mov, year, num, rat):
    error = 0
    csv_file = os.path.join(settings.BASE_DIR, 'we23', 'datasets', 'movies.csv')
    with open(csv_file, 'r', encoding='utf-8') as file:
        movies = pd.read_csv(csv_file)
    
    csv_file = os.path.join(settings.BASE_DIR, 'we23', 'datasets', 'ratings.csv')
    with open(csv_file, 'r', encoding='utf-8') as file:
        ratings = pd.read_csv(csv_file)

    # Calculate the average rating for each movie
    avg_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()

    # Merge the movies and average ratings dataframes
    movies = pd.merge(movies, avg_ratings, on='movieId')

    # Create a TfidfVectorizer object to convert the movie titles into vectors
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['title'])

    # Calculate the cosine similarity between the movie title vectors
    cosine_sim = cosine_similarity(tfidf_matrix)

    # Define a function to get movie recommendations based on user input
    def get_recommendations(title, cosine_sim=cosine_sim, movies=movies):
        # Get the index of the movie that matches the title
        idx = movies[movies['title'] == title].index[0]

        # Get the cosine similarity scores for all movies compared to the input movie
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the movies by their similarity scores in descending order
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the top 10 most similar movies (excluding the input movie)
        # sim_scores.loc[sim_scores['rating'] >= int(rat)]
        # sim_scores = sim_scores[1:int(num)+1]
        movie_indices = [i[0] for i in sim_scores]
        recommendations = movies.iloc[movie_indices][['title', 'genres', 'rating']]
        return recommendations

    try: 
        recommendations = get_recommendations(string.capwords(mov) + ' ' + '(' + year + ')')
        recommendations = recommendations[recommendations['rating'] >= int(rat)]
        recommendations = recommendations[1:int(num)+1]
        # for x in recommendations:
        #   print(x)
        return(recommendations.sort_values(by=['rating'], ascending=[False]))
    except IndexError:
        print('error')


def movie_recommendations(mov, year, num, rat):
    # Get movie recommendations
    movie_list = movie(mov = mov,year = year, num = num, rat = rat)
    # movie_list = movie_list.to_html(index=False, classes='table')
    if movie_list is None:
        return {}
    else:
        movie_list = movie_list.to_html(index = False, classes='table table-bordered')
        # Render the template with the movie recommendations
        context = {'movie_list': movie_list}
        # return render(request, 'recom.html', context)
        return context

def msg(request):
    return render(request, 'msg.html')

def home(request):
    # Generate list of years for dropdown
    years = range(1903, 2018 + 1)
    number = range(10,50+1, 5)
    rating = range(1,6)
    # Handle form submission
    if request.method == 'POST':
        movie_name = request.POST['movie_name']
        movie_year = request.POST.get('movie_year', None)
        num = request.POST.get('number', None)
        rat = request.POST.get('rating', None)
        if movie_year and num and rat:
            movie_list = movie_recommendations(movie_name, movie_year, num, rat)
            
        else:
            return render(request, 'msg.html')
        if len(movie_list) == 0:
            return render(request, 'msg.html')
        else:
            return render(request, 'recom.html', movie_list)
    else:
    # Render the template with the list of years and number of movies
        context = {}
        context['years'] = years
        context['number'] = number
        context['rating'] = rating
        return render(request, 'home.html', context)