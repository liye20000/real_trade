#!/usr/bin/env python
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError

config_logging(logging, logging.DEBUG)

# key = ""
# secret = ""
key = "nGXPRad8iBKt2h83U3JOitYPBinu4un7pp5gsBnKSzWACUkvu51UOzNMeNkaDQIN"
secret = "g7EIyuylKe2N28I6SAgK7XFUcBtQDeZYSIGEgojnGHAaJzoitGHMJz3dCaH0Lkpt"

um_futures_client = UMFutures(key=key, secret=secret)

try:
    response = um_futures_client.new_order(
        symbol="DOGEUSDT",
        side="SELL",
        positionSide = "LONG",
        type="LIMIT",
        quantity=32,
        timeInForce="GTC",
        price=0.16,
    )
    logging.info(response)
except ClientError as error:
    logging.error(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )
