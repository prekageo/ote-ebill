#!/usr/bin/python
# coding=utf-8

""" Provides basic connectivity to the web application database. """

import settings
if settings.database_driver == 'sqlite3':
  import sqlite3
elif settings.database_driver == 'mysql':
  import MySQLdb

def get_db_conn():
  """ Returns a connection to the database. """

  if settings.database_driver == 'sqlite3':
    return sqlite3.connect(settings.database_path)
  elif settings.database_driver == 'mysql':
    conn = MySQLdb.connect(db = settings.database, user = settings.database_user)
    conn.cursor().execute('SET time_zone = "+00:00"')
    return conn
  else:
    raise NotImplementedError

def get_db_cursor():
  """ Returns a cursor to the database. """

  return get_db_conn().cursor()

def datetime(column):
  if settings.database_driver == 'sqlite3':
    return 'strftime("%%s",%s)' % column
  elif settings.database_driver == 'mysql':
    return 'UNIX_TIMESTAMP(`%s`)' % column
  else:
    raise NotImplementedError

def datetime_start_of(column, unit):
  if settings.database_driver == 'sqlite3':
    return 'strftime("%%s",date(%s,"start of %s"))' % (column,unit)
  elif settings.database_driver == 'mysql':
    if unit == 'day':
      return 'UNIX_TIMESTAMP(DATE(`%s`))' % column
    elif unit == 'month':
      return 'UNIX_TIMESTAMP(DATE_FORMAT(`%s`,"%%%%Y-%%%%c-1"))' % column
    else:
      raise NotImplementedError
  else:
    raise NotImplementedError

def datetime_now():
  if settings.database_driver == 'sqlite3':
    return 'strftime("%s",datetime("now"))'
  elif settings.database_driver == 'mysql':
    return 'UNIX_TIMESTAMP(NOW())'
  else:
    raise NotImplementedError

def normalize_sql(sql):
  if settings.database_driver == 'sqlite3':
    return sql
  elif settings.database_driver == 'mysql':
    sql = sql.replace('?','%s')
    return sql
  else:
    raise NotImplementedError
