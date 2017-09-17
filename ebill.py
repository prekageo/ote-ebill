#!/usr/bin/python
# coding=utf-8

"""
Downloads call records from OTE e-Bill (https://ebill.cosmote.gr/wwwote/) to an
SQLite database named ote-ebill.db. Be sure the set the settings first in the
corresponding file.

Usage:
./ebill.py
"""

import codecs
import cookielib
import datetime
import decimal
import gzip
import optparse
import os
import settings
import sqlite3
import sys
import urllib
import urllib2
from lxml import html
try:
    import json
except ImportError:
    import simplejson as json

class WebPlayer:
  """
  Represents an HTTP client supporting cookies and custom headers for simulating
  user action on web pages.
  """

  def __init__(self, debug=False):
    """
    Initializes the HTTP client.
    debug -- if set to True will write to a file every response received
    """

    cj = cookielib.CookieJar()
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    self.headers = {}
    self.debug = debug
    self.counter = 1

  def set_headers(self, headers):
    """Modifies HTTP headers sent to the web server."""

    self.headers = headers

  def visit(self, url, validator=None, params=None):
    """
    Visits a URL, possibly running a validator function on the response.
    url -- the URL to visit
    validator -- a function to call passing the response text for validation
    params -- POST parameters (they should be gived with no URL encoding)
    """

    sys.stdout.write('Visiting %s...' % url)
    if params != None:
      params = urllib.urlencode(params)
    req = urllib2.Request(url,params,self.headers)
    usock = self.opener.open(req)
    response = usock.read()
    if usock.headers.get('content-encoding', None) == 'gzip':
        response = gzip.GzipFile(fileobj=StringIO.StringIO(response)).read()
    print 'done'
    if self.debug:
      f = open('debug_%02d.html' % self.counter, "w")
      f.write(response)
      f.close()
      self.counter += 1
    if validator != None:
      validator(response)
    return response

def assert_by_id(node, id, tag=None, attribs={}):
  """
  Asserts the presence of a specific node in an HTML document.
  node -- the root node of the HTML document
  id -- the id of the node looked for
  tag -- if given, will match the tag of the node found with this value
  attribs -- the node found should have the given attributes
  """

  try:
    element = node.get_element_by_id(id)
    if tag != None and element.tag != tag:
      raise Exception('Tag mismatch. Expected "%s". Got "%s".' % (tag,
          element.tag))
    for attrib in attribs:
      if element.attrib.get(attrib) != attribs[attrib]:
        raise Exception('Attribute "%s" mismatch. Expected "%s". Got "%s".' %
            (attrib,attribs[attrib],element.attrib.get(attrib)))

  except KeyError:
    raise Exception('Node with ID "%s" not found in document.' % id)

def assert_by_xpath(node, xpath):
  """
  Asserts the presence of at least one node that matches the given XPath.
  node -- the root node of the HTML document
  xpath -- the XPath expression
  """

  if len(node.xpath(xpath)) == 0:
    raise Exception('XPath "%s" not found in document.' % xpath)

def validate_1(html_str):
  """Validate the intermediate login page."""

  root = html.fromstring(html_str)
  assert_by_id(root,'form-password','input',{'type':'password'})

def validate_2(html_str):
  """Validate the main page after login."""

  root = html.fromstring(html_str)
  assert_by_xpath(root,'//form[@name="forwardfrm"]')

def validate_3(html_str):
  """Validate the results page."""

  root = html.fromstring(html_str)
  assert_by_id(root,'results','td')

def validate_4(html_str):
  """ Validate the invoices page. """

  root = html.fromstring(html_str)
  assert_by_xpath(root,'//select[@id="inv_info"]')

def login(web_player):
  """ Login to the web application. """

  DATA1 = {'IDToken2':settings.password,'IDToken1':settings.username,
    'realm':'oteportal','goto':'https://www.cosmote.gr/fixed/my-ote/my-bill'}

  base_path = 'https://myebill.cosmote.gr/wwwote/'
  response = web_player.visit('https://idmextsso.ote.gr/opensso/OTECloudLogin',None,DATA1)
  root = html.fromstring(response)
  value = root.xpath('//*[@name="iPlanetDirectoryProExtProd"]')[0].value
  DATA2 = {'iPlanetDirectoryProExtProd':value,'stage':'2','target':'https://www.cosmote.gr/fixed/my-ote/my-bill'}
  web_player.visit('https://idmextsso.cosmote.gr/opensso/OTECloudLogin',None,DATA2)
  response = web_player.visit('%s'%base_path,validate_1)
  root = html.fromstring(response)
  DATA2 = {
    'j_username':settings.username,
    'j_password':root.xpath('//*[@id="form-password"]')[0].value
  }
  web_player.visit('%sj_security_check' % base_path,validate_2,DATA2)

def get_invoices(web_player):
  """ Get all invoices from the web application. """

  DATA = {
    'cust_code':settings.cust_code,
    'ebaction':'7',
    'ccname':'',
  }
  base_path = 'https://myebill.cosmote.gr/wwwote/'
  response = web_player.visit('%sController' % base_path,validate_4,DATA)
  root = html.fromstring(response)
  options = root.xpath('//select[@id="inv_info"]/option')
  return [option.attrib.get('value') for option in options]

def get_calls_in_html(web_player, inv_info):
  """
  Executes the WebPlayer to receive the HTML page of the calls for a specified
  invoice.
  inv_info -- the invoice ID
  """

  DATA3 = {
    'cust_code':settings.cust_code,
    'ebaction':'8',
    'inv_info':inv_info,
    'phones':settings.phones,
    'phone_no_info':codecs.getencoder('iso-8859-7')(settings.phone_no_info)[0],
  }
  base_path = 'https://myebill.cosmote.gr/wwwote/'
  ret = web_player.visit('%sController' % base_path,None,DATA3)
  root = html.fromstring(ret)
  h2 = root.xpath('//h2')
  if len(h2) > 0:
    h2 = h2[0]
    print h2.text.strip()
    return None
  validate_3(ret)
  return ret

def adapt_timedelta(timedelta):
  """Transform a timedelta type for SQLite storage."""
  total_seconds = timedelta.days * 86400 + timedelta.seconds
  return str(total_seconds)

def adapt_decimal(decimal):
  """Transform a decimal type for SQLite storage."""
  return str(decimal)

sqlite3.register_adapter(datetime.timedelta, adapt_timedelta)
sqlite3.register_adapter(decimal.Decimal, adapt_decimal)

class Call:
  """Represents a call."""

  call_group = {
    u'ΑΛΛΕΣ ΚΛΗΣΕΙΣ': 'ALK',
    u'\'ΑΛΛΕΣ ΚΛΗΣΕΙΣ': 'ALK',
    u'ΔΙΕΘΝΕΙΣ ΚΛΗΣΕΙΣ': 'DIE',
    u'ΑΣΤΙΚΕΣ ΚΛΗΣΕΙΣ': 'AST',
    u'ΚΛΗΣΕΙΣ ΠΡΟΣ ΑΛΛΑ ΣΤΑΘΕΡΑ ΔΙΚΤΥΑ': 'ALD',
    u'ΚΛΗΣΕΙΣ ΠΡΟΣ ΚΙΝΗΤΑ': 'KIN',
    u'ΥΠΕΡΑΣΤΙΚΕΣ ΚΛΗΣΕΙΣ': 'YPE',
    u'ΠΡΟΣ ΣΥΝΤΟΜΟΥΣ ΚΩΔΙΚΟΥΣ': 'SKO',
    u'Χρήση Ψηφιακών Ευκολιών': 'PSE',
    u'Υπηρεσίες Πολυμεσικής Πληροφόρησης MEDIATEL': 'ALK',
    u'ΑΣΤΙΚΕΣ ΟΤΕ DOUBLE PLAY 2 ECONOMY 240': 'AST',
    u'ΥΠΕΡΑΣΤΙΚΕΣ ΟΤΕ DOUBLE PLAY 2 ECONOMY 240': 'YPE',
    u'ΠΡΟΣ ΚΙΝΗΤΑ ΟΤΕ DOUBLE PLAY 2 ECONOMY 240': 'KIN',
    u'ΠΡΟΣ ΑΛΛΑ ΣΤΑΘΕΡΑ ΔΙΚΤΥΑ ΟΤΕ DOUBLE PLAY 2 ECONOMY 240': 'ALD',
    u'ΑΣΤΙΚΕΣ ΟΤΕ DOUBLE PLAY 2 ΑΠΕΡΙΟΡΙΣΤΑ': 'AST',
    u'ΥΠΕΡΑΣΤΙΚΕΣ ΟΤΕ DOUBLE PLAY 2 ΑΠΕΡΙΟΡΙΣΤΑ': 'YPE',
    u'ΠΡΟΣ ΑΛΛΑ ΣΤΑΘΕΡΑ ΔΙΚΤΥΑ ΟΤΕ DOUBLE PLAY 2 ΑΠΕΡΙΟΡΙΣΤΑ': 'ALD',
    u'Υπηρεσίες Πολυμεσικής Πληροφόρησης NEWSPHONE': 'ALK',
    u'Υπηρεσίες Πολυμεσικής Πληροφόρησης Ολιγοψήφιος 14784': 'ALK',
    u'ΑΣΤΙΚΕΣ ΟΤΕ DOUBLE PLAY 4 ΑΠΕΡΙΟΡΙΣΤΑ PLUS': 'AST',
    u'ΥΠΕΡΑΣΤΙΚΕΣ ΟΤΕ DOUBLE PLAY 4 ΑΠΕΡΙΟΡΙΣΤΑ PLUS': 'YPE',
    u'ΠΡΟΣ ΚΙΝΗΤΆ ΟΤΕ DOUBLE PLAY 4 ΑΠΕΡΙΟΡΙΣΤΑ PLUS': 'KIN',
    u'ΠΡΟΣ ΑΛΛΑ ΣΤΑΘΕΡΑ ΔΙΚΤΥΑ ΟΤΕ DOUBLE PLAY 4 ΑΠΕΡΙΟΡΙΣΤΑ PLUS': 'ALD',
    u'ΑΣΤΙΚΕΣ COSMOTE HOME DOUBLE PLAY 4 XL': 'AST',
    u'ΥΠΕΡΑΣΤΙΚΕΣ COSMOTE HOME DOUBLE PLAY 4 XL': 'YPE',
    u'ΠΡΟΣ ΚΙΝΗΤΑ COSMOTE HOME DOUBLE PLAY 4 XL': 'KIN',
    u'ΠΡΟΣ ΑΛΛΑ ΣΤΑΘΕΡΑ ΔΙΚΤΥΑ COSMOTE HOME DOUBLE PLAY 4 XL': 'ALD',
    u'ΣΥΝΤΟΜΟΙ ΚΩΔΙΚΟΙ': 'SKO',
    u'ΥΠΗΡΕΣΙΕΣ ΠΟΛΥΜΕΣΙΚΗΣ ΠΛΗΡΟΦΟΡΗΣΗΣ ΤΡΙΤΩΝ': 'ALK',
    u'ΚΛΗΣΕΙΣ ΠΡΟΣ ΣΤΑΘΕΡΑ COSMOTE HOME DOUBLE PLAY 4 XL': 'STA',
    u'ΥΠΗΡΕΣΙΕΣ ΠΟΛΥΜΕΣΙΚΗΣ ΠΛΗΡΟΦΟΡΗΣΗΣ ΟΤΕ': 'ALK',
    u"'ΑΛΛΕΣ ΚΛΗΣΕΙΣ": 'ALK',
    u'ΚΛΗΣΕΙΣ ΠΡΟΣ ΣΤΑΘΕΡΑ COSMOTE HOME DOUBLE PLAY 24 XL': 'STA',
    u'ΠΡΟΣ ΚΙΝΗΤΑ COSMOTE HOME DOUBLE PLAY 24 XL': 'KIN',
    u'ΠΡΟΣ ΚΙΝΗΤΑ COSMOTE HOME 1000 ΠΡΟΣ ΚΙΝΗΤΑ COSMOTE': 'KIN',
  }

  def __init__(self, service, callee, datetime, duration, seg, cost):
    """
    Initializes a new call.
    service -- unknown
    callee -- the called number
    datetime -- the start date and time of the call
    duration -- duration of the call
    seg -- unknown
    cost -- the cost of the call
    """

    self.service = service;
    self.callee = callee;
    self.datetime = datetime;
    self.duration = duration;
    self.seg = seg;
    self.cost = cost;
    self.group = 'UNK';

  def __repr__(self):
    return str(self.__dict__)

  def set_group(self, group_full_name):
    """Set the group of the call."""

    self.group = self.call_group[group_full_name]

  def save(self, cursor):
    """
    Save the call to the underlying database if it does not already exist.
    cursor -- the database cursor to use for saving
    """

    params = (self.callee,self.datetime)
    cursor.execute('select count(*) from calls where callee=? and datetime=?',
        params)
    if cursor.fetchone()[0] > 0:
      return False

    row = {
      'service': self.service,
      'callee': self.callee,
      'datetime': self.datetime,
      'duration': self.duration,
      'seg': self.seg,
      'cost': self.cost,
      'call_group': self.group,
    }
    self.call_category = Call.compute_call_category(row)

    params = (self.service,self.callee,self.datetime,self.duration,self.seg,
        self.cost,self.group,self.call_category)
    cursor.execute('insert into calls values (?,?,?,?,?,?,?,?)', params)
    return True

  @staticmethod
  def init_db(cursor):
    """Create the table for saving the calls into the database."""

    cursor.execute('''create table if not exists calls (service,callee,datetime,
          duration,seg,cost,call_group,call_category)''')

    try:
      cursor.execute('''select call_category from calls where 1=0''')
    except sqlite3.OperationalError:
      cursor.execute('''alter table calls add column call_category''')

  @staticmethod
  def run_category_rules(conn):
    """
    Update the call category for every call by running the rules found in the
    configuration.
    """

    cursor = conn.cursor()
    cursor.execute('''select * from calls''')

    cursor2 = conn.cursor()
    sql = '''update calls set call_category=? where callee=? and datetime=?'''
    for row in cursor:
      call_category = Call.compute_call_category(row)
      params = (call_category, row['callee'], row['datetime'])
      cursor2.execute(sql,params)
      assert cursor2.rowcount == 1
    conn.commit()

  @staticmethod
  def compute_call_category(call):
    """
    Runs a set of configured rules against a row of the calls table and returns
    a string that identifies the call category (local, long distance, etc.)
    """

    global conf
    for rule in conf['rules']:
      res = eval(rule)
      if res is not None:
        return res

    return 'special'

def parse_date_time(date_str, time_str):
  """Transform a date and time from string form to a datetime object."""

  day,month,year = [int(x) for x in date_str.split('/')]
  hour,minute,second = [int(x) for x in time_str.split(':')]
  return datetime.datetime(year+2000,month,day,hour,minute,second)

def parse_duration(time_str):
  """Transform a duration from string form to a timedelta object."""

  v = [int(x) for x in time_str.split(':')]
  if len(v) == 2:
    return datetime.timedelta(minutes=v[0],seconds=v[1])
  elif len(v) == 3:
    return datetime.timedelta(hours=v[0],minutes=v[1],seconds=v[2])
  else:
    raise Exception('Invalid duration: %s' % time_str)

def parse_cost(cost_str):
  """ Transform a cost from string form to a decimal value."""

  return decimal.Decimal(cost_str.replace(',','.'))

def get_calls(html_str):
  """Traverse the HTML page of the calls and return a list of call objects."""

  root = html.fromstring(html_str)
  rows = root.xpath('/html/body/table/tbody/form/tr/td/table/tr[2]/td/table/tr/td/table/tbody/tr/td/table/tbody/tr')

  exception_text = 'Invalid HTML encountered. Code=%d.'

  if len(rows[0]) != 2:
    raise Exception(exception_text % 1)
  if len(rows[1]) != 8:
    raise Exception(exception_text % 2)

  total_duration = datetime.timedelta()
  total_cost = 0
  def verify_correct_totals():
    if total_duration.total_seconds() != 0:
      raise Exception(exception_text % 7)
    elif total_cost != 0:
      raise Exception(exception_text % 8)

  row_counter = 0
  for row in rows[2:]:
    no_columns = len(row)
    if no_columns == 8:
      row_counter += 1
      row_0 = row[0].text
      if row_0[0] == 'K':
        row_0 = row_0[1:]
      if int(row_0) != row_counter:
        raise Exception(exception_text % 3)
      service = row[1].text.strip()
      callee = row[2].text.strip()
      datetime_ = parse_date_time(row[3].text,row[4].text)
      duration = parse_duration(row[5].text)
      seg = row[6].text.strip()
      cost = parse_cost(row[7].text)
      call = Call(service,callee,datetime_,duration,seg,cost)
      call.set_group(type)
      yield call
      total_duration -= duration
      total_cost -= cost
    elif no_columns == 1 and row[0].attrib.get('colspan') == '8':
      pass
    elif no_columns == 4 and row[0].attrib.get('colspan') == '5':
      verify_correct_totals()
      type = row[0][0].text.strip()
      total_duration = parse_duration(row[1].text)
      total_cost = parse_cost(row[3].text)
    else:
      raise Exception(exception_text % 5)
  verify_correct_totals()

def store_calls(database_filename,html_str):
  """
  Store calls found in the HTML results into the database.
  database_filename -- the filename of the database to use
  html_str -- the calls in HTML form
  """

  saved = 0
  unsaved = 0

  conn = sqlite3.connect(database_filename)
  c = conn.cursor()
  Call.init_db(c)
  for call in get_calls(html_str):
    if call.save(c) == True:
      saved += 1
    else:
      unsaved += 1
  conn.commit()
  return saved,unsaved

def main():
  """
  Read the invoice ID from the command line arguments and save the calls into
  the database.
  """

  with open(os.path.join(os.path.dirname(__file__), 'ebill.conf.js'),'r') as f:
    global conf
    conf = json.load(f)

  parser = optparse.OptionParser()
  parser.add_option('--run-category-rules', action='store_true',
      dest='run_category_rules', default=False,
      help='run category rules and store results in the database')
  (options, args) = parser.parse_args()

  if options.run_category_rules:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    Call.init_db(conn.cursor())
    Call.run_category_rules(conn)
    return

  web_player = WebPlayer(debug = False)
  print 'Login...'
  login(web_player)
  print 'Listing invoices...'
  invoices = get_invoices(web_player)
  print 'Found invoices: %r' % invoices
  for inv_info in invoices:
    print 'Getting records for invoice "%s"...' % inv_info
    html_str = get_calls_in_html(web_player, inv_info)
    if html_str is None:
      continue
    saved,unsaved = store_calls(settings.database_path,html_str)
    print 'Total records: %d, Saved: %d, Duplicates: %d' % (saved+unsaved,saved,
        unsaved)

if __name__ == '__main__':
  main()
