import re
from dateutil import parser

def all_gamenames(cursor):
    """Returns a list of all distinct game names"""
    for name, in cursor.execute( 'SELECT DISTINCT gamename FROM messages'):
        yield name


def game_from_db(cursor, game_name=None):
    """Returns a list of all messages from the given game.

       If no game is given, all messages are returned.
    """
    if game_name is not None:
        messages = cursor.execute('SELECT sent, subject, body, gamename '
                                  'FROM messages '
                                  'WHERE gamename=?', (game_name,)).fetchall()
    else:
        messages = cursor.execute('SELECT sent, subject, body, gamename '
                                  'FROM messages').fetch_all()
    messages = sorted(messages, key=lambda x: (x[-1], parser.parse(x[0])))
    for sent, subject, body, gamename in messages:
        if not body:
            body = ""
        #body = body.replace("u\xa0", " ") if body else ""
        try:
            body = body.encode("utf8").decode("unicode-escape")
        except UnicodeEncodeError:
            body = body.encode("ISO-8859-1").decode("unicode-escape")
        yield sent, subject, body, gamename


def game_params(game):
    """Returns a list of all parameter change notifications from the game"""
    params = []
    for date, subj, msg, _ in game:
        if msg is None:
            continue
        idx = msg.find("has changed the parameters for game")
        if idx >= 0:
            idx_from = msg[idx:].find("\n")
            idx_to = msg[idx:].find("\n\n")
            params.append(msg[idx + idx_from + 1:idx + idx_to])
    return params


def milestones(game):
    """Returns a list of all distinct time points (e.g. F1920M)"""
    milestones = []
    for date, subj, msg, _ in game:
        m = re.search(r"- (.* )?(.*) Results", subj)
        if m:
            milestone = m.groups()[-1]
            if milestone not in milestones:
                milestones.append(milestone)
    return milestones


def presses(game):
    """Returns a list of all presses (p2p messages) in a game."""
    presses = []
    for date, subj, msg, _ in game:
        m = re.search("Press from (.) to (.)", subj)
        if m and msg.startswith("Message from"):
            fro, to = m.groups()
            presses.append((fro, to, subj, msg))
    return presses
