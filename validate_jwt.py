import sys

import requests
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError, JWTClaimsError

def validate_eve_jwt(jwt_token):
    jwk_set_url = "https://login.eveonline.com/oauth/jwks"

    res = requests.get(jwk_set_url)
    res.raise_for_status()

    data = res.json()

    try:
        jwk_sets = data['keys']
    except KeyError as e:
        print("Something went wrong when retrieving the JWK set. The returned "
              "payload did not have the expected key {}. \nPayload returned "
              "from the SSO looks like: {}".format(e, data))
        sys.exit(1)

    jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))

    try:
        return jwt.decode(
            jwt_token,
            jwk_set,
            algorithms=jwk_set["alg"],
            issuer="login.eveonline.com"
        )
    except ExpiredSignatureError as e:
        print("The JWT token has expired: {}".format(str(e)))
        sys.exit(1)
    except JWTError as e:
        print("The JWT signature was invalid: {}").format(str(e))
        sys.exit(1)
    except JWTClaimsError as e:
        try:
            return jwt.decode(
                        jwt_token,
                        jwk_set,
                        algorithms=jwk_set["alg"],
                        issuer="https://login.eveonline.com"
                    )
        except JWTClaimsError as e:
            print("The issuer claim was not from login.eveonline.com or "
                  "https://login.eveonline.com: {}".format(str(e)))
            sys.exit(1)
