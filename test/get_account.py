#!/usr/bin/env python
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError

config_logging(logging, logging.INFO)

# HMAC authentication with API key and secret
key = "nGXPRad8iBKt2h83U3JOitYPBinu4un7pp5gsBnKSzWACUkvu51UOzNMeNkaDQIN"
secret = "g7EIyuylKe2N28I6SAgK7XFUcBtQDeZYSIGEgojnGHAaJzoitGHMJz3dCaH0Lkpt"

hmac_client = UMFutures(key=key, secret=secret)
logging.info(hmac_client.account(recvWindow=5000))

# RSA authentication with RSA key
# key = ""
# with open("/Users/john/private_key.pem", "r") as f:
#     private_key = f.read()

# rsa_client = UMFutures(key=key, private_key=private_key)

# try:
#     response = rsa_client.account(recvWindow=6000)
#     logging.info(response)
# except ClientError as error:
#     logging.error(
#         "Found error. status: {}, error code: {}, error message: {}".format(
#             error.status_code, error.error_code, error.error_message
#         )
#     )
