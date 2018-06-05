import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class carmodel(Base):
    __tablename__ = 'model'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# return in serialized form
    @property
    def serialize(self):
        return {
            'name' : self.name,
            'id':self.id,
            
        }

class modelcategory(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
    classification = Column(String(250))
    car_name = Column(Integer,ForeignKey('model.id'))
    model = relationship(carmodel)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


# return in serialized form
    @property
    def serialize(self):
        return {
            'id':self.name,
            'name' :self.name,
            'description':self.description,
            'classification': self.classification,
        }

engine = create_engine('sqlite:///carmodel.db')
Base.metadata.create_all(engine)
