from dateutil import parser

def all_gamenames(cursor):
    for name in cursor.execute( 'SELECT DISTINCT gamename FROM messages'):
        yield name


def messages(cursor, game_name=None):
    if game_name is not None:
        messages = cursor.execute('SELECT sent, subject, body, gamename '
                                  'FROM messages '
                                  'WHERE gamename=?', game_name).fetch_all()
    else:
        messages = cursor.execute('SELECT sent, subject, body, gamename '
                                  'FROM messages').fetch_all()
    messages = sorted(messages, key=lambda x: (x[-1], parser.parse(x[0])))
    return messages
