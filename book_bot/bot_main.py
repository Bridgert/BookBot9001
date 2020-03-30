import discord
import os
import calendar

from discord.utils import get

from .database.database import *
from dotenv import load_dotenv
from dotenv import set_key

load_dotenv()  # loads environmental values stored in .env
TOKEN = os.getenv("DISCORD_TOKEN")  # bot's token

connect = Connect()

client = discord.Client()

book_channel = os.getenv("BOOK_CLUB_ID")

test_channel = os.getenv("TEST_CHANNEL_ID")

admin_id = os.getenv("ADMIN_ID")

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


def get_emoji_discord(my_emoji):
    for key, value in emoji_list.items():
        if value == my_emoji:
            return key
    return False


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


def make_print_string(nominations_table, votes_table):

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
            table_dict[current_book].append(user.mention)
        table_dict[current_book].append(count_votes(att[0], votes_table))
        if att[3]:
            table_dict[current_book].append(get_emoji_discord(att[3]))
        else:
            table_dict[current_book].append("No emoji")

    to_print = ""

    print(table_dict)

    for book in list(table_dict.keys()):
        to_print += "{} - '{}' ({}) has {} votes\n".format(table_dict[book][0], book,
                                                           table_dict[book][2], table_dict[book][1])

    return to_print


@client.event
async def on_ready():  # sends ready message
    print(f'{client.user} is ready to connect do Discord!')


@client.event
async def on_connect():  # sends connect message
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):  # handles user messages/commands

    if message.channel.id != int(book_channel) and message.channel.id != int(test_channel):
        return

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

    if message_cmd == 'commands' or message_cmd == 'help':  # shows non-admin bot commands
        command_list = '%nominate (book name) - Pick a nomination (up to 2 per user)\n' \
                       '(user is username/discriminator/displayname/userid\n' \
                       '%delete (nomination) - Deletes your nomination\n' \
                       '%book - Shows this month\'s book\n' \
                       '%oldbooks - Shows all previous months\' books (overview)\n'

        await message.channel.send(command_list)

        return

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

    if message_cmd == 'makenew':
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        try:
            nominations_table = connect.get_table('nominations')
        except:
            await message.channel.send("Unable to load nominations")
            return

        try:
            votes_table = connect.get_table('votes')
        except:
            await message.channel.send("Unable to load votes")
            return

        to_print = make_print_string(nominations_table, votes_table)

        sent_message = False

        if to_print:
            sent_message = await message.channel.send(to_print)
        else:
            await message.channel.send("Unable to show overview")
            return

        try:
            monthly_message = connect.get_message()
        except:
            monthly_message = False

        try:
            channel = await client.fetch_channel(book_channel)
            message = await channel.fetch_message(monthly_message)
            await message.delete()
        except:
            print("Message not found")

        if sent_message:
            monthly_message = sent_message.id
            connect.change_message(monthly_message)
            await sent_message.pin()

        return

    if message_cmd == 'clear':  # clears entire database
        if message.author.id == int(admin_id):
            connect.clear_all()
            await message.channel.send("Cleared everything")
        else:
            await message.channel.send("You do not have the required privileges for that command")
        return

    if message_cmd == 'insertmessage':
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        connect.insert_message(1)

        return

    # if message_cmd == 'get':  # gets users' nominations
    #     if not content_flag:  # gets own user's nominations
    #         my_nominations = connect.get_nominations(message.author.id)
    #
    #         if my_nominations:
    #             if len(my_nominations) == 1:
    #                 await message.channel.send(
    #                     "You have nominated '{}' this month".format(my_nominations[0][0]))
    #             else:
    #                 await message.channel.send(
    #                     "You have nominated '{}' and '{}' this month".format(my_nominations[0][0],
    #                                                                          my_nominations[1][0]))
    #         else:
    #             await message.channel.send("They haven't nominated this month yet")
    #         return
    #
    #     user = get_user(message_content)
    #
    #     if not user:
    #         await message.channel.send("No such user")
    #         return
    #
    #     my_nominations = connect.get_nominations(user.id)
    #
    #     if my_nominations:  # gets other user's nominations
    #         if len(my_nominations) == 1:
    #             await message.channel.send(
    #                 "{} has nominated '{}' this month".format(user.name, my_nominations[0][0]))
    #         else:
    #             await message.channel.send(
    #                 "{} has nominated '{}' and '{}' this month".format(user.name, my_nominations[0][0],
    #                                                                    my_nominations[1][0]))
    #     else:
    #         await message.channel.send("They haven't nominated this month yet")
    #     return



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

    # if message_cmd == 'vote':  # vote command
    #     if not content_flag:
    #         await message.channel.send("Enter a nomination")
    #         return
    #
    #     try:
    #         connect.user_vote(message_content, message.author.id)
    #     except DoubleVote as error:
    #         await message.channel.send(error.message)
    #     except SelfVote as error:
    #         await message.channel.send(error.message)
    #     except NoNomination as error:
    #         await message.channel.send(error.message)
    #     except Exception as error:
    #         print("Unknown error: ", error)
    #         await message.channel.send("Something went wrong")
    #     else:
    #         await message.channel.send("{} has voted for {}".format(message.author.name, message_content))
    #
    #     return

    if message_cmd == 'unvoteall':  # remove all votes command
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        try:
            connect.clear_all_votes()
        except:
            await message.channel.send("Unable to delete votes")

        return

    # if message_cmd == 'unvote':  # remove vote command
    #     try:
    #         connect.delete_vote(message.author.id)
    #     except:
    #         await message.channel.send("Unable to delete vote")
    #         return
    #
    #     await message.channel.send("Removed {}\'s vote".format(message.author.name))
    #     return

    # if message_cmd == 'count':  # handles count command
    #     if not content_flag:
    #         await message.channel.send("Enter nomination")
    #         return
    #
    #     try:
    #         count = connect.count_votes(message_content)
    #     except NoNomination as error:
    #         await message.channel.send(error.message)
    #         return
    #     except GenError as error:
    #         await message.channel.send(error.message)
    #         return
    #     else:
    #         await message.channel.send("{} has {} votes".format(message_content, count))
    #
    #     return

    if message_cmd == 'masternom':  # admin master nomination - nominates under id = 1
        if not message.author.id == int(admin_id):
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

    # if message_cmd == 'allvotes':  # prints all votes
    #     try:
    #         table = connect.get_table('votes')
    #     except:
    #         await message.channel.send("Unable to load table")
    #
    #     table_dict = {}
    #
    #     for tup in table:
    #         book_name = connect.get_book_name_by_nomination_id(tup[0])
    #         if book_name not in table_dict:
    #             table_dict[book_name] = count_votes(tup[0], table)
    #
    #     to_print = ""
    #
    #     for books in list(table_dict.keys()):
    #         to_print += "Nomination: '{}' has {} votes\n".format(books, table_dict[books])
    #
    #     await message.channel.send(to_print)
    #
    #     return

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

    if message_cmd == 'removeemojis':
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        connect.remove_all_emojis()

        print("Succeeded")

        return

    # if message_cmd == 'getall' or message_cmd == 'overview':  # gets all of this month's nominations
    #     try:
    #         nominations_table = connect.get_table('nominations')
    #     except:
    #         await message.channel.send("Unable to load nominations")
    #         return
    #
    #     try:
    #         votes_table = connect.get_table('votes')
    #     except:
    #         await message.channel.send("Unable to load votes")
    #         return
    #
    #     table_dict = {}
    #
    #     for att in nominations_table:
    #         print(att)
    #         current_book = att[1]
    #         table_dict[current_book] = []
    #         current_user_id = connect.get_user_id_by_id_nominations(att[0])
    #         print(current_user_id)
    #         user = get_user(current_user_id)
    #         print(user)
    #         if not user:
    #             table_dict[current_book].append("Unknown User")
    #         else:
    #             table_dict[current_book].append(user.name)
    #         table_dict[current_book].append(count_votes(att[0], votes_table))
    #         if att[3]:
    #             table_dict[current_book].append(att[3])
    #         else:
    #             table_dict[current_book].append("No emoji")
    #
    #     to_print = ""
    #
    #     print(table_dict)
    #
    #     for book in list(table_dict.keys()):
    #         to_print += "{} has nominated '{}' ({}) with {} votes\n".format(table_dict[book][0], book,
    #                                                                         table_dict[book][2], table_dict[book][1])
    #
    #     if to_print:
    #         await message.channel.send(to_print)
    #     else:
    #         await message.channel.send("Unable to show overview")
    #
    #     return

    # if message_cmd == 'fixshit':
    #     if not message.author.id == int(admin_id):
    #         await message.channel.send("Invalid user")
    #         return
    #
    #     connect.oops()
    #
    #     print("Fixed")
    #
    #     return

    if message_cmd == 'settle':
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        try:
            connect.settle_emojis()
        except EmptyNomination as error:
            await message.channel.send(error.message)
        except:
            await message.channel.send("Something went wrong")

        return

    if message_cmd == 'resolve':  # automatically chooses this month's nominations
        if not message.author.id == int(admin_id):
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

    if message_cmd == 'choose':  # chooses manually this month's nominations
        if not message.author.id == int(admin_id):
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

    if message_cmd == 'book':  # gets this month's book
        try:
            book = connect.get_current_book()
        except EmptyNomination:
            await message.channel.send("No monthly book chosen")
            return

        await message.channel.send("This month's book is: {}".format(book))
        return

    if message_cmd == 'clearnomination':  # clear a nomination
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        if not content_flag:
            await message.channel.send("Enter nomination")
            return

        try:
            connect.clear_nomination(message_content)
        except EmptyNomination as error:
            await message.channel.send(error.message)
        except:
            await message.channel.send("Failed to delete {}".format(message_content))
        else:
            await message.channel.send("Successfully deleted {}".format(message_content))

        return

    if message_cmd == 'clearbook':  # clears this month's book
        if not message.author.id == int(admin_id):
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

    if message_cmd == 'clearallbooks':  # clears all book table
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        try:
            connect.clear_all_books()
        except:
            await message.channel.send("Failed to clear all previous books")
        else:
            await message.channel.send("Cleared all book history")
        return

    if message_cmd == 'clearallnominations':  # clears all of this month's nominations
        if not message.author.id == int(admin_id):
            await message.channel.send("Invalid user")
            return

        try:
            connect.clear_all_nominations()
        except:
            await message.channel.send("Failed to clear all nominations")
        else:
            await message.channel.send("Cleared all nominations")
        return

    if message_cmd == 'oldbooks' or message_cmd == 'prevbooks' or message_cmd == 'getbooks':  # gets all previous books
        try:
            nominations_table = connect.get_table('books')
        except:
            await message.channel.send("Unable to load table")
            return

        today = date.today()

        to_print = ''

        for tup in nominations_table:
            if tup[1].year != today.year or tup[1].month != today.month:
                to_print += "{}, {}'s nomination was '{}'\n".format(tup[1].year, calendar.month_name[tup[1].month],
                                                                    tup[0])
            else:
                to_print += "{}, {}'s nomination is '{}'\n".format(tup[1].year, calendar.month_name[tup[1].month],
                                                                   tup[0])

        if to_print:
            await message.channel.send(to_print)
        else:
            await message.channel.send("No books chosen")

        return

    if message_cmd == 'exit' or message_cmd == 'close':  # closes connection to server
        if message.author.id == int(admin_id):
            connect.close_connection()
        return

    if message_cmd == 'open' or message_cmd == 'start':  # starts connection to server
        if message.author.id == int(admin_id):
            connect.__init__()
        return

    await message.channel.send("Unknown command")


@client.event
async def on_raw_reaction_add(reaction_event):

    monthly_message = connect.get_message()

    if reaction_event.channel_id != int(book_channel) and reaction_event.channel_id != int(test_channel):
        return

    if reaction_event.message_id != int(monthly_message):
        print("Wrong message")
        return

    channel = await client.fetch_channel(book_channel)
    message = await channel.fetch_message(reaction_event.message_id)
    user = await client.fetch_user(reaction_event.user_id)

    print("User {} has added emoji: {}".format(reaction_event.user_id, reaction_event.emoji.name))

    try:
        connect.user_vote_by_emoji(reaction_event.user_id, reaction_event.emoji)
    except EmptyNomination as error:
        print(error.message)
        await message.remove_reaction(reaction_event.emoji.name, user)
        return
    except SelfVote as error:
        print(error.message)
        await message.remove_reaction(reaction_event.emoji.name, user)
        return
    except:
        print("General error in voting")
        await message.remove_reaction(reaction_event.emoji.name, user)
        return
    else:
        try:
            nominations_table = connect.get_table('nominations')
        except:
            print("Unable to load nominations")
            return

        try:
            votes_table = connect.get_table('votes')
        except:
            print("Unable to load votes")
            return

        to_print = make_print_string(nominations_table, votes_table)

        print(to_print)

        await message.edit(content=to_print)


@client.event
async def on_raw_reaction_remove(reaction_event):

    monthly_message = connect.get_message()

    if reaction_event.channel_id != int(book_channel) and reaction_event.channel_id != int(test_channel):
        return

    if reaction_event.message_id != int(monthly_message):
        print("Wrong message")
        return

    channel = await client.fetch_channel(book_channel)
    message = await channel.fetch_message(reaction_event.message_id)

    print("User {} has removed emoji: {}".format(reaction_event.user_id, reaction_event.emoji.name))

    try:
        connect.delete_vote_by_emoji(reaction_event.user_id, reaction_event.emoji.name)
    except EmptyNomination as error:
        print(error.message)
        return
    except GenError:
        print("Something's gone wrong with the server")
        return

    try:
        nominations_table = connect.get_table('nominations')
    except:
        print("Unable to load nominations")
        return

    try:
        votes_table = connect.get_table('votes')
    except:
        print("Unable to load votes")
        return

    to_print = make_print_string(nominations_table, votes_table)

    print(to_print)

    await message.edit(content=to_print)

client.run(TOKEN)
