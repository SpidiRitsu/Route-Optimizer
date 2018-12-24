#!/usr/bin/python3.7

import base64
import hashlib
import secrets
import os

from shared_flow import print_auth_url
from shared_flow import send_token_request
from shared_flow import handle_sso_token_response

def main():
    # Generate PKCE code challange
    random = secrets.token_urlsafe(32).encode()
    m = hashlib.sha256()
    m.update(random)
    d = m.digest()
    code_challange = base64.urlsafe_b64encode(d).decode().replace("=", "")

    CLIENT_ID = os.environ['CLIENT_ID']
    
    print_auth_url(CLIENT_ID, code_challange)

    auth_code = input("Copy the \"code\" query parameter and enter it here: ")

    code_verifier = base64.urlsafe_b64encode(random).decode().replace("=", "")

    form_values = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier
    }

    res = send_token_request(form_values)

    handle_sso_token_response(res)


if __name__ == "__main__":
    main()
