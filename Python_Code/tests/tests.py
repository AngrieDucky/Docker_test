import json
import unittest
import requests
import numpy as np

endpoint = "http://127.0.0.1/getPercent"

class SuccessfulTest(unittest.TestCase):

    def setUp(self):
        self.endpoint = endpoint
        self.conn_string = "dbname='postgres' user='postgres' host='localhost' password='mysecretpassword'"
    

    def test_normal_run(self):
        params = {"audience1": "Age BETWEEN 18 AND 35", "audience2": "Sex = 2 AND Age >= 18"}
        resp = requests.get(url=self.endpoint, params=params)
        self.assertEqual(resp.status_code, 200)
        self.assertAlmostEqual(np.float64(json.loads(resp.text)["percent"]), np.float64(0.4395441332083433162552543041))
    
    def test_zero_section(self):
        params = {"audience1": "Age BETWEEN 18 AND 19", "audience2": "Age BETWEEN 20 AND 21"}
        resp = requests.get(url=self.endpoint, params=params)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(np.float64(json.loads(resp.text)["percent"]), np.float64(0))

    def test_full_section(self):
        params = {"audience1": "Sex = 2 AND Age >= 18", "audience2": "Sex = 2 AND Age >= 18"}
        resp = requests.get(url=self.endpoint, params=params)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(np.float64(json.loads(resp.text)["percent"]), np.float64(1))

class UnsuccessfulTests(unittest.TestCase):
    def setUp(self):
        self.endpoint = endpoint
        self.conn_string = "dbname='postgres' user='postgres' host='app-db-local' password='mysecretpassword'"

    def test_bad_input(self):
        params = {"audience1": "Sex = ###sex### AND Age <= -18", "audience2": "Sex = 2 AND Age >= 18"}
        resp = requests.get(url=self.endpoint, params=params)
        self.assertEqual(resp.status_code, 404)

    def test_empty_imput(self):
        params = {"audience1": "", "audience2": "Sex = 2 AND Age >= 18"}
        resp = requests.get(url=self.endpoint, params=params)
        self.assertEqual(resp.status_code, 400)
    
    def test_injection(self):
        params = {"audience1": "Sex = 2; dRoP tAble 'respondents';", "audience2": "Sex = 2 AND Age >= 18"}
        resp = requests.get(url=self.endpoint, params=params)
        self.assertEqual(resp.status_code, 400)

if __name__ == '__main__':
    unittest.main()
