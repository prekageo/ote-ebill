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

    for k,v in changes.iteritems():
      if isinstance(v, dict):
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
    self.costs['monthly_charges'] = self.conf['monthly_charges'] * days/30
    self.costs['monthly_charges'] = self.costs['monthly_charges'].quantize(q)
    self.costs['total'] = reduce(lambda x, y: x+self.costs[y], self.costs, zero)
    return self.costs

  def get_call_cost(self, row):
    """ Calculate and return the cost of the given call. """

    time = datetime.datetime.fromtimestamp(int(row[2]))
    self.min_time = min(self.min_time, time)
    self.max_time = max(self.max_time, time)
    duration = int(row[3])
    duration_left = duration
    call_group = row[6]
    cost = decimal.Decimal(0)

    category_name = self.category_from_call_group(call_group)
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
        datetimes = self.choose_time_interval(category['datetime'], time)
        tiered_fee = self.choose_tiered_fee(datetimes['tiered_fee'],
          duration - duration_left)
        duration_left,time = consume(tiered_fee['step'])
        cost += tiered_fee['charge']

    rounded_cost = cost.quantize(decimal.Decimal('.0001'))
    self.costs[category_name] += rounded_cost
    return rounded_cost

  def category_from_call_group(self, call_group):
    """ Map the call group given by OTE e-bill service to the call category. """

    map = {
      'AST':'local',
      'KIN':'mobile',
      'YPE':'long_distance',
    }
    return map[call_group]

  def choose_time_interval(self, datetimes, time):
    """ Choose the time interval into which the given time falls in. """

    for datetime in datetimes:
      if datetime['days'][time.weekday()] == ' ':
        continue
      if datetime['hours'][time.hour] == ' ':
        continue
      return datetime

  def choose_tiered_fee(self, tiered_fees, duration):
    """
    Choose the current tiered fee that applies to the given duration of the
    call.
    """

    sum = 0
    for tiered_fee in tiered_fees:
      len = tiered_fee['len']
      if len == -1:
        return tiered_fee
      sum += len
      if duration < sum:
        return tiered_fee

  @cherrypy.expose
  def calculate(self,min,max):
    """
    Calculate the costs for all products by using call data for the time period
    between min and max timestamps. Return a summary of all products sorted by
    total cost.
    """

    cursor = db.get_db_cursor()
    sql = '''select service, callee, '''+db.datetime('datetime')+''' datetime,
             duration, seg, cost, call_group from calls where call_group not in
             ("ALD","SKO","ALK","PSE") and '''+db.datetime('datetime')+''' >= ?
             and '''+db.datetime('datetime')+''' < ?'''
    sql = db.normalize_sql(sql)
    cursor.execute(sql, (str(min),str(max)))
    rows = [row for row in cursor]
    ret = []
    for conf in self.products:
      self.begin(conf)
      for row in rows:
        cost = self.get_call_cost(row)
      results = self.end()
      line = (conf,self.companies[self.configurations[conf]['company']],results)
      ret.append(line)

    ret.sort(key=lambda x:x[2]['total'])
    for i in ret:
      for j in i[2]:
        i[2][j] = str(i[2][j].quantize(decimal.Decimal('0.01')))
    return json.dumps(ret)
