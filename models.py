from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///produtos.sqlite3', echo=False)
Base = declarative_base()


class Produto(Base):
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    price = Column(Float)
    thumbnail = Column(String)

    reviews = relationship("Review", back_populates="produto", cascade=""
                                                                       ", delete-orphan")


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'), nullable=False)
    rating = Column(Integer)
    comment = Column(String)
    date = Column(String)
    reviewerName = Column(String)
    reviewerEmail = Column(String)

    produto = relationship("Produto", back_populates="reviews")


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def obter_sessao():
    return Session()
