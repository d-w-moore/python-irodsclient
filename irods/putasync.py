#!/usr/bin/env python
from __future__ import print_function
import time,os,threading
import irods.test.helpers as h
s = h.make_session()
d = {}
#d = False
c = h.home_collection(s)
s.data_objects.put( 'thing',c + '/thing', async_ = d
                )

print(d)
notifier = None
try:
    notifier = d.get('notifier')
except:
    pass


if notifier:

    progress = notifier.progress
    INTERVAL = float(os.environ.get('INTERVAL','-1'))
    if INTERVAL < 0: INTERVAL = 0.25

    while progress != [progress[1]]*2:
        print (progress)
        time.sleep(INTERVAL)

