"""
Axion Update Manager
Editor elegante com edição e reordenação de changelog
"""

import os
import sys
import json

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QComboBox, QFrame,
    QMessageBox, QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(BASE_DIR)

CHANGELOG_PATH = os.path.join(BASE_DIR, "changelog.json")
VERSION_PATH = os.path.join(BASE_DIR, "version.json")

PREFIXOS = {
    "Adicionar": "[ + ] Adicionado",
    "Remover": "[ - ] Removido",
    "Correção Bug": "[ * ] Corrigido Bug",
    "Desativar": "[ ! ] Desativado temporariamente"
}

# ================= UTILS =================

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================= MAIN WINDOW =================

class EditorWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Axion Update Manager")
        self.setFixedSize(680, 580)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Removed: self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._drag_pos = None
        self.current_page = "changelog"
        
        # Load data
        self.dados_changelog = load_json(CHANGELOG_PATH, {"changes": []})
        self.dados_version = load_json(VERSION_PATH, {"game_version": "", "axion_release": ""})
        
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: #1a1a1a;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(container)
        
        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # Titlebar
        root.addWidget(self.create_titlebar())
        
        # Header
        root.addWidget(self.create_header())
        
        # Tabs
        root.addWidget(self.create_tabs())
        
        # Content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(18, 18, 18, 18)
        self.content_layout.setSpacing(0)
        
        root.addWidget(self.content_widget, 1)
        
        # Show initial page
        self.show_page("changelog")
    
    def create_titlebar(self):
        titlebar = QWidget()
        titlebar.setFixedHeight(32)
        titlebar.setStyleSheet("""
            background: #0a0a0a;
            border-bottom: 1px solid rgba(255, 255, 255, 15);
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        
        layout = QHBoxLayout(titlebar)
        layout.setContentsMargins(12, 0, 12, 0)
        
        title = QLabel("AXION UPDATE MANAGER")
        title.setFont(QFont("Consolas", 9))
        title.setStyleSheet("color: #aaaaaa; letter-spacing: 1px; background: transparent; border: none;")
        layout.addWidget(title)
        layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFont(QFont("Segoe UI", 12))
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton { 
                color: #cc3333; 
                background: transparent;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover { 
                color: #ff5555; 
                background: rgba(255, 50, 50, 30); 
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return titlebar
    
    def create_header(self):
        header = QWidget()
        header.setStyleSheet("background: transparent; border-bottom: 1px solid rgba(255, 255, 255, 13);")
        layout = QVBoxLayout(header)
        layout.setContentsMargins(22, 18, 22, 12)
        
        title = QLabel("Axion Update Manager")
        title.setFont(QFont("Segoe UI", 18, QFont.DemiBold))
        title.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        layout.addWidget(title)
        
        return header
    
    def create_tabs(self):
        tabs_widget = QWidget()
        tabs_widget.setStyleSheet("background: rgba(0, 0, 0, 77); border-bottom: 1px solid rgba(255, 255, 255, 13);")
        
        layout = QHBoxLayout(tabs_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.tab_changelog = self.create_tab("Changelog", "changelog")
        self.tab_version = self.create_tab("Versão", "version")
        
        layout.addWidget(self.tab_changelog)
        layout.addWidget(self.tab_version)
        layout.addStretch()
        
        return tabs_widget
    
    def create_tab(self, text, page_id):
        tab = QLabel(text)
        tab.setFont(QFont("Segoe UI", 11))
        tab.setCursor(Qt.PointingHandCursor)
        tab.setFixedHeight(36)
        tab.setStyleSheet("""
            QLabel {
                color: #999999;
                background: transparent;
                border-bottom: 2px solid transparent;
                padding: 0 20px;
            }
        """)
        tab.mousePressEvent = lambda e: self.show_page(page_id)
        tab.page_id = page_id
        return tab
    
    def show_page(self, page_id):
        self.current_page = page_id
        
        # Update tabs
        for tab in [self.tab_changelog, self.tab_version]:
            if tab.page_id == page_id:
                tab.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        background: rgba(120, 40, 220, 20);
                        border-bottom: 2px solid #7828dc;
                        padding: 0 20px;
                    }
                """)
            else:
                tab.setStyleSheet("""
                    QLabel {
                        color: #999999;
                        background: transparent;
                        border-bottom: 2px solid transparent;
                        padding: 0 20px;
                    }
                """)
        
        # Clear content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Load page
        if page_id == "changelog":
            self.load_changelog_page()
        elif page_id == "version":
            self.load_version_page()
    
    def load_changelog_page(self):
        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #141414;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 6px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(16)
        
        # Input section
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(list(PREFIXOS.keys()))
        self.combo_tipo.setFixedWidth(140)
        self.combo_tipo.setFont(QFont("Segoe UI", 11))
        self.combo_tipo.setStyleSheet("""
            QComboBox {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 26);
                border-radius: 4px;
                padding: 8px 11px;
                color: #cccccc;
            }
            QComboBox:focus {
                border-color: #7828dc;
                background: rgba(0, 0, 0, 204);
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #1a1a1a;
                border: 1px solid rgba(255, 255, 255, 26);
                selection-background-color: #7828dc;
                color: #cccccc;
            }
        """)
        input_row.addWidget(self.combo_tipo)
        
        self.entry_texto = QLineEdit()
        self.entry_texto.setPlaceholderText("Digite a descrição...")
        self.entry_texto.setFont(QFont("Segoe UI", 11))
        self.entry_texto.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 26);
                border-radius: 4px;
                padding: 8px 11px;
                color: #cccccc;
            }
            QLineEdit:focus {
                border-color: #7828dc;
                background: rgba(0, 0, 0, 204);
            }
        """)
        input_row.addWidget(self.entry_texto, 1)
        
        btn_add = QPushButton("Adicionar")
        btn_add.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background: rgba(120, 40, 220, 128);
                border: 1px solid rgba(150, 50, 255, 153);
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background: rgba(130, 50, 220, 179);
                border-color: rgba(180, 80, 255, 230);
            }
            QPushButton:pressed {
                background: rgba(110, 30, 200, 153);
            }
        """)
        btn_add.clicked.connect(self.adicionar_item)
        input_row.addWidget(btn_add)
        
        card_layout.addLayout(input_row)
        
        # List
        self.listbox = QListWidget()
        self.listbox.setFont(QFont("Consolas", 11))
        self.listbox.setDragDropMode(QListWidget.InternalMove)
        self.listbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listbox.setWordWrap(True)
        self.listbox.setStyleSheet("""
            QListWidget {
                background: #0f0f0f;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 4px;
                padding: 8px;
                color: #cccccc;
            }
            QListWidget::item {
                background: rgba(255, 255, 255, 8);
                border-left: 2px solid #7828dc;
                border-radius: 3px;
                padding: 10px 12px 10px 8px;
                margin-bottom: 5px;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 15);
            }
            QListWidget::item:selected {
                background: rgba(120, 40, 220, 60);
                border-left-color: #a855f7;
                color: #ffffff;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 80);
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(120, 40, 220, 150);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(120, 40, 220, 200);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.listbox.setMaximumHeight(280)
        card_layout.addWidget(self.listbox)
        
        # Update list
        self.atualizar_lista()
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255, 255, 255, 13); border: none;")
        card_layout.addWidget(sep)
        
        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(8)
        
        # Left actions
        left_actions = QHBoxLayout()
        left_actions.setSpacing(8)
        
        btn_edit = QPushButton("✎")
        btn_edit.setFont(QFont("Segoe UI", 13))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setToolTip("Editar selecionado")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 38);
                border-radius: 4px;
                color: #999999;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 8);
                border-color: rgba(255, 255, 255, 64);
                color: #cccccc;
            }
        """)
        btn_edit.clicked.connect(self.editar_item)
        left_actions.addWidget(btn_edit)
        
        btn_up = QPushButton("↑")
        btn_up.setFont(QFont("Segoe UI", 14))
        btn_up.setFixedSize(32, 32)
        btn_up.setToolTip("Mover para cima")
        btn_up.setCursor(Qt.PointingHandCursor)
        btn_up.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 38);
                border-radius: 4px;
                color: #999999;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 8);
                border-color: rgba(255, 255, 255, 64);
                color: #cccccc;
            }
        """)
        btn_up.clicked.connect(self.mover_cima)
        left_actions.addWidget(btn_up)
        
        btn_down = QPushButton("↓")
        btn_down.setFont(QFont("Segoe UI", 14))
        btn_down.setFixedSize(32, 32)
        btn_down.setToolTip("Mover para baixo")
        btn_down.setCursor(Qt.PointingHandCursor)
        btn_down.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 38);
                border-radius: 4px;
                color: #999999;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 8);
                border-color: rgba(255, 255, 255, 64);
                color: #cccccc;
            }
        """)
        btn_down.clicked.connect(self.mover_baixo)
        left_actions.addWidget(btn_down)
        
        btn_remove = QPushButton("Remover")
        btn_remove.setFont(QFont("Segoe UI", 11))
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 38);
                border-radius: 4px;
                padding: 6px 14px;
                color: #999999;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 8);
                border-color: rgba(255, 255, 255, 64);
                color: #cccccc;
            }
        """)
        btn_remove.clicked.connect(self.remover_item)
        left_actions.addWidget(btn_remove)
        
        actions.addLayout(left_actions)
        actions.addStretch()
        
        # Right action
        btn_save = QPushButton("Salvar Changelog")
        btn_save.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background: rgba(120, 40, 220, 128);
                border: 1px solid rgba(150, 50, 255, 153);
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background: rgba(130, 50, 220, 179);
                border-color: rgba(180, 80, 255, 230);
            }
        """)
        btn_save.clicked.connect(self.salvar_changelog)
        actions.addWidget(btn_save)
        
        card_layout.addLayout(actions)
        
        self.content_layout.addWidget(card)
        self.content_layout.addStretch()
    
    def load_version_page(self):
        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #141414;
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 6px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(18)
        
        # Game version
        game_label = QLabel("VERSÃO DO JOGO")
        game_label.setFont(QFont("Segoe UI", 10))
        game_label.setStyleSheet("color: #888888; background: transparent; border: none;")
        card_layout.addWidget(game_label)
        
        self.entry_game = QLineEdit()
        self.entry_game.setText(self.dados_version.get("game_version", ""))
        self.entry_game.setFont(QFont("Segoe UI", 12))
        self.entry_game.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 26);
                border-radius: 4px;
                padding: 10px 12px;
                color: #cccccc;
            }
            QLineEdit:focus {
                border-color: #7828dc;
                background: rgba(0, 0, 0, 204);
            }
        """)
        card_layout.addWidget(self.entry_game)
        
        # Axion version
        axion_label = QLabel("RELEASE DO AXION")
        axion_label.setFont(QFont("Segoe UI", 10))
        axion_label.setStyleSheet("color: #888888; background: transparent; border: none;")
        card_layout.addWidget(axion_label)
        
        self.entry_axion = QLineEdit()
        self.entry_axion.setText(self.dados_version.get("axion_release", ""))
        self.entry_axion.setFont(QFont("Segoe UI", 12))
        self.entry_axion.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 26);
                border-radius: 4px;
                padding: 10px 12px;
                color: #cccccc;
            }
            QLineEdit:focus {
                border-color: #7828dc;
                background: rgba(0, 0, 0, 204);
            }
        """)
        card_layout.addWidget(self.entry_axion)
        
        # Save button
        btn_save = QPushButton("Salvar Version.json")
        btn_save.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background: rgba(120, 40, 220, 128);
                border: 1px solid rgba(150, 50, 255, 153);
                border-radius: 4px;
                padding: 11px 20px;
                color: #ffffff;
            }
            QPushButton:hover {
                background: rgba(130, 50, 220, 179);
                border-color: rgba(180, 80, 255, 230);
            }
        """)
        btn_save.clicked.connect(self.salvar_version)
        card_layout.addWidget(btn_save)
        
        self.content_layout.addWidget(card)
        self.content_layout.addStretch()
    
    # ===== METHODS =====
    
    def adicionar_item(self):
        texto = self.entry_texto.text().strip()
        if not texto:
            QMessageBox.warning(self, "Aviso", "Digite a descrição da alteração.")
            return
        
        frase = f"{PREFIXOS[self.combo_tipo.currentText()]} {texto}"
        self.dados_changelog["changes"].append(frase)
        self.atualizar_lista()
        self.entry_texto.clear()
    
    def atualizar_lista(self):
        self.listbox.clear()
        for item in self.dados_changelog["changes"]:
            list_item = QListWidgetItem(f"⋮⋮  {item}")
            self.listbox.addItem(list_item)
    
    def editar_item(self):
        current_row = self.listbox.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um item para editar.")
            return
        
        texto_atual = self.dados_changelog["changes"][current_row]
        
        # Remove prefixo para edição
        prefixo_encontrado = ""
        texto_limpo = texto_atual
        for key, prefixo in PREFIXOS.items():
            if texto_atual.startswith(prefixo):
                prefixo_encontrado = key
                texto_limpo = texto_atual[len(prefixo):].strip()
                break
        
        texto_novo, ok = QInputDialog.getText(
            self, 
            "Editar Item",
            "Descrição:",
            text=texto_limpo
        )
        
        if ok and texto_novo.strip():
            # Reconstrói com o prefixo original
            if prefixo_encontrado:
                novo_texto = f"{PREFIXOS[prefixo_encontrado]} {texto_novo.strip()}"
            else:
                novo_texto = texto_novo.strip()
            
            self.dados_changelog["changes"][current_row] = novo_texto
            self.atualizar_lista()
            self.listbox.setCurrentRow(current_row)
    
    def mover_cima(self):
        current_row = self.listbox.currentRow()
        if current_row <= 0:
            return
        
        # Swap
        self.dados_changelog["changes"][current_row], self.dados_changelog["changes"][current_row - 1] = \
            self.dados_changelog["changes"][current_row - 1], self.dados_changelog["changes"][current_row]
        
        self.atualizar_lista()
        self.listbox.setCurrentRow(current_row - 1)
    
    def mover_baixo(self):
        current_row = self.listbox.currentRow()
        if current_row < 0 or current_row >= len(self.dados_changelog["changes"]) - 1:
            return
        
        # Swap
        self.dados_changelog["changes"][current_row], self.dados_changelog["changes"][current_row + 1] = \
            self.dados_changelog["changes"][current_row + 1], self.dados_changelog["changes"][current_row]
        
        self.atualizar_lista()
        self.listbox.setCurrentRow(current_row + 1)
    
    def remover_item(self):
        current_row = self.listbox.currentRow()
        if current_row >= 0:
            del self.dados_changelog["changes"][current_row]
            self.atualizar_lista()
    
    def salvar_changelog(self):
        # Atualiza ordem baseado no drag & drop
        nova_ordem = []
        for i in range(self.listbox.count()):
            texto = self.listbox.item(i).text()
            # Remove o handle "⋮⋮  "
            texto_limpo = texto.replace("⋮⋮  ", "")
            nova_ordem.append(texto_limpo)
        
        self.dados_changelog["changes"] = nova_ordem
        save_json(CHANGELOG_PATH, self.dados_changelog)
        QMessageBox.information(self, "Sucesso", "changelog.json atualizado")
    
    def salvar_version(self):
        self.dados_version["game_version"] = self.entry_game.text().strip()
        self.dados_version["axion_release"] = self.entry_axion.text().strip()
        save_json(VERSION_PATH, self.dados_version)
        QMessageBox.information(self, "Sucesso", "version.json atualizado")
    
    # ===== DRAG =====
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(self.pos() + event.globalPos() - self._drag_pos)
            self._drag_pos = event.globalPos()

# ================= MAIN =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    sys.exit(app.exec_())
