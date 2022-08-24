#
# usage decode-signed-jwks.py entity-statement.jwt signed-jwks.jwt
#

import sys
from jwcrypto import jwt, jwk
from jwcrypto.common import base64url_decode
import json
from datetime import datetime

# read entity statement from file
with open(sys.argv[1], "r", encoding="utf-8-sig") as fp:
    entity_statement = fp.read().strip()

# decode entity statement jwt
c = entity_statement.split('.')
if len(c) != 3:
    raise Exception("Entity statement: Invalid JWS")

# read entity statement claims
body = json.loads(base64url_decode(c[1]))

# read jwks embedded in entity statement
entity_statement_jwks = jwk.JWKSet.from_json(json.dumps(body["jwks"]))

# validate self-signed entity statement signature
body = json.loads(jwt.JWT(key=entity_statement_jwks, jwt=entity_statement).claims)

# validate claims
iss = body["iss"]
if iss != body["sub"]:
    raise Exception("Entity statement: Invalid subject")
exp = datetime.fromtimestamp(body["exp"])
if datetime.today() > exp:
    raise Exception("Entity statement: Expired")

# read signed_jwks_uri
signed_jwks_uri = body["metadata"]["openid_provider"]["signed_jwks_uri"]

# TODO: fetch signed jwks from signed_jwks_uri

# FIXME: read signed jwks from file
with open(sys.argv[2], "r", encoding="utf-8-sig") as fp:
    signed_jwks = fp.read().strip()

# validate signed jwks signature
body = json.loads(jwt.JWT(key=entity_statement_jwks, jwt=signed_jwks).claims)

# validate signed jwks claims
if iss != body["iss"]:
    raise Exception("Signed JWKS: Invalid issuer")
if iss != body["sub"]:
    raise Exception("Signed JWKS: Invalid subject")

# read jwks
jwks = jwk.JWKSet.from_json(json.dumps({"keys": body["keys"]}))

print(jwks.export())
