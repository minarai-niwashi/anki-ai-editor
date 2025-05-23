import os
import secrets
from difflib import HtmlDiff
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from anki.client import AnkiClient
from card_editor.generator import CardEditor

a = Flask(__name__)
a.secret_key = os.getenv("FLASK_SECRET_KEY", default=secrets.token_urlsafe(16))

anki = AnkiClient()
editor = CardEditor()
html_diff = HtmlDiff(tabsize=4, wrapcolumn=80)

PAGE_SIZE = 10
TEMPLATES_PATH = Path(__file__).parent / "templates"


@a.route("/")
def index():
    """デッキ一覧を表示"""
    decks = anki.get_all_decks()
    return render_template("index.html", decks=decks)


@a.route("/deck/<deck_name>")
def deck(deck_name):
    """選択されたデッキのカード一覧をページング表示"""
    page = int(request.args.get("page", 1))
    offset = (page - 1) * PAGE_SIZE

    cards = anki.get_cards_by_deck(deck_name)
    page_cards = cards[offset : offset + PAGE_SIZE]

    total_pages = (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE

    return render_template(
        "deck.html",
        deck_name=deck_name,
        cards=page_cards,
        page=page,
        total_pages=total_pages,
    )


@a.route("/card/<int:note_id>", methods=["GET", "POST"])
def card_view(note_id: int):
    """カード個別ページ：差分プレビュー & 編集"""
    from flask import get_flashed_messages

    # 参照デッキ名をクエリで渡す
    deck_name = request.args.get("deck")
    redirect_target = url_for("deck", deck_name=deck_name)

    if request.method == "GET":
        get_flashed_messages()

    # fetch note info
    info = anki._invoke("notesInfo", notes=[note_id])[0]
    question_html = info["fields"]["表面"]["value"]
    answer_html = info["fields"]["裏面"]["value"]

    # HTML タグを除去
    from anki.client import strip_html

    question = strip_html(question_html)
    original_answer = strip_html(answer_html)

    # edited タグの有無で再推敲ボタン制御
    already_edited = "edited" in info.get("tags", [])

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update":
            new_answer = request.form.get("answer", "").strip()
            if new_answer and new_answer != original_answer:
                anki.update_note_answer(note_id, new_answer)
                anki.add_ai_tag_to_note(note_id, tag="edited")
                flash("カードを更新しました ✅", "success")
            else:
                flash("変更がないため更新しませんでした", "info")
            return redirect(redirect_target)

        if action == "refine":
            refined = editor.edit(
                category=deck_name, question=question, answer=original_answer
            )
            diff_html = html_diff.make_table(
                original_answer.split(),
                refined.split(),
                fromdesc="Original",
                todesc="Refined",
            )
            return render_template(
                "card.html",
                note_id=note_id,
                deck_name=deck_name,
                question=question,
                original=original_answer,
                answer=refined,
                diff_html=diff_html,
                already_edited=already_edited,
            )

    diff_html = ""  # 初回は差分なし
    return render_template(
        "card.html",
        note_id=note_id,
        deck_name=deck_name,
        question=question,
        original=original_answer,
        answer=original_answer,
        diff_html=diff_html,
        already_edited=already_edited,
    )


if __name__ == "__main__":
    a.run(debug=True, port=5050)
