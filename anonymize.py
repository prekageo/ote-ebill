#!/usr/bin/env python

import sqlite3
import random

def main():
  conn = sqlite3.connect('ote-ebill.db')
  cur = conn.cursor()

  cur.execute('select distinct callee from calls')
  m = {}
  for x in cur.fetchall():
    y = x[0]
    z = range(ord('A'),ord('Z'))
    random.shuffle(z)
    m[y] = ''.join(map(lambda x:chr(x),z[:10]))
  
  for x in m:
    cur = conn.cursor()
    cur.execute('update calls set callee=? where callee=?',(m[x],x))

  conn.commit()

if __name__ == '__main__':
  main()