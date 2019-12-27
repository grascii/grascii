
import unittest
import alphabet

class TestGrascii(unittest.TestCase):

    def test_mat(self):
        self.assertEqual('foo'.upper(), 'FOO')

class TestTokenizer(unittest.TestCase):

    def test_mat(self):
        self.assertEqual(alphabet.make_tokens('MAT'),
                ['M', 'A', 'T'])

    def test_nd(self):
        self.assertEqual(alphabet.make_tokens('ND'),
                ['ND'])

    def test_multicharacter_tokens(self):
        self.assertEqual(alphabet.make_tokens('SPNDICH'), ['S', 'PND', 'I', 'CH'])
        self.assertEqual(alphabet.make_tokens('ATHLF'), ['A', 'TH', 'L', 'F'])
        self.assertEqual(alphabet.make_tokens('DFLRNTGBSRM'), ['DF', 'L','R', 'NT', 'G', 'B', 'S', 'R', 'M'])

    def test_invalid_character(self):
        self.assertRaises(Exception, alphabet.make_tokens, 'MaT')

    def test_pending_symbols(self):
        self.assertEqual(alphabet.determine_pending_symbols(['NT',
                'MD',
                'JNT',
                'E',
                'M',
                'PND',
                '\\']), {'N', 'J', 'P', 'M'})

    def test_pending_symbols_tokens(self):
        self.assertEqual(alphabet.determine_pending_symbols(
                alphabet.tokens),
                {'C', 'D', 'J', 'M', 'N', 'P', 'S', 'T', '/'}
            )

if __name__ == '__main__':
    unittest.main()
