# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
@File    :   encode.py
@Time    :   2022/01/15 19:52:58
@Author  :   AllenLuo
@Version :   1.0
@Contact :   username@163.com
@Desc    :   None
"""

import string
import requests
import json
from tools import logger
def encode_request(url, plaintext_data, ChannelNo="CUP CAR LOAN_YIXIN") -> json:
  """
  Description: Request parameter encryption method
  ---------
  Arguments: url: Encryption endpoint URL
             plaintext_data: Plaintext request parameters
  ---------
  Returns:
  -------
  """
  try: 
    raw_url = f"{url}/IM/encode/request/?apiId=100008&transNo=159463662161357829085&reqTime=20200713063705&reqChannelNo={ChannelNo}&rspChannelNo={ChannelNo}"
    request_payload = json.dumps(plaintext_data)
    logger.debug(f"Plaintext request parameters: {request_payload}")
    req_response = requests.request("POST", raw_url, data=request_payload)
    return req_response.json()
  except BaseException as e:
    logger.error(f'encode_request error-{e}')

def decode_request(url, ciphertext_data) -> string:
  """
  
  Description: Request parameter decryption method
  ---------
  
  Arguments: url: Decryption endpoint URL
             ciphertext_data: Ciphertext request parameters
  ---------
  
  
  Returns:
  -------
  
  """
  url = f"{url}/IM/decode/request"
  decode_request_payload = json.dumps(ciphertext_data) # Convert to JSON for transmission
  headers = {
    'Content-Type': 'application/json'
  }
  response = requests.request("POST", url, headers=headers, data=decode_request_payload)
  logger.debug(f"Decrypted request parameter: {response.text}")
  return response.text
  
def encode_respone(url, ciphertext_data) -> string:
  """
  
  Description: Response parameter encryption
  ---------
  
  Arguments: url: API endpoint URL to encrypt
             api_path: API path, e.g. /IM/calculateIRR
             ciphertext_data: Encrypted request parameters
  ---------

  Returns: JSON-format response data
  -------
  
  """

  headers = {
    'Content-Type': 'application/json'
  }
  encode_response = requests.request("POST", url=url, headers=headers, data=json.dumps(ciphertext_data))
  logger.debug(f"Encrypted response: {encode_response.text}")
  return encode_response.text


def decode_response(url, data) -> string:
  try:
    decode_response_url = url + "/IM/decode/response"
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url=decode_response_url, headers=headers, data=data)
    logger.debug(f"Decrypted response: {response.text}")
    return json.loads(response.text)
  except BaseException as e:
    logger.error(f'decode_response error-{e}')
