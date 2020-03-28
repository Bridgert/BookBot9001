import os
import psycopg2
import discord

from discord.utils import get
from datetime import date
import calendar

from .database.database import Connect
from .database.database import TripleNominate
from .database.database import EmptyNomination
from .database.database import NoNomination
from .database.database import WrongUser
from .database.database import DoubleVote
from .database.database import SelfVote
from .database.database import GenError
from .database.database import NominationExists
from .database.database import DoubleBook
from dotenv import load_dotenv

load_dotenv()  # loads environmental values stored in .env
TOKEN = os.getenv("DISCORD_TOKEN")  # bot's token

connect = Connect()

client = discord.Client()


def get_user(message_content):
    user = get(client.get_all_members(), name=message_content)
    if user:
        return user
    user = get(client.get_all_members(), discriminator=message_content)
    if user:
        return user
    user = get(client.get_all_members(), display_name=message_content)
    if user:
        return user
    user = get(client.get_all_members(), id=message_content)
    if user:
        return user
    return False


def count_votes(index, table):
    count = 0
    for ele in table:
        if ele[0] == index:
            count += 1
    return count


def find_max(table_dict):
    max_votes = 0
    for book in table_dict:
        if table_dict[book] > max_votes:
            max_votes = table_dict[book]

    return max_votes


@client.event
async def on_ready():  # sends ready message
    print(f'{client.user} is ready to connect do Discord!')


@client.event
async def on_connect():  # sends connect message
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):  # handles user messages/commands

    # if message.channel.id != 692331084565839904:
    #     return

    content_flag = True

    if message.author == client.user:  # ignores own messages
        return

    if message.content[0] != '%':  # % is the command prefix
        return

    try:
        message_cmd = message.content.split(' ', 1)[0][1:].lower()  # stores possible command into message_cmd
    except:
        await message.channel.send("Unrecognized command")
        return
    else:
        if not message_cmd:
            await message.channel.send("Send a command")
            return

    try:
        message_content = message.content.split(' ', 1)[1]  # stores message content if available (after command)
    except Exception as exc:
        content_flag = False

    print("Entered command is '{}'".format(message_cmd))

    if message_cmd == 'nominate':  # nominate command
        if not content_flag:
            await message.channel.send("Enter a nomination")
            return

        try:
            connect.add_nomination(message_content, message.author.id)
        except NominationExists as error:
            await message.channel.send(error.message)
        except TripleNominate as error:
            await message.channel.send(error.message)
        except:
            await message.channel.send("Failed to add nomination")
        else:
            await message.channel.send(
                "Added '{0}' to {1}'s nominations".format(message_content.lower(), message.author.name))

        return

    # if message_cmd == 'modify':  # modify command
    #     try:
    #         message_content
    #     except:
    #         await message.channel.send("Enter a nomination")
    #         return
    #
    #     try:
    #         connect.modify_nomination(message_content, message.author.id)
    #     except EmptyNomination:
    #         await message.channel.send(EmptyNomination.message)
    #     except:
    #         await message.channel.send("Failed to modify nomination")
    #     else:
    #         await message.channel.send("Changed {0}'s nomination to {1}".format(message.author.name, message_content))
    #
    #     return

    if message_cmd == 'clear':
        if message.author.id == 110050968401358848:
            connect.clear_all()
            await message.channel.send("Cleared everything")
        else:
            await message.channel.send("You do not have the required privileges for that command")
        return

    if message_cmd == 'get':  # gets users' nominations
        if not content_flag:  # gets own user's nominations
            my_nominations = connect.get_nominations(message.author.id)

            if my_nominations:
                if len(my_nominations) == 1:
                    await message.channel.send(
                        "You have nominated '{}' this month".format(message.author.name, my_nominations[0][0]))
                else:
                    await message.channel.send(
                        "You have nominated '{}' and '{}' this month".format(message.author.name, my_nominations[0][0],
                                                                             my_nominations[1][0]))
            else:
                await message.channel.send("They haven't nominated this month yet")
            return

        user = get_user(message_content)

        if not user:
            await message.channel.send("No such user")
            return

        my_nominations = connect.get_nominations(user.id)

        if my_nominations:
            if len(my_nominations) == 1:
                await message.channel.send(
                    "{} has nominated '{}' this month".format(user.name, my_nominations[0][0]))
            else:
                await message.channel.send(
                    "{} has nominated '{}' and '{}' this month".format(user.name, my_nominations[0][0],
                                                                       my_nominations[1][0]))
        else:
            await message.channel.send("They haven't nominated this month yet")
        return

    # if message_cmd == 'getid':  # get ID command
    #     try:
    #         message_content
    #     except:
    #         await message.channel.send("Enter a nomination")
    #         return
    #
    #     try:
    #         nomination_id = connect.get_id(message_content)
    #     except NoNomination as error:
    #         await message.channel.send(error.message)
    #         return
    #     else:
    #         await message.channel.send(nomination_id)
    #
    #     return

    if message_cmd == 'delete':  # delete nomination command
        if not content_flag:
            await message.channel.send("Enter a nomination")
            return

        try:
            connect.delete_nomination(message_content, message.author.id)
        except EmptyNomination as error:
            await message.channel.send(error.message)
            return
        except WrongUser as error:
            await message.channel.send(error.message)
            return
        else:
            await message.channel.send("Nomination '{}' has been deleted".format(message_content))

        return

    if message_cmd == 'vote':  # vote command
        if not content_flag:
            await message.channel.send("Enter a nomination")
            return

        try:
            connect.user_vote(message_content, message.author.id)
        except DoubleVote as error:
            await message.channel.send(error.message)
            return
        except SelfVote as error:
            await message.channel.send(error.message)
            return
        else:
            await message.channel.send("{} has voted for {}".format(message.author.name, message_content))

        return

    if message_cmd == 'unvote':  # remove vote command
        try:
            connect.delete_vote(message.author.id)
        except:
            await message.channel.send("Unable to delete vote")
            return

        await message.channel.send("Removed {}\'s vote".format(message.author.name))
        return

    if message_cmd == 'count':
        if not content_flag:
            await message.channel.send("Enter nomination")
            return

        try:
            count = connect.count_votes(message_content)
        except NoNomination as error:
            await message.channel.send(error.message)
            return
        except GenError as error:
            await message.channel.send(error.message)
            return
        else:
            await message.channel.send("{} has {} votes".format(message_content, count))

        return

    if message_cmd == 'masternom':
        if not message.author.id == 110050968401358848:
            await message.channel.send("Invalid user")
            return

        if not content_flag:
            await message.channel.send("Enter nomination")
            return

        try:
            connect.master_nominate(message_content)
        except:
            await message.channel.send("Error")

        return

    if message_cmd == 'allvotes':
        try:
            table = connect.get_table('votes')
        except:
            await message.channel.send("Unable to load table")

        table_dict = {}

        for tup in table:
            book_name = connect.get_book_name_by_nomination_id(tup[0])
            if book_name not in table_dict:
                table_dict[book_name] = count_votes(tup[0], table)

        to_print = ""

        for books in list(table_dict.keys()):
            to_print += "Nomination: '{}' has {} votes\n".format(books, table_dict[books])

        await message.channel.send(to_print)

        return

    # if message_cmd == 'test':
    #     if not message_content:
    #         print("Fail")
    #         return
    #
    #     user_id = get_user(message_content)
    #
    #     if user_id:
    #         await message.channel.send(user_id)
    #     else:
    #         await message.channel.send("No such user")
    #
    #     return

    if message_cmd == 'getall' or message_cmd == 'overview':
        try:
            nominations_table = connect.get_table('nominations')
        except:
            await message.channel.send("Unable to load table")
            return

        try:
            votes_table = connect.get_table('votes')
        except:
            await message.channel.send("Unable to load table")
            return

        table_dict = {}

        for att in nominations_table:
            print(att)
            current_book = att[1]
            table_dict[current_book] = []
            current_user_id = connect.get_user_id_by_id_nominations(att[0])
            print(current_user_id)
            user = get_user(current_user_id)
            print(user)
            if not user:
                table_dict[current_book].append("Unknown User")
            else:
                table_dict[current_book].append(user.name)
            table_dict[current_book].append(count_votes(att[0], votes_table))

        to_print = ""

        for book in list(table_dict.keys()):
            to_print += "{} has nominated '{}' with {} votes\n".format(table_dict[book][0], book, table_dict[book][1])

        if to_print:
            await message.channel.send(to_print)
        else:
            await message.channel.send("Unable to show overview")

        return

    if message_cmd == 'resolve':
        if not message.author.id == 110050968401358848:
            await message.channel.send("Invalid user")
            return

        try:
            table = connect.get_table('votes')
        except:
            await message.channel.send("Unable to load table")
            return

        table_dict = {}

        for tup in table:
            book_name = connect.get_book_name_by_nomination_id(tup[0])
            if book_name not in table_dict:
                table_dict[tup[0]] = count_votes(tup[0], table)

        max_voted = find_max(table_dict)
        count = 0
        my_book = 0

        print(table_dict)

        for book in table_dict:
            if table_dict[book] == max_voted:
                count += 1
                my_book = book

        if count > 1:
            await message.channel.send("Multiple highest voted, cannot resolve")
            return

        if my_book == 0:
            await message.channel.send("No votes")
            return

        try:
            connect.choose_nomination(nomination_id=my_book)
        except NoNomination:
            await message.channel.send("Could not find nomination")
        except EmptyNomination:
            await message.channel.send("Nomination does not exist")
        except GenError:
            await message.channel.send("Failed to insert")
        except DoubleBook as error:
            await message.channel.send(error.message)
        except:
            await message.channel.send("Error")
        else:
            await message.channel.send("Chose {} as this month's nomination".format(connect.get_current_book()))

        return

    if message_cmd == 'choose':
        if not message.author.id == 110050968401358848:
            await message.channel.send("Invalid user")
            return

        if not content_flag:
            await message.channel.send("Enter nomination")
            return

        try:
            connect.choose_nomination(nomination=message_content)
        except EmptyNomination:
            await message.channel.send("No such nomination")
        except DoubleBook as error:
            await message.channel.send(error.message)
        except:
            await message.channel.send("Failed to nominate")
        else:
            await message.channel.send("Chose {} as this month's nomination".format(message_content))

        return

    if message_cmd == 'book':
        try:
            book = connect.get_current_book()
        except EmptyNomination:
            await message.channel.send("No monthly book chosen")
            return

        await message.channel.send("This month's book is: {}".format(book))
        return

    if message_cmd == 'clearbook':
        if not message.author.id == 110050968401358848:
            await message.channel.send("Invalid user")
            return

        try:
            connect.clear_book()
        except GenError:
            await message.channel.send("No book chosen this month")
        except:
            await message.channel.send("Failed to delete this month's nomination")
        else:
            await message.channel.send("Successfully deleted this month's nomination")

        return

    if message_cmd == 'clearallbooks':
        if message.author.id == 110050968401358848:
            connect.clear_all_books()
            await message.channel.send("Cleared all book history")
        else:
            await message.channel.send("You do not have the required privileges for that command")
        return

    if message_cmd == 'getbooks':
        try:
            nominations_table = connect.get_table('books')
        except:
            await message.channel.send("Unable to load table")
            return

        today = date.today()

        to_print = ''

        for tup in nominations_table:
            if tup[1].year != today.year or tup[1].month != today.month:
                to_print += "{}, {}'s nomination was '{}'\n".format(tup[1].year, calendar.month_name[tup[1].month], tup[0])
            else:
                to_print += "{}, {}'s nomination is '{}'\n".format(tup[1].year, calendar.month_name[tup[1].month], tup[0])

        if to_print:
            await message.channel.send(to_print)
        else:
            await message.channel.send("No books chosen")

        return

    if message_cmd == 'exit':
        if message.author.id == 110050968401358848:
            connect.close_connection()
        return

    if message_cmd == 'start':
        if message.author.id == 110050968401358848:
            connect.__init__()
        return

    await message.channel.send("Unknown command")


client.run(TOKEN)
