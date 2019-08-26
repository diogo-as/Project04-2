from models import Base, Categoria, Item
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///catalogo.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Clean database
session.query(Item).delete()
session.query(Categoria).delete()
session.commit()

# To populate DB for example purposes


categories = {
  1: "Cicling",
  2: "Tennis",
  3: "Skate",
  4: "Basketball",
  5: "Football",
  6: "Climbing",
  7: "Skate",
  8: "Basketball",
  9: "Golf",
  10: "Handball"
}

for i in categories.values():
    addGuest = Categoria(name=str(i))
    session.add(addGuest)
    session.commit()

for i in range(1, 51):
    if i <= 10:
        item = Item(
            name="item "+str(i),
            description="description "+str(i),
            categoria_id=int(i)
        )
        session.add(item)
        session.commit()
    if 10 < i <= 20:
        item = Item(
            name="item "+str(i),
            description="description "+str(i),
            categoria_id=int(i)-10
        )
        session.add(item)
        session.commit()
    if 20 < i <= 30:
        item = Item(
            name="item "+str(i),
            description="description "+str(i),
            categoria_id=int(i)-20
        )
        session.add(item)
        session.commit()
    if 30 < i <= 40:
        item = Item(
            name="item "+str(i),
            description="description "+str(i),
            categoria_id=int(i)-30
        )
        session.add(item)
        session.commit()
    if 40 < i <= 50:
        item = Item(
            name="item "+str(i),
            description="description "+str(i),
            categoria_id=int(i)-40
        )
        session.add(item)
session.commit()
