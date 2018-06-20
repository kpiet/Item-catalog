
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import  Base, modelcategory, carmodel, User

engine = create_engine('sqlite:///carmodel.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# lamborghini model category - Urus
model1 = carmodel(name="Urus")

session.add(model1)
session.commit()

category1 = modelcategory(name = "Urus", classification = "SUV", description = "A super sports car soul and the functionality typical for an SUV: this is the Lamborghini Urus, the world's first Super Sport Utility Vehicle. Urus' disctinctive silhouette  with a dynamic flying coupe line shows its super sports origins, while its outstanding proportions convey strength, solidity and safety. " , model = model1)

session.add(category1)
session.commit()



# lamborghini model category - Huracan
model1= carmodel(name="Huracan")

session.add(model1)
session.commit()

category1 = modelcategory(name = "Huracan coupe", classification = "coupe", description = "The Huracan Coupe has been created for unprecedented performance. All the power and acceleration of a naturally aspirated V-10 engine, without giving up control or fun of driving. This is all thanks to the all-wheel drive system and the 7-speed Lamborghini Doppia Frizione(LDF) dual-clutch transmission.", model = model1)

session.add(category1)
session.commit()

category2 = modelcategory(name = "Huracan spyder", classification = "spyder", description = "Designed to cut through the air and become one with the sky, the Huracan Spyder is the pinnacle of italian taste and hand craftsmanship, a sports car concenpt elevated to the performance and sensation of a coupe. ", model = model1)

session.add(category2)
session.commit()


# lamborghini model category - Aventador
model1 = carmodel(name="Aventador")

session.add(model1)
session.commit()


category1 = modelcategory(name = "Aventador s coupe", classification = "coupe", description = "Exclusive Lamborghini design and the new V12 engine with a whopping 740 HP now join the most sophisticaed technology of the range, featuring the new LDVA(Lamborghini Dinamica Veicolo Attiva/Lamborghini Active Vehicle Dynamics), which offer an unparalleled driving experience. ", model = model1)

session.add(category1)
session.commit()

category2 = modelcategory(name = "Aventador s roadster", classification = "roadster", description = "The new V12 engine with a whopping 740 HP and the exclusiveness of Lamborghini design, unparalleled in this open top version, are joined in the Aventador S Roadster by the most sophisticated technology of the range, including the new LDVA(Lamborghini Dinamica Veicolo Attiva). ", model = model1)

session.add(category2)
session.commit()




# lamborghini model category - Centenario

model4 = carmodel(name="Centenario")

session.add(model4)
session.commit()

category1 = modelcategory(name = "Centenario roadster", classification = "roadster", description = "The new Lamborghini Centenario represents a new, extremely precious piece in the Lamborghini's one_off strategy. It is a perfect example of the innovative design and the engineering skills of the bull- branded manufacturer. ", model = model4)

session.add(category1)
session.commit()

print ("Categories have been added")
