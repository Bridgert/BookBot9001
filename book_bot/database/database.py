import psycopg2
import os
import emoji
from datetime import date
from psycopg2 import sql

emoji_list = {':zero:': ':keycap_0:', ':one:': ':keycap_1:', ':two:': ':keycap_2:', ':three:': ':keycap_3:',
              ':four:': ':keycap_4:', ':five:': ':keycap_5:', ':six:': ':keycap_6:', ':seven:': ':keycap_7:',
              ':eight:': ':keycap_8:', ':nine:': ':keycap_9:',
              ':regional_indicator_a:': ':regional_indicator_symbol_letter_a:',
              ':regional_indicator_b:': ':regional_indicator_symbol_letter_b:',
              ':regional_indicator_c:': ':regional_indicator_symbol_letter_c:',
              ':regional_indicator_d:': ':regional_indicator_symbol_letter_d:',
              ':regional_indicator_e:': ':regional_indicator_symbol_letter_e:',
              ':regional_indicator_f:': ':regional_indicator_symbol_letter_f:',
              ':regional_indicator_g:': ':regional_indicator_symbol_letter_g:',
              ':regional_indicator_h:': ':regional_indicator_symbol_letter_h:',
              ':regional_indicator_i:': ':regional_indicator_symbol_letter_i:',
              ':regional_indicator_j:': ':regional_indicator_symbol_letter_j:',
              ':regional_indicator_k:': ':regional_indicator_symbol_letter_k:',
              ':regional_indicator_l:': ':regional_indicator_symbol_letter_l:',
              ':regional_indicator_m:': ':regional_indicator_symbol_letter_m:',
              ':regional_indicator_n:': ':regional_indicator_symbol_letter_n:',
              ':regional_indicator_o:': ':regional_indicator_symbol_letter_o:',
              ':regional_indicator_p:': ':regional_indicator_symbol_letter_p:',
              ':regional_indicator_q:': ':regional_indicator_symbol_letter_q:',
              ':regional_indicator_r:': ':regional_indicator_symbol_letter_r:',
              ':regional_indicator_s:': ':regional_indicator_symbol_letter_s:',
              ':regional_indicator_t:': ':regional_indicator_symbol_letter_t:',
              ':regional_indicator_u:': ':regional_indicator_symbol_letter_u:',
              ':regional_indicator_v:': ':regional_indicator_symbol_letter_v:',
              ':regional_indicator_w:': ':regional_indicator_symbol_letter_w:',
              ':regional_indicator_x:': ':regional_indicator_symbol_letter_x:',
              ':regional_indicator_y:': ':regional_indicator_symbol_letter_y:',
              ':regional_indicator_z:': ':regional_indicator_symbol_letter_z:'}


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

        database_url = os.environ['DATABASE_URL']

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
            "UserID"	bigint,
            "Emoji" TEXT
        )'''

        create_votes_table = '''CREATE TABLE IF NOT EXISTS votes (
            "NominationID"	integer,
            "UserID"	bigint
        )'''

        create_books_table = '''CREATE TABLE IF NOT EXISTS books (
            "BookName"	text,
            "Date"	date
        )'''

        create_message_table = '''CREATE TABLE IF NOT EXISTS message (
            "MessageID" bigint
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

        try:
            self.cur.execute(create_message_table)
        except:
            print("Error in creating message table")

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

        select = '''SELECT * FROM nominations WHERE "BookName" = %s;'''
        # select_check = select.format(book_name)

        self.cur.execute(sql.SQL(select), (book_name,))
        if self.cur.fetchone():
            raise NominationExists

        nomination_emojis = self.get_emojis()

        print(nomination_emojis)

        if not nomination_emojis:
            raise EmptyNomination

        input_emoji = None

        global emoji_list

        for key, value in emoji_list.items():
            if value not in nomination_emojis:
                input_emoji = value
                break

        insert = '''INSERT INTO nominations ("BookName", "UserID", "Emoji") VALUES (%s, %s, %s)'''
        # insert_nomination = insert.format(book_name.lower(), user_id)

        print(insert)

        try:
            self.cur.execute(sql.SQL(insert), (book_name.lower(), user_id, input_emoji))
        except:
            raise GenError

        self.conn.commit()

    def master_nominate(self, book_name):

        insert = '''INSERT INTO nominations ("BookName", "UserID") VALUES (%s, 1)'''
        # insert_nomination = insert.format(book_name.lower())

        print(insert)

        try:
            self.cur.execute(sql.SQL(insert), (book_name.lower(),))
        except:
            raise GenError

        self.conn.commit()

    def get_id(self, nomination):

        get = '''SELECT "ID" FROM nominations WHERE "BookName" = %s;'''
        # get_id = get.format(nomination.lower())

        self.cur.execute(sql.SQL(get), (nomination,))
        try:
            return self.cur.fetchone()[0]
        except:
            raise NoNomination

    def settle_emojis(self):

        my_emojis = self.get_emojis()

        print(my_emojis)

        try:
            for nom in self.get_table('nominations'):
                print(nom)
                if not self.does_nomination_have_emoji(nom[0]):
                    for emote in emoji_list.items():
                        if emote[1] not in my_emojis:
                            print(emote)
                            insert = '''UPDATE nominations SET "Emoji" = %s WHERE "ID" = %s'''

                            try:
                                self.cur.execute(sql.SQL(insert), (emote[1], nom[0]))
                            except:
                                raise GenError
                            else:
                                self.conn.commit()
                                emoji_list.pop(emoji[0])
                                break
        except EmptyNomination:
            raise EmptyNomination
        except:
            raise GenError

    def remove_all_emojis(self):

        delete = '''UPDATE nominations SET "Emoji" = %s'''

        self.cur.execute(sql.SQL(delete), (None,))

        self.conn.commit()

    def get_message(self):

        select = '''SELECT * FROM message'''

        self.cur.execute(select)

        try:
            return self.cur.fetchone()[0]
        except:
            raise GenError

    def change_message(self, message_id):

        change = '''UPDATE message SET "MessageID" = %s'''

        try:
            self.cur.execute(sql.SQL(change), (message_id, ))
        except:
            raise GenError

    def insert_message(self, message_id):

        insert = '''INSERT INTO message ("MessageID") VALUES (%s)'''

        try:
            self.cur.execute(sql.SQL(insert), (message_id, ))
        except:
            raise GenError

    def does_nomination_have_emoji(self, nomination_id):

        select = '''SELECT "Emoji" FROM nominations WHERE "ID" = %s'''

        self.cur.execute(sql.SQL(select), (nomination_id,))

        try:
            if self.cur.fetchone()[0]:
                return True
            return False
        except:
            raise EmptyNomination

    def get_user_id_by_nomination_id_votes(self, nomination_id):

        get = '''SELECT "UserID" FROM votes WHERE "NominationID" = %s;'''
        # get_user_id = get.format(nomination_id)

        self.cur.execute(sql.SQL(get), (nomination_id,))

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_user_id_by_id_nominations(self, nomination_id):

        get = '''SELECT "UserID" FROM nominations WHERE "ID" = %s;'''
        # get_user_id = get.format(nomination_id)

        self.cur.execute(sql.SQL(get), (nomination_id,))

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_nomination_id_by_user_vote(self, user_id):

        get = '''SELECT "NominationID" FROM votes WHERE "UserID" = %s'''

        self.cur.execute(sql.SQL(get), (user_id,))

        try:
            return self.cur.fetchone()[0]
        except TypeError:
            raise EmptyNomination
        except IndexError:
            raise EmptyNomination
        except:
            raise GenError

    def get_book_name_by_nomination_id(self, nomination_id):

        get = '''SELECT "BookName" FROM nominations WHERE "ID" = %s'''
        # get_book = get.format(nomination_id)

        self.cur.execute(sql.SQL(get), (nomination_id,))

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_nominations(self, user_id):

        select = '''SELECT "BookName" FROM nominations WHERE "UserID" = %s'''
        # select_nomination = select.format(user_id)

        self.cur.execute(sql.SQL(select), (user_id,))
        return self.cur.fetchall()

    def get_emoji_by_nomination(self, nomination):

        get = '''SELECT "Emoji" FROM nominations WHERE "BookName" = %s'''

        self.cur.execute(sql.SQL(get), (nomination, ))

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_nomination_by_emoji(self, disc_emoji):

        get = '''SELECT "BookName" FROM nominations WHERE "Emoji" = %s'''

        self.cur.execute(sql.SQL(get), (disc_emoji,))

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def has_voted(self, user_id):  # returns if user has voted already
        check = '''SELECT "NominationID" FROM votes WHERE "UserID" = %s'''
        # check_voted = check.format(user_id)

        self.cur.execute(sql.SQL(check), (user_id,))

        if self.cur.fetchone():
            return True
        else:
            return False

    def get_nominator_id(self, nomination_id):

        get = '''SELECT "UserID" FROM nominations WHERE "ID" = %s'''
        # get_id = get.format(nomination_id)

        self.cur.execute(sql.SQL(get), (nomination_id,))
        return self.cur.fetchone()[0]

    def user_vote(self, nomination, user_id):
        try:
            nomination_id = self.get_id(nomination)
        except NoNomination:
            raise NoNomination

        insert = '''INSERT INTO votes ("NominationID", "UserID") VALUES (%s, %s)'''
        # insert_vote = insert.format(nomination_id, user_id)

        try:
            # if self.has_voted(user_id):
            #     raise DoubleVote
            if self.get_nominator_id(nomination_id) == user_id:
                raise SelfVote
            else:
                self.cur.execute(sql.SQL(insert), (nomination_id, user_id))
        # except DoubleVote:
        #     raise DoubleVote
        except SelfVote:
            raise SelfVote
        except:
            raise GenError

        self.conn.commit()

    def user_vote_by_emoji(self, user_id, disc_emoji):

        disc_emoji = emoji.demojize(str(disc_emoji))

        try:
            nomination = self.get_nomination_by_emoji(disc_emoji)
        except:
            raise EmptyNomination

        try:
            self.user_vote(nomination, user_id)
        # except DoubleVote:
        #     raise DoubleVote
        except SelfVote:
            raise SelfVote
        except:
            raise GenError

    def delete_vote(self, nomination, user_id):

        try:
            nomination_id = self.get_id(nomination)
        except:
            return EmptyNomination

        delete = '''DELETE FROM votes WHERE "UserID" = %s AND "NominationID" = %s'''
        # delete_vote = delete.format(user_id)

        try:
            self.cur.execute(sql.SQL(delete), (user_id, nomination_id))
        except:
            raise GenError

        self.conn.commit()

    def delete_vote_by_emoji(self, user_id, disc_emoji):

        disc_emoji = emoji.demojize(str(disc_emoji))

        try:
            nomination = self.get_nomination_by_emoji(disc_emoji)
        except:
            raise EmptyNomination

        try:
            self.delete_vote(nomination, user_id)
        except:
            raise GenError

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

        delete = '''DELETE FROM nominations WHERE "ID" = %s'''
        # delete_nomination = delete.format(nomination_id)

        delete_vote = '''DELETE FROM votes WHERE "NominationID" = %s'''
        # delete_vote_sql = delete_vote.format(nomination_id)

        try:
            self.cur.execute(sql.SQL(delete), (nomination_id,))
            self.cur.execute(sql.SQL(delete_vote), (nomination_id,))
        except:
            raise GenError

        self.conn.commit()

    def count_votes(self, nomination):

        try:
            nomination_id = self.get_id(nomination)
        except NoNomination:
            raise NoNomination

        count = '''SELECT COUNT (*) FROM votes WHERE "NominationID" = %s;'''
        # count_votes = count.format(nomination_id)

        self.cur.execute(sql.SQL(count), (nomination_id,))
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

        select = '''SELECT "BookName" FROM books WHERE "Date" = %s;'''
        # select_book = select.format(my_date)

        self.cur.execute(sql.SQL(select), (my_date,))

        try:
            return self.cur.fetchone()[0]
        except:
            raise EmptyNomination

    def get_emojis(self):

        nominations_table = self.get_table('nominations')

        if not nominations_table:
            return []

        emoji_arr = []

        for tup in nominations_table:
            emoji_arr.append(tup[3])

        return emoji_arr

    def check_if_book_chosen(self):

        today = date.today()

        my_date = date(today.year, today.month, 1)

        select = '''SELECT * FROM books WHERE "Date" = %s;'''
        # select_book = select.format(my_date)

        self.cur.execute(sql.SQL(select), (my_date,))

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

        select = '''SELECT * FROM nominations WHERE "ID" = %s'''
        # select_nomination = select.format(nomination_id)

        self.cur.execute(sql.SQL(select), (nomination_id,))

        try:
            book = self.cur.fetchone()
            print(book)
        except:
            raise EmptyNomination
            return

        today = date.today()

        my_date = date(today.year, today.month, 1)

        insert = '''INSERT INTO books ("BookName", "Date") VALUES (%s, %s)'''
        # insert_nomination = insert.format(book[1], my_date)

        try:
            self.cur.execute(sql.SQL(insert), (book[1], my_date))
        except:
            raise GenError

        self.conn.commit()

        try:
            self.clear_monthly()
        except:
            GenError

    def clear_nomination(self, nomination):

        try:
            nomination_id = self.get_id(nomination)
        except NoNomination:
            raise NoNomination

        delete = '''DELETE FROM nominations WHERE "ID" = %s;'''
        # delete_book = delete.format(my_date)

        self.cur.execute(sql.SQL(delete), (nomination_id,))

        self.conn.commit()

    def clear_book(self):

        if not self.check_if_book_chosen():
            raise GenError

        today = date.today()

        my_date = date(today.year, today.month, 1)

        delete = '''DELETE FROM books WHERE "Date" = %s;'''
        # delete_book = delete.format(my_date)

        self.cur.execute(sql.SQL(delete), (my_date,))

        self.conn.commit()

    def clear_all_nominations(self):
        delete_nominations = '''DELETE FROM nominations'''

        self.cur.execute(delete_nominations)

        self.conn.commit()

    def clear_all_books(self):
        delete_books = '''DELETE FROM books'''

        self.cur.execute(delete_books)

        self.conn.commit()

    def clear_all_votes(self):

        delete_nominations = '''DELETE FROM votes'''

        self.cur.execute(delete_nominations)

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
