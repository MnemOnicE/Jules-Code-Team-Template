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
