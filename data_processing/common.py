import re
from dateutil import parser
import operator
from collections import defaultdict

kCOUNTRIES = ["England", "Austria", "Germany", "France", "Russia", "Italy", "Turkey"]
kADJECTIVES = ["English", "Austrian", "German", "French", "Russian", "Italian", "Turkish"]
kVARIANT = re.compile("Variant: [a-zA-Z0-9 ]*")
kGOODVARS = ["Standard", "Standard Gunboat"]

def all_gamenames(cursor):
    """Returns a list of all distinct game names"""
    for name, in cursor.execute( 'SELECT DISTINCT gamename FROM messages'):
        yield name

def game_to_variant(cursor):
    """
    Returns mapping from game to variant type
    """
    counts = defaultdict(dict)

    for gg, mm in cursor.execute('select gamename, body from messages where body like "%Variant:%"'):
        for ii in [x.replace("Variant:", "").strip() for x in kVARIANT.findall(mm)]:
            counts[gg][ii] = counts[gg].get(ii, 0) + 1

    mapping = {}
    for ii in counts:
        mapping[ii] = max(counts[ii].iteritems(), key=operator.itemgetter(1))[0]

    return mapping


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
        if idx == -1:
            idx = msg.find("\nThe parameters for")
        year = re.search(r"\b([SF]\d\d\d\d\w\w?)\b", subj)
        if idx >= 0 and year:
            idx_from = msg[idx:].find("\n")
            idx_to = msg[idx:].find("\n\n")
            params.append((year.groups()[0], msg[idx + idx_from + 1:idx + idx_to]))
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
        m = re.search("Press from (.) to (.*)", subj)
        if m and msg.startswith("Message from"):
            fro, to = m.groups()
            presses.append((fro, to, subj, msg))
    return presses


def grey_presses(game):
    """Returns a list of all grey (anonymous) presses (p2p messages) in a game."""
    presses = []
    for date, subj, msg, _ in game:
        m = re.search("Press to (.*)", subj)
        if m and msg.startswith("Message to"):
            to, = m.groups()
            presses.append((to, subj, msg))
    return presses


def broadcasts(game):
    """Returns a list of all broadcasted messages in a game."""
    broadcasts = []
    for date, subj, msg, _ in game:
        m = re.search("Broadcast from (.)", subj)
        if m and msg.startswith("Broadcast message from"):
            fro, = m.groups()
            broadcasts.append((fro, subj, msg))
    return broadcasts