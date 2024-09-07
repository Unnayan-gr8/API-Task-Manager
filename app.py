from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, marshal_with, reqparse, fields
from werkzeug.exceptions import HTTPException
from werkzeug.sansio.response import Response
from datetime import datetime

app = Flask(__name__)
api = Api(app)
#------------------------------------DATABASE MANAGEMENT---------------------------------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///sampledb.sqlite3"

db = SQLAlchemy(app)

app.app_context().push()

class Tasks(db.Model):
    created_on = db.Column(db.DateTime(), nullable = False)
    LUO = db.Column(db.DateTime(), nullable = False)
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    description = db.Column(db.String())
    status = db.Column(db.String(), nullable = False)

#------------------------------------Error Handling---------------------------------------------------------------------

class NotFoundError(HTTPException):
    def __init__(self, message, status_code):
        self.response = make_response(message, status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(jsonify(message), status_code)

class AlreadyExists(HTTPException):
    def __init__(self, message, status_code):
        self.response = make_response(message, status_code)
 
#------------------------------------API Routes---------------------------------------------------------------------

task_m = {
            "created_on"        : fields.DateTime,
            "LUO"  : fields.DateTime,
            "id"           : fields.Integer,
            "name"         : fields.String,
            "description"  : fields.String,
            "status"       : fields.String,
       }

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('description')
parser.add_argument('status')

class TaskApi(Resource):
    @marshal_with(task_m)
    def get(self, id):
        s = db.session.query(Tasks).filter(Tasks.id == id).first()
        
        if s:
            return s
        
        raise NotFoundError(message= "Task Not Found", status_code=404)
    
    @marshal_with(task_m)
    def post(self):
        args = parser.parse_args()
        time = datetime.now()
        name = args.get('name', None)
        description = args.get('description', None)
        status = args.get('status', None)
        
        if time == None:
            raise BusinessValidationError(status_code=400, error_code="TASK001", error_message="TASK ID REQUIRED")
        if name == None or name.strip() == "":
            raise BusinessValidationError(status_code=400, error_code="TASK002", error_message="TASK NAME REQUIRED")
        if status == None or name.strip() == "":
            raise BusinessValidationError(status_code=400, error_code="TASK003", error_message="TASK STATUS REQUIRED")
        
        texist = db.session.query(Tasks).filter(Tasks.name == name).first()

        if texist:
            raise AlreadyExists(message = "Task Already Exists", status_code=409)
        
        new_entry = Tasks(created_on=time, LUO=time, name=name, description=description, status=status)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry
    
    @marshal_with(task_m)
    def put(self, id):
        args = parser.parse_args()
        LUO = datetime.now()
        name = args.get('name', None)
        description = args.get('description', None)
        status = args.get('status', None)
        
        if LUO == None:
            raise BusinessValidationError(status_code=400, error_code="TASK001", error_message="TASK ID REQUIRED")
        if id == None:
            raise BusinessValidationError(status_code=400, error_code="TASK001", error_message="TASK ID REQUIRED")
        if name == None or name.strip() == "":
            raise BusinessValidationError(status_code=400, error_code="TASK002", error_message="TASK NAME REQUIRED")
        if status == None or name.strip() == "":
            raise BusinessValidationError(status_code=400, error_code="TASK003", error_message="TASK STATUS REQUIRED")
        
        texist = db.session.query(Tasks).filter(Tasks.id == id).first()

        if texist == None:
            raise NotFoundError(message="Task Not Found", status_code=404)
        
        name_exists = db.session.query(Tasks).filter(Tasks.name == name).first()
        
        if name_exists and texist != name_exists:
            raise AlreadyExists(message = "Task Name Already Exists", status_code=409)
        
        texist.LUO = LUO
        texist.name = name
        texist.description = description
        texist.status = status

        db.session.commit()
        return texist
    
    def delete(self, id):
        texists = db.session.query(Tasks).filter(Tasks.id == id).first()

        if texists == None:
            raise NotFoundError(status_code=404)
        
        db.session.delete(texists)
        db.session.commit()
        return make_response("")
    
class StatsTotalTasks(Resource):
    def get(self):
        total_tasks = db.session.query(Tasks).count()
        return jsonify({"total_tasks": total_tasks})

class StatsCompletedTasks(Resource):
    def get(self):
        completed_tasks = db.session.query(Tasks).filter(Tasks.status == 'Completed').count()
        return jsonify({"completed_tasks": completed_tasks})


api.add_resource(TaskApi, '/task', '/task/<int:id>')
api.add_resource(StatsTotalTasks, '/stats/total_tasks')
api.add_resource(StatsCompletedTasks, '/stats/completed_tasks')

if __name__ == '__main__':
    app.run(debug=True)