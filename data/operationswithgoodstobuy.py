from data import db_session
from data.users import User
from data.goodtobuy import Goodstobuy

promolist = [['test', 15], ['-1', 0]]
def clear(name):
    db_sess = db_session.create_session()
    goods = db_sess.query(Goodstobuy).filter(Goodstobuy.name_customer == name)
    for el in goods:
        db_sess.delete(el)
    db_sess.commit()
    goods = []


def getprice(user):
    db_sess = db_session.create_session()
    goods = db_sess.query(Goodstobuy).filter(Goodstobuy.name_customer == user.name)
    sm = 0
    for el in goods:
        sm += el.good.price * el.amount
    sm -= (sm // 100) * user.discount
    return sm


def checkdiscount(user, promo):
    for i in range(len(promolist)):
        if promo == promolist[i][0]:
            db_sess = db_session.create_session()
            need_user = db_sess.query(User).filter(User.name == user.name).first()
            need_user.discount = promolist[i][1]
            db_sess.commit()
            break

