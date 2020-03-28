import psycopg2
import os
from datetime import date


class Error(Exception):
    pass


class NominationExists(Error):

    def __init__(self):
        self.message = "Nomination already exists"


class TripleNominate(Error):

    def __init__(self):
        self.message = "User has nominated twice already"


class GenError(Error):

    def __init__(self):
        self.message = "Something has gone wrong"


class EmptyNomination(Error):

    def __init__(self):
        self.message = "User has no nominations"


class DoubleVote(Error):

    def __init__(self):
        self.message = "User has already voted"


class SelfVote(Error):

    def __init__(self):
        self.message = "Cannot vote for yourself"


class NoNomination(Error):

    def __init__(self):
        self.message = "Nomination does not exist"


class WrongUser(Error):

    def __init__(self):
        self.message = "Invalid user"


class DoubleBook(Error):

    def __init__(self):
        self.message = "This month already has a nomination"


class Connect:

    def __init__(self):

        database_url = os.environ['database_url']

        try:
            self.conn = psycopg2.connect(database_url, sslmode='require')
        except:
            raise Exception("Connection error")
        else:
            print("Connected")
        self.cur = self.conn.cursor()

        self.connect_db()

    def connect_db(self):

        create_nomination_table = '''CREATE TABLE IF NOT EXISTS nominations (
            "ID"	serial PRIMARY KEY,
            "BookName"	text,
            "UserID"	bigint
        )'''

        create_votes_table = '''CREATE TABLE IF NOT EXISTS votes (
            "NominationID"	integer,
            "UserID"	bigint
        )'''

        create_books_table = '''CREATE TABLE IF NOT EXISTS books (
            "BookName"	text,
            "Date"	date
        )'''

        try:
            self.cur.execute(create_nomination_table)
        except:
            print("Error in creating nomination table")

        try:
            self.cur.execute(create_votes_table)
        except:
            print("Error in creating votes table")

        try:
            self.cur.execute(create_books_table)
        except:
            print("Error in creating books table")

        self.conn.commit()

    # def modify_nomination(self, book_name, user_id):
    #
    #     if not self.get_nominations():
    #         raise EmptyNomination
    #
    #     delete = '''DELETE FROM nominations WHERE "UserID" = {}'''
    #     delete_nomination = delete.format(user_id)
    #
    #     try:
    #         self.cur.execute(delete_nomination)
    #     except:
    #         print(":))")
    #         pass
    #
    #     self.conn.commit()
    #
    #     try:
    #         self.add_nomination((book_name, user_id))
    #     except:
    #         raise GenError

    def add_nomination(self, book_name, user_id):

        if len(self.get_nominations(user_id)) >= 2:
            raise TripleNominate

        select = '''SELECT * FROM nominations WHERE "BookName" = '{}';'''
        select_check = select.format(book_name)

        self.cur.execute(select_check)
        if self.cur.fetchone():
            raise NominationExists

        insert = '''INSERT INTO nominations ("BookName", "UserID") VALUES ('{}', {})'''
        insert_nomination = insert.format(book_name.lower(), user_id)

        print(insert_nomination)

        try:
            self.cur.execute(insert_nomination)
        except:
            raise GenError

        self.conn.commit()

    def master_nominate(self, book_name):

        insert = '''INSERT INTO nominations ("BookName", "UserID") VALUES ('{}', 1)'''
        insert_nomination = insert.format(book_name.lower())

        print(insert_nomination)

        try:
            self.cur.execute(insert_nomination)
        except:
            raise GenError

        self.conn.commit()

    def get_id(self, nomination):

        get = '''SELECT "ID" FROM nominations WHERE "BookName" = '{}';'''
        get_id = get.format(nomination.lower())

        self.cur.execute(get_id)
        try:
            return self.cur.fetchone()[0]
        except:
            raise NoNomination

    def get_user_id_by_nomination_id_votes(self, nomination_id):

        get = '''SELECT "UserID" FROM votes WHERE "NominationID" = {};'''
        get_user_id = get.format(nomination_id)

        self.cur.execute(get_user_id)

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_user_id_by_id_nominations(self, nomination_id):

        get = '''SELECT "UserID" FROM nominations WHERE "ID" = {};'''
        get_user_id = get.format(nomination_id)

        self.cur.execute(get_user_id)

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_book_name_by_nomination_id(self, nomination_id):

        get = '''SELECT "BookName" FROM nominations WHERE "ID" = {}'''
        get_book = get.format(nomination_id)

        self.cur.execute(get_book)

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_nominations(self, user_id):

        select = '''SELECT "BookName" FROM nominations WHERE "UserID" = {}'''
        select_nomination = select.format(user_id)

        print(select_nomination)

        self.cur.execute(select_nomination)
        return self.cur.fetchall()

    def has_voted(self, user_id):  # returns if user has voted already
        check = '''SELECT "NominationID" FROM votes WHERE "UserID" = {}'''
        check_voted = check.format(user_id)

        self.cur.execute(check_voted)

        if self.cur.fetchone():
            return True
        else:
            return False

    def get_nominator_id(self, nomination_id):

        get = '''SELECT "UserID" FROM nominations WHERE "ID" = {}'''
        get_id = get.format(nomination_id)

        self.cur.execute(get_id)
        return self.cur.fetchone()[0]

    def user_vote(self, nomination, user_id):
        try:
            nomination_id = self.get_id(nomination)
        except NoNomination:
            raise NoNomination

        insert = '''INSERT INTO votes ("NominationID", "UserID") VALUES ({}, {})'''
        insert_vote = insert.format(nomination_id, user_id)

        try:
            if self.has_voted(user_id):
                raise DoubleVote
            elif self.get_nominator_id(nomination_id) == user_id:
                raise SelfVote
            else:
                self.cur.execute(insert_vote)
        except DoubleVote:
            raise DoubleVote
        except SelfVote:
            raise SelfVote

        self.conn.commit()

    def delete_vote(self, user_id):

        delete = '''DELETE FROM votes WHERE "UserID" = {}'''
        delete_vote = delete.format(user_id)

        try:
            self.cur.execute(delete_vote)
        except:
            raise GenError

        self.conn.commit()

    def delete_nomination(self, nomination, user_id):
        try:
            nomination_id = self.get_id(nomination)
        except NoNomination:
            raise NoNomination

        try:
            check_user_id = self.get_user_id_by_id_nominations(nomination_id)
        except:
            raise EmptyNomination

        if not user_id == check_user_id:
            raise WrongUser

        delete = '''DELETE FROM nominations WHERE "ID" = {}'''
        delete_nomination = delete.format(nomination_id)

        delete_vote = '''DELETE FROM votes WHERE "NominationID" = {}'''
        delete_vote_sql = delete_vote.format(nomination_id)

        try:
            self.cur.execute(delete_nomination)
            self.cur.execute(delete_vote_sql)
        except:
            raise GenError

        self.conn.commit()

    def count_votes(self, nomination):

        try:
            nomination_id = self.get_id(nomination)
        except NoNomination:
            raise NoNomination

        count = '''SELECT COUNT (*) FROM votes WHERE "NominationID" = '{}';'''
        count_votes = count.format(nomination_id)

        self.cur.execute(count_votes)
        try:
            return self.cur.fetchone()[0]
        except:
            raise GenError

    def get_table(self, table_name):

        get = '''SELECT * FROM {}'''
        get_all = get.format(table_name.lower())

        self.cur.execute(get_all)

        table = self.cur.fetchall()
        print(table)

        return table

    def get_current_book(self):

        today = date.today()

        my_date = date(today.year, today.month, 1)

        select = '''SELECT "BookName" FROM books WHERE "Date" = '{}';'''
        select_book = select.format(my_date)

        self.cur.execute(select_book)

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def check_if_book_chosen(self):

        today = date.today()

        my_date = date(today.year, today.month, 1)

        select = '''SELECT * FROM books WHERE "Date" = '{}';'''
        select_book = select.format(my_date)

        self.cur.execute(select_book)

        try:
            self.cur.fetchone()[0]
        except:
            return False

        return True

    def choose_nomination(self, nomination=None, nomination_id=None):

        if self.check_if_book_chosen():
            raise DoubleBook

        if nomination:
            try:
                nomination_id = self.get_id(nomination)
            except NoNomination:
                raise NoNomination
            except AttributeError:
                raise AttributeError

        select = '''SELECT * FROM nominations WHERE "ID" = {}'''
        select_nomination = select.format(nomination_id)

        self.cur.execute(select_nomination)

        try:
            book = self.cur.fetchone()
            print(book)
        except:
            raise EmptyNomination
            return

        today = date.today()

        my_date = date(today.year, today.month, 1)

        insert = '''INSERT INTO books ("BookName", "Date") VALUES ('{}', '{}')'''
        insert_nomination = insert.format(book[1], my_date)

        try:
            self.cur.execute(insert_nomination)
        except:
            raise GenError

        self.conn.commit()

        try:
            self.clear_monthly()
        except:
            GenError

    def clear_book(self):

        if not self.check_if_book_chosen():
            raise GenError

        today = date.today()

        my_date = date(today.year, today.month, 1)

        delete = '''DELETE FROM books WHERE "Date" = '{}';'''
        delete_book = delete.format(my_date)

        self.cur.execute(delete_book)

        self.conn.commit()

    def clear_all_books(self):
        delete_books = '''DELETE FROM books'''

        self.cur.execute(delete_books)

        self.conn.commit()

    def clear_monthly(self):
        delete_nominations = '''DELETE FROM nominations'''
        delete_votes = '''DELETE FROM votes'''

        self.cur.execute(delete_nominations)
        self.cur.execute(delete_votes)

        self.conn.commit()

    def clear_all(self):
        delete_nominations = '''DELETE FROM nominations'''
        delete_votes = '''DELETE FROM votes'''
        delete_book = '''DELETE FROM books'''

        self.cur.execute(delete_nominations)
        self.cur.execute(delete_votes)
        self.cur.execute(delete_book)

        self.conn.commit()

    def close_connection(self):
        self.cur.close()
        self.conn.close()
