import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

class Good(SqlAlchemyBase):
    __tablename__ = 'goods'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    rating = sqlalchemy.Column(sqlalchemy.Float)
    count_rating = sqlalchemy.Column(sqlalchemy.Integer)
    amount = sqlalchemy.Column(sqlalchemy.Integer)
    picture = sqlalchemy.Column(sqlalchemy.String)
    goodstobuy = orm.relation("Goodstobuy", back_populates='good')