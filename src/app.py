from anki.client import AnkiClient
from card_editor.generator import CardEditor
from utis import DiffViewer


class App:
    def __init__(self):
        self.anki = AnkiClient()
        self.viewer = DiffViewer()
        self.editor = CardEditor()

    def run(self):
        print("Ankiからカードを取得中...")
        cards = self.anki.get_all_cards()
        for card in cards:
            category = card["category"]
            question = card["question"]
            answer = card["answer"]
            revised = self.editor.edit(
                category=category, question=question, answer=answer
            )

            if self.viewer.show_gui(
                question=question, original=answer, revised=revised
            ):
                print("-> 更新しました")

            else:
                print("-> スキップ")
