import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHANGELOG_PATH = os.path.join(BASE_DIR, "changelog.json")
VERSION_PATH = os.path.join(BASE_DIR, "version.json")

PREFIXOS = {
    "Adicionar": "[ + ] Adicionado",
    "Remover": "[ - ] Removido",
    "Correção Bug": "[ * ] Corrigido Bug",
    "Desativar": "[ ! ] Desativado temporariamente"
}


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ================== JANELA ==================

root = tk.Tk()
root.title("Axion • Update Manager")
root.geometry("900x560")
root.configure(bg="#0f1115")

style = ttk.Style()
style.theme_use("clam")

# ================== ESTILO ==================

style.configure("TFrame", background="#0f1115")
style.configure("Card.TFrame", background="#161a22", relief="flat")
style.configure("Header.TLabel", background="#0f1115", foreground="#ffffff", font=("Segoe UI", 16, "bold"))
style.configure("Label.TLabel", background="#161a22", foreground="#cfd3dc", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10), padding=8)
style.map("TButton",
          background=[("active", "#2a2f3a")],
          foreground=[("active", "#ffffff")])

style.configure("TNotebook", background="#0f1115", borderwidth=0)
style.configure("TNotebook.Tab", padding=[18, 10], background="#161a22", foreground="#cfd3dc")
style.map("TNotebook.Tab",
          background=[("selected", "#1f2430")],
          foreground=[("selected", "#ffffff")])

# ================== HEADER ==================

header = ttk.Frame(root)
header.pack(fill="x", pady=(20, 10), padx=20)

ttk.Label(header, text="Axion Update Manager", style="Header.TLabel").pack(anchor="w")

# ================== ABAS ==================

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=10)

# ======================================================
# CHANGLOG
# ======================================================

frame_changelog = ttk.Frame(notebook)
notebook.add(frame_changelog, text="Changelog")

card = ttk.Frame(frame_changelog, style="Card.TFrame")
card.pack(fill="both", expand=True, padx=10, pady=10)

dados_changelog = load_json(CHANGELOG_PATH, {"changes": []})

top = ttk.Frame(card)
top.pack(fill="x", pady=10, padx=10)

combo_tipo = ttk.Combobox(top, values=list(PREFIXOS.keys()), state="readonly", width=18)
combo_tipo.set("Adicionar")
combo_tipo.pack(side="left", padx=(0, 10))

entry_texto = ttk.Entry(top)
entry_texto.pack(side="left", fill="x", expand=True, padx=(0, 10))


def add_change():
    texto = entry_texto.get().strip()
    if not texto:
        messagebox.showwarning("Aviso", "Digite a descrição.")
        return
    frase = f"{PREFIXOS[combo_tipo.get()]} {texto}"
    dados_changelog["changes"].append(frase)
    update_list()
    entry_texto.delete(0, tk.END)


ttk.Button(top, text="Adicionar", command=add_change).pack(side="left")

list_frame = ttk.Frame(card)
list_frame.pack(fill="both", expand=True, padx=10, pady=10)

listbox = tk.Listbox(
    list_frame,
    bg="#0f1115",
    fg="#cfd3dc",
    selectbackground="#2a2f3a",
    relief="flat",
    font=("Consolas", 10)
)
listbox.pack(side="left", fill="both", expand=True)

scroll = ttk.Scrollbar(list_frame, command=listbox.yview)
scroll.pack(side="right", fill="y")
listbox.config(yscrollcommand=scroll.set)


def update_list():
    listbox.delete(0, tk.END)
    for item in dados_changelog["changes"]:
        listbox.insert(tk.END, item)


def remove_selected():
    if listbox.curselection():
        del dados_changelog["changes"][listbox.curselection()[0]]
        update_list()


bottom = ttk.Frame(card)
bottom.pack(fill="x", pady=10, padx=10)

ttk.Button(bottom, text="Remover selecionado", command=remove_selected).pack(side="left")
ttk.Button(
    bottom,
    text="Salvar Changelog",
    command=lambda: (
        save_json(CHANGELOG_PATH, dados_changelog),
        messagebox.showinfo("OK", "Changelog atualizado")
    )
).pack(side="right")

update_list()

# ======================================================
# VERSION
# ======================================================

frame_version = ttk.Frame(notebook)
notebook.add(frame_version, text="Versão")

card_v = ttk.Frame(frame_version, style="Card.TFrame")
card_v.pack(fill="both", expand=True, padx=10, pady=10)

dados_version = load_json(VERSION_PATH, {"game_version": "", "axion_release": ""})

form = ttk.Frame(card_v)
form.pack(pady=60)

ttk.Label(form, text="Versão do jogo", style="Label.TLabel").grid(row=0, column=0, sticky="e", padx=15, pady=15)
entry_game = ttk.Entry(form, width=30)
entry_game.grid(row=0, column=1)

ttk.Label(form, text="Release do Axion", style="Label.TLabel").grid(row=1, column=0, sticky="e", padx=15, pady=15)
entry_axion = ttk.Entry(form, width=30)
entry_axion.grid(row=1, column=1)

entry_game.insert(0, dados_version.get("game_version", ""))
entry_axion.insert(0, dados_version.get("axion_release", ""))


def save_version():
    dados_version["game_version"] = entry_game.get().strip()
    dados_version["axion_release"] = entry_axion.get().strip()
    save_json(VERSION_PATH, dados_version)
    messagebox.showinfo("OK", "Version.json atualizado")


ttk.Button(card_v, text="Salvar Version.json", command=save_version).pack(pady=20)

root.mainloop()
