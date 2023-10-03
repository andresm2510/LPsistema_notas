from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import classes

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Defina uma chave secreta para sua aplicação

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

'''
# Classe de Usuário
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
'''
# Função para carregar usuário do banco de dados
@login_manager.user_loader
def load_user(user_id):
    user_data = classes.db.usuarios.find_one({'_id': user_id})
    if not user_data:
        return None
    return classes.Usuario(user_data['_id'])

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = classes.db.usuarios.find_one({'nomeU': username})

        if user_data and check_password_hash(user_data['senha'], password):
            user = classes.Usuario(user_data['_id'])
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
    return render_template('login.html')

# Rota de dashboard protegida
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
