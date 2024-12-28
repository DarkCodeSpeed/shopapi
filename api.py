from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, marshal_with, abort, fields, Api, Resource
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

# Model
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"


# Request Parser
user_args = reqparse.RequestParser()
user_args.add_argument("name", type=str, required=False, help="Name cannot be blank!")
user_args.add_argument("email", type=str, required=False, help="Email cannot be blank!")

# Marshaling fields
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}

# Resources
class Users(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        if not args['name'] or not args['email']:
            abort(400, message="Both name and email are required.")
        user = UserModel(name=args['name'], email=args['email'])
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="User with this name or email already exists.")
        return user, 201


class User(Resource):
    @marshal_with(user_fields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found.")
        return user

    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found.")
        db.session.delete(user)
        db.session.commit()
        return {'message': f"User with ID {id} deleted successfully."}, 200

    @marshal_with(user_fields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found.")
        if args.get('name'):
            user.name = args['name']
        if args.get('email'):
            user.email = args['email']
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="User with this name or email already exists.")
        return user


# API Endpoints
api.add_resource(Users, "/api/users/")
api.add_resource(User, "/api/users/<int:id>")

# Root Route
@app.route("/")
def home():
    return "<h1>Flask Application. It's made by the Asef.</h1>"

if __name__ == "__main__":
    app.run(debug=True)
