import difflib
import os
import platform
import subprocess
import tempfile
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import requests


class DiffViewer:
    def __init__(self):
        self.use_gui = not self._is_wsl()

    def _is_wsl(self) -> bool:
        return (
            "WSL_DISTRO_NAME" in os.environ
            or "microsoft" in platform.uname().release.lower()
        )

    def display_diff(self, original: str, revised: str) -> str:
        diff = list(difflib.ndiff(a=[original], b=[revised]))
        filtered_diff = [line for line in diff if not line.startswith("?")]
        changes = [
            line
            for line in filtered_diff
            if line.startswith("+") or line.startswith("-")
        ]
        if not changes:
            return ""
        return "\n".join(filtered_diff)

    def show_cli(self, question: str, original: str, revised: str) -> str | None:
        diff = self.display_diff(original=original, revised=revised)
        print(f"質問: {question}")
        if not diff:
            print("差分はありません。")
            return None

        print("--- 差分 ---")
        print(diff)
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w+", encoding="utf-8"
        ) as temp_file:
            temp_file.write(revised)
            temp_file.flush()
            editor = os.environ.get("EDITOR", default="vi")
            subprocess.call(args=[editor, temp_file.name])
            temp_file.seek(0)
            updated = temp_file.read().strip()
        os.unlink(path=temp_file.name)
        ans = input("更新しますか？ (y/n): ").strip().lower()
        return updated if ans == "y" else None

    def show_gui(self, question: str, original: str, revised: str) -> str | None:
        if not self.use_gui:
            return self.show_cli(question=question, original=original, revised=revised)

        diff = self.display_diff(original=original, revised=revised)
        if not diff:
            print(f"質問: {question}")
            print("差分はありません。")
            return None

        root = tk.Tk()
        root.title(string="差分プレビュー")
        root.geometry(newGeometry="900x800")
        root.resizable(width=False, height=False)

        question_label = tk.Label(
            master=root, text=f"質問: {question}", wraplength=800, justify="left"
        )
        question_label.pack(side="top", anchor="w", padx=10, pady=10)

        diff_frame = tk.Frame(master=root)
        diff_frame.pack(expand=True, fill="both", padx=10)

        diff_text = scrolledtext.ScrolledText(
            master=diff_frame, width=110, height=25, font=("Meiryo UI", 10)
        )
        diff_text.insert(index=tk.END, chars=diff)
        diff_text.config(state=tk.DISABLED)
        diff_text.pack(side="left", fill="both", expand=True)

        edit_frame = tk.LabelFrame(
            master=root, text="編集（必要に応じて修正してください）", padx=10, pady=10
        )
        edit_frame.pack(expand=True, fill="both", padx=10, pady=5)

        edit_text = scrolledtext.ScrolledText(
            master=edit_frame, width=110, height=8, font=("Meiryo UI", 10)
        )
        edit_text.insert(index="1.0", chars=revised)
        edit_text.pack(fill="both", expand=True)

        button_frame = tk.Frame(master=root)
        button_frame.pack(pady=15)

        def on_confirm():
            root.edited_text = edit_text.get(index1="1.0", index2="end-1c")
            root.destroy()

        def on_cancel():
            root.edited_text = None
            root.destroy()

        ttk.Button(master=button_frame, text="✅ 更新する", command=on_confirm).grid(
            row=0, column=0, padx=20
        )
        ttk.Button(master=button_frame, text="⏭️ スキップ", command=on_cancel).grid(
            row=0, column=1, padx=20
        )

        root.edited_text = None
        root.mainloop()

        return root.edited_text

    def confirm_resubmit(self, question: str, answer: str) -> bool:
        message = f"このカードは既にAIで推敲されています。\n\n質問: {question}\n答え: {answer}\n\n再度推敲しますか？"
        if not self.use_gui:
            print(message)
            ans = input("(y/n): ").strip().lower()
            return ans == "y"

        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            title="再推敲",
            message=message,
        )
        root.destroy()
        return result

    def select_deck(self, deck_names: list[str]) -> str:
        if not self.use_gui:
            print("デッキを選択してください：")
            for i, name in enumerate(deck_names):
                print(f"{i + 1}: {name}")
            index = int(input("番号を入力してください：")) - 1
            return deck_names[index]

        root = tk.Tk()
        root.title("デッキ選択")
        root.geometry("400x200")
        selected = tk.StringVar(root)
        selected.set(deck_names[0])

        tk.Label(root, text="使用するデッキを選んでください：").pack(pady=20)
        dropdown = ttk.OptionMenu(root, selected, deck_names[0], *deck_names)
        dropdown.pack()

        def on_confirm():
            root.selected_deck = selected.get()
            root.destroy()

        ttk.Button(root, text="OK", command=on_confirm).pack(pady=20)
        root.selected_deck = deck_names[0]
        root.mainloop()
        return root.selected_deck


def check_response_ok(response):
    if not response.ok:
        raise requests.HttpError(
            f"AnkiConnect request failed with status {response.status_code}: {response.text}"
        )
    json_response = response.json()
    if json_response["error"]:
        raise ValueError(f"AnkiConnect error: {json_response['error']}")
    return json_response["result"]
