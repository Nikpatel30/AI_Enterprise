
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

#Creating a flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://NIKSBOT/AI_Enterprise?driver=SQL+Server?trusted_connection=yes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


#Student class to store values for student
class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25))
    last_name = db.Column(db.String(25))
    dob = db.Column(db.String(25))
    amount_due = db.Column(db.Integer)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, first_name, last_name, dob, amount_due):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.amount_due = amount_due

    def __repr__(self):
        return '' % self.id


db.create_all()


class StudentSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Student
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    dob = fields.String(required=True)
    amount_due = fields.Number(required=True)


@app.route('/student', methods=['GET'])
def index():
    get_students = Student.query.all()
    student_schema = StudentSchema(many=True)
    students = student_schema.dump(get_students)
    return make_response(jsonify({"student": students}))


@app.route('/students/<id>', methods=['GET'])
def get_student_by_id(id):
    get_student = Student.query.get(id)
    student_schema = StudentSchema()
    student = student_schema.dump(get_student)
    return make_response(jsonify({"student": student}))


@app.route('/students/<id>', methods=['PUT'])
def update_student_by_id(id):
    data = request.get_json()
    get_student = Student.query.get(id)
    if data.get('first_name'):
        get_student.first_name = data['first_name']
    if data.get('last_name'):
        get_student.last_name = data['last_name']
    if data.get('dob'):
        get_student.dob = data['dob']
    if data.get('amount_due'):
        get_student.amount_due = data['amount_due']
    db.session.add(get_student)
    db.session.commit()
    student_schema = StudentSchema(
        only=['id', 'first_name', 'last_name', 'dob', 'amount_due'])
    student = student_schema.dump(get_student)
    return make_response(jsonify({"student": student}))


@app.route('/students/<id>', methods=['DELETE'])
def delete_student_by_id(id):
    get_student = Student.query.get(id)
    db.session.delete(get_student)
    db.session.commit()
    return make_response("", 204)


@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    student_schema = StudentSchema()
    student = student_schema.load(data)
    result = student_schema.dump(student.create())
    return make_response(jsonify({"student": result}), 200)


if __name__ == "__main__":
    app.run(debug=True)
