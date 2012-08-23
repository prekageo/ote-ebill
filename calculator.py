#!/usr/bin/python
# coding=utf-8

""" Implements the calculator component of the web application. """

# TODO: improve performance
# TODO: cost is different among various mobile providers
# TODO: check for no data and return total cost 0

# DONE: bundles, e.g. internet+telephony or isdn+telephony or pstn+telephony
# DONE: addons, e.g. OTE EPILEGMENOI PROORISMOI

from __future__ import with_statement
import copy
import datetime
import decimal
import os.path
try:
    import json
except ImportError:
    import simplejson as json
import db
import cherrypy

def recursive_decimal_to_string(obj):
  """
  Helper method that recursively converts decimals to string. It can traverse
  lists, dictionaries and tuples. Decimals are rounded to 2 decimal places.
  """

  if isinstance(obj, decimal.Decimal):
    return str(obj.quantize(decimal.Decimal('0.01')))
  elif isinstance(obj, dict):
    ret = {}
    for key in obj:
      ret[key] = recursive_decimal_to_string(obj[key])
    return ret
  elif isinstance(obj, list):
    ret = []
    for el in obj:
      ret.append(recursive_decimal_to_string(el))
    return ret
  elif isinstance(obj, tuple):
    ret = []
    for el in obj:
      ret.append(recursive_decimal_to_string(el))
    return tuple(ret)
  else:
    return obj

def div_round_up(x, y):
  """ Divide and round up. """
  return (x+y-1)/y

class Calculator:
  """ The calculator component of the web application. """

  def __init__(self):
    """ Read the JSON configuration and store data into respective fields. """

    with open(os.path.join(os.path.dirname(__file__), 'calculator_conf.js'),'r') as f:
      data = json.load(f, parse_float=decimal.Decimal)
    self.companies = data['companies']
    self.configurations = data['configurations']
    self.assets = data['assets']
    self.resolve_dependencies()
    self.make_products()

  def resolve_dependencies(self):
    """
    Resolve dependencies of assets. An asset may be a copy_of another asset. In
    that case copy the template asset into the target one and make the defined
    changes to it.
    """

    deps = {}
    for asset_name in self.assets:
      conf = self.assets[asset_name]
      if 'copy_of' in conf:
        deps[asset_name] = conf['copy_of']
      else:
        deps[asset_name] = None
    while len(deps) > 0:
      for k,v in deps.iteritems():
        if v == None:
          break
      del deps[k]
      if 'copy_of' in self.assets[k]:
        changes = self.assets[k]['changes']
        self.assets[k] = copy.deepcopy(self.assets[self.assets[k]['copy_of']])
        if 'addon_to' in self.assets[k]:
          self.merge(self.assets[k]['changes'], changes)
        else:
          self.merge(self.assets[k], changes)
      for kk in deps:
        if deps[kk] == k:
          deps[kk] = None

  def make_products(self):
    """ Make products by combining assets according to the configuration. """

    self.products = {}
    for conf_name in self.configurations:
      assets = self.configurations[conf_name]['assets']
      self.products[conf_name] = copy.deepcopy(self.assets[assets[0]])
      for i in xrange(1,len(assets)):
        compatible_with = self.assets[assets[i]]['addon_to']
        assert assets[0] in compatible_with, conf_name.encode('utf8')
        self.merge(self.products[conf_name], self.assets[assets[i]]['changes'])

  def merge(self, dest, changes):
    """
    Merge changes into destination asset. This method deep merges the given
    dictionaries. A feature included is that when merging montly_charges the
    change can be given relative to the original value, e.g. '+1' means
    'increase the original value by 1'.
    """

    if changes is None:
      return

    for k,v in changes.iteritems():
      if isinstance(v, dict):
        if k not in dest:
          dest[k] = {}
        self.merge(dest[k], v)
      else:
        if k == 'monthly_charges' and isinstance(v,basestring) and \
            v.startswith('+'):
          if isinstance(dest[k],basestring) and dest[k].startswith('+'):
            dest[k] = '+%s' % (decimal.Decimal(dest[k][1:]) + decimal.Decimal(v[1:]))
          else:
            dest[k] += decimal.Decimal(v[1:])
        else:
          dest[k] = v

  def begin(self, product_name):
    """
    Initialize the calculator for calculating the telecommunication cost for the
    given product name.
    """

    self.costs = {}
    self.skipped = []
    self.min_time = datetime.datetime.fromtimestamp(2**31-1)
    self.max_time = datetime.datetime.fromtimestamp(0)
    self.conf = self.products[product_name]
    self.free = copy.deepcopy(self.conf['free'])
    for f in self.free:
      if 'mins' in self.free[f]:
        self.free[f]['secs']=self.free[f]['mins']*60
    categories = self.conf['categories']
    for category in categories:
      self.costs[category] = decimal.Decimal(0)

  def end(self):
    """ Return the total cost for the calls included in the calculation. """

    q = decimal.Decimal('.0001')
    zero = decimal.Decimal(0)

    days = (self.max_time-self.min_time).days+1
    self.costs['time_based_charges'] = reduce(lambda x, y: x+self.costs[y], self.costs, zero)
    self.costs['monthly_charges'] = self.conf['monthly_charges'] * days/30
    self.costs['total'] = self.costs['time_based_charges'] + self.costs['monthly_charges']

    self.costs['monthly_charges'] = self.costs['monthly_charges'].quantize(q)
    return self.costs

  def get_call_cost(self, row):
    """ Calculate and return the cost of the given call. """

    time = datetime.datetime.fromtimestamp(int(row['datetime']))
    self.min_time = min(self.min_time, time)
    self.max_time = max(self.max_time, time)
    duration = int(row['duration'])
    duration_left = duration
    cost = decimal.Decimal(0)

    category_name = row['call_category']
    category = self.conf['categories'][category_name]
    free = self.free[category['use_free']]

    def consume(seconds):
      return (duration_left-seconds, time + datetime.timedelta(seconds=seconds))

    if free['secs'] > 0:
      if free['secs'] < free['min_duration']:
        free['secs'] = 0
      else:
        duration_left,time = consume(free['min_duration'])
        free['secs'] -= free['min_duration']

    while duration_left > 0:
      if free['secs'] > 0:
        duration_left,time = consume(free['step'])
        self.free[category['use_free']]['secs'] -= free['step']
      else:
        datetimes,datetime_time = self.choose_time_interval(category['datetime'], time)
        tiered_fee,tier_time = self.choose_tiered_fee(datetimes['tiered_fee'],
          duration - duration_left)

        seconds = min(duration_left,tier_time,datetime_time)
        count = div_round_up(seconds,tiered_fee['step'])
        duration_left,time = consume(tiered_fee['step']*count)
        cost += tiered_fee['charge']*count

    rounded_cost = cost.quantize(decimal.Decimal('.0001'))
    self.costs[category_name] += rounded_cost
    return rounded_cost

  def choose_time_interval(self, datetimes, time):
    """ Choose the time interval into which the given time falls in. """

    next_hour = datetime.datetime(time.year,time.month,time.day,time.hour)
    next_hour += datetime.timedelta(hours=1)
    time_left = (next_hour - time).seconds

    for datetime_ in datetimes:
      if datetime_['days'][time.weekday()] == ' ':
        continue
      if datetime_['hours'][time.hour] == ' ':
        continue
      return datetime_,time_left

  def choose_tiered_fee(self, tiered_fees, duration):
    """
    Choose the current tiered fee that applies to the given duration of the
    call.
    """

    sum = 0
    for tiered_fee in tiered_fees:
      len = tiered_fee['len']
      if len == -1:
        return tiered_fee,2**31-1
      sum += len
      if duration < sum:
        return tiered_fee,sum-duration

  @cherrypy.expose
  def calculate(self,min,max):
    """
    Calculate the costs for all products by using call data for the time period
    between min and max timestamps. Return a summary of all products sorted by
    total cost.
    """

    cursor = db.get_db_cursor()
    sql = '''select service, callee, '''+db.datetime('datetime')+''' datetime,
             duration, seg, cost, call_category from calls where
             '''+db.datetime('datetime')+''' >= ?
             and '''+db.datetime('datetime')+''' < ?'''
    sql = db.normalize_sql(sql)
    cursor.execute(sql, (str(min),str(max)))
    rows = [row for row in cursor]

    overview = {
      'count_calls': len(rows),
      'cost': {
        'local': 0,
        'long_distance': 0,
        'mobile': 0,
        'other': 0,
      },
      'duration': {
        'local': 0,
        'long_distance': 0,
        'mobile': 0,
        'other': 0,
      },
      'first_call_timestamp': 0,
      'last_call_timestamp': 0,
      'count_days': 0,
    }
    min_time = 2**31-1
    max_time = 0
    import __builtin__
    for row in rows:
      call_category = row['call_category']
      if call_category is None:
        call_category = 'other'
      overview['cost'][call_category] += decimal.Decimal(row['cost'])
      overview['duration'][call_category] += int(row['duration'])
      datetime_ = int(row['datetime'])
      min_time = __builtin__.min(min_time, datetime_)
      max_time = __builtin__.max(max_time, datetime_)
    overview['first_call_timestamp'] = min_time
    overview['last_call_timestamp'] = max_time
    overview['count_days'] = (datetime.datetime.fromtimestamp(max_time) - datetime.datetime.fromtimestamp(min_time)).days+1

    skipped = []
    for row in rows:
      if row['call_category'] is None:
        skipped.append(row)

    overview['skipped'] = {
      'list': [row['callee'] for row in skipped],
      'total_cost': sum(decimal.Decimal(row['cost']) for row in skipped),
    }

    ret = []
    for conf in self.products:
      self.begin(conf)
      for row in rows:
        if row['call_category'] is not None:
          cost = self.get_call_cost(row)
      results = self.end()
      line = (conf,self.companies[self.configurations[conf]['company']],results)
      ret.append(line)

    ret.sort(key=lambda x:x[2]['total'])
    ret = recursive_decimal_to_string(ret)
    overview = recursive_decimal_to_string(overview)

    ret = {
      'invoices': ret,
      'overview': overview,
    }
    return json.dumps(ret)
