import requests


def _get(self, endpoint: str, components: str):
    if self.token is None or self.token_is_expired:
        self.refresh_token()
    response = requests.get(
        self.BASE_URL + endpoint,
        params={"components": components},
        headers=self.headers,
    )
    if response.status_code != 200:
        print(response.content)
        return
    return response.json()


def get_vendors(self):
    r = self._get(
        f"/Destiny2/{self.membershipType}/Profile/"
        "{self.destinyMembershipId}/Character/{self.characterId}/Vendors/",
        components="400,401,402",
    )
    return r


def get_vendor(self, vendor_hash):
    return self._get(
        f"/Destiny2/{self.membershipType}/Profile/"
        "{self.destinyMembershipId}/Character/{self.characterId}/Vendors/{vendor_hash}/",
        components="402",
    )
