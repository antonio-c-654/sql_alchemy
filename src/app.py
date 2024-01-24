from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

load_dotenv()

#app de ORM
app = Flask(__name__)

#lo de dentro de [] lo saca de la docuentacion # antonio es la PASSWORD
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#contexto para el db.create_all()
app.app_context().push()

#conexion a base de datos y configuracion
db = SQLAlchemy(app) 
ma = Marshmallow(app)


#crear modelo para base de datos, almacenar tareas. 
# Creamos objeto que es la base de datos y sus atributos son columnas y elemntos de la db
# la clase task HEREDA de db.model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))

    #necesito constructor, con este objeto podremos crear tareas, esto podremos introducirlo en la bd
    def __init__(self, title, description):
        self.title = title
        self.description = description

#crea la base  de datos, necesita contexto
# lee todas lac lases que sean db.model
#crea todas las tablas que tengamos ...
db.create_all()

# creamos un esquema para interactuar de forma facil con nuestros modelos
class TaskSchema(ma.Schema):
    #esto es una clase dentro de una clase esta en la docu
    class Meta:
        fields = ('id', 'title', 'description')


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# comentario... ver platform...

@app.route('/tasks', methods=['POST'])
def create_task():

    # print(request.json)
    title = request.json['title']
    description = request.json['description']

    #llamamos al constructor de Task para crear una nueva tarea
    new_task = Task(title, description)
    print("Tarea creada con exito.")

    #almacenamos los datos en la base de datos, esto es como un INSERT
    db.session.add(new_task)
    db.session.commit()
    print("Almacenamiento en la base de datos -->OK!")

    # en formato json devolvemos la tarea
    return task_schema.jsonify(new_task)


#ruta read all task - GET
@app.route('/tasks', methods=['GET'])
def get_tasks():
    #que devuelve todas las tareas
    all_tasks = Task.query.all()
    #lista con los datos
    result = tasks_schema.dump(all_tasks)
    # convertimos en json los resultados del select de la base de datos por el ORM
    return jsonify(result)

# ruta read single task por eso la ruta task y no tasks, tienes que poner el id en la url con la task que quieras ver - GET
@app.route('/task/<id>', methods=['GET'])
def get_task(id):
    task = Task.query.session.get(Task, id)

    return task_schema.jsonify(task)

# ruta update task - PUT
@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):

    #necesito recibir los nuevos datos
    task = Task.query.session.get(Task, id)
    title = request.json['title']
    description = request.json['description']

    # print(title, description) #si quieres ver result
    task.title = title
    task.description = description

    db.session.commit()

    return task_schema.jsonify(task)

# ruta metodo para borrar
@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.session.get(Task, id)

    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)

# ruta de landign page - pagina de inicio
@app.route('/', methods=['GET'])
def index():

    return jsonify({'message':'welcome to my fist API with Python Flask and Mysql'})


# borramos todos las tasks
@app.route('/tasks/delete', methods=['DELETE'])
def delete_tasks():

    db.session.query(Task).delete()
    db.session.commit()

    return jsonify({"message":"All task deleted!!!"})


if __name__ == "__main__":
    app.run(debug=True)

# hemos ejecutado esto en Visual
## mysql -u root -p
## create database flaskmysql; #tiene que coincidir el nombre con app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/flaskmysql'
## show databases;

# locahost:5000
# pip install mysql-connector-python
# Thunder Client --> extension --> new request
