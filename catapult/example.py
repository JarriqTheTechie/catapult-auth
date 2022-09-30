import datetime

from flask import Flask, g

from catapult import Catapult, render_inline

from catapult_ext import JinjaX


app = Flask(__name__)
app.jinja_env.add_extension('catapult.catapult_ext.CatapultExt')
app.secret_key = "agadgdgaj"

Catapult(app)
CATAPULT_ANNOTATE = True


@app.before_request
def before_request():
    mydate = datetime.datetime.now()
    g.current_month = mydate.strftime("%B")
    g.current_year = str(datetime.datetime.now().year)
    g.prior_year = str(datetime.datetime.now().year - 1)


@app.route('/')
def index():
    return "hi"


if __name__ == '__main__':
    app.run()
