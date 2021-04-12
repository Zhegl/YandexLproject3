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
from data.operationswithgoodstobuy import clear, getprice, checkdiscount

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


@app.route("/promo", methods=['POST', 'GET'])
@login_required
def promo():
    if request.method == 'GET':
        return render_template('promo.html', discount=current_user.discount)
    elif request.method == 'POST':
        checkdiscount(current_user, request.form['promo'])
        return redirect("/promo")

@app.route("/pay", methods=['POST', 'GET'])
@login_required
def pay():
    create(current_user)
    return render_template('buy.html', name='static/img/' + current_user.name + '.png')


@app.route('/afterpay')
def afterpay():
    return 'Спасибо за оформление заказа!'

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/choose", methods=['POST', 'GET'])
@login_required
def choose():
    db_sess = db_session.create_session()
    goods = db_sess.query(Goodstobuy).filter(Goodstobuy.name_customer == current_user.name)

    if request.method == 'GET':
        return render_template('choose.html', price=getprice(current_user))
    elif request.method == 'POST':
        checkdiscount(current_user, '-1')
        print('----------Новый заказ----------')
        print('Пользоватьель', current_user.name, 'на адрес', current_user.about)
        for el in goods:
            el.good.amount -= el.amount
            print(el.good.name, 'кол-во:', el.amount)
        db_sess.commit()
        print('Тип доставки:', request.form['delivery'])
        print('Комментарии к доставке:', request.form['about'])
        print('-------------------------------')
        clear(current_user.name)

        return redirect("/afterpay")


@app.route("/catalog")
def catalog():
    db_sess = db_session.create_session()
    goods = db_sess.query(Good).filter(Good.amount > 0)
    return render_template('catalog.html', goods=goods, title='Каталог')


@app.route('/edit', methods=['POST', 'GET'])
@login_required
def edit():
    if request.method == 'GET':
        return render_template('edit.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        toedit = db_sess.query(User).filter(User.name == current_user.name).first()
        toedit.about = request.form['about']
        db_sess.commit()
        return redirect("/pay")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/goodstobuy', methods=['POST', 'GET'])
@login_required
def goodstobuy():
    db_sess = db_session.create_session()
    goods = db_sess.query(Goodstobuy).filter(Goodstobuy.name_customer == current_user.name)
    if request.method == 'POST':
        clear(current_user.name)
        goods = []
    return render_template('goodstobuy.html', price=getprice(current_user), goods=goods)


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
