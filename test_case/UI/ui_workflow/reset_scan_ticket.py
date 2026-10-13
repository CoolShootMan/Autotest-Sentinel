"""
reset_scan_ticket.py — Precondition: reset scanner ticket to un-redeemed.

Same pattern as step 4 in test_linda_t0000_precondition_obtain_all_accounts_token.py:
sign_in(p05_email, password) -> linda05_token, then call orders.ticket_status.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "API auto script"))
sys.path.insert(0, API_DIR)

from core.http_client import ApiClient
from api.auth import AuthApi
from api.orders import OrdersApi

# p05 credentials (same as test_linda_t0000 step 4)
P05_EMAIL = "linda.zhou.ext+05@1m.app"
PASSWORD = "7EbE8F4BdE4A38768AcF9C2833aF2Db5"

client = ApiClient("https://release.katana-api.1m.app")
auth = AuthApi(client)
orders = OrdersApi(client)

# sign_in as linda05
token = auth.sign_in(body={"email": P05_EMAIL, "password": PASSWORD}).json()["data"]["token"]

# reset ticket to IN_PROCESSING
orders.ticket_status(
    body={
        "orderLineItemId": "1a764e96-7cd4-4600-b2b2-34460596c1a6",
        "orderLineItemUnitIds": ["af382384-a807-4e1a-a08b-9ab30ea50d49"],
        "status": "IN_PROCESSING",
    },
    token=token,
)
print("[reset_scan_ticket] done", flush=True)
