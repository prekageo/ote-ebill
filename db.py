#!/usr/bin/python
# coding=utf-8

""" Provides basic connectivity to the web application database. """

import settings
import sqlite3

def get_db_conn():
  """ Returns a connection to the database. """

  return sqlite3.connect(settings.database_path)

def get_db_cursor():
  """ Returns a cursor to the database. """

  return get_db_conn().cursor()
