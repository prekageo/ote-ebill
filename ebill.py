#!/usr/bin/python
# coding=utf-8

"""
Downloads call records from OTE e-Bill (https://ebill.ote.gr/wwwote/) to an
SQLite database named ote-ebill.db. Be sure the set the settings first in the
corresponding file.

Usage:
./ebill.py "A 123456789#DD/MM/YYYY"
"""

import codecs
import cookielib
import datetime
import decimal
import gzip
import settings
import sqlite3
import sys
import urllib
import urllib2
from lxml import html

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
  
def validate_0(html_str):
  """Validate the login page."""
  
  root = html.fromstring(html_str)
  assert_by_id(root,'IDToken1','input',{'type':'text'})
  assert_by_id(root,'IDToken2','input',{'type':'password'})

def validate_1(html_str):
  """Validate the intermediate login page."""
  
  root = html.fromstring(html_str)
  assert_by_id(root,'form-password','input',{'type':'password'})

def validate_2(html_str):
  """Validate the main page after login."""
  
  root = html.fromstring(html_str)
  assert_by_id(root,'logout','input',{'type':'button'})

def validate_3(html_str):
  """Validate the results page."""
  
  root = html.fromstring(html_str)
  assert_by_id(root,'results','td')

def get_calls_in_html(inv_info):
  """
  Executes the WebPlayer to receive the HTML page of the calls for a specified
  invoice.
  inv_info -- the invoice ID
  """
  
  DATA1 = {'IDToken2':settings.password,'IDToken1':settings.username,
    'realm':'oteportal','goto':'https://ebill.ote.gr/wwwote/index.jsp'}
  DATA3 = {
    'cust_code':settings.cust_code,
    'ebaction':'8',
    'inv_info':inv_info,
    'phones':settings.phones,
    'phone_no_info':codecs.getencoder('iso-8859-7')(settings.phone_no_info)[0],
  }

  web_player = WebPlayer(debug=False)
  base_path = 'https://ebill.ote.gr/wwwote/'
  web_player.visit('%sindex.jsp' % base_path,validate_0)
  response = web_player.visit('https://am.ote.gr/amserver/UI/Login',validate_1,DATA1)
  root = html.fromstring(response)
  DATA2 = {
    'j_username':settings.username,
    'j_password':root.xpath('//*[@id="form-password"]')[0].value
  }
  web_player.visit('%sj_security_check' % base_path,validate_2,DATA2)
  return web_player.visit('%sController' % base_path,validate_3,DATA3)

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
    u'Αλλες Κλήσεις': 'ALK',
    u'Αστικές': 'AST',
    u'Προς \'Αλλα Σταθερά Δίκτυα': 'ALD',
    u'Προς Κινητά': 'KIN',
    u'Υπεραστικές': 'YPE',
    u'Προς Σύντομους Κωδικούς': 'SKO',
    u'Χρήση Ψηφιακών Ευκολιών': 'PSE',
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
    params = (self.service,self.callee,self.datetime,self.duration,self.seg,
        self.cost,self.group)
    cursor.execute('insert into calls values (?,?,?,?,?,?,?)', params)
    return True
  
  @staticmethod
  def init_db(cursor):
    """Create the table for saving the calls into the database."""
    
    cursor.execute('''create table if not exists calls (service,callee,datetime,
          duration,seg,cost,call_group)''')
    
def parse_date_time(date_str, time_str):
  """Transform a date and time from string form to a datetime object."""
  
  day,month,year = [int(x) for x in date_str.split('/')]
  hour,minute,second = [int(x) for x in time_str.split(':')]
  return datetime.datetime(year+2000,month,day,hour,minute,second)
  
def parse_duration(time_str):
  """Transform a duration from string form to a timedelta object."""
  
  minutes,seconds = [int(x) for x in time_str.split(':')]
  return datetime.timedelta(minutes=minutes,seconds=seconds)

def get_calls(html_str):
  """Traverse the HTML page of the calls and return a list of call objects."""
  
  root = html.fromstring(html_str)
  rows = root.xpath('/html/body/table/tbody/form/tr/td/table/tr[2]/td/table/tr/td/table/tbody/tr/td/table/tbody/tr')

  exception_text = 'Invalid HTML encountered. Code=%d.'
  
  if len(rows[0]) != 2:
    raise Exception(exception_text % 1)
  if len(rows[1]) != 8:
    raise Exception(exception_text % 2)

  calls = []
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
      datetime = parse_date_time(row[3].text,row[4].text)
      duration = parse_duration(row[5].text)
      seg = row[6].text.strip()
      cost = decimal.Decimal(row[7].text.replace(',','.'))
      calls.append(Call(service,callee,datetime,duration,seg,cost))
    elif no_columns == 1 and row[0].attrib.get('colspan') == '8':
      group = row[0][0].text.strip()
      (type,count) = group.split(':')
      type = type.strip()
      count = int(count)
      if (len(calls) != count):
        raise Exception(exception_text % 4)
      for call in calls:
        call.set_group(type)
        yield call
      calls = []
    else:
      raise Exception(exception_text % 5)
  if len(calls) > 0:
    raise Exception(exception_text % 6)

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
  
  if len(sys.argv) < 2:
    raise Exception('Insufficient number of command line arguments.')
  inv_info = sys.argv[1]
  print 'Gettings records for invoice "%s"...' % inv_info
  html_str = get_calls_in_html(inv_info)
  saved,unsaved = store_calls(settings.database_path,html_str)
  print 'Total records: %d, Saved: %d, Duplicates: %d' % (saved+unsaved,saved,
      unsaved)

if __name__ == '__main__':
  main()
