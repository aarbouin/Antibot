import logging

import jwt
from bottle import request
from jwt import InvalidTokenError
from pyckson import parse
from pymongo.database import Database

from antibot.addons.descriptors import AddOnDescriptor
from antibot.constants import ADDON_INSTALLATIONS_DB
from antibot.storage import Storage
from pynject import pynject


class AddOnInstallation:
    def __init__(self, capabilities_url: str, oauth_id: str, oauth_secret: str, group_id: str, room_id: str):
        self.capabilities_url = capabilities_url
        self.oauth_id = oauth_id
        self.oauth_secret = oauth_secret
        self.group_id = group_id
        self.room_id = room_id


@pynject
class AuthChecker:
    def __init__(self, db: Database):
        self.storage = Storage(ADDON_INSTALLATIONS_DB, db)

    def check_auth(self, addon: AddOnDescriptor):
        jwt_str = request.query.signed_request

        try:
            jwt_data = jwt.decode(jwt_str, verify=False)
        except InvalidTokenError:
            return False

        room_id = jwt_data['context']['room_id']
        data = self.storage.get(addon.db_key(room_id))
        if data is None:
            logging.error('could not find auth data for {}'.format(addon.db_key(room_id)))
            return False

        installation = parse(AddOnInstallation, data)

        try:
            jwt.decode(jwt_str, key=installation.oauth_secret)
            return True
        except InvalidTokenError:
            return False
