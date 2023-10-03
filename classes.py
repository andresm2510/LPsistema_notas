#classes
from pymongo import MongoClient
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os
cluster = os.getenv("cluster")
db = cluster["structure"]
collection = db["users"]
collection2 = db["alunos"]
collection3 = db["tarefas"]
collection4 = db["listas"]
collection5 = db["notas"]

post = {"_id": 0, "name": "", "senha": "" }
collection.insert_one(post)
#para alunos     post = {"_id": 0, "name": ""}
#para tarefas    post = {"_id": 0, "name": "", "descricao": "", "dataEntrega": "" , "entrega": ""}
#para listas     post = {"_id": 0, "listaX": "", "descricao": "", "dataEntrega": "" , "entrega": ""}
#para notas      post = {"_id": 0, "aluno_id": "", "tarefa_id": "", "nota": "" , "notaL": ""}

class Usuario(UserMixin):
    def __init__(self, user_id, username,email, password):
        self.__id =user_id
        self.nome = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return self.__id
    
    def autenticar(self, nome, senha):
        pass    

    def cadastrar():
        #para usuarios   post = {"_id": 0, "name": "", "senha": "" }
        pass

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

    def cadastrarTarefa():
        pass

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

    def cadastrar():
        pass

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
