# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from hypothesis import given, strategies as st
import unittest

def add(x, y):
    """A simple function to test properties on."""
    return x + y

class TestInvariants(unittest.TestCase):
    @given(st.integers(), st.integers())
    def test_addition_associativity(self, x, y):
        """Verify that addition is commutative: x + y == y + x"""
        self.assertEqual(add(x, y), add(y, x))

    @given(st.integers())
    def test_addition_identity(self, x):
        """Verify the identity property: x + 0 == x"""
        self.assertEqual(add(x, 0), x)

if __name__ == '__main__':
    unittest.main()
