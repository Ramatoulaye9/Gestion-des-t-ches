# database.py
import mysql.connector
from flask import g

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''  # Remplacez par votre mot de passe MySQL
    app.config['MYSQL_DB'] = 'gestion_de_taches'

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Remplacez par votre mot de passe MySQL
            database='gestion_de_taches'
        )
    return g.db