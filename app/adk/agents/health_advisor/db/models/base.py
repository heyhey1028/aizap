"""SQLAlchemy ベースクラス"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy ベースクラス

    全てのモデルはこのクラスを継承する。
    """

    pass
