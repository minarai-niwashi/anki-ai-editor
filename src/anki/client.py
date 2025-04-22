import json
import re
from html.parser import HTMLParser

import requests

from config import ANKI_URL, KEY


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data: str):
        self.fed.append(data)

    def get_data(self):
        return "".join(self.fed)


def strip_html(html: str) -> str:
    html = re.sub(
        pattern=r"<(style|script).*?>.*?</\1>", repl="", string=html, flags=re.DOTALL
    )
    s = HTMLStripper()
    s.feed(data=html)
    return s.get_data().strip()


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
        cards = []
        for note in notes:
            note_id = note["note"]
            question = strip_html(html=note["question"])
            answer = strip_html(html=note["answer"])
            categoty = note["deckName"]
            cards.append(
                {
                    "note_id": note_id,
                    "question": question,
                    "answer": answer,
                    "category": categoty,
                }
            )
        return cards

    def update_note_answer(self, note_id: str, new_answer: str):
        return self._invoke(
            action="updateNoteFields",
            note={"id": note_id, "fields": {"Back": new_answer}},
        )
