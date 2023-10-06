from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import  url_encode
from pymongo import MongoClient
import re
import classes

#FALTA PAG PARA LANÇAR NOTAS E VER NOTAS!!!!!!!!!!!!

app = Flask(__name__)
app.secret_key = 'uma_chave'  

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
admin_permission = Permission(RoleNeed('admin'))
aluno_permission = Permission(RoleNeed('aluno'))

@login_manager.user_loader
def load_user(user_id):
    user_data = classes.db.usuarios.find_one({'_id': user_id})
    
    if not user_data:
        return None
    return classes.Usuario(user_data['_id'])

# Rota de login
@app.route('/', methods=['GET', 'POST'])
def init():
    return(redirect(url_for('login')))

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
            return redirect(url_for('/'))
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        matricula = request.form['matricula']

        existing_user = classes.collection.find_one({'email': email})
        if existing_user:
            flash('Este email já está registrado. Faça login ou use outro email.', 'danger')
            return render_template ('cadastro.html')
        if matricula.isdigit() and len(matricula) == 9:  # Aluno: matrícula contém apenas dígitos e tem comprimento 9
            roles = ['aluno']
            classes.Usuario.cadastrar(user_id=matricula, username=username, email=email, password=password, roles=roles)
            classes.Aluno.cadastrar( aluno_id=matricula,nome=username, matricula=matricula)
            return redirect(url_for('/'))
        elif re.match(r'^[A-Z]{3}\d{3}$', matricula):  # Administrador: matrícula no formato 'XXX000'
            roles = ['admin']
            classes.Usuario.cadastrar(user_id=matricula, username=username, email=email, password=password, roles=roles)
            classes.Administrador.cadastrar(user_id=matricula, username=username)
        else:
            flash('Formato de matrícula inválido. Use um formato válido.', 'danger')
            return render_template("cadastro.html")

        classes.Usuario.cadastrar(user_id=None, username=username, email=email, password=password, roles=roles)

        flash('Registro bem-sucedido! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')
    

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@classes.admin_permission.require(http_exception=403)
def admin_dashboard(): 
    if request.method== 'POST':
        if "cadastro_tarefas" in request.form:
            return redirect(url_for('cadastrar_tarefa'))
        if "cadastro_listas" in request.form:
            return redirect(url_for('cadastrar_lista'))	
        if "lancar_notas" in request.form:
            return redirect(url_for('lancar_notas'))
        if "vizualizar_notas" in request.form:
            return redirect(url_for('vizualizar_notas'),classes.Administrador.visualizarAlunos())
        

    return render_template('admin_dashboard.html')


@app.route('/aluno_dashboard')
@login_required
@classes.aluno_permission.require(http_exception=403)
def aluno_dashboard():
    if request.method== 'POST':
        if "enviar_tarefa" in request.form:
            return redirect(url_for('receber_tarefa'))
        if "enviar_listas" in request.form:
            return redirect(url_for('receber_lista'))	
        if "vizualizar_notas" in request.form:
            return redirect(url_for('vizualizar_notas'),classes.Notas.consultar(current_user.get_id()))
    return render_template('aluno_dashboard.html')



@app.route('/cadastrar_tarefa', methods=['GET', 'POST'])
@login_required
@classes.admin_permission.require(http_exception=403)
def cadastrar_tarefa():
    if classes.current_user.is_admin:
        if request.method == 'POST':
            nome = request.form['nome']
            descricao = request.form['descricao']
            data_entrega = request.form['data_entrega']
            
            classes.Administrador.cadastrarTarefa(nome, descricao, data_entrega) 

            flash('Tarefa cadastrada com sucesso!', 'success')
            return redirect(url_for('admin_dashboard')) 
        return render_template('cadastrar_tarefa.html') 
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    return (redirect(url_for('admin_dashboard')))

@app.route('/cadastrar_lista', methods=['GET', 'POST'])
@login_required  
@classes.admin_permission.require(http_exception=403)
def cadastrar_lista():
    if classes.current_user.is_admin: 
        if request.method == 'POST':

            numero_lista = request.form['numero_lista']
            descricao = request.form['descricao']
            data_entrega = request.form['data_entrega']
            
            classes.Administrador.cadastrarLista(numero_lista, descricao, data_entrega) 

            flash('Lista cadastrada com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))  
        return render_template('cadastrar_lista.html') 
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('admin_dashboard'))  

@app.route('/receber_lista', methods=['GET', 'POST'])
@login_required 
@classes.aluno_permission.require(http_exception=403)
def receber_lista():
    if classes.current_user.is_aluno: 
        if request.method == 'POST':
            # Obtenha os dados do formulário
            numero_lista = request.form['numero_lista']
            arquivo_entregue = request.files['arquivo_entregue']
            
            classes.Tarefa.receberlista(numero_lista, arquivo_entregue, current_user.get_id())

            flash('lista entregue com sucesso!', 'success')
            return redirect(url_for('aluno_dashboard'))  
        return render_template('receber_lista.html')  
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('aluno_dashboard'))  
    
@app.route('/receber_tarefa', methods=['GET', 'POST'])
@login_required  
@classes.aluno_permission.require(http_exception=403)
def receber_tarefa():
    if classes.current_user.is_aluno: 
        if request.method == 'POST':

            tarefa_id = request.form['tarefa_id']
            arquivo_entregue = request.files['arquivo_entregue']
            
            classes.Tarefa.receber(tarefa_id, arquivo_entregue, current_user.get_id())

            flash('Tarefa entregue com sucesso!', 'success')
            return redirect(url_for('aluno_dashboard'))  
        return render_template('receber_tarefa.html') 
    else:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('aluno_dashboard')) 


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

