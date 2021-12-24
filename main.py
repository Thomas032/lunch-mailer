from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from handle_actions import *
import threading
import time
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Profile(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    email = db.Column(db.String(100), nullable = False, primary_key=True)
    time = db.Column(db.String(50), nullable=False)
    code = db.Column(db.Integer, nullable=True)
    def __repr__(self):
        return f"{self.email},{self.time},{self.code}"


profile_put_args = reqparse.RequestParser()
profile_put_args.add_argument("email", type = str, help="Email must be added to request!", required=True)  
profile_put_args.add_argument("time", type = str, help="Time must be added to request!", required=True) 
profile_put_args.add_argument("code", type = str, required=False) # don't require user code -> only for changes like time ...

profile_del_args = reqparse.RequestParser()
profile_del_args.add_argument("email", type =str, help="email must be added to request!", required=True)
profile_del_args.add_argument("code", type =int , help = "user code must be added to request!", required=True)

profile_patch_args = reqparse.RequestParser()
profile_patch_args.add_argument("email", type = str, help="Email must be added to request", required=True)  
profile_patch_args.add_argument("time", type = str) 
profile_patch_args.add_argument("code", type = str) # don't require user code -> only for changes like time ...


fields = {
    "id":fields.Integer,
    "email":fields.String,
    "time":fields.String,
    "code":fields.Integer
}
db.create_all()
class Profile_auth(Resource):
    @marshal_with(fields)
    def put(self): #function for handling post request + authenticating
        args = profile_put_args.parse_args()
        if Profile.query.filter_by(email=args["email"]).first():
            abort(405, message="Profile already exists")
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
            if args["email"]:
                item = "Email"
                user.email = args["email"]
            elif  args["time"]:
                item = "Time"
                user.time = args["time"]
            elif args["code"]:
                item = "Code"
                user.code = args["code"]   
            db.session.commit()
            print("data updated!!")
        return user, 202
                                
                
            
    def delete(self):
        args = profile_del_args.parse_args()
        if Profile.query.filter_by(email=args["email"]).first(): # account exists
            user = Profile.query.filter_by(email=args["email"]).first()
            if user.code == args["code"]:
                db.session.delete(user)
                db.session.commit()
                return '', 204
            else:
                abort(406, message="Wrong code!")
        else:
            abort(404, message = "Email not found!")
        
                    
api.add_resource(Profile_auth, "/auth")

def check_time():
    times = []
    emails = []
    while True:
        query = Profile.query.all()
        for q in query:
            splitted = str(q).split(',')
            user_time = splitted[1]
            user_email = splitted[0]
            times.append(user_time)
            emails.append(user_email)
        for user_t in times:
            now = datetime.datetime.now().strftime("%H:%M")
            if str(now) == user_t:
                print("Matched!!!")
                send_mail(emails[times.index(user_t)])
                time.sleep(60)
                
       


if __name__ == "__main__":
    #app.run(debug = True)
    t1 = threading.Thread(target=app.run)
    t2 = threading.Thread(target = check_time)
    t1.start()
    t2.start()
  
    