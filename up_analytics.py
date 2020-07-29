#!/usr/bin/env python

"""
************************************************************************
Playing with the UP API
************************************************************************
"""
__author__ = "Hamish Gunasekara"
__version__ = "1.0.0"
__email__ = "hamish.gunasekara@gmail.com"


import requests
import json
from configparser import ConfigParser
import psycopg2
import yaml
from datetime import datetime, timedelta

def connect_to_db():
    config_info = open("config.yaml")
    parsed_config_info = yaml.load(config_info, Loader=yaml.FullLoader)


    API_KEY = parsed_config_info['config']['api_info']['api_key']
    header = {'Authorization': 'Bearer ' + API_KEY}

    # connect to db
    con = psycopg2.connect(
        host="localhost", database="upBank", user="postgres", password="hamish123"
    )

    # cursor
    cur = con.cursor()
    return header, cur, con


def test_ping(header):
    test_ping = requests.get("https://api.up.com.au/api/v1/util/ping", headers=header)

    print("Status code = " + str(test_ping.status_code))
    print("Response is = " + str(test_ping.json()))

def extract_latest_transactions(cur, con, header):
    cur.execute("select created_at from	d_transaction order by created_at desc limit 1")
    latest_dt = cur.fetchall()
    latest_date = latest_dt[0][0] + timedelta(seconds=2)
    transaction_params = {'page[size]': 100, 'filter[since]': latest_date}
    extract_transactions(header, cur, con, transaction_params)


def upload_to_db(
        transaction_id,
        tran_type,
        description,
        message,
        roundup,
        roundup_value,
        roundup_value_base,
        amount_value,
        amount_value_base,
        created_at,
        user_id,
        account_id,
        cur,
        con):
    print("Uploading {} to the database".format(description))
    cur.execute(
        "insert into d_transaction (transaction_id, tran_type, description, message, roundup, roundup_value, roundup_value_base, amount_value, amount_value_base, created_at, user_id, account_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (transaction_id,
         tran_type,
         description,
         message,
         isinstance(roundup,dict),
         roundup_value,
         roundup_value_base,
         amount_value,
         amount_value_base,
         created_at,
         user_id,
         account_id))

    # commit everything
    con.commit()
    print("Upload success!")



# transaction_params = {'page[size]': 10}
# r = requests.get("https://api.up.com.au/api/v1/transactions",
#                  headers=header, params=transaction_params)

# print("Status code = " + str(r.status_code))
# print("Response is = " + str(r.json()))

# transactions = json.loads(r.text)
# print("next is " + transactions['links']['next'])

# for key in transactions['data']:
#     print("KEY IS: " + str(key))


def extract_transactions(header, cur, con, transaction_params):
    tran_page_url = "https://api.up.com.au/api/v1/transactions"
    while tran_page_url:
        r = requests.get(tran_page_url, headers=header, params=transaction_params)
        print("Status code = " + str(r.status_code))
        current_page = json.loads(r.text)
        
        for info in current_page['data']:
            transaction_id = info['id']
            tran_type = info['type']
            description = info['attributes']['description']
            message = info['attributes']['message']
            roundup = info['attributes']['roundUp']
            if roundup:
                roundup_value = info['attributes']['roundUp']['amount']['value']
                roundup_value_base = info['attributes']['roundUp']['amount']['valueInBaseUnits']
            else:
                roundup_value = 0
                roundup_value_base = 0
            amount_value = info['attributes']['amount']['value']
            amount_value_base = info['attributes']['amount']['valueInBaseUnits']
            created_at = info['attributes']['createdAt']
            user_id = 0
            account_id = info['relationships']['account']['data']['id']

            # print("id is " + str(transaction_id))
            # print("tran_type is " + str(tran_type))
            # print("description is " + str(description))
            # print("message is " + str(message))
            # print("roundUp is " + str(roundup))
            # print("value is " + str(amount_value))
            # print("valueInBaseUnits is " + str(amount_value_base))
            upload_to_db(
                transaction_id,
                tran_type,
                description,
                message,
                roundup,
                roundup_value,
                roundup_value_base,
                amount_value,
                amount_value_base,
                created_at,
                user_id,
                account_id,
                cur,
                con)
        tran_page_url = current_page['links']['next']



def close_db(cur, con):
    #close the cursor
    cur.close()

    #close the connection
    con.close()


# main function
def main():
    header, cur, con = connect_to_db()
    transaction_params = {'page[size]': 100}
    extract_transactions(header, cur, con, transaction_params)
    close_db(cur, con)


if __name__ == "__main__":
    #main()
    print("main is commented out")