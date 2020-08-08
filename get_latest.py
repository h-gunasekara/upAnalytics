#!/usr/bin/env python

"""
************************************************************************
Finding and uploading only the most recent transactions to conserve 
resources 
************************************************************************
"""

__author__      =       "Hamish Gunasekara"
__version__     =       "1.0.0"
__email__       =       "hamish.gunasekara@gmail.com"


import up_analytics
import requests
import json
import sys
from datetime import datetime, timedelta

if sys.argv:
    user_id = sys.argv[1]
    if user_id == 'hamish' or user_id == 'nina':
        cur, con = up_analytics.connect_to_db()
        header = up_analytics.connect_to_up(user_id)

        up_analytics.extract_latest_transactions(cur, con, header, user_id)

        up_analytics.close_db(cur, con)
    else:
        print("user_id is invalid")
else:
    print("No user_id supplied")
