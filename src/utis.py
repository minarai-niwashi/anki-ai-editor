import difflib
import os
import platform
import tkinter as tk
from tkinter import scrolledtext, ttk


class DiffViewer:
    def __init__(self):
        self.use_gui = not self._is_wsl()

    def _is_wsl(self) -> bool:
        return (
            "WSL_DISTRO_NAME" in os.environ
            or "microsoft" in platform.uname().release.lower()
        )

    def display_diff(self, original: str, revised: str) -> str:
        diff = difflib.ndiff(a=original.split(), b=revised.split())
        return "\n".join(diff)

    def show_cli(self, question: str, original: str, revised: str) -> bool:
        print(f"質問: {question}")
        print("--- 差分 ---")
        print(self.display_diff(original=original, revised=revised))
        ans = input("更新しますか？ (y/n): ").strip().lower()
        return ans == "y"

    def show_gui(self, question: str, original: str, revised: str):
        if not self.use_gui:
            return self.show_cli(question=question, original=original, revised=revised)
        root = tk.Tk()
        root.title(string="差分プレビュー")
        root.geometry(newGeometry="900x600")
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
        diff_text.insert(
            index=tk.END, chars=self.display_diff(original=original, revised=revised)
        )
        diff_text.config(state=tk.DISABLED)
        diff_text.pack(side="left", fill="both", expand=True)

        button_frame = tk.Frame(master=root)
        button_frame.pack(pady=15)

        def on_confirm():
            root.confirm_result = True
            root.destroy()

        def on_cancel():
            root.confirm_result = False
            root.destroy()

        ttk.Button(master=button_frame, text="✅ 更新する", command=on_confirm).grid(
            row=0, column=0, padx=20
        )
        ttk.Button(master=button_frame, text="⏭️ スキップ", command=on_cancel).grid(
            row=0, column=1, padx=20
        )

        root.confirm_result = False
        root.mainloop()

        return root.confirm_result
