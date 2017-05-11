import logging

from pynject import pynject, singleton

from antibot.domain.room import Room
from antibot.flow.api import HipchatApi


@pynject
@singleton
class RoomsRepository:
    def __init__(self, api: HipchatApi):
        self.api = api
        logging.getLogger(__name__).info('Listing hipchat rooms from api')
        self.rooms = list(api.list_rooms())
        self.rooms_by_jid = {room.jid: room for room in self.rooms}

    def by_jid(self, jid: str) -> Room:
        return self.rooms_by_jid.get(jid)

    def by_id(self, id: int) -> Room:
        for room in self.rooms:
            if room.api_id == id:
                return room

    def by_name(self, name: str) -> Room:
        for room in self.rooms:
            if room.name.lower() == name.lower():
                return room

    def find(self, name_or_jid) -> Room:
        room = self.by_jid(name_or_jid)
        if room is None:
            return self.by_name(name_or_jid)
        return room
