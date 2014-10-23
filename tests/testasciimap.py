from __future__ import print_function

# NB: unittest.mock is part of the standard lib in later Pythons
try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call

from .util import DownloadedDatasetTestCase

import ruaumoko.asciiart as raa

expected_output_60_20 = [
    "                                                            ",
    "              .::-::+****+::    ...           ..            ",
    ".  ::::. .... ...::. :*##=.      ::..    .  .:-:::.-.:    ..",
    "   .--====::::   .:.  -        =: ...........::::::::=--::.:",
    "    .   :=---:.. .::            . ......:....:-:-===-.   :  ",
    "          ++*-:::::          :-::-:..-- .:+*+=++==:-.       ",
    "          :=+-..:            :=:.   --=+=#+@@@@%+: ...      ",
    "           .=+              :::=-:-::=- :.::::-*=:.         ",
    "    .        +   ..         .:-----::--.  ::. :-.           ",
    "                . :.        .::-::--+=:    .   ..           ",
    "                 :......        -:-==.         . .:.::      ",
    "                 *+.::--        :===-.                      ",
    "                   %.:=.        -===  =           .::::     ",
    "                   %.-:          ==-  :           ---.:.    ",
    "                   -             ::               .  ...    ",
    "                  -.                                      . ",
    "                   .                                        ",
    "                                                            ",
    "                  .-         ..:::.--=***--+*##*****#*+==-: ",
    "   .::-=++++++++-:....:.:-=++*####%%%%%%%%%%%%%%%%####***=. ",
]

class TestASCIIMap(DownloadedDatasetTestCase):
    def test_simple_output(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20', '--tile-shape', '20x10', self.dataset_path])
        print_patch = patch('__builtin__.print')

        # Call the ascii map generator main function
        with argv_patch, print_patch as mock_print:
            raa.main()
            self.assertEqual(mock_print.call_count, len(expected_output_60_20))
            mock_print.assert_has_calls(list(call(x) for x in expected_output_60_20), any_order=False)

