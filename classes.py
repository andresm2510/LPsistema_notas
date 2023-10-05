#classes
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_decode
from dotenv import load_dotenv
load_dotenv()
import os
mongoUrl = os.getenv("cluster")
banco = MongoClient(mongoUrl)
db = banco["structures"]
collection = db["users"]
collection2_1 = db["alunos"]
collection2_2 = db["admins"]
collection3 = db["tarefas"]
collection3_1 = db["entregaTarefas"]
collection3_2 = db["entregaListas"]
collection4 = db["listas"]
collection5 = db["notas"]
collectionC = db["config"]



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

    def visualizarAlunos():
        x = collection2_1.find()
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

    num_total_listas = 0  # Variável global para o número total de listas

def cadastrarLista(numero_lista, descricao, data_entrega):
    # Atualiza o número total de listas no banco de dados
    num_listas = collectionC.find_one({})  
    num_listas = num_listas.get('num_listas', 0) + 1
    collectionC.update_one({}, {"$set": {"num_listas": num_listas}}, upsert=True)

    # Cria a nova lista
    nova_lista = {
        "numero_lista": numero_lista,
        "descricao": descricao,
        "data_entrega": data_entrega,
        "entrega": ""
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
    
    def __init__(self, _id, aluno_nome, tarefa_id, lista_id, nota):
        self.___id = _id
        self.aluno_nome = aluno_nome
        self.tarefa_id = tarefa_id
        self.lista_id = lista_id 
        self.nota = nota

    def lancarTarefa(self):
        # Buscar o ID do aluno com base no nome do aluno
        aluno_data = collection2_1.find_one({'nomeA': self.aluno_nome})
        i=1
        if aluno_data:
            aluno_id = aluno_data['_id']

            # Cadastrar a nota no banco de dados com o ID do aluno
            result = collection5.insert_one({
                "aluno_id": aluno_id,
                "tarefa": self.tarefa_id,
                "nota": self.nota
            })
            return result.inserted_id  # Retorna o ID da nota cadastrada
        else:
            return None  # Retorna None se o aluno não for encontrado

    def lancarLista(aluno_nome, lista_id, nota):
        # Buscar o ID do aluno com base no nome do aluno
        aluno_data = collection2_1.find_one({'nomeA': aluno_nome})
        
        if aluno_data:
            aluno_id = aluno_data['_id']

            # Cadastrar a nota no banco de dados com o ID do aluno
            result = collection5.insert_one({
                "aluno_id": aluno_id,
                "lista_id": lista_id,
                "nota": nota
            })
            return result.inserted_id  # Retorna o ID da nota cadastrada
        else:
            return None  # Retorna None se o aluno não for encontrado
        

    def consultar(aluno_nome):
        # Buscar o ID do aluno com base no nome do aluno
        aluno_data = collection2_1.find_one({'nomeA':aluno_nome})
        
        if aluno_data:
            aluno_id = aluno_data['_id']

            # Consultar as notas do aluno no banco de dados com o ID do aluno
            notas = collection5.find({"aluno_id": aluno_id})
            return list(notas)  # Retorna uma lista de notas do aluno
        else:
            return None  # Retorna None se o aluno não for encontrado

    def calcularSituacao(self):
    # Consultar as notas das tarefas do aluno no banco de dados
        aluno_data = collection2_1.find_one({'nomeA': self.aluno_nome})
        if aluno_data:
            aluno_id = aluno_data['_id']

            #Suponha que você tem o prefixo "tarefa_" seguido do ID da tarefa para os campos de notas das tarefas
            notas_tarefas = collection5.find_one({"aluno_id": aluno_id})
        
            if notas_tarefas:
                    t1 = notas_tarefas.get(f"tarefa_{self.tarefa1}", 0)  # Obtém a nota da primeira tarefa (ou 0 se não existir)
                    t2 = notas_tarefas.get(f"tarefa_{self.tarefa2}", 0)  # Obtém a nota da segunda tarefa (ou 0 se não existir)
            else:
                    t1 = t2 = 0  # Define notas como 0 se não houver notas registradas

            x = (t1 + t2) * 0.8

            # Consultar as notas das listas do aluno no banco de dados
            config = collectionC.find_one({})  # Supondo que você tenha uma coleção chamada "config" para armazenar configurações
            if config:
                num_listas = config.get('num_listas', 0)
                return num_listas
            else:
                num_listas = 0
        
            
            notas_listas = []
            for lista_id in range(1, num_listas + 1):  # Suponha que você tenha um número total de listas
                nota_lista = notas_tarefas.get(f"lista_{lista_id}", 0)  # Obtém a nota da lista (ou 0 se não existir)
                notas_listas.append(nota_lista)

            # Calcular a média das notas das listas
            if notas_listas:
                media_listas = sum(notas_listas) / len(notas_listas)
            else:
                media_listas = 0

            # Calcular a nota final (np) usando a fórmula fornecida
            np = x + (media_listas * 0.2)

            # Determinar a situação com base na nota final
            if np >= 7:
                return (np, "Passou")
            elif 3 <= np < 7:
                return (np, "Final")
            else:
                return (np, "Reprovado")
        else:
            return None  # Retorna None se o aluno não for encontrado
