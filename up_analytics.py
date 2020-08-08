#!/usr/bin/env python

"""
************************************************************************
Playing with the UP API
************************************************************************
"""

__author__      =       "Hamish Gunasekara"
__version__     =       "1.0.1"
__email__       =       "hamish.gunasekara@gmail.com"


import requests
import json
import psycopg2
import yaml
import sys
from datetime import datetime, timedelta
from configparser import ConfigParser

def connect_to_db():
    # connect to db
    con = psycopg2.connect(
        host="localhost",
        database="upBank",
        user="postgres",
        password="hamish123")
    # cursor
    cur = con.cursor()
    return cur, con


def connect_to_up(user_id):
    config_info = open("config.yaml")
    parsed_config_info = yaml.load(config_info, Loader=yaml.FullLoader)
    API_KEY = parsed_config_info['config']['api_key'][user_id]
    header = {'Authorization': 'Bearer ' + API_KEY}
    return header

def test_ping(header):
    test_ping = requests.get(
        "https://api.up.com.au/api/v1/util/ping",
        headers=header)

    print("Status code = " + str(test_ping.status_code))
    print("Response is = " + str(test_ping.json()))


def extract_latest_transactions(cur, con, header, user_id):
    select_statement = "select created_at from	d_transaction where user_id = '{}' order by created_at desc limit 1".format(user_id)
    cur.execute(select_statement)
    latest_dt = cur.fetchall()
    latest_date = latest_dt[0][0] + timedelta(seconds=2)
    transaction_params = {'page[size]': 100, 'filter[since]': latest_date}
    extract_transactions(header, cur, con, transaction_params, user_id)


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
    print("Uploading transaction from {} to the database".format(description))
    cur.execute(
        "insert into d_transaction (transaction_id, tran_type, description, message, roundup, roundup_value, roundup_value_base, amount_value, amount_value_base, created_at, user_id, account_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (transaction_id,
         tran_type,
         description,
         message,
         isinstance(
             roundup,
             dict),
            roundup_value,
            roundup_value_base,
            amount_value,
            amount_value_base,
            created_at,
            user_id,
            account_id))

    # commit everything
    con.commit()
    print("Uploaded transaction from {}!".format(description))


def extract_transactions(header, cur, con, transaction_params, user_id):
    tran_page_url = "https://api.up.com.au/api/v1/transactions"
    while tran_page_url:
        r = requests.get(
            tran_page_url,
            headers=header,
            params=transaction_params)
        current_page = json.loads(r.text)
        data = current_page['data']

        if r.status_code == 200:
            print("Connected to Up API")
        
        if not data:
            print("Nothing to Upload")
        else:
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
                
        # Go to next page
        tran_page_url = current_page['links']['next']


def close_db(cur, con):
    # close the cursor
    cur.close()

    # close the connection
    con.close()


# main function
def main():
    if sys.argv:
        user_id = sys.argv[0]
        if user_id == 'hamish' or user_id == 'nina':
            cur, con = connect_to_db()
            header = connect_to_up(user_id)
            transaction_params = {'page[size]': 100}
            extract_transactions(header, cur, con, transaction_params, user_id)
            close_db(cur, con)
        else:
            print("user_id is invalid")
    else:
        print("No user_id supplied")


if __name__ == "__main__":
    # main()
    print("main is commented out")
