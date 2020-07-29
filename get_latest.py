import up_analytics
import requests
import json
from datetime import datetime, timedelta


header, cur, con = up_analytics.connect_to_db()

up_analytics.extract_latest_transactions(cur, con, header)

up_analytics.close_db(cur, con)