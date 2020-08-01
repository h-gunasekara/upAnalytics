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
from datetime import datetime, timedelta


header, cur, con = up_analytics.connect_to_db()

up_analytics.extract_latest_transactions(cur, con, header)

up_analytics.close_db(cur, con)