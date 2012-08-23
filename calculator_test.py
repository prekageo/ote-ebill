import sys

class FakeSettings:
  def __init__(self):
    self.database_driver = None

sys.modules['settings'] = FakeSettings()

import calculator
import unittest
import datetime
import time
import calendar
from decimal import Decimal

class Call(object):
  def __init__(self,datetime,duration,call_category):
    self.arr = [None,None,datetime,duration,None,None,call_category]

  def __getitem__(self,index):
    dict = {
      'service'      : self.arr[0],
      'callee'       : self.arr[1],
      'datetime'     : self.arr[2],
      'duration'     : self.arr[3],
      'seg'          : self.arr[4],
      'cost'         : self.arr[5],
      'call_category': self.arr[6],
    }
    if index in dict:
      return dict[index]
    return self.arr[index]

  @property
  def duration(self):
    return self.arr[3]

  @duration.setter
  def duration(self, value):
    self.arr[3] = value

  @property
  def datetime(self):
    return self.arr[2]

  @datetime.setter
  def datetime(self, value):
    self.arr[2] = value

class CalculatorTest(unittest.TestCase):
  def setUp(self):
    self.c = calculator.Calculator()
    self.c.min_time = datetime.datetime.fromtimestamp(2**31-1)
    self.c.max_time = datetime.datetime.fromtimestamp(0)
    self.c.costs = {
      'cat1': 0,
      'cat2': 0,
    }
    self.c.free = {
      'free1': {'secs': 0, 'min_duration': 0, 'step': 1},
    }
    self.c.conf = {
      'categories': {
        'cat1': {
          'use_free': 'free1',
          'datetime': [
            {'days': 'MTWTFSS', 'hours': '0123456789012           ', 'tiered_fee': [{'step': 1, 'len': -1, 'charge': 1},{'step': 1, 'len': -1, 'charge': 3}]},
            {'days': 'MTWTFSS', 'hours': '             34567890123', 'tiered_fee': [{'step': 1, 'len': -1, 'charge': 2}]},
          ],
        },
        'cat2': {
          'use_free': 'free1',
          'datetime': [
            {'days': 'MTWTFSS', 'hours': '012345678901234567890123', 'tiered_fee': [{'step': 1, 'len': -1, 'charge': 1}]},
          ],
        },
      },
    }

  def FAILS_test_precision(self):
    """ Fails due to precision errors. """
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),50,'cat1')
    self.c.conf['categories']['cat1']['datetime'][0]['tiered_fee'][0]['charge'] = 0.001223
    self.assertEqual(Decimal('0.0612'), self.c.get_call_cost(c))

  def test_rounding(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.conf['categories']['cat1']['datetime'][0]['tiered_fee'][0]

    def _test(duration, charge, expected):
      c.duration = duration
      conf['charge'] = charge
      self.assertEqual(expected, self.c.get_call_cost(c))

    _test(2,3,6)
    _test(1,Decimal('0.0001'),Decimal('0.0001'))

    _test(1,Decimal('0.00004999999'),Decimal('0.0000'))
    _test(1,Decimal('0.00005000000'),Decimal('0.0000'))
    _test(1,Decimal('0.00005000001'),Decimal('0.0001'))

    _test(10,Decimal('0.01234499999'),Decimal('0.1234'))
    _test(10,Decimal('0.01234500000'),Decimal('0.1234'))
    _test(10,Decimal('0.01234500001'),Decimal('0.1235'))

    _test(10,Decimal('0.01235499999'),Decimal('0.1235'))
    _test(10,Decimal('0.01235500000'),Decimal('0.1236'))
    _test(10,Decimal('0.01235500001'),Decimal('0.1236'))

  def test_free_min_duration(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.free['free1']

    def _test(duration, min_duration, remaining_free):
      conf['secs'] = 60
      c.duration = duration
      conf['min_duration'] = min_duration
      self.assertEqual(0, self.c.get_call_cost(c))
      self.assertEqual(remaining_free, conf['secs'])

    _test(1, 1, 59)
    _test(2, 1, 58)
    _test(10, 1, 50)
    _test(59, 1, 1)
    _test(60, 1, 0)

    _test(1, 2, 58)
    _test(2, 2, 58)
    _test(3, 2, 57)
    _test(10, 2, 50)
    _test(59, 2, 1)
    _test(60, 2, 0)

    _test(1, 10, 50)
    _test(9, 10, 50)
    _test(10, 10, 50)
    _test(11, 10, 49)
    _test(59, 10, 1)
    _test(60, 10, 0)

    _test(1, 60, 0)
    _test(10, 60, 0)
    _test(59, 60, 0)
    _test(60, 60, 0)

  def test_free_step(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.free['free1']

    def _test(duration, step, remaining_free):
      conf['secs'] = 60
      c.duration = duration
      conf['step'] = step
      self.assertEqual(0, self.c.get_call_cost(c))
      self.assertEqual(remaining_free, conf['secs'])

    _test(1, 1, 59)
    _test(2, 1, 58)
    _test(10, 1, 50)
    _test(59, 1, 1)
    _test(60, 1, 0)

    _test(1, 2, 58)
    _test(2, 2, 58)
    _test(3, 2, 56)
    _test(10, 2, 50)
    _test(58, 2, 2)
    _test(59, 2, 0)
    _test(60, 2, 0)

    _test(1, 10, 50)
    _test(9, 10, 50)
    _test(10, 10, 50)
    _test(11, 10, 40)
    _test(50, 10, 10)
    _test(51, 10, 0)
    _test(59, 10, 0)
    _test(60, 10, 0)

    _test(1, 60, 0)
    _test(10, 60, 0)
    _test(59, 60, 0)
    _test(60, 60, 0)

  def test_free_min_duration_and_step(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.free['free1']

    def _test(duration, min_duration, step, remaining_free):
      conf['secs'] = 60
      c.duration = duration
      conf['min_duration'] = min_duration
      conf['step'] = step
      self.assertEqual(0, self.c.get_call_cost(c))
      self.assertEqual(remaining_free, conf['secs'])

    _test(1, 1, 1, 59)
    _test(2, 1, 1, 58)
    _test(59, 1, 1, 1)
    _test(60, 1, 1, 0)

    """
    Q: what does min duration and step means?
    A: there are two approaches and we follow approach A
    approach A:
    actual duration: 0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10,11,12,13,14,15,16,17,18,19,20
    billed duration: 10,10,10,10,10,10,10,10,10,10,10,13,13,13,16,16,16,19,19,19,22
    approach B:
    actual duration: 0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10,11,12,13,14,15,16,17,18,19,20
    billed duration: 10,10,10,10,10,10,10,10,10,10,10,12,12,15,15,15,18,18,18,19,21

    Q: what happens if the remaining free time is less than the step?
    A: there are three approaches and we follow approach A
    approach A: step duration is considered free
    approach B: the remaining free time is considered free, stepping starts over
    approach C: the remaining free time is lost
    """

    _test(1, 10, 3, 50)
    _test(10, 10, 3, 50)
    _test(11, 10, 3, 47)
    _test(55, 10, 3, 5)
    _test(56, 10, 3, 2)
    _test(57, 10, 3, 2)
    _test(58, 10, 3, 2)

    # TODO: CHECK: glitch here
    _test(59, 10, 3, -1)
    _test(60, 10, 3, -1)
    _test(61, 10, 3, -1)

  def test_free_min_duration_and_step_and_available_free(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.free['free1']

    def _test(duration, available_free, min_duration, step, remaining_free, cost):
      conf['secs'] = available_free
      c.duration = duration
      conf['min_duration'] = min_duration
      conf['step'] = step
      self.assertEqual(cost, self.c.get_call_cost(c))
      self.assertEqual(remaining_free, conf['secs'])

    _test(1, 60, 10, 3, 50, 0)
    _test(1, 11, 10, 3, 1, 0)
    _test(1, 10, 10, 3, 0, 0)
    _test(11, 10, 10, 3, 0, 1)

    # TODO: CHECK: glitch here
    _test(11, 11, 10, 3, -2, 0)
    _test(12, 11, 10, 3, -2, 0)
    _test(13, 11, 10, 3, -2, 0)
    _test(11, 9, 10, 3, 0, 11)

  def test_free_min_duration_and_step_multiple_categories(self):
    c1 = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    c2 = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat2')
    conf = self.c.free['free1']

    def _test(call, duration, min_duration, step, remaining_free):
      call.duration = duration
      conf['min_duration'] = min_duration
      conf['step'] = step
      self.assertEqual(0, self.c.get_call_cost(call))
      self.assertEqual(remaining_free, conf['secs'])

    conf['secs'] = 60
    _test(c1,1,10,3,50)
    _test(c2,11,10,3,37)
    conf['secs'] = 60
    _test(c1,10,10,3,50)
    _test(c2,10,10,3,40)
    _test(c1,40,10,3,0)

  def test_datetime(self):
    c = Call(None,10,'cat1')

    def _test(timetuple, cost):
      c.datetime = time.mktime(timetuple)
      self.assertEqual(cost, self.c.get_call_cost(c))

    _test((2012,8,22,12,59,50,0,0,-1), 10)
    _test((2012,8,22,12,59,51,0,0,-1), 11)
    _test((2012,8,22,12,59,55,0,0,-1), 15)
    _test((2012,8,22,12,59,59,0,0,-1), 19)
    _test((2012,8,22,13,0,0,0,0,-1), 20)
    _test((2012,8,22,14,0,0,0,0,-1), 20)
    _test((2012,8,22,23,59,50,0,0,-1), 20)
    _test((2012,8,22,23,59,51,0,0,-1), 19)
    _test((2012,8,22,23,59,55,0,0,-1), 15)
    _test((2012,8,22,23,59,59,0,0,-1), 11)
    _test((2012,8,22,0,0,0,0,0,-1), 10)
    _test((2012,8,22,1,0,0,0,0,-1), 10)

  def test_datetime_with_step(self):
    c = Call(None,10,'cat1')
    conf = self.c.conf['categories']['cat1']['datetime']

    def _test(step1, step2, timetuple, cost):
      conf[0]['tiered_fee'][0]['step'] = step1
      conf[1]['tiered_fee'][0]['step'] = step2
      c.datetime = time.mktime(timetuple)
      self.assertEqual(cost, self.c.get_call_cost(c))

    # TODO: CHECK: this
    _test(1, 1, (2012,8,22,12,59,50,0,0,-1), 10)
    _test(2, 3, (2012,8,22,12,59,50,0,0,-1), 5)
    _test(2, 3, (2012,8,22,12,59,51,0,0,-1), 5)
    _test(2, 3, (2012,8,22,12,59,52,0,0,-1), 6)
    _test(2, 3, (2012,8,22,12,59,53,0,0,-1), 6)
    _test(2, 3, (2012,8,22,12,59,54,0,0,-1), 7)
    _test(2, 3, (2012,8,22,12,59,55,0,0,-1), 7)
    _test(2, 3, (2012,8,22,12,59,56,0,0,-1), 6)
    _test(2, 3, (2012,8,22,12,59,57,0,0,-1), 6)
    _test(2, 3, (2012,8,22,12,59,58,0,0,-1), 7)
    _test(2, 3, (2012,8,22,12,59,59,0,0,-1), 7)
    _test(2, 3, (2012,8,22,13,0,0,0,0,-1), 8)

  def test_tiers_length(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.conf['categories']['cat1']['datetime'][0]['tiered_fee'][0]

    def _test(length, duration, cost):
      conf['len'] = length
      c.duration = duration
      self.assertEqual(cost, self.c.get_call_cost(c))

    _test(11, 10, 10)
    _test(9, 10, 12)
    _test(-1, 999, 999)

  def test_tiers_length_and_step(self):
    c = Call(time.mktime((2012,8,22,0,0,0,0,0,0)),None,'cat1')
    conf = self.c.conf['categories']['cat1']['datetime'][0]['tiered_fee']

    def _test(length, step1, step2, duration, cost):
      conf[0]['len'] = length
      conf[0]['step'] = step1
      conf[1]['step'] = step2
      c.duration = duration
      self.assertEqual(cost, self.c.get_call_cost(c))

    _test(10, 2, 3, 15, 11)
    _test(10, 2, 3, 16, 11)
    _test(10, 2, 3, 17, 14)

    # TODO: CHECK: this
    _test(10, 3, 2, 14, 7)
    _test(10, 3, 2, 15, 10)
    _test(10, 3, 2, 16, 10)
    _test(10, 3, 2, 17, 13)

  def test_free_datetime_tier(self):
    c = Call(time.mktime((2012,8,22,12,59,50,0,0,-1)),20,'cat1')
    self.c.free['free1']['secs']=3
    self.c.conf['categories']['cat1']['datetime'][0]['tiered_fee'][0]['len']=5
    """
    we follow approach B
    approach A: tier 1 is consumed after the free time is exhausted
    approach B: tier 1 is consumed at the same time with the free time
    """
    self.assertEqual(37, self.c.get_call_cost(c))

if __name__ == '__main__':
  unittest.main()
