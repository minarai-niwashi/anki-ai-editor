import json
import re
from html.parser import HTMLParser

import requests

from config import ANKI_URL, KEY
from utis import check_response_ok


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
        response = requests.post(
            url=self.url,
            data=json.dumps(
                obj={"action": action, "version": 6, "params": param, "key": self.key}
            ),
        )
        return check_response_ok(response=response)

    def get_all_cards(self):
        query = "deck:*"
        card_ids = self._invoke(action="findCards", query=query)
        notes = self._invoke(action="cardsInfo", cards=card_ids)
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
            note={"id": note_id, "fields": {"裏面": new_answer}},
        )

    def add_ai_tag_to_note(self, note_id: int, tag: str = "edited"):
        return self._invoke(action="addTags", notes=[note_id], tags=tag)

    def has_tag(self, note_id: int, tag: str = "edited"):
        result = self._invoke(action="notesInfo", notes=[note_id])
        if result and "tags" in result[0]:
            return tag in result[0]["tags"]
        return False

    def get_all_decks(self) -> list[str]:
        return self._invoke(action="deckNames")

    def get_cards_by_deck(self, deck_name: str) -> list[dict]:
        card_ids = self._invoke(action="findCards", query=f"deck:{deck_name}")
        notes = self._invoke(action="cardsInfo", cards=card_ids)
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
