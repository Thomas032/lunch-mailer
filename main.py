from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from handle_actions import *
import threading
import time
from sqlalchemy import create_engine

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)


class Profile(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, primary_key=True)
    time = db.Column(db.String(50), nullable=False)
    code = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"{self.email},{self.time},{self.code}"


profile_put_args = reqparse.RequestParser()
profile_put_args.add_argument("email", type=str, help="Email must be added to request!", required=True)
profile_put_args.add_argument("time", type=str, help="Time must be added to request!", required=True)
profile_put_args.add_argument("code", type=str,
                              required=False)  # don't require user code -> only for changes like time ...

profile_del_args = reqparse.RequestParser()
profile_del_args.add_argument("email", type=str, help="email must be added to request!", required=True)
profile_del_args.add_argument("code", type=int, help="user code must be added to request!", required=True)

profile_patch_args = reqparse.RequestParser()
profile_patch_args.add_argument("email", type=str, help="Email must be added to request", required=True)
profile_patch_args.add_argument("time", type=str)
profile_patch_args.add_argument("code", type=str)  # don't require user code -> only for changes like time ...

fields = {
    "id": fields.Integer,
    "email": fields.String,
    "time": fields.String,
    "code": fields.Integer
}


db.create_all()


class ProfileAuth(Resource):
    @marshal_with(fields)
    def put(self):  # function for handling post request + authenticating
        args = profile_put_args.parse_args()
        user = Profile.query.filter_by(email=args["email"]).first()
        if user:
            abort(405, message="Profile already exists")
        for profile in Profile.query.all():
            if profile.time == args["time"]:
                abort(403, message="Time ia already reserved")

        else:
            profile = Profile(email=args["email"], time=args["time"], code=args["code"])
            db.session.add(profile)
            db.session.commit()
            print(f"User {args['email']} added to database!!")

            return profile, 201

    @marshal_with(fields)
    def patch(self):
        args = profile_patch_args.parse_args()
        user = Profile.query.filter_by(email=args["email"]).first()
        if not user:
            abort(404, message="Email not found!")
        else:
            if args["time"]:
                item = "Time"
                user.time = args["time"]
            elif args["code"]:
                item = "Code"
                user.code = args["code"]
            db.session.commit()
        return user, 202

    @marshal_with(fields)
    def delete(self):
        args = profile_del_args.parse_args()
        if Profile.query.filter_by(email=args["email"]).first():  # account exists
            user = Profile.query.filter_by(email=args["email"]).first()
            db.session.delete(user)
            db.session.commit()
            return '', 204
        else:
            abort(404, message="Email not found!")

    @marshal_with(fields)
    def get(self):
        args = profile_patch_args.parse_args()
        profile = Profile.query.filter_by(email=args["email"]).first()
        if profile:
            return profile, 200
        else:
            abort(404, message="Profile couldnt be found!")


api.add_resource(ProfileAuth, "/auth")


def check_time():
    engine = create_engine("sqlite:///database.db")
    connection = engine.raw_connection()

    while True:
        table = connection.execute("SELECT email ,time FROM Profile")
        for row in table:
            cur_time = datetime.datetime.now().strftime("%H:%M")

            if cur_time == row[1] and datetime.datetime.today().isoweekday()!= 7 or datetime.datetime.today().isoweekday()!= 6:
                print("matched")
                send_mail(row[0])
                delay = 60 - int(datetime.datetime.now().strftime("%S"))
                time.sleep(delay)


if __name__ == "__main__":
    t1 = threading.Thread(target=app.run)
    t1.start()
    t2 = threading.Thread(target=check_time)
    t2.start()
