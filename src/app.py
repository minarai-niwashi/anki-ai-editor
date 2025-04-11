from anki.client import AnkiClient
from utis import DiffViewer


class App:
    def __init__(self):
        self.anki = AnkiClient()
        self.viewer = DiffViewer()

    def run(self):
        print("Ankiからカードを取得中...")
        cards = self.anki.get_all_cards()
        for card in cards:
            question = card["question"]
            answer = card["answer"]
            revised = "revisedanswer"  # Placeholder for the revised answer

            if self.viewer.show_gui(
                question=question, original=answer, revised=revised
            ):
                print("-> 更新しました")

            else:
                print("-> スキップ")
