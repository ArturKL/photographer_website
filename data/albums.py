import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from transliterate import translit


class Album(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'albums'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    translit_name = sqlalchemy.Column(sqlalchemy.String)
    lenght = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.Date)

