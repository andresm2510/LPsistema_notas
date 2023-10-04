from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import re
import classes

#FALTA PAG PARA LANÇAR NOTAS E VER NOTAS!!!!!!!!!!!!

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Defina uma chave secreta para sua aplicação

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
        a=classes.Usuario.autenticar(username, password)

        if a==2:
            # Determine o papel do usuário com base nas informações do banco de dados   
            flash('Login bem-sucedido como administrador!', 'success')
            return redirect(url_for('admin_dashboard'))  # Redirecione para a página de administrador
    
        elif a==1:  
            flash('Login bem-sucedido como aluno!', 'success')
            return redirect(url_for('aluno_dashboard'))  # Redirecione para a página de aluno

        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
            return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Obtenha os dados do formulário de registro
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        matricula = request.form['matricula']

        # Verifique se o usuário já existe
        existing_user = classes.collection.find_one({'email': email})
        if existing_user:
            flash('Este email já está registrado. Faça login ou use outro email.', 'danger')
            return redirect(url_for('cadastro'))
        if matricula.isdigit() and len(matricula) == 9:  # Aluno: matrícula contém apenas dígitos e tem comprimento 9
            roles = ['aluno']
            classes.Usuario.cadastrar(user_id=matricula, username=username, email=email, password=password, roles=roles)
            classes.Aluno.cadastrar(user_id=matricula, username=username, matricula=matricula)
        elif re.match(r'^[A-Z]{3}\d{3}$', matricula):  # Administrador: matrícula no formato 'XXX000'
            roles = ['admin']
            classes.Usuario.cadastrar(user_id=matricula, username=username, email=email, password=password, roles=roles)
            classes.Administrador.cadastrar(user_id=matricula, username=username)
        else:
            flash('Formato de matrícula inválido. Use um formato válido.', 'danger')
            return redirect(url_for('cadastro'))

        # Crie um novo usuário com a função determinada
        classes.Usuario.cadastrar(user_id=None, username=username, email=email, password=password, roles=roles)

        flash('Registro bem-sucedido! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

@app.route('/admin/dashboard')
@login_required
@classes.admin_permission.require(http_exception=403)
def admin_dashboard():
    #opcoes para a pag de cadsatro de tarefas e listas, lancamento de notas e 
    return render_template('admin_dashboard.html')


@app.route('/aluno/dashboard')
@login_required
@classes.aluno_permission.require(http_exception=403)
def aluno_dashboard():
    return render_template('aluno_dashboard.html')
#tem q ter rotas pra enviar tarefas,listas e ver notas
# Rota de dashboard protegida
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/receber-tarefa', methods=['GET', 'POST'])
@login_required  # Certifica-se de que o usuário está autenticado como aluno
@classes.aluno_permission.require(http_exception=403)
def receber_tarefa():
    if classes.current_user.is_aluno:  # Supondo que você tenha um atributo 'is_aluno' no seu modelo de usuário para verificar se é um aluno
        if request.method == 'POST':
            # Obtenha os dados do formulário
            tarefa_id = request.form['tarefa_id']
            arquivo_entregue = request.files['arquivo_entregue']
            
            classes.Tarefa.receber(tarefa_id, arquivo_entregue, current_user.get_id())

            flash('Tarefa entregue com sucesso!', 'success')
            return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada
        return render_template('receber_tarefa.html')  # Renderize o formulário HTML para receber a tarefa
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada
    
@app.route('/receber-lista', methods=['GET', 'POST'])
@login_required  # Certifica-se de que o usuário está autenticado como aluno
@classes.aluno_permission.require(http_exception=403)
def receber_tarefa():
    if classes.current_user.is_aluno:  # Supondo que você tenha um atributo 'is_aluno' no seu modelo de usuário para verificar se é um aluno
        if request.method == 'POST':
            # Obtenha os dados do formulário
            numero_lista = request.form['numero_lista']
            arquivo_entregue = request.files['arquivo_entregue']
            
            classes.Tarefa.receberlista(numero_lista, arquivo_entregue, current_user.get_id())

            flash('lista entregue com sucesso!', 'success')
            return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada
        return render_template('receber_lista.html')  # Renderize o formulário HTML para receber a tarefa
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Rota para cadastrar tarefa (somente para administradores)
@app.route('/cadastrar-tarefa', methods=['GET', 'POST'])
@login_required  # Certifica-se de que o usuário está autenticado como administrador
@classes.admin_permission.require(http_exception=403)
def cadastrar_tarefa():
    if classes.current_user.is_admin:  # Supondo que você tenha um atributo 'is_admin' no seu modelo de usuário para verificar se é um administrador
        if request.method == 'POST':
            # Obtenha os dados do formulário
            nome = request.form['nome']
            descricao = request.form['descricao']
            data_entrega = request.form['data_entrega']
            
            # Execute a lógica para cadastrar a tarefa no banco de dados
            classes.Administrador.cadastrarTarefa(nome, descricao, data_entrega) 

            flash('Tarefa cadastrada com sucesso!', 'success')
            return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada
        return render_template('cadastrar_tarefa.html')  # Renderize o formulário HTML para cadastrar a tarefa
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada
    
@app.route('/cadastrar-lista', methods=['GET', 'POST'])
@login_required  # Certifica-se de que o usuário está autenticado como administrador
@classes.admin_permission.require(http_exception=403)
def cadastrar_lista():
    if classes.current_user.is_admin:  # Supondo que você tenha um atributo 'is_admin' no seu modelo de usuário para verificar se é um administrador
        if request.method == 'POST':
            # Obtenha os dados do formulário
            numero_lista = request.form['numero_lista']
            descricao = request.form['descricao']
            data_entrega = request.form['data_entrega']
            
            # Execute a lógica para cadastrar a lista no banco de dados
            classes.Administrador.cadastrarLista(numero_lista, descricao, data_entrega) 

            flash('Lista cadastrada com sucesso!', 'success')
            return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada
        return render_template('cadastrar_lista.html')  # Renderize o formulário HTML para cadastrar a lista
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))  # Redirecione para a página de dashboard ou outra página apropriada

if __name__ == '__main__':
    app.run(debug=True)

