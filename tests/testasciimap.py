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

        # Patch sys.stdout.write
        stdout_write_patch = patch('sys.stdout.write')

        # Call the ascii map generator main function
        with argv_patch, stdout_write_patch as mock_write:
            raa.main()
            captured_output = ''.join(args[0] for args, kwargs in mock_write.call_args_list)
            captured_output = captured_output.splitlines()

        # Check that the right number of lines were output
        self.assertEqual(len(captured_output), len(expected_output_60_20))

        # Check each line
        for co_line, eo_line in zip(captured_output, expected_output_60_20):
            self.assertEqual(co_line, eo_line)

