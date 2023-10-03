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
collection2 = db["alunos"]
collection3 = db["tarefas"]
collection3_1 = db["entregaTarefas"]
collection3_2 = db["entregaListas"]
collection4 = db["listas"]
collection5 = db["notas"]

post = {"_id": 0, "name": "", "senha": "" }
collection.insert_one(post)
#para alunos     post = {"_id": 0, "name": ""}
#para tarefas    post = {"_id": 0, "name": "", "descricao": "", "dataEntrega": "" , "entrega": ""}
#para listas     post = {"_id": 0, "listaX": "", "descricao": "", "dataEntrega": "" , "entrega": ""}
#para notas      post = {"_id": 0, "aluno_id": "", "tarefa_id": "", "nota": "" , "notaL": ""}

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
                user.roles = ['admin']
                return 2
            
            else:
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

    def listar():
        pass

    def receber():
        pass

class Notas:

    def __init__(self, _id, aluno_id, tarefa_id, nota):
        self.___id =_id
        self.aluno_id = aluno_id
        self.tarefa_id = tarefa_id
        self.nota = nota

    def cadastrar():
        pass

    def consultar():
        pass
