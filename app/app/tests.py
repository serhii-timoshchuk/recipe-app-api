'''
Sample tests
'''
from django.test import SimpleTestCase

from . import calc


class CalcTest(SimpleTestCase):
    """Test the calc modul"""
    def test_add(self):
        '''TEst adding numbers together '''
        result = calc.add(5, 6)
        self.assertEqual(result, 11)

    def test_substract_number(self):
        '''Test substarcitng numbers'''
        res = calc.substract(10, 15)

        self.assertEqual(res, 5)
