About
=====

django_hits allow you to count hits to database objects and/or any unique identifier you want. It may
use multiple buckets for counting to keep different hits apart (list view of object is different from
detail page). In addition you may store historical data, if you want to (for example by calling "manage.py
hits_create_history" every week).
