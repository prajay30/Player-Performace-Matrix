from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'fplayerpm.db'

# Database connection function
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Enables accessing results by column name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 🏠 Home Page
@app.route('/')
def home():
    return render_template('index.html', title="Player Performance Matrix")

# 📖 About Page
@app.route('/about')
def about():
    return render_template('about.html', title="About - Football Player Performance Metrics")

# 🔎 Search Player Page
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('player')
    if not query:
        return redirect(url_for('home'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM players WHERE name LIKE ?", ('%' + query + '%',))
    player = cursor.fetchone()

    if player:
        return redirect(url_for('player_profile', player_id=player['id']))
    
    return "Player not found", 404

# 📞 Player Profile Page
@app.route('/player/<int:player_id>')
def player_profile(player_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT p.id, p.name, p.position, p.club, p.nationality, p.age, p.appearances, p.image_url,
               s.goals, s.assists, s.shots_on_target, s.total_passes_per_game, 
               s.tackles_won, s.distance_covered, s.clean_sheets
        FROM players p 
        LEFT JOIN player_stats s ON p.id = s.player_id
        WHERE p.id = ?
    """, (player_id,))
    
    player = cursor.fetchone()
    
    if not player:
        return "Player not found", 404
    
    player_data = dict(player)
    player_data['image_url'] = player_data['image_url'].replace('\\', '/').replace('static/', '')  # Fix image path
    
    player_stats = {key: player[key] for key in ['goals', 'assists', 'shots_on_target', 'total_passes_per_game', 'tackles_won', 'distance_covered', 'clean_sheets'] if key in player}
    
    return render_template('player.html', title="Player Profile", player=player_data, player_stats=player_stats)

# 🔄 Compare Page (Select Players)
@app.route('/compare')
def compare():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, position, club FROM players")
    players = cursor.fetchall()
    
    return render_template('compare.html', title="Compare Players", players=players)

# ⚔️ Compare Players (Results Page)
@app.route('/compare/<int:player1_id>/<int:player2_id>')
def compare_players(player1_id, player2_id):
    db = get_db()
    cursor = db.cursor()
    
    print(f"🔍 Checking Player IDs: {player1_id}, {player2_id}")  # Debugging

    # Fetch both players in one query
    cursor.execute("""
    SELECT p.id, p.name, p.position, p.club, p.age, p.image_url,
           s.goals, s.assists, s.shots_on_target, s.total_passes_per_game, 
           s.tackles_won, s.distance_covered, s.clean_sheets 
    FROM players p 
    LEFT JOIN player_stats s ON p.id = s.player_id 
    WHERE p.id IN (?, ?)
    """, (player1_id, player2_id))

    players = {p["id"]: dict(p) for p in cursor.fetchall()}  # Convert Row to dict

    print(f"✅ Fetched Players Count: {len(players)}")  # Debugging

    # Ensure we have exactly 2 players
    if player1_id not in players or player2_id not in players:
        print("❌ Error: One or both players not found!")
        return "One or both players not found", 404  

    player1 = players[player1_id]
    player2 = players[player2_id]

    print(f"✅ Player 1: {player1['name']} - {player1['club']}")  # Debugging
    print(f"✅ Player 2: {player2['name']} - {player2['club']}")  # Debugging

    # Ensure image paths are correctly formatted
    if player1['image_url']:
        player1['image_url'] = player1['image_url'].replace('\\', '/')
    if player2['image_url']:
        player2['image_url'] = player2['image_url'].replace('\\', '/')
    
    return render_template(
        'compare_result.html', 
        title="Comparison Results", 
        player1=player1, 
        player2=player2
    )


if __name__ == '__main__':
    app.run(debug=True)
