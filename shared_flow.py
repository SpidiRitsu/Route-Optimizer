import urllib

import requests

import json

from validate_jwt import validate_eve_jwt

from functools import reduce

BASE_ESI_URL = "https://esi.evetech.net/"
ESI_VERSION = "latest/"

def print_auth_url(client_id, code_challange):
    base_auth_url = "https://login.eveonline.com/v2/oauth/authorize/"
    params = {
        "response_type": "code",
        "redirect_uri": "https://localhost/callback/",
        "client_id": client_id,
        "scope": "esi-ui.write_waypoint.v1",
        "state": "unique-state"        # change this later
    } 

    if code_challange:
        params.update({
            "code_challange": code_challange,
            "code_challange_method": "S256"
        })

    string_params = urllib.parse.urlencode(params)
    full_auth_url = f"{base_auth_url}?{string_params}"

    print("\nOpen the following link in your browser:\n\n{}\n\n Once you "
          "have logged in as a character you will get redirected to "
          "https://localhost/callback/.".format(full_auth_url))

def send_token_request(form_values, add_headers={}, verbose=False):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.eveonline.com",
    }
    if add_headers:
        headers.update(add_headers)

    res = requests.post(
        "https://login.eveonline.com/v2/oauth/token",
        data=form_values,
        headers=headers,
    )

    if verbose:
        print("Request sent to URL {} with headers {} and form values: "
            "{}\n".format(res.url, headers, form_values))
    res.raise_for_status()
    return res

def handle_sso_token_response(sso_response, verbose=True):
    if sso_response.status_code == 200:
        data = sso_response.json()
        access_token = data["access_token"]

        if verbose:
            print("\nVerifying access token JWT...")

        jwt = validate_eve_jwt(access_token)
        character_id = jwt["sub"].split(":")[2]
        character_name = jwt["name"]

        with open(f"characters/{character_id}", 'w') as f:
            data_to_save = {
                "access_token": data['access_token'],
                "refresh_token": data['refresh_token'],
                "character_id": character_id,
                "character_name": character_name          
            }
            f.write(json.dumps(data_to_save))

        if verbose:
            print(f"Success! A new access file was created for character {character_name} [ID: {character_id}]")

        return access_token

        # blueprint_path = ("https://esi.evetech.net/latest/characters/{}/"
        #                  "blueprints/".format(character_id))

        # print("\nSuccess! Here is the payload received from the EVE SSO: {}"
        #       "\nYou can use the access_token to make an authenticated "
        #       "request to {}".format(data, blueprint_path))

        # input("\nPress any key to have this program make the request for you:")

        # headers = {
        #     "Authorization": "Bearer {}".format(access_token)
        # }

        # res = requests.get(blueprint_path, headers=headers)
        # print("\nMade request to {} with headers: "
        #       "{}".format(blueprint_path, res.request.headers))
        # res.raise_for_status()

        # data = res.json()
        # print("\n{} has {} blueprints".format(character_name, len(data)))
    else:
        print("\nSomething went wrong! Re read the comment at the top of this "
              "file and make sure you completed all the prerequisites then "
              "try again. Here's some debug info to help you out:")
        print("\nSent request with url: {} \nbody: {} \nheaders: {}".format(
            sso_response.request.url,
            sso_response.request.body,
            sso_response.request.headers
        ))
        print("\nSSO response code is: {}".format(sso_response.status_code))
        print("\nSSO response JSON is: {}".format(sso_response.json()))

def get_access_token(client_id, refresh_token, scopes={}, verbose=True):
    form_values = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }

    res = send_token_request(form_values, scopes)

    access_token = handle_sso_token_response(res, verbose)

    return access_token

def send_waypoint(access_token, waypoint, custom_params={}):
    base_url = "ui/autopilot/waypoint/"

    params = {
        "add_to_beginning": "false",
        "clear_other_waypoints": "false",
        "destination_id": waypoint
    }

    if custom_params:
        params.update(custom_params)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    string_params = urllib.parse.urlencode(params)
    full_url = f"{reduce(urllib.parse.urljoin, [BASE_ESI_URL, ESI_VERSION, base_url])}?{string_params}"

    res = requests.post(
        full_url,
        headers=headers
    )
    res.raise_for_status()

    return res

if __name__ == "__main__":
    import os
    client_id = os.environ['CLIENT_ID']
    access_token = get_access_token(client_id, input("Refresh token: "))
    print(send_waypoint(access_token, "30045351"))