import os
import sys

if not (BUNGIE_TOKEN := os.getenv("BUNGIE_TOKEN", default=False)):
    # \033[foo;bar; blah makes the ERROR text red
    sys.exit(
        "\033[38;2;255;0;0mERROR:\033[0m BUNGIE_TOKEN env variable not supplied, quitting..."
    )
if not (BUNGIE_CLIENT_ID := os.getenv("BUNGIE_CLIENT_ID", default=False)):
    # \033[foo;bar; blah makes the ERROR text red
    sys.exit(
        "\033[38;2;255;0;0mERROR:\033[0m BUNGIE_CLIENT_ID env variable not supplied, quitting..."
    )

if not (BUNGIE_CLIENT_SECRET := os.getenv("BUNGIE_CLIENT_SECRET", default=False)):
    # \033[foo;bar; blah makes the ERROR text red
    sys.exit(
        "\033[38;2;255;0;0mERROR:\033[0m BUNGIE_CLIENT_SECRET env variable not supplied, quitting..."
    )

VENDOR_IDS = {"Banshee-44": 4161623890, "Xur": 2190858386, "Spider": 8639403560}
BASE_URL = "https://www.bungie.net/platform"
HEADERS = {"X-API-Key": BUNGIE_TOKEN}


class AuthenticationError(Exception):
    ...


class StateError(Exception):
    ...


# --------- Discord Commands ----------

# Get MembershipID
"""
displayName = "KGB.33"
memId = requests.get(
    BASE_URL + f"/Destiny2/SearchDestinyPlayer/{membershipType}/{displayName}/",
    headers=HEADERS,
).json()
print(memId)
"""

# Get Character ID
"""
charId = requests.get(
    BASE_URL
    + f"/Destiny2/{membershipType}/Profile/{destinyMembershipId}/?components=characters",
    headers=HEADERS,
)
print(charId)
print(charId.json()['Response'])
"""

# api = BungieAPI(BUNGIE_CLIENT_ID, BUNGIE_CLIENT_SECRET)
# print(api.get_vendors())
