#!/bin/bash

start='2016-01-01'
stop='2016-02-01'

for i in {0..720}; do
  echo -n "$start "
  sqlite3 db.db "select call_category,sum(duration)/60 from (select case call_category when 'long_distance' then 'local' else call_category end call_category,(duration+59)/60*60 as duration from calls where datetime between '$start' and '$stop') group by call_category" | tr '|' ' ' | xargs
  start=$(date +%Y-%m-%d -d "$start + 1 day")
  stop=$(date +%Y-%m-%d -d "$stop + 1 day")
done
