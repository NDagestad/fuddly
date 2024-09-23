################################################################################
#
#  Copyright 2014-2016 Eric Lacombe <eric.lacombe@security-labs.org>
#
################################################################################
#
#  This file is part of fuddly.
#
#  fuddly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  fuddly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with fuddly. If not, see <http://www.gnu.org/licenses/>
#
################################################################################

import unittest

from fuddly.test import args
import fuddly.test.unit, fuddly.test.integration
import argparse
import argcomplete

if len(args) == 2 and args[1] == "fuddly.test":
    del args[1]

if len(args) == 1:
    args.append('fuddly.test.unit')
    args.append('fuddly.test.integration')

argcomplete.autocomplete(parser)
args = parser.parse_args()
unittest.main(verbosity=2, argv=args, defaultTest=None, exit=False)
