#!/usr/bin/python
# coding=utf-8

"""
Implements a web application that provides a way to visualize telephone call
records retrieved from the OTE e-bill web service. Also provides a comparison
tool for different telecommunication providers based on usage data gathered by
the OTE e-bill web service.

Usage:
./stats.py

Connect using your web browser to http://localhost:8080/
"""

import calculator
import cherrypy
import os.path
import stats

class Webapp:
  """ The root of the web application. """

  def __init__(self):
    """ Initialize the components of this web application. """

    self.stats = stats.EbillStats()
    self.calculator = calculator.Calculator()

conf = os.path.join(os.path.dirname(__file__), 'webapp.conf')

cherrypy.config.update({'tools.staticdir.dir': os.path.dirname(__file__)})

if __name__ == '__main__':
  cherrypy.quickstart(Webapp(), config=conf)
else:
  cherrypy.tree.mount(Webapp(), config=conf)
