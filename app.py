import os
from datetime import datetime
import pytz

from flask import Flask, request, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import desc


tz = pytz.timezone("Africa/Nairobi")


app = Flask(__name__)

# project_dir = os.path.dirname(os.path.abspath(__file__))
# database_file = "sqlite:///{}".format(os.path.join(project_dir, "sqlite.db"))
# app.config["SQLALCHEMY_DATABASE_URI"] = database_file

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Wisdom(db.Model):
    symbol = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    trend = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Float, nullable=False, default=0.0)
    atr = db.Column(db.Float, nullable=False, default=0.0)
    h1choppy = db.Column(db.String(100))
    m15choppy = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime)


class Accumulator(db.Model):
    symbol = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    trend = db.Column(db.String(100), nullable=False)
    accumulate = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime)


# +-------------------------------------------------------------+
# Wise

@app.route('/wise', methods=['GET'])
def index():
    currencies = Wisdom.query.order_by(desc(Wisdom.points)).all()
    return render_template('index.html', currencies=currencies)


@app.route('/wise/mt4', methods=['GET', 'POST'])
def wise():
    try:
        symbol = request.args.get('symbol', type=str)
        trend = request.args.get('trend', type=str)
        points = request.args.get('points', type=float)
        atr = request.args.get('atr', type=float)
        h1choppy = request.args.get('h1choppy', type=str)
        m15choppy = request.args.get('m15choppy', type=str)

        currency = Wisdom.query.filter_by(symbol=symbol).first()

        if currency:
            currency.trend = trend
            currency.points = points
            currency.atr = atr
            currency.updated_at = datetime.now(tz)
            currency.h1choppy = h1choppy
            currency.m15choppy = m15choppy
            db.session.commit()

        else:
            currency = Wisdom(symbol=symbol, trend=trend, points=points, atr=atr, updated_at=datetime.now(tz), h1choppy=h1choppy, m15choppy=m15choppy)
            db.session.add(currency)
            db.session.commit()

    except Exception as e:
        print("Error: ", e)
        return Response("{'error':'error'}", status=500, mimetype='application/json')

    return Response("{'ok':'ok'}", status=200, mimetype='application/json')


@app.route("/wise/delete", methods=['GET', 'POST'])
def delete():
    try:
        symbol = request.args.get('symbol', type=str)
        currency = Wisdom.query.filter_by(symbol=symbol).first()
        db.session.delete(currency)
        db.session.commit()

    except Exception as e:
        print("Error: ", e)
        return Response("{'error':'error'}", status=500, mimetype='application/json')

    return Response("{'ok':'ok'}", status=200, mimetype='application/json')


# +-------------------------------------------------------------+
# Accumulate

@app.route('/', methods=['GET'])
@app.route('/acc', methods=['GET'])
def acce():
    currencies = Accumulator.query.order_by(desc(Accumulator.accumulate)).all()
    return render_template('accumulator.html', currencies=currencies)


@app.route('/acc/mt4', methods=['GET', 'POST'])
def accumulator():
    try:
        symbol = request.args.get('symbol', type=str)
        trend = request.args.get('trend', type=str)
        accumulate = request.args.get('accumulate', type=float)

        currency = Accumulator.query.filter_by(symbol=symbol).first()

        if currency:
            currency.trend = trend
            currency.accumulate = accumulate
            currency.updated_at = datetime.now(tz)
            db.session.commit()

        else:
            currency = Accumulator(symbol=symbol, trend=trend, accumulate=accumulate, updated_at=datetime.now(tz))
            db.session.add(currency)
            db.session.commit()

    except Exception as e:
        print("Error: ", e)
        return Response("{'error':'error'}", status=500, mimetype='application/json')

    return Response("{'ok':'ok'}", status=200, mimetype='application/json')


@app.route("/acc/delete", methods=['GET', 'POST'])
def Accdelete():
    try:
        symbol = request.args.get('symbol', type=str)
        currency = Accumulator.query.filter_by(symbol=symbol).first()
        db.session.delete(currency)
        db.session.commit()

    except Exception as e:
        print("Error: ", e)
        return Response("{'error':'error'}", status=500, mimetype='application/json')

    return Response("{'ok':'ok'}", status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
