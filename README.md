# catapult-auth
<h3>Authentication/Authorization System</h3>


This project automatically adds the following routes to a project. Uses LDAP authentication using local domain of the webserver. Role-Based.

/auth/login <br>
/auth/logout <br>
/welcome <br>


```
from flask import Flask
from catapult_auth import CatapultAuth, login_required, templated, roles_allowed, roles_denied

app = Flask(__name__)
app.secret_key = "OMG"
CatapultAuth(app)


@app.get('/')
@login_required
@roles_denied(['System Administrator'])
@templated('index.html')
def index():
    pass


if __name__ == '__main__':
    app.run()
```
