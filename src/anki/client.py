import json

import requests

from config import ANKI_URL, KEY


class AnkiClient:
    def __init__(self):
        self.url = ANKI_URL
        self.key = KEY

    def _invoke(self, action: dict, **param):
        return requests.post(
            url=self.url,
            data=json.dumps(
                obj={"action": action, "version": 6, "params": param, "key": self.key}
            ),
        ).json()

    def get_all_cards(self):
        query = "deck:*"
        card_ids = self._invoke(action="findCards", query=query)["result"]
        notes = self._invoke(action="cardsInfo", cards=card_ids)["result"]
        return [(note["note"], note["question"], note["answer"]) for note in notes]

    def update_note_answer(self, note_id: str, new_answer: str):
        return self._invoke(
            action="updateNoteFields",
            note={"id": note_id, "fields": {"Back": new_answer}},
        )
