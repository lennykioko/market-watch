import os

from flask import Flask, request, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(
    os.path.join(project_dir, "sqlite.db"))


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Wisdom(db.Model):
    symbol = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    trend = db.Column(db.String(100), nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False, default=False)
    atr = db.Column(db.Float, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class Accumulator(db.Model):
    symbol = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    trend = db.Column(db.String(100), nullable=False)
    accumulate = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


# +-------------------------------------------------------------+
# Wise

@app.route('/wise', methods=['GET'])
def index():
    currencies = Wisdom.query.filter_by(is_valid=True).all()
    return render_template('index.html', currencies=currencies)


@app.route('/wise/mt4', methods=['GET', 'POST'])
def wise():
    try:
        symbol = request.args.get('symbol', type=str)
        trend = request.args.get('trend', type=str)
        is_valid = request.args.get('is_valid', type=bool)
        atr = request.args.get('atr', type=float)

        currency = Wisdom.query.filter_by(symbol=symbol).first()

        if currency:
            currency.trend = trend
            currency.is_valid = is_valid
            currency.atr = atr
            db.session.commit()

        else:
            currency = Wisdom(symbol=symbol, trend=trend, is_valid=is_valid, atr=atr)
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
            db.session.commit()

        else:
            currency = Accumulator(symbol=symbol, trend=trend, accumulate=accumulate)
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
