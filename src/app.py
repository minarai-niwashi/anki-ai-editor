from anki.client import AnkiClient
from card_editor.generator import CardEditor
from utis import DiffViewer


class App:
    def __init__(self):
        self.anki = AnkiClient()
        self.viewer = DiffViewer()
        self.editor = CardEditor()

    def run(self):
        deck_names = self.anki.get_all_decks()
        selected_deck = self.viewer.select_deck(deck_names=deck_names)
        print("Ankiからカードを取得中...")
        cards = self.anki.get_cards_by_deck(deck_name=selected_deck)
        for card in cards:
            category = card["category"]
            question = card["question"]
            answer = card["answer"]
            if self.anki.has_tag(note_id=card["note_id"], tag="edited"):
                if not self.viewer.confirm_resubmit(question=question, answer=answer):
                    print("-> スキップ")
                    continue

            revised = self.editor.edit(
                category=category, question=question, answer=answer
            )

            updated = self.viewer.show_gui(
                question=question, original=answer, revised=revised
            )
            if updated is not None:
                self.anki.update_note_answer(
                    note_id=card["note_id"], new_answer=updated
                )
                self.anki.add_ai_tag_to_note(note_id=card["note_id"], tag="edited")
                print("-> 更新 & タグを追加しました")

            else:
                print("-> スキップ")
