from __future__ import print_function

# NB: unittest.mock is part of the standard lib in later Pythons
try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call

from nose.tools import raises

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
            rv = raa.main()
            captured_output = ''.join(args[0] for args, kwargs in mock_write.call_args_list)
            captured_output = captured_output.splitlines()

        # Check success
        self.assertEqual(rv, 0)

        # Check that the right number of lines were output
        self.assertEqual(len(captured_output), len(expected_output_60_20))

        # Check each line
        for co_line, eo_line in zip(captured_output, expected_output_60_20):
            self.assertEqual(co_line, eo_line)

    @raises(ValueError)
    def test_incorrect_tile_size(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20', '--tile-shape', '30x10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_tile_size_negative(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20', '--tile-shape', '20x-10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_tile_size_non_int(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20', '--tile-shape', 'twentyx10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_tile_size_too_few(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20', '--tile-shape', '20', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_tile_size_too_many(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20', '--tile-shape', '20x10x1', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_output_size_negative(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x-20', '--tile-shape', '20x10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_output_size_non_int(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60xtwenty', '--tile-shape', '20x10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_output_size_too_few(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60', '--tile-shape', '20x10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)

    def test_invalid_output_size_too_many(self):
        argv_patch = patch('sys.argv', [
            'ruaumoko-ascii-map', '-s', '60x20x1', '--tile-shape', '20x10', self.dataset_path])
        with argv_patch:
            rv = raa.main()
        self.assertNotEqual(rv, 0)
