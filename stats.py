#!/usr/bin/python
# coding=utf-8

""" Implements the statistics component of the web application. """

import cherrypy
try:
    import json
except ImportError:
    import simplejson as json
import db

class EbillStats:
  """ The statistics component of the web application. """

  call_group = {
    'ALK': {'color':'#f00','desc':'Αλλες Κλήσεις'},
    'AST': {'color':'#0f0','desc':'Αστικές'},
    'ALD': {'color':'#00f','desc':'Προς Άλλα Σταθερά Δίκτυα'},
    'KIN': {'color':'#ff0','desc':'Προς Κινητά'},
    'YPE': {'color':'#f0f','desc':'Υπεραστικές'},
    'SKO': {'color':'#0ff','desc':'Προς Σύντομους Κωδικούς'},
    'PSE': {'color':'#ccc','desc':'Χρήση Ψηφιακών Ευκολιών'},
    'REST':{'color':'#888','desc':'Υπόλοιπες'},
  }

  def result_set_to_html_table(self, cursor, header = True, headings = None):
    """ Returns an HTML table filled in with data from a result set. """

    row = cursor.fetchone()
    html = '<table>'
    if header:
      html += '<tr>'
      for i in xrange(len(row)):
        if headings is None or i>=len(headings):
          heading = 'Column ' + str(i)
        else:
          heading = headings[i]
        html += '<th>' + heading + '</th>'
      html += '</tr>'
    while row:
      html += '<tr>'
      for column in row:
        html += '<td>' + str(column) + '</td>'
      row = cursor.fetchone()
      html += '</tr>\n'
    return html

  def get_default_min_max_time(self,cursor,min,max):
    """
    Returns the default minimum and maximum timestamps so that all telephone
    records are retrieved from the database.

    The default minimum timestamp is 0 and the default maximum timestamp is the
    current timestamp.
    """

    if min is None:
      min = 0

    if max is None:
      cursor.execute(db.normalize_sql('select ' + db.datetime_now()))
      max = cursor.fetchone()[0]
    return (min,max)

  def cost_per_unit_of_time(self,min,max,unit,tops):
    """
    Returns a JSON response containing plot data of telephone calls between
    "min" and "max" timestamps, aggregating over "unit" periods of time (e.g.
    days or months) and highlighting specified "tops" call groups.
    """

    cursor = db.get_db_cursor()

    if tops is None:
      tops = []
    elif isinstance(tops,str):
      tops = [tops]

    (min,max)=self.get_default_min_max_time(cursor,min,max)

    def get_data_for_top(top,top_condition):
      params = (min,max)
      sql = '''select '''+db.datetime_start_of('datetime',unit)+''' as day,
               sum(cost) from calls where call_group '''+top_condition+'''
               and '''+db.datetime('datetime')+''' >= ? and '''
      sql +=   db.datetime('datetime')+''' <= ? group by day order by day'''
      sql = db.normalize_sql(sql)
      cursor.execute(sql, params)
      return {
        'label':self.call_group[top]['desc'],
        'color':self.call_group[top]['color'],
        'data':[[1000*int(row[0]),float(row[1])] for row in cursor],
      }

    data = []
    for top in tops:
      data.append(get_data_for_top(top,'= "' + top + '"'))

    tops_list = ','.join(['"'+top+'"' for top in tops])
    data.append(get_data_for_top('REST','not in ('+tops_list+')'))

    return json.dumps(data)

  # TODO: table sorting and filtering via javascript
  # TODO: master-detail with drilldown per day/month, master view shows
  # cumulative data per call group
  @cherrypy.expose
  def viewcalls(self):
    """ Returns an HTML table containing all telephone records. """

    cursor = db.get_db_cursor()
    cursor.execute(db.normalize_sql('select * from calls order by datetime desc'))
    headings = ['service','callee','datetime','duration','seg','cost',
                'call_group']
    return self.result_set_to_html_table(cursor, headings = headings)

  # TODO: the count of top destinations should be user controllable
  # TODO: top destinations can also refer to callee number
  @cherrypy.expose
  def gettops(self,min=None,max=None):
    """
    Returns the top 3 most expensive call groups for a specified period of time.
    """

    cursor = db.get_db_cursor()
    (min,max)=self.get_default_min_max_time(cursor,min,max)
    params = (min,max)

    cursor.execute(db.normalize_sql('''select call_group from calls where '''+
                      db.datetime('datetime')+'''>= ? and '''+
                      db.datetime('datetime')+''' <= ? group by call_group order
                      by sum(cost) desc limit 3'''), params)
    tops = [row[0] for row in cursor]
    return json.dumps(tops)

  @cherrypy.expose
  def costperday(self,min=None,max=None,tops=None):
    """ Returns data for the cost per day graph. """

    return self.cost_per_unit_of_time(min,max,'day',tops)

  @cherrypy.expose
  def costpermonth(self,min=None,max=None,tops=None):
    """ Returns data for the cost per month graph. """

    return self.cost_per_unit_of_time(min,max,'month',tops)

  @cherrypy.expose
  def getcalls(self,min,max):
    """
    Returns a detailed listing of the calls made between the specified
    timestamps.
    """

    cursor = db.get_db_cursor()
    params = (min,max)
    sql = '''select callee,round(sum(cost),2),call_group,`desc` from calls left
             outer join telbook on callee=number where '''
    sql +=   db.datetime('datetime')+'''>= ? and '''+db.datetime('datetime')
    sql +=   ''' <= ? group by callee order by sum(cost) desc'''
    cursor.execute(db.normalize_sql(sql), params)
    data = [[row[0],
             float(row[1]),
             self.call_group[row[2]]['color'],
             row[3]] for row in cursor]
    return json.dumps(data)

  @cherrypy.expose
  def addphone(self,number,desc):
    """ Adds or changes a description for a telephone number. """

    conn = db.get_db_conn()
    cursor = conn.cursor()

    desc = desc.strip()
    if len(desc) == 0:
      cursor.execute(db.normalize_sql('delete from telbook where number=?'),(number,))
      conn.commit()
      return

    cursor.execute(db.normalize_sql('select count(*) from telbook where number=?'),(number,))
    if cursor.fetchone()[0] == 0:
      cursor.execute(db.normalize_sql('insert into telbook values (?,?)'), (number,desc))
    else:
      cursor.execute(db.normalize_sql('update telbook set `desc`=? where number=?'), (desc,number))
    conn.commit()
