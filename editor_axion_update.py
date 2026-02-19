"""
Axion Update Editor
Editor compacto e moderno para gerenciar changelog e versões
"""

import os
import sys
import json
import subprocess
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QComboBox, QTextEdit,
    QFrame, QMessageBox, QListWidgetItem, QScrollArea
)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(BASE_DIR)

CHANGELOG_PATH = os.path.join(BASE_DIR, "changelog.json")
VERSION_PATH = os.path.join(BASE_DIR, "version.json")
PUBLICAR_BAT = os.path.join(BASE_DIR, "publicar_update.bat")

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

# ================= LOG SIGNAL =================

class LogEmitter(QObject):
    log_signal = pyqtSignal(str)

# ================= MAIN WINDOW =================

class EditorWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Axion Update Editor")
        self.setFixedSize(750, 520)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._drag_pos = None
        self.current_page = "changelog"
        
        # Load data
        self.dados_changelog = load_json(CHANGELOG_PATH, {"changes": []})
        self.dados_version = load_json(VERSION_PATH, {"game_version": "", "axion_release": ""})
        
        # Log emitter
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)
        
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
                background: rgba(0, 0, 0, 215);
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(container)
        
        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # ===== TITLEBAR =====
        root.addWidget(self.create_titlebar())
        
        # ===== BODY =====
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        
        # Sidebar
        body.addWidget(self.create_sidebar())
        
        # Content stack
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(0)
        
        body.addWidget(self.content_widget, 1)
        
        root.addLayout(body, 1)
        
        # Show initial page
        self.show_page("changelog")
    
    def create_titlebar(self):
        titlebar = QWidget()
        titlebar.setFixedHeight(32)
        titlebar.setStyleSheet("""
            background: rgba(10, 10, 10, 248);
            border-bottom: 1px solid rgba(255, 255, 255, 15);
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        
        layout = QHBoxLayout(titlebar)
        layout.setContentsMargins(12, 0, 12, 0)
        
        title = QLabel("AXION UPDATE EDITOR")
        title.setFont(QFont("Consolas", 9))
        title.setStyleSheet("color: #aaaaaa; letter-spacing: 1px; background: transparent; border: none;")
        layout.addWidget(title)
        layout.addStretch()
        
        close_btn = QLabel("✕")
        close_btn.setFont(QFont("Segoe UI", 12))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QLabel { color: #cc3333; padding: 2px 6px; border-radius: 2px; background: transparent; border: none; }
            QLabel:hover { color: #ff5555; background: rgba(255, 50, 50, 30); }
        """)
        close_btn.mousePressEvent = lambda e: self.close()
        layout.addWidget(close_btn)
        
        return titlebar
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(140)
        sidebar.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 128);
                border-right: 1px solid rgba(255, 255, 255, 26);
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(0)
        
        # Logo section
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(12, 0, 12, 15)
        logo_layout.setSpacing(3)
        
        logo = QLabel("AXION")
        logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo.setStyleSheet("color: #7828dc; background: transparent; border: none;")
        logo_layout.addWidget(logo)
        
        subtitle = QLabel("Update Editor")
        subtitle.setFont(QFont("Consolas", 8))
        subtitle.setStyleSheet("color: #555555; background: transparent; border: none;")
        logo_layout.addWidget(subtitle)
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255, 255, 255, 13); border: none;")
        logo_layout.addWidget(sep)
        
        layout.addWidget(logo_widget)
        
        # Section title
        section_title = QLabel("EDITOR")
        section_title.setFont(QFont("Segoe UI", 9))
        section_title.setStyleSheet("""
            color: #555555;
            background: transparent;
            border: none;
            padding: 8px 12px 8px 12px;
        """)
        layout.addWidget(section_title)
        
        # Nav items
        self.nav_changelog = self.create_nav_item("Changelog", "changelog")
        self.nav_version = self.create_nav_item("Versão", "version")
        self.nav_publish = self.create_nav_item("Publicar", "publish")
        
        layout.addWidget(self.nav_changelog)
        layout.addWidget(self.nav_version)
        layout.addWidget(self.nav_publish)
        
        layout.addStretch()
        
        return sidebar
    
    def create_nav_item(self, text, page_id):
        item = QLabel(text)
        item.setFont(QFont("Segoe UI", 11))
        item.setCursor(Qt.PointingHandCursor)
        item.setFixedHeight(36)
        item.setStyleSheet("""
            QLabel {
                color: #999999;
                background: transparent;
                border-left: 2px solid transparent;
                padding-left: 10px;
            }
        """)
        item.mousePressEvent = lambda e: self.show_page(page_id)
        item.page_id = page_id
        return item
    
    def show_page(self, page_id):
        self.current_page = page_id
        
        # Update nav styling
        for nav in [self.nav_changelog, self.nav_version, self.nav_publish]:
            if nav.page_id == page_id:
                nav.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        background: rgba(120, 40, 220, 20);
                        border-left: 2px solid #7828dc;
                        padding-left: 10px;
                    }
                """)
            else:
                nav.setStyleSheet("""
                    QLabel {
                        color: #999999;
                        background: transparent;
                        border-left: 2px solid transparent;
                        padding-left: 10px;
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
        elif page_id == "publish":
            self.load_publish_page()
    
    def load_changelog_page(self):
        # Header
        title = QLabel("Changelog")
        title.setFont(QFont("Segoe UI", 18, QFont.DemiBold))
        title.setStyleSheet("color: #ffffff; background: transparent; border: none; margin-bottom: 4px;")
        self.content_layout.addWidget(title)
        
        subtitle = QLabel("Gerencie as mudanças da versão")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #666666; background: transparent; border: none; margin-bottom: 20px;")
        self.content_layout.addWidget(subtitle)
        
        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(15, 15, 15, 153);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 6px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(12)
        
        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(list(PREFIXOS.keys()))
        self.combo_tipo.setFixedWidth(140)
        self.combo_tipo.setFont(QFont("Segoe UI", 11))
        self.combo_tipo.setStyleSheet("""
            QComboBox {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 4px;
                padding: 8px 10px;
                color: #cccccc;
            }
            QComboBox:focus {
                border-color: #7828dc;
                background: rgba(0, 0, 0, 204);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a1a;
                border: 1px solid rgba(255, 255, 255, 20);
                selection-background-color: #7828dc;
                color: #cccccc;
            }
        """)
        input_row.addWidget(self.combo_tipo)
        
        self.entry_texto = QLineEdit()
        self.entry_texto.setPlaceholderText("Digite a mudança...")
        self.entry_texto.setFont(QFont("Segoe UI", 11))
        self.entry_texto.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 4px;
                padding: 8px 10px;
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
        self.listbox.setStyleSheet("""
            QListWidget {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 4px;
                padding: 8px;
                color: #aaaaaa;
            }
            QListWidget::item {
                background: rgba(255, 255, 255, 5);
                border-left: 2px solid #7828dc;
                border-radius: 3px;
                padding: 8px 10px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 13);
            }
            QListWidget::item:selected {
                background: rgba(120, 40, 220, 38);
                border-left-color: #a855f7;
                color: #cccccc;
            }
        """)
        self.listbox.setMaximumHeight(220)
        card_layout.addWidget(self.listbox)
        
        # Update list
        self.atualizar_lista()
        
        # Actions
        actions_sep = QFrame()
        actions_sep.setFixedHeight(1)
        actions_sep.setStyleSheet("background: rgba(255, 255, 255, 10); border: none;")
        card_layout.addWidget(actions_sep)
        
        actions = QHBoxLayout()
        
        btn_remove = QPushButton("Remover")
        btn_remove.setFont(QFont("Segoe UI", 11))
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 38);
                border-radius: 4px;
                padding: 8px 16px;
                color: #999999;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 8);
                border-color: rgba(255, 255, 255, 64);
                color: #cccccc;
            }
        """)
        btn_remove.clicked.connect(self.remover_item)
        actions.addWidget(btn_remove)
        
        actions.addStretch()
        
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
        # Header
        title = QLabel("Versão")
        title.setFont(QFont("Segoe UI", 18, QFont.DemiBold))
        title.setStyleSheet("color: #ffffff; background: transparent; border: none; margin-bottom: 4px;")
        self.content_layout.addWidget(title)
        
        subtitle = QLabel("Configure as versões do jogo e do Axion")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #666666; background: transparent; border: none; margin-bottom: 20px;")
        self.content_layout.addWidget(subtitle)
        
        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(15, 15, 15, 153);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 6px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
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
                border: 1px solid rgba(255, 255, 255, 20);
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
                border: 1px solid rgba(255, 255, 255, 20);
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
                padding: 10px 20px;
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
    
    def load_publish_page(self):
        # Header
        title = QLabel("Publicar")
        title.setFont(QFont("Segoe UI", 18, QFont.DemiBold))
        title.setStyleSheet("color: #ffffff; background: transparent; border: none; margin-bottom: 4px;")
        self.content_layout.addWidget(title)
        
        subtitle = QLabel("Execute o processo de publicação da atualização")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #666666; background: transparent; border: none; margin-bottom: 20px;")
        self.content_layout.addWidget(subtitle)
        
        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(15, 15, 15, 153);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 6px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(12)
        
        # Log label
        log_label = QLabel("LOG DE PUBLICAÇÃO")
        log_label.setFont(QFont("Segoe UI", 10))
        log_label.setStyleSheet("color: #888888; background: transparent; border: none;")
        card_layout.addWidget(log_label)
        
        # Log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setFixedHeight(250)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 153);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 4px;
                padding: 10px;
                color: #888888;
            }
        """)
        card_layout.addWidget(self.log_text)
        
        # Publish button
        btn_publish = QPushButton("Publicar Atualização")
        btn_publish.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        btn_publish.setCursor(Qt.PointingHandCursor)
        btn_publish.setStyleSheet("""
            QPushButton {
                background: rgba(120, 40, 220, 128);
                border: 1px solid rgba(150, 50, 255, 153);
                border-radius: 4px;
                padding: 12px 24px;
                color: #ffffff;
            }
            QPushButton:hover {
                background: rgba(130, 50, 220, 179);
                border-color: rgba(180, 80, 255, 230);
            }
        """)
        btn_publish.clicked.connect(self.executar_publicacao)
        card_layout.addWidget(btn_publish)
        
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
            self.listbox.addItem(item)
    
    def remover_item(self):
        current_row = self.listbox.currentRow()
        if current_row >= 0:
            del self.dados_changelog["changes"][current_row]
            self.atualizar_lista()
    
    def salvar_changelog(self):
        save_json(CHANGELOG_PATH, self.dados_changelog)
        QMessageBox.information(self, "Sucesso", "changelog.json atualizado")
    
    def salvar_version(self):
        self.dados_version["game_version"] = self.entry_game.text().strip()
        self.dados_version["axion_release"] = self.entry_axion.text().strip()
        save_json(VERSION_PATH, self.dados_version)
        QMessageBox.information(self, "Sucesso", "version.json atualizado")
    
    def executar_publicacao(self):
        if not os.path.exists(PUBLICAR_BAT):
            QMessageBox.critical(self, "Erro", "publicar_update.bat não encontrado.")
            return

        reply = QMessageBox.question(
            self,
            "Publicar Atualização",
            "Isso irá executar o processo de publicação.\n\nDeseja continuar?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.log_text.clear()

        log_path = os.path.join(BASE_DIR, "publish.log")

        # remove log antigo
        if os.path.exists(log_path):
            os.remove(log_path)

        # EXECUTA IGUAL AO DUPLO CLIQUE (Explorer)
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "", PUBLICAR_BAT],
            cwd=BASE_DIR,
            shell=True
        )

        def monitor_log():
            self.append_log("Iniciando publicação...\n")
            last_pos = 0

            while True:
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_pos)
                        new_data = f.read()
                        if new_data:
                            self.append_log(new_data.rstrip())
                            last_pos = f.tell()

                            # condição de término
                            if "Publicacao finalizada." in new_data:
                                break

        threading.Thread(target=monitor_log, daemon=True).start()

    def append_log(self, message):
        self.log_text.append(message)
    
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
