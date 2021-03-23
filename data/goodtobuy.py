import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Goodstobuy(SqlAlchemyBase):
    __tablename__ = 'goodstobuy'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name_customer = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.name"))
    user = orm.relation('User')
    name_good = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("goods.name"))
    good = orm.relation('Good')
    amount = sqlalchemy.Column(sqlalchemy.Integer)