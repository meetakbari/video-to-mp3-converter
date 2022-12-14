import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    print("before db connection....")
    try:
        conn = mysql.connection
        print("conn ---> ", conn)
        cur = conn.cursor()
        print("cur ---> ", cur)
    except:
        return "db connection error", 500

    print("after getting cursor ----> ", cur)
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )
    print("result of execution of query : ", res)

    if res > 0:
        user_row = cur.fetchone()
        cur.close();
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials [JWT token]", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded_jwt = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403 #403: client is forbidden from accessing a valid URL
    
    return decoded_jwt, 200 


def createJWT(username, secret, authz):
    """ 
    function used to create JWT token based on username passed to the login route with 
    secret key taken from environ variable JWT_SECRET
    """
    return jwt.encode({
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        }, 
        secret,
        algorithm="HS256"    
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000, debug=True)