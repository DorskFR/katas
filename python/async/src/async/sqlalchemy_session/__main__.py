from contextlib import contextmanager
from typing import Iterator

import sqlalchemy
from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("sqlite:///:memory:")
Base = declarative_base(engine)


class Potato(Base):
    __tablename__ = "potato"
    id = Column(Integer, primary_key=True)
    variety = Column(Text)
    skin_color = Column(Text)


SessionMaker = sessionmaker(bind=engine)


@contextmanager
def TransactionalSession() -> Iterator[Session]:
    session: Session
    with SessionMaker.begin() as session:  # type: ignore
        yield session


@contextmanager
def ClassicSession() -> Iterator[Session]:
    session: Session
    with SessionMaker() as session:
        yield session


def session_zero() -> None:
    with ClassicSession() as session:
        potato = Potato(variety="Purple Viking", skin_color="Purple")
        session.add(potato)


def session_one() -> None:
    with TransactionalSession() as session:
        potato = Potato(variety="Red Gold", skin_color="Red")
        session.add(potato)


def session_two() -> None:
    try:
        with ClassicSession() as session:
            potato1 = Potato(id=2, variety="Adironck Blue", skin_color="Purple")
            potato2 = Potato(id=2, variety="Adironck Blue", skin_color="Purple")
            session.add(potato1)
            session.add(potato2)
            session.commit()
    except sqlalchemy.exc.IntegrityError as error:
        print(f"Error! Cannot add the same potato twice. {error}")


def session_three() -> None:
    try:
        with TransactionalSession() as session:
            potato1 = Potato(id=3, variety="Kennebec", skin_color="Buff")
            potato2 = Potato(id=3, variety="Kennebec", skin_color="Buff")
            session.add(potato1)
            session.add(potato2)
    except sqlalchemy.exc.IntegrityError as error:
        print(f"Error! Cannot add the same potato twice. {error}")


def session_four() -> None:
    with ClassicSession() as session:
        try:
            potato1 = Potato(id=4, variety="French Fingerling", skin_color="Pink")
            potato2 = Potato(id=4, variety="French Fingerling", skin_color="Pink")
            session.add(potato1)
            session.add(potato2)
            session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            session.rollback()
            print(f"Error! Cannot add the same potato twice. {error}")


def session_five() -> None:
    try:
        with TransactionalSession() as session:
            try:
                potato1 = Potato(id=5, variety="Satina", skin_color="Yellow")
                potato2 = Potato(id=5, variety="Satina", skin_color="Yellow")
                session.add(potato1)
                session.add(potato2)
            except sqlalchemy.exc.IntegrityError as error:
                print(f"Error! Cannot add the same potato twice. {error}")
                raise
    except sqlalchemy.exc.IntegrityError as error:
        print(f"The inner try catch did not catch a transactional session error: {error}")



def print_db_content() -> None:
    with ClassicSession() as session:
        for potato in session.query(Potato).all():
            print(f"{potato.id=}, {potato.variety=}, {potato.skin_color=}")
    print("\n")


def main() -> None:
    print("=> session_zero")
    session_zero()
    print_db_content()
    print("=> session_one")
    session_one()
    print_db_content()
    print("=> session_two")
    session_two()
    print_db_content()
    print("=> session_three")
    session_three()
    print_db_content()
    print("=> session_four")
    session_four()
    print_db_content()
    print("=> session_five")
    session_five()
    print_db_content()


if __name__ == "__main__":
    Base.metadata.create_all()
    main()
    Base.metadata.drop_all()
