import unittest
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from service import RiskEngine
from models import ServiceError

class Cases(unittest.TestCase):
    """Visible behavior checks for return-fraud-risk."""
    def error(self,expected_status,code,fn,*args,**kwargs):
        with self.assertRaises(ServiceError) as ctx:
            fn(*args,**kwargs)
        self.assertEqual((ctx.exception.status,ctx.exception.code),(expected_status,code))

    def test_low_risk(self):
        """Approves a low-value return from an established customer with the best rating."""
        self.assertEqual(RiskEngine().evaluate(5,500,365)['decision'],'approve')

    def test_high_risk(self):
        """Adds rating, value and age points to produce the maximum risk score."""
        self.assertEqual(RiskEngine().evaluate(1,50000,10)['score'],95)

    def test_invalid(self):
        """Rejects a rating below the permitted range."""
        self.error(400,'invalid_input',RiskEngine().evaluate,0,100,30)

if __name__ == '__main__':
    unittest.main()
