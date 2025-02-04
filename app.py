# app.py
import datetime
from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from bcrypt import hashpw, gensalt, checkpw
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = 'secret_key'  # Nécessaire pour certaines fonctionnalités de Flask
app.config['JWT_SECRET_KEY'] = '@u2'
CORS(app)
jwt = JWTManager(app)
init_db(app)

# Page d'accueil
@app.route('/')
def home():
    return render_template('index.html')

# Inscription (création d'un compte utilisateur)
@app.route('/inscription', methods=['POST'])
def inscription():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'message': "Le nom d'utilisateur et le mot de passe sont requis."}), 400

        db = get_db()
        cursor = db.cursor()
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({'message': "Nom d'utilisateur déjà pris!"}), 400

        hashed_password = hashpw(password.encode(), gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        return jsonify({'message': 'Utilisateur créé avec succès'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Connexion (authentification)
@app.route('/connexion', methods=['POST'])
def connexion():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user and checkpw(password.encode(), user['password'].encode()):
        access_token = create_access_token(identity=str(user['id']), expires_delta=datetime.timedelta(days=1))
        return jsonify({'token': access_token}), 200
    return jsonify({'message': 'Identifiants incorrects !'}), 401


# Récupérer les tâches de l'utilisateur connecté
@app.route('/taches', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        user_id = get_jwt_identity()
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
        tasks = cursor.fetchall()
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ajouter une tâche
@app.route('/taches', methods=['POST'])
@jwt_required()
def create_task():
    try:
        data = request.get_json()
        title = data.get('title')
        due_date = data.get('due_date')  # Récupère la date
        if not title:
            return jsonify({'message': "Le titre de la tâche est requis."}), 400

        status = data.get('status', 'pending')
        user_id = get_jwt_identity()
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, status, due_date, user_id) VALUES (%s, %s, %s, %s)",
            (title, status, due_date, user_id)  # Ajout de la due_date
        )
        db.commit()
        return jsonify({'message': 'Tâche ajoutée !'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/taches/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'message': "Le statut de la tâche est requis."}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s",
            (status, task_id, get_jwt_identity())
        )
        db.commit()
        
        return jsonify({'message': 'Tâche mise à jour avec succès!'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/taches/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, get_jwt_identity())
        )
        db.commit()
        
        return jsonify({'message': 'Tâche supprimée avec succès!'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)