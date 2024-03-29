from json import dumps
from . import Singleton
from typing import Dict, Any, Union
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()


class Read(Base):
    __tablename__ = 'reads'

    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer)
    value = Column(String)
    metric = relationship("Metric", back_populates="reads")

    def as_dict(self) -> Dict[str, Any]:
        return {'sensor_id': self.sensor_id,
                'value':     self.value}

    def __str__(self) -> str:
        return dumps(self.as_dict() )


class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    reads = relationship('Read', order_by=Read.id)

    def as_dict(self) -> Dict[str, Any]:
        return {'id':    self.id,
                'date':  self.date,
                'reads': [r.asDict() for r in self.reads]}

    def __str__(self) -> str:
        return dumps(self.as_dict())


class Database(Singleton):
    def __init__(self) -> None:
        engine = create_engine('db.sqlite3')
        Base.metadata.create_all(engine)
        self.session = Session(bind=engine)

    def add(self, value: Union[Read, Metric]):
        try:
            self.session.add(value)
        except:
            self.session.rollback()
            raise
        else:
            self.session.commit()

    def delete(self, value: Union[Read, Metric]):
        try:
            self.session.delete(value)
        except:
            self.session.rollback()
            raise
        else:
            self.session.commit()
