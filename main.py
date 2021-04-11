from flask import Flask, make_response, jsonify, render_template, request, url_for
from werkzeug.utils import redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.goods import Good
from data.goodtobuy import Goodstobuy
from data.loginform import LoginForm
from data.user import RegisterForm
from data.users import User
from data.address import create

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/")
def index():
    return render_template('index.html', title='Главная страница')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/pay", methods=['POST', 'GET'])
@login_required
def pay():
    if request.method == 'GET':
        create(current_user)
        return render_template('buy.html', name='static/img/' + current_user.name + '.png')
    elif request.method == 'POST':
        return render_template('buy.html')


@app.route("/catalog")
def catalog():
    db_sess = db_session.create_session()
    goods = db_sess.query(Good).filter(Good.amount > 0)
    return render_template('catalog.html', goods=goods, title='Каталог')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/goodstobuy', methods=['POST', 'GET'])
@login_required
def goodtobuy():
    db_sess = db_session.create_session()
    goods = db_sess.query(Goodstobuy).filter(Goodstobuy.name_customer == current_user.name)
    sm = 0
    if request.method == 'POST':
        for el in goods:
            db_sess.delete(el)
        db_sess.commit()
        goods = []
    for el in goods:
        sm += el.good.price * el.amount
    return render_template('goodstobuy.html', price=sm, goods=goods)


@app.route("/catalog/<name>/<rate>", methods=['GET'])
def rate(name, rate):
    rate = int(rate)
    if 0 <= rate <= 5:
        db_sess = db_session.create_session()
        new_good = db_sess.query(Good).filter(Good.name == name).first()
        new_good.rating = (new_good.rating * new_good.count_rating + rate) / (new_good.count_rating + 1)
        new_good.count_rating += 1
        db_sess.commit()
    return render_template('rating.html')


@app.route("/catalog/<name>", methods=['POST', 'GET'])
def good(name):
    db_sess = db_session.create_session()
    goods = db_sess.query(Good).filter(Good.name == name)

    if request.method == 'POST':
        db_sess = db_session.create_session()
        goods_del = db_sess.query(Goodstobuy).filter(Goodstobuy.name_good == name,
                                                     Goodstobuy.name_customer == current_user.name).first()
        if goods_del:
            db_sess.delete(goods_del)
            db_sess.commit()
        new_good = Goodstobuy(name_good=name, name_customer=current_user.name, amount=request.form['amount'])
        db_sess.add(new_good)
        db_sess.commit()

    return render_template('good.html', item=goods[0], title=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/goods.db")
    app.run()


if __name__ == '__main__':
    main()
