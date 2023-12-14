# Importando bibliotecas
import csv
from flask import Flask, request, jsonify, render_template, redirect
import random

app = Flask(__name__)

# Simulando um banco de dados de usuários e filmes
users = {}
movies = {}

# Carregando dados de usuários do arquivo CSV
with open('users.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        user_id = row[0]
        name = row[1]
        password = row[2]
        genre = row[3]
        users[name] = {'id': user_id, 'password': password, 'genre': genre}

# Carregando dados de filmes do arquivo CSV
with open('movies.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        movies[row['movieId']] = {'id': row['movieId'],
                                  'title': row['title'], 'genre': row['genres']}
        # Carregando dados de músicas do arquivo CSV
songs = {}

with open('songs.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        songs[row['songId']] = {'id': row['songId'], 'title': row['title'], 'artist': row['artist'], 'genre': row['genre']}

# Simulando avaliações dos usuários
ratings = {}
your_genre_options = ['Action', 'Comedy', 'Drama', 'Pop', 'Rock', 'Funk']

# Rota principal da aplicação
@app.route('/')
def index():
    return render_template('index.html')

# Rota de registro de novos usuários
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        film_genre = request.form['film_genre']
        music_genre = request.form['music_genre']

        if name in users:
            return jsonify({'error': 'Username already exists'}), 400

        user_id = len(users) + 1
        users[name] = {'id': user_id, 'password': password, 'film_genre': film_genre, 'music_genre': music_genre}

        # Salvando dados de usuários no arquivo CSV
        with open('users.csv', 'a', newline='') as csvfile:
            fieldnames = ['id', 'name', 'password', 'film_genre', 'music_genre']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'id': user_id, 'name': name,
                            'password': password, 'film_genre': film_genre, 'music_genre': music_genre})

        return redirect('/login')

    return render_template('register.html')

# Rota de autenticação de usuários registrados
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name in users and users[name]['password'] == password:
            return redirect(f'/recommendations?user_id={name}')
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    return render_template('login.html')

# Rota de recomendação dos filmes
@app.route('/recommendations')
def get_recommendations():
    user_id = request.args.get('user_id')
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404

    film_genre = users[user_id]['film_genre']
    music_genre = users[user_id]['music_genre']
    user_ratings = ratings.get(user_id, {})

    # Filtragem colaborativa simples para filmes
    movie_recommendations = [movie_info for movie_id, movie_info in movies.items() if movie_info['genre'] == film_genre and movie_id not in user_ratings]

    # Filtragem colaborativa simples para músicas
    song_recommendations = [song_info for song_id, song_info in songs.items() if song_info['genre'] == music_genre and song_id not in user_ratings]

    # Selecionar aleatoriamente até 5 filmes e 5 músicas do mesmo gênero
    selected_movies = random.sample(movie_recommendations, min(5, len(movie_recommendations)))
    selected_songs = random.sample(song_recommendations, min(5, len(song_recommendations)))

    # Crie listas separadas de recomendações para filmes e músicas
    movie_recommendations_list = [{
        'title': movie_info['title'],
        'description': movie_info['genre']
    } for movie_info in selected_movies]

    song_recommendations_list = [{
        'title': song_info['title'],
        'description': song_info['genre'],
        'artist': song_info['artist']
    } for song_info in selected_songs]

    # Renderiza diretamente a página HTML com as recomendações
    return render_template('recommendations.html', movie_recommendations=movie_recommendations_list, song_recommendations=song_recommendations_list)

if __name__ == '__main__':
    app.run(debug=True)

    # Rota de edição do perfil
    @app.route('/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        user_id = request.args.get('user_id')
        
        if request.method == 'POST':
            film_genre = request.form['film_genre']
            music_genre = request.form['music_genre']

            # Atualize as categorias de filmes e músicas no perfil do usuário
            users[user_id]['film_genre'] = film_genre
            users[user_id]['music_genre'] = music_genre

            # Atualize os dados no arquivo CSV se necessário

            return redirect(f'/recommendations?user_id={user_id}')

        # Renderize a página de edição do perfil
        return render_template('edit_profile.html', user_id=user_id, genres=your_genre_options)
