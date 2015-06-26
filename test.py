import unittest


class MyTest(unittest.TestCase):

    def test_add(self):
        self.assertEqual(1 + 3, 4)

    def test_divide(self):
        self.assertEqual(8 / 2, 4)

    # def test_hulde(self):
    #     self.assertEqual(8, 8)


if __name__ == '__main__':
    unittest.main()
