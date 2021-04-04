import uuid
import time
import json
from dataclasses import dataclass, asdict

import requests

from src import db


from . import (
    HEADERS,
    BUNGIE_CLIENT_ID,
    BUNGIE_CLIENT_SECRET,
    StateError,
    AuthenticationError,
)


@dataclass
class BungieUser:
    """
    Defines the needed info to make API calls
    for a authorized user
    """

    membershipType: int
    destinyMembershipId: int
    characterId: int
    discord_id: int
    token: dict

    @staticmethod
    def init_from_auth_token(token, discord_id):
        headers = HEADERS.copy()
        headers.update({"Authorization": f"Bearer {token['access_token']}"})

        # Get D2 membership info
        response = requests.get(
            "https://www.bungie.net/Platform/User/GetMembershipsForCurrentUser/",
            headers=headers,
        )
        data = response.json()["Response"]
        destinyMembershipId = data["primaryMembershipId"]
        membershipType = [
            membership["membershipType"]
            for membership in data["destinyMemberships"]
            if membership["membershipId"] == destinyMembershipId
        ][0]

        # Get Character Info
        response = requests.get(
            "https://www.bungie.net/Platform/Destiny2/"
            f"{membershipType}/Profile/{destinyMembershipId}"
            "/?components=Characters",
            headers=headers,
        )
        data = response.json()
        characterId, maxLight = 0, 0
        for id_, info in data["Response"]["characters"]["data"].items():
            if info["light"] > maxLight:
                characterId = id_
                maxLight = info["light"]

        return BungieUser(
            membershipType, destinyMembershipId, characterId, discord_id, token
        )

    def save_to_db(self):
        db.set(self.discord_id, json.dumps(asdict(self)))

    @staticmethod
    def load_from_db(discord_id, r):
        BungieUser(**json.loads(r.get(discord_id).decode("utf-8")))

    @property
    def token_is_expired(self):
        return int(self.token["expires_in"]) + self.token_refreshed_time >= time.time()

    def refresh_token(self):
        if self.token is None:
            code = self._get_user_code()
            self._get_auth_token(code)
        else:
            self._renew_auth_token()

    @staticmethod
    async def _get_user_code(prompt: callable = input):
        state = str(uuid.uuid4())
        redirect_url = "https://github.com/KGB33/Discord-Bot?"
        auth_url = (
            f"https://www.bungie.net/en/oauth/authorize?"
            f"client_id={BUNGIE_CLIENT_ID}&"
            f"response_type=code&state={state}"
        )
        input_url = await prompt(
            f"Go to {auth_url}, authenticate the app, then enter the redirected URL."
        )
        input_url = input_url.removeprefix(redirect_url)
        code, returned_state = input_url.split("&")
        code = code.removeprefix("code=")
        returned_state = returned_state.removeprefix("state=")
        if state != returned_state:
            raise StateError(
                "State not consistant between request and response, please Try again"
            )
        return code

    @staticmethod
    def _get_auth_token(code):
        token = requests.post(
            "https://www.bungie.net/Platform/App/OAuth/Token/",
            headers=HEADERS,
            data={
                "client_id": BUNGIE_CLIENT_ID,
                "client_secret": BUNGIE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
            },
        )
        if token.status_code != 200:
            raise AuthenticationError(token.content)

        return token.json()

    def _renew_auth_token(self):
        token = requests.post(
            "https://www.bungie.net/Platform/App/OAuth/Token/",
            headers=self.headers,
            data={
                "client_id": BUNGIE_CLIENT_ID,
                "client_secret": BUNGIE_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": self.token["refresh_token"],
            },
        )
        if token.status_code != 200:
            raise AuthenticationError(token.content)

        self.headers.update({"Authorization": f"Bearer {token.json()['access_token']}"})
        self.token = token.json()
        self.token_refreshed_time = time.time()
