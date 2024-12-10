from django.test import SimpleTestCase


class CalcTest(SimpleTestCase):
    def test_add_numbers(self):
        r = 6 + 5
        self.assertEqual(r, 12)

