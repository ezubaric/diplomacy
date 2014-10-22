situations = ["""\
Turkey: Army Bulgaria SUPPORT Italian Army Apulia -> Greece.  (*cut*)

Austria: Army Serbia SUPPORT Russian Fleet Rumania -> Bulgaria (east coast).
Austria: Fleet Albania -> Greece.  (*bounce*)


Italy: Fleet Ionian Sea CONVOY Army Apulia -> Greece.
Italy: Army Apulia -> Ionian Sea -> Greece.  (*bounce*)


Russia: Fleet Rumania -> Bulgaria (east coast).  (*bounce*)
""",

"""\
Austria: Army Serbia SUPPORT Italian Fleet Ionian Sea -> Greece.  (*cut*)
Austria: Army Budapest -> Vienna.
Austria: Fleet Albania SUPPORT Italian Fleet Ionian Sea -> Greece.

Italy: Army Tyrolia SUPPORT Austrian Army Budapest -> Vienna.
Italy: Army Trieste SUPPORT Austrian Army Budapest -> Vienna.
Italy: Army Venice SUPPORT Army Tyrolia.
Italy: Fleet Naples -> Ionian Sea.  (*bounce*)
Italy: Fleet Ionian Sea -> Greece.  (*bounce*)

Russia: Army Galicia SUPPORT Army Vienna -> Budapest.
Russia: Fleet Sevastopol -> Rumania.
Russia: Army Vienna -> Budapest.  (*bounce, dislodged*)
""",

"""\
England: Fleet St Petersburg (north coast) HOLD.  (*dislodged*)
Russia: Army Moscow -> St Petersburg.
Turkey: Fleet Gulf of Bothnia SUPPORT Russian Army Moscow -> St Petersburg.
""",

"""\
England: Fleet Black Sea -> St Petersburg (south coast).
Turkey: Army Rumania SUPPORT English Fleet Black Sea -> St Petersburg.
"""
]

from nose.tools import assert_in, assert_equal

from ..dyad import (supports, attacks_on_home, attacks_with_hold,
                    attacks_mutual, important_orders)

situations = map(important_orders, situations)


def test_supports():
    """Test that we identify all supports"""
    supp = supports(situations[0])
    assert_in(('T', 'I'), supp)
    assert_in(('A', 'R'), supp)
    assert_equal(len(supp), 2)


def test_attacks_with_hold():
    """Test that when a unit moves onto a holding unit, it's an attack."""
    attk = attacks_with_hold(situations[2])
    assert_in(('R', 'E'), attk)


def test_attacks_with_support():
    """Test that we identify supports of attacks as attacks"""
    _, attk = attacks_with_hold(situations[2], return_supports=True)
    assert_in(('T', 'E'), attk, msg="Supporting attack on hold not identified")
    _, attk = attacks_on_home(situations[3], return_supports=True)
    assert_in(('T', 'R'), attk, msg="Supporting attack on home not identified")
    _, attk = attacks_mutual(situations[1], return_supports=True)
    assert_in(('I', 'R'), attk, msg="Supporting mutual attack not identified")
    # XXX: some situations are missing here


def test_attacks_on_home():
    attk = attacks_on_home(situations[3])
    assert_in(('E', 'R'), attk, msg="Attack on home not identified")


def test_mutual_move():
    attk = attacks_mutual(situations[1])
    assert_in(('R', 'A'), attk)
    assert_in(('A', 'R'), attk)
