from typing import List, Union

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import sessionmaker, Session


class DB:
    def __init__(self, db_url: str, **kwargs):
        """
        Initializes a class.

        :param str db_url: a URL containing all the necessary parameters to connect to a DB
        """
        self.db_url = db_url
        self.engine = create_engine(self.db_url, **kwargs)
        self.Base = None
        self.s: Session = sessionmaker(bind=self.engine)()
        self.conn = self.engine.connect()

    def create_tables(self, base):
        """
        Creates tables.

        :param base: a base class for declarative class definitions
        """
        self.Base = base
        self.Base.metadata.create_all(self.engine)

    def all(self, entities, *criterion) -> list:
        """
        Fetches all rows.

        :param entities: an ORM entity
        :param criterion: criterion for rows filtering
        :return list: the list of rows
        """
        if criterion:
            return self.s.query(entities).filter(*criterion).all()

        return self.s.query(entities).all()

    def one(self, entities, *criterion, from_the_end: bool = False):
        """
        Fetches one row.

        :param entities: an ORM entity
        :param criterion: criterion for rows filtering
        :param from_the_end: get the row from the end
        :return list: found row or None
        """
        rows = self.all(entities, *criterion)
        if rows:
            if from_the_end:
                return rows[-1]

            return rows[0]

        return None

    def execute(self, query, *args):
        """
        Executes SQL query.

        :param query: the query
        :param args: any additional arguments
        """
        result = self.conn.execute(text(query), *args)
        self.commit()
        return result

    def commit(self):
        """
        Commits changes.
        """
        try:
            self.s.commit()

        except DatabaseError:
            self.s.rollback()

    def insert(self, row: Union[object, List[object]]):
        """
        Inserts rows.

        :param Union[object, List[object]] row: an ORM entity or list of entities
        """
        if isinstance(row, list):
            self.s.add_all(row)

        elif isinstance(row, object):
            self.s.add(row)

        else:
            raise ValueError('Wrong type!')

        self.commit()
