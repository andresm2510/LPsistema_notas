#classes
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os
cluster = os.getenv("cluster")
db = cluster["structure"]
collection = db["users"]
collection2_1 = db["alunos"]
collection2_2 = db["admins"]
collection3 = db["tarefas"]
collection3_1 = db["entregaTarefas"]
collection3_2 = db["entregaListas"]
collection4 = db["listas"]
collection5 = db["notas"]

post = {"_id": 0, "name": "", "senha": "" }
collection.insert_one(post)

admin_permission = Permission(RoleNeed('admin'))
professor_permission = Permission(RoleNeed('professor'))
aluno_permission = Permission(RoleNeed('aluno'))

class Usuario(UserMixin):
    def __init__(self, user_id, username,email, password, roles=None):
        self.__id =user_id
        self.nome = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.roles  = roles or ['aluno']

    def get_id(self):
        return self.__id
    
    def autenticar(username, password):
        user_data = db.usuarios.find_one({'nomeU': username})
        if user_data and check_password_hash(user_data['senha'], password):
            user = Usuario(user_data['_id'], user_data['nomeU'], user_data['email'], password)

            # Determine o papel do usuário com base nas informações do banco de dados
            if 'admin' in user_data.get('roles', []):
                user.is_admin = True
                user.roles = ['admin']
                return 2
            
            else:
                user.is_aluno = True
                user.roles = ['aluno']
                return 1
        


    def cadastrar(user_id, username,email, password, roles=None):
        novo_usuario = Usuario(user_id=None, username=username, email=email, password=password, roles=['aluno'])
        result=collection.insert_one({
            'nomeU': username,
            'email': email,
            'senha': novo_usuario.password_hash
        })
        novo_usuario.__id = result.inserted_id
        return novo_usuario

class Aluno:
    def __init__(self,_id,nome):
        self.___id =_id
        self.nome = nome
    
    def cadastrar(aluno_id,nome,matricula):
        novo_aluno = Aluno(aluno_id=matricula, nome=nome)
        result=collection2_1.insert_one({
            '_id': aluno_id,  # O ID do aluno é o mesmo do usuário
            'nomeA': nome,
            'matricula': matricula
        })
        novo_aluno.___id = result.inserted_id
        return novo_aluno
    
    def listar():
        pass

    def enviar():
        pass

    def calcularSituacao():
        
        pass


class Administrador:

    def __init__(self, _id, nome):
        self.___id =_id
        self.nome = nome

    def cadastrar(self,admin_id,nome,matricula):
        novo_admin = Administrador(admin_id=matricula, nome=nome)
        result=collection2_2.insert_one({
            '_id': admin_id,  # O ID do administrador é o mesmo do usuário
            'nomeA': nome,
    
        })
        novo_admin.___id = result.inserted_id
        return novo_admin
    
    def calcularSituacao():
        pass

    def visualizarAlunos():
        pass

class Tarefa:

    def __init__(self, _id, nome, descricao, dataEntrega):
        self.___id =_id
        self.nome = nome
        self.descricao = descricao
        self.dataEntrega = dataEntrega

    def cadastrarTarefa(nome, descricao, data_entrega):
        nova_tarefa = {
                "nome": nome,
                "descricao": descricao,
                "data_entrega": data_entrega,
                "entrega": ""  # Você pode definir o valor padrão aqui
            }
        collection3.insert_one(nova_tarefa)

    def cadastrarLista(numero_lista, descricao, data_entrega):
        nova_lista = {
                "numero_lista": numero_lista,
                "descricao": descricao,
                "data_entrega": data_entrega,
                "entrega": ""  # Você pode definir o valor padrão aqui
            }
        collection4.insert_one(nova_lista)

    
    def receberlista(arquivo_entregue, numero_lista,current_user):
        arquivo_entregue.save('pasta_de_entregas/' + arquivo_entregue.filename)
        nova_entrega = {
                "aluno_id": current_user.get_id(),  # Obtém o ID do aluno atualmente logado
                "numero_lista": numero_lista,
                "arquivo_entregue": 'pasta_de_entregas/' + arquivo_entregue.filename
            }
        collection3_2.insert_one(nova_entrega)

    def receber(arquivo_entregue, tarefa_id,current_user):
        # Salve o arquivo entregue em algum lugar (por exemplo, em uma pasta no servidor)
        # Nomeie o arquivo de forma única para evitar conflitos
        arquivo_entregue.save('pasta_de_entregas/' + arquivo_entregue.filename)
        nova_entrega = {
                "aluno_id": current_user.get_id(),  # Obtém o ID do aluno atualmente logado
                "tarefa_id": tarefa_id,
                "arquivo_entregue": 'pasta_de_entregas/' + arquivo_entregue.filename
            }
        collection3_1.insert_one(nova_entrega)


class Notas:

    def __init__(self, _id, aluno_nome, tarefa_id, nota):
        self.___id = _id
        self.aluno_nome = aluno_nome
        self.tarefa_id = tarefa_id
        self.nota = nota

    def cadastrar(self):
        # Buscar o ID do aluno com base no nome do aluno
        aluno_data = collection2_2.find_one({'nomeA': self.aluno_nome})
        
        if aluno_data:
            aluno_id = aluno_data['_id']

            # Cadastrar a nota no banco de dados com o ID do aluno
            result = collection5.insert_one({
                "aluno_id": aluno_id,
                "tarefa_id": self.tarefa_id,
                "nota": self.nota
            })
            return result.inserted_id  # Retorna o ID da nota cadastrada
        else:
            return None  # Retorna None se o aluno não for encontrado

    def consultar(self):
        # Buscar o ID do aluno com base no nome do aluno
        aluno_data = collection2_2.find_one({'nomeA': self.aluno_nome})
        
        if aluno_data:
            aluno_id = aluno_data['_id']

            # Consultar as notas do aluno no banco de dados com o ID do aluno
            notas = collection5.find({"aluno_id": aluno_id})
            return list(notas)  # Retorna uma lista de notas do aluno
        else:
            return None  # Retorna None se o aluno não for encontrado
