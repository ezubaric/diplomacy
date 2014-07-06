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

def all_gamenames_standard(cursor):
    """Returns a list of all games that are of standard or standard gunboat
    variant"""
    for name, in cursor.execute("select distinct gamename from messages where body like \"%Variant: Standard%\";").fetchall():
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

def generate_all_game_presses(cursor, game_name):
    """Returns a list of all p2p presses in the given game.
    """
    messages = cursor.execute('SELECT subject, body, sent '
                              'FROM messages '
                              'WHERE gamename=? '
                              'AND (subject like "%Press from % to %" '
                              'OR subject like "USAK:%Press to %" '
                              'OR subject like "%Broadcast%") '
                              'ORDER BY gamename, sent;',
                              (game_name,)).fetchall()

    
    for subject, body, sent in messages:
        if subject.count("Error Flag") > 0:
            continue # just a bounce message
        
        if not body:
            body = ""
        try:
            body = body.encode("ISO-8859-1").decode("unicode-escape")
        except UnicodeEncodeError:
            body = body.encode("utf8").decode("unicode-escape")

        # get milestone
        try:
            # This is more reliable than parsing from subject, as subject sometimes has 2  names, sometimes zero
            milestone = body.split("Deadline: ")[1].split(" ")[0] 
        except IndexError:
            try:
                # Get from subject
                milestone = subject.split("- ")[1].split(" ")[0]
            except:
                continue # not actually a press message; invalid credential message

        # regular p2p or p2group presses
        if subject.count("Press from ") > 0:
        
            sender = subject.lower().split("press from ")[1].split(" ")[0].upper() # lowercased to capture some cases
            receivers = subject.lower().split("to ")[1].upper() # lowercased to capture some cases

            if subject.count("Rcpt:") > 0 or subject.count("Re:") > 0:
                # receiver and sender are exchanged if the message is a reply or receipt notice
                temp = sender
                sender = receivers
                receivers = temp
                sender = "Re-"+sender
                receivers = "Re-"+receivers
        
            msg = body.split("End of message.")[0]
            try:
                msg = re.split("in[\s+]\'"+game_name+"\':",msg)[1] # The main message is of the format "... in '<game number>': <Message>\n\nEnd of message. ..."
            except IndexError:
                continue # not actually a press message; game state message
            yield sender, receivers, milestone, sent, msg

        # grey presses
        elif subject.count("Press to ") > 0:
            sender = "unknown"
            receivers = subject.lower().split("to ")[1].upper() # lowercased to capture some cases

            if subject.count("Rcpt:") > 0 or subject.count("Re:") > 0:
                # receiver and sender are exchanged if the message is a reply or receipt notice
                temp = sender
                sender = receivers
                receivers = temp
                sender = "Re-"+sender
                receivers = "Re-"+receivers
        
            msg = body.split("End of message.")[0]
            try:
                msg = re.split("in[\s+]\'"+game_name+"\':",msg)[1] # The main message is of the format "... in '<game number>': <Message>\n\nEnd of message. ..."
            except IndexError:
                continue # not actually a press message; game state message
            yield sender, receivers, milestone, sent, msg

        elif subject.count("Broadcast") > 0:
            msg = body.split("End of message.")[0]
            
            sender = msg.split(" in \'" + game_name + "\':")[0].split(' ') # Sender name in broadcast is many times in body, many times in subject
            if sender[-2] == "as":
                sender = sender[-1][0] # sender name from body
            else:
                if subject.count(" from ") > 0 and not (subject.startswith('Re:') or subject.startswith('Rcpt:')): # sender name from subject
                    sender = subject.split(" from ")[1]
                else:
                    sender = "unknown"
            receivers = "all"

            try:
                msg = re.split("in[\s+]\'"+game_name+"\':",msg)[1] # The main message is of the format "... in '<game number>': <Message>\n\nEnd of message. ..."
            except IndexError:
                continue
            yield sender, receivers, milestone, sent, msg


def generate_game_broadcast_presses(cursor, game_name):
    """Returns all broadcast messages in a game"""
    messages = cursor.execute('SELECT subject, body, sent '
                                  'FROM messages '
                                  'WHERE gamename="'+ game_name + '" AND subject like "%Broadcast% to %" ORDER BY gamename, sent;').fetchall()

    for subject, body, sent in messages:
        if subject.count("Error Flag") > 0:
            continue # just a bounce message
        if not body:
            body = ""
        try:
            body = body.encode("utf8").decode("unicode-escape")
        except UnicodeEncodeError:
            body = body.encode("ISO-8859-1").decode("unicode-escape")
    
        body = body.replace("\n"," ").replace(","," ")
        msg = body.split("End of message.")[0]
            
        sender = msg.split(" in \'" + game_name + "\':")[0].split(' ') # Sender name in broadcast is many times in body, many times in subject
        if sender[-2] == "as":
            sender = sender[-1][0] # sender name from body
        else:
            if subject.count(" from ") > 0 and not (subject.startswith('Re:') or subject.startswith('Rcpt:')): # sender name from subject
                sender = subject.split(" from ")[1]
            else:
                sender = "unknown"
        receivers = "all"

        try:
            # This is more reliable than parsing from subject, as subject sometimes has 2  names, sometimes zero
            milestone = body.split("Deadline: ")[1].split(" ")[0] 
        except IndexError:
            try:
                # Get from subject
                milestone = subject.split("- ")[1].split(" ")[0]
            except:
                continue # not actually a press message; invalid credential message

        try:
            msg = msg.split("in \'" + game_name+ "\':")[1] # The main message is of the format "... in '<game number>': <Message>\n\nEnd of message. ..."
        except IndexError:
            continue
        yield sender, receivers, milestone, sent, msg
