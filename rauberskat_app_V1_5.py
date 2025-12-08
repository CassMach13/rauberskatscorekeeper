import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, 
                             QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QLabel, QComboBox, QLineEdit, QPushButton, QCheckBox,
                             QFormLayout, QGroupBox, QTableWidget, QHeaderView, QDateEdit, QTimeEdit,
                             QFileDialog)
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont, QBrush, QColor
from PyQt6.QtCore import Qt, QDate, QTime
from rauberskat_backend_oficial import RauberskatScorekeeper


def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scorekeeper = None
        self.game_state = "setup" # "setup", "playing", "ended"

        self.setWindowTitle("Räuberskat Scorekeeper")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setObjectName("central_widget") # Adicionado para aplicar estilo
        self.main_layout = QVBoxLayout(self.central_widget)

        # Header
        header_label = QLabel("Räuberskat Scorekeeper")
        header_label.setObjectName("header_label")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(header_label)

        # StackedWidget para gerenciar as telas
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Criar as telas (páginas)
        self.setup_screen = self.create_setup_screen()
        self.game_screen = self.create_game_screen()
        self.end_screen = self.create_end_screen()

        # Adicionar telas ao StackedWidget
        self.stacked_widget.addWidget(self.setup_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.end_screen)

        # Carregar estilos
        # O estilo será definido diretamente aqui para garantir a aplicação correta.
        self.apply_stylesheet()

        self.update_game_state("setup")

    def apply_stylesheet(self):
        # Use barras normais para o caminho, é mais portável
        image_path = "c:/Users/cassi/Downloads/Rauberskat_app_Gemini/Fundo Skat.jpeg".replace("\\", "/")
        # O caminho da imagem agora é relativo e usa a função resource_path
        # Garanta que o arquivo "Fundo Skat.jpeg" esteja na mesma pasta que o seu script .py
        # ou em uma subpasta (ex: "assets/Fundo Skat.jpeg")
        image_path_raw = resource_path("Fundo Skat.jpeg")
        image_path = image_path_raw.replace("\\", "/") # Converte para barras normais para o CSS

        background_style = f"""
        QMainWindow {{
            background-image: url({image_path});
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed; /* Mantém a imagem fixa durante o scroll */
        }}
        /* Torna os widgets de fundo transparentes para a imagem aparecer */
        #central_widget, QStackedWidget > QWidget {{
            background-color: transparent;
        }}
        #header_label {{
            background-color: rgba(20, 20, 20, 0.85);
            color: white;
            font-size: 28px;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #444;
            margin-bottom: 15px;
        }}
        QGroupBox {{
            background-color: rgba(20, 20, 20, 0.85); /* Um pouco mais escuro e opaco */
            border: 1px solid #444;
            border-radius: 6px;
            margin-top: 15px;
            padding-top: 20px; /* Espaço interno para o conteúdo não colar no título */
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 5px 10px;
            color: #f0f0f0; /* Alterado para branco para melhor legibilidade */
        }}
        QLabel, QCheckBox {{
            color: #f0f0f0;
            font-size: 14px;
            background-color: rgba(20, 20, 20, 0.7); /* Fundo escuro semitransparente */
            padding: 4px; /* Espaçamento interno para o texto não colar na borda */
            border-radius: 4px; /* Bordas arredondadas */
            margin: 1px; /* Pequena margem para não colar em outros elementos */
        }}
        /* Estilo específico para os rótulos dentro de um QFormLayout */
        QFormLayout > QLabel {{
            color: #f0f0f0;
            font-size: 14px;
            background-color: rgba(20, 20, 20, 0.7);
            padding: 4px;
            border-radius: 4px;
        }}
        QLineEdit, QComboBox {{
            background-color: #333;
            color: white;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border-color: #0d6efd; /* Destaque azul ao focar */
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{ /* Estilo da lista dropdown */
            background-color: #333;
            color: white;
            selection-background-color: #0d6efd;
        }}
        QPushButton {{
            background-color: #0d6efd; /* Azul da referência */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #0b5ed7; /* Azul um pouco mais escuro */
        }}
        #log_label {{
            color: #f0f0f0;
            font-size: 14px;
            background-color: rgba(20, 20, 20, 0.7); /* Fundo para o log */
            padding: 8px;
            border-radius: 5px;
        }}
        QTableWidget::item {{
            padding: 5px; /* Adiciona espaçamento interno às células */
        }}
        """
        self.setStyleSheet(background_style)

    def update_game_state(self, new_state):
        self.game_state = new_state
        if self.game_state == "setup":
            self.stacked_widget.setCurrentWidget(self.setup_screen)
        elif self.game_state == "playing":
            self.stacked_widget.setCurrentWidget(self.game_screen)
        elif self.game_state == "ended":
            self.stacked_widget.setCurrentWidget(self.end_screen)

    def create_setup_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        group = QGroupBox("Configuração da Partida")
        group.setMaximumWidth(400)
        form_layout = QFormLayout(group)

        self.combo_quantos_jogadores = QComboBox()
        self.combo_quantos_jogadores.addItems(["3", "4"])
        self.combo_quantos_jogadores.currentIndexChanged.connect(self.atualizar_campos_jogadores)
        form_layout.addRow("Quantos Jogadores?", self.combo_quantos_jogadores)

        self.line_jogador1 = QLineEdit()
        self.line_jogador2 = QLineEdit()
        self.line_jogador3 = QLineEdit()
        self.line_jogador4 = QLineEdit()
        self.label_jogador4 = QLabel("Jogador 4:")
        
        form_layout.addRow("Jogador 1:", self.line_jogador1)
        form_layout.addRow("Jogador 2:", self.line_jogador2)
        form_layout.addRow("Jogador 3:", self.line_jogador3)
        form_layout.addRow(self.label_jogador4, self.line_jogador4)

        # Novos campos de detalhes da partida
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.venue_edit = QLineEdit()
        self.table_name_edit = QLineEdit() # Novo campo para Nome da Mesa
        self.start_time_edit = QTimeEdit(QTime.currentTime())
        self.end_time_edit = QTimeEdit() # Novo campo para Horário de Término

        form_layout.addRow("Data:", self.date_edit)
        form_layout.addRow("Sede:", self.venue_edit)
        form_layout.addRow("Nome da Mesa:", self.table_name_edit)
        form_layout.addRow("Horário de Início:", self.start_time_edit)
        form_layout.addRow("Horário de Término:", self.end_time_edit)

        self.btn_iniciar_jogo = QPushButton("Iniciar Jogo")
        self.btn_iniciar_jogo.clicked.connect(self.iniciar_jogo)
        self.btn_iniciar_jogo.setAutoDefault(True)

        layout.addWidget(group)
        layout.addWidget(self.btn_iniciar_jogo)
        
        self.atualizar_campos_jogadores()
        return screen

    def create_game_screen(self):
        screen = QWidget()
        main_hbox = QHBoxLayout(screen)

        # --- Coluna da Esquerda (Controles) ---
        left_vbox = QVBoxLayout()
        
        # Info da Rodada
        info_group = QGroupBox("Informações da Rodada")
        info_group.setContentsMargins(10, 20, 10, 10) # Adiciona margem interna
        info_layout = QFormLayout(info_group)
        self.label_rodada = QLabel()
        self.label_dealer = QLabel()
        info_layout.addRow("Rodada Atual:", self.label_rodada)
        info_layout.addRow("Dealer Atual:", self.label_dealer)
        left_vbox.addWidget(info_group)

        # Nova Jogada
        nova_jogada_group = QGroupBox("Registrar Nova Jogada")
        nova_jogada_group.setContentsMargins(10, 10, 10, 10)
        self.adicionar_pontuacao_layout = QFormLayout(nova_jogada_group)

        self.combo_jogador = QComboBox()
        self.combo_jogo = QComboBox()
        self.combo_com_sem = QComboBox()
        self.combo_com_sem.addItems(["", "1", "2", "3", "4"])
        self.check_hand = QCheckBox()
        self.check_ouvert = QCheckBox()
        self.check_schneider = QCheckBox()
        self.check_schneider_anunciado = QCheckBox()
        self.check_schwartz = QCheckBox()
        self.check_schwartz_anunciado = QCheckBox()
        self.check_kontra = QCheckBox()
        self.check_reh = QCheckBox()
        self.check_bock = QCheckBox()
        self.check_rursch = QCheckBox()
        self.line_quantos_pontos = QLineEdit()
        self.check_houve_empate = QCheckBox()
        self.combo_jogador_que_empatou = QComboBox()
        self.check_jungfrau = QCheckBox()
        self.combo_skat_empurrado = QComboBox()
        self.combo_skat_empurrado.addItems(["0", "1", "2", "3"])
        self.check_jogador_perdeu = QCheckBox()

        # Adicionando widgets ao layout do formulário
        self.adicionar_pontuacao_layout.setVerticalSpacing(8) # Adiciona espaçamento vertical
        self.adicionar_pontuacao_layout.addRow("Jogador que pontua:", self.combo_jogador)
        self.adicionar_pontuacao_layout.addRow("Jogo:", self.combo_jogo)
        self.adicionar_pontuacao_layout.addRow("Com ou Sem:", self.combo_com_sem)
        self.adicionar_pontuacao_layout.addRow("Hand:", self.check_hand)
        self.adicionar_pontuacao_layout.addRow("Ouvert:", self.check_ouvert)
        self.adicionar_pontuacao_layout.addRow("Schneider:", self.check_schneider)
        self.adicionar_pontuacao_layout.addRow("Schneider Anunciado:", self.check_schneider_anunciado)
        self.adicionar_pontuacao_layout.addRow("Schwartz:", self.check_schwartz)
        self.adicionar_pontuacao_layout.addRow("Schwartz Anunciado:", self.check_schwartz_anunciado)
        self.adicionar_pontuacao_layout.addRow("Kontra:", self.check_kontra)
        self.adicionar_pontuacao_layout.addRow("Reh:", self.check_reh)
        self.adicionar_pontuacao_layout.addRow("Bock:", self.check_bock)
        self.adicionar_pontuacao_layout.addRow("Rürsch:", self.check_rursch)
        self.adicionar_pontuacao_layout.addRow("Pontos (Ramsch):", self.line_quantos_pontos) # Este será corrigido em configurar_visibilidade_inicial_pontuacao
        self.adicionar_pontuacao_layout.addRow("Houve empate:", self.check_houve_empate)
        self.adicionar_pontuacao_layout.addRow("Jogador que empatou:", self.combo_jogador_que_empatou)
        self.adicionar_pontuacao_layout.addRow("Jüngfrau:", self.check_jungfrau)
        self.adicionar_pontuacao_layout.addRow("Skat empurrado:", self.combo_skat_empurrado)
        self.adicionar_pontuacao_layout.addRow("O Jogador perdeu:", self.check_jogador_perdeu)

        self.btn_calcular_pontuacao = QPushButton("Calcular Pontuação")
        self.btn_calcular_pontuacao.setAutoDefault(True)
        self.adicionar_pontuacao_layout.addRow(self.btn_calcular_pontuacao)

        left_vbox.addWidget(nova_jogada_group)
        left_vbox.addStretch()

        # --- Coluna da Direita (Resumo e Log) ---
        right_vbox = QVBoxLayout()

        # Tabela de Resumo
        resumo_group = QGroupBox("Resumo da Partida")
        resumo_layout = QVBoxLayout(resumo_group)
        self.tabela_resumo_partida = QTableWidget()
        self.tabela_resumo_partida.setColumnCount(5)
        self.tabela_resumo_partida.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_resumo_partida.horizontalHeader().setVisible(True)
        self.tabela_resumo_partida.verticalHeader().setVisible(True)
        self.tabela_resumo_partida.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        resumo_layout.addWidget(self.tabela_resumo_partida)
        right_vbox.addWidget(resumo_group)

        # Log da Última Jogada
        log_group = QGroupBox("Resultado da Última Jogada")
        log_group.setContentsMargins(10, 20, 10, 10) # Adiciona margem interna
        log_layout = QVBoxLayout(log_group)
        self.label_log_ultima_jogada = QLabel("Aguardando a primeira jogada...")
        self.label_log_ultima_jogada.setObjectName("log_label")
        self.label_log_ultima_jogada.setWordWrap(True)
        self.label_log_ultima_jogada.setAlignment(Qt.AlignmentFlag.AlignTop)
        log_layout.addWidget(self.label_log_ultima_jogada)
        right_vbox.addWidget(log_group)

        # Botões de Ação
        action_buttons_layout = QHBoxLayout()
        self.btn_desfazer = QPushButton("Desfazer Última Jogada")
        self.btn_desfazer.setAutoDefault(True)
        self.btn_fim_jogo = QPushButton("Finalizar Jogo")
        self.btn_fim_jogo.setAutoDefault(True)
        action_buttons_layout.addWidget(self.btn_desfazer) 
        action_buttons_layout.addWidget(self.btn_fim_jogo)
        right_vbox.addLayout(action_buttons_layout)

        main_hbox.addLayout(left_vbox, 1)
        main_hbox.addLayout(right_vbox, 2)

        # Conectar Sinais
        self.check_schneider.stateChanged.connect(self.atualizar_visibilidade_schneider_e_schwartz)
        self.check_schwartz.stateChanged.connect(self.atualizar_visibilidade_schneider_e_schwartz)
        self.check_kontra.stateChanged.connect(self.atualizar_visibilidade_multiplicadores)
        self.check_reh.stateChanged.connect(self.atualizar_visibilidade_multiplicadores)
        self.check_bock.stateChanged.connect(self.atualizar_visibilidade_multiplicadores)
        self.check_houve_empate.stateChanged.connect(self.atualizar_visibilidade_empate)
        self.combo_jogador.currentTextChanged.connect(self.atualizar_combo_jogador_que_empatou)
        self.btn_calcular_pontuacao.clicked.connect(self.calcular_pontuacao_e_avancar)
        self.btn_desfazer.clicked.connect(self.desfazer_ultima_jogada)
        self.combo_jogo.currentTextChanged.connect(self.atualizar_campos_por_jogo)
        self.btn_fim_jogo.clicked.connect(self.finalizar_jogo)

        # Inicializa o dicionário de campos e os esconde
        self.configurar_visibilidade_inicial_pontuacao()

        return screen

    def create_end_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.end_game_label = QLabel()
        self.end_game_label.setObjectName("log_label")
        self.end_game_label.setWordWrap(True)
        
        self.btn_novo_jogo = QPushButton("Iniciar Novo Jogo")
        self.btn_novo_jogo.clicked.connect(self.resetar_para_novo_jogo)
        self.btn_novo_jogo.setAutoDefault(True)
        
        self.btn_exportar_resultado = QPushButton("Exportar Resultado")
        self.btn_exportar_resultado.clicked.connect(self.exportar_resultado)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_novo_jogo)
        buttons_layout.addWidget(self.btn_exportar_resultado)
        
        layout.addWidget(self.end_game_label)
        layout.addLayout(buttons_layout)
        
        return screen
    def configurar_visibilidade_inicial_pontuacao(self):
        # Mapeia labels e widgets para facilitar o show/hide
        self.all_game_fields = {
            "com_sem": (self.adicionar_pontuacao_layout.labelForField(self.combo_com_sem), self.combo_com_sem),
            "hand": (self.adicionar_pontuacao_layout.labelForField(self.check_hand), self.check_hand),
            "ouvert": (self.adicionar_pontuacao_layout.labelForField(self.check_ouvert), self.check_ouvert),
            "schneider": (self.adicionar_pontuacao_layout.labelForField(self.check_schneider), self.check_schneider),
            "schneider_anunciado": (self.adicionar_pontuacao_layout.labelForField(self.check_schneider_anunciado), self.check_schneider_anunciado),
            "schwartz": (self.adicionar_pontuacao_layout.labelForField(self.check_schwartz), self.check_schwartz),
            "schwartz_anunciado": (self.adicionar_pontuacao_layout.labelForField(self.check_schwartz_anunciado), self.check_schwartz_anunciado),
            "kontra": (self.adicionar_pontuacao_layout.labelForField(self.check_kontra), self.check_kontra),
            "reh": (self.adicionar_pontuacao_layout.labelForField(self.check_reh), self.check_reh),
            "bock": (self.adicionar_pontuacao_layout.labelForField(self.check_bock), self.check_bock),
            "rursch": (self.adicionar_pontuacao_layout.labelForField(self.check_rursch), self.check_rursch),
            "pontos_ramsch": (self.adicionar_pontuacao_layout.labelForField(self.line_quantos_pontos), self.line_quantos_pontos), # O label é encontrado aqui
            "houve_empate": (self.adicionar_pontuacao_layout.labelForField(self.check_houve_empate), self.check_houve_empate),
            "jogador_que_empatou": (self.adicionar_pontuacao_layout.labelForField(self.combo_jogador_que_empatou), self.combo_jogador_que_empatou),
            "jungfrau": (self.adicionar_pontuacao_layout.labelForField(self.check_jungfrau), self.check_jungfrau),
            "skat_empurrado": (self.adicionar_pontuacao_layout.labelForField(self.combo_skat_empurrado), self.combo_skat_empurrado),
            "perdeu": (self.adicionar_pontuacao_layout.labelForField(self.check_jogador_perdeu), self.check_jogador_perdeu),
        }
        for label, widget in self.all_game_fields.values():
            if label: label.hide()
            if widget: widget.hide()

    def atualizar_visibilidade_schneider_e_schwartz(self):
        schneider_ativo = self.check_schneider.isChecked()
        schwartz_ativo = self.check_schwartz.isChecked()
        
        label_sa, widget_sa = self.all_game_fields["schneider_anunciado"]
        label_s, widget_s = self.all_game_fields["schwartz"]
        label_sza, widget_sza = self.all_game_fields["schwartz_anunciado"]

        # Schneider Anunciado
        if schneider_ativo:
            label_sa.show()
            widget_sa.show()
        else:
            label_sa.hide()
            widget_sa.setChecked(False)
            widget_sa.hide()

        # Schwartz
        if schneider_ativo:
            label_s.show()
            widget_s.show()
        else:
            label_s.hide()
            widget_s.setChecked(False)
            widget_s.hide()

        # Schwartz Anunciado
        if schneider_ativo and schwartz_ativo:
            label_sza.show()
            widget_sza.show()
        else:
            label_sza.hide()
            widget_sza.setChecked(False)
            widget_sza.hide()

    def atualizar_visibilidade_multiplicadores(self):
        jogo = self.combo_jogo.currentText().strip().lower()
        jogos_com_multiplicadores = ["ouros", "copas", "espadas", "paus", "grand", "null", "null revolution", "grand hand"]

        if jogo not in jogos_com_multiplicadores:
            # Oculta e desmarca todos
            for label, checkbox in [
                self.all_game_fields["kontra"],
                self.all_game_fields["reh"],
                self.all_game_fields["bock"],
                self.all_game_fields["rursch"],
            ]:
                label.hide()
                checkbox.setChecked(False)
                checkbox.hide()
            return

        # Mostra Kontra sempre
        self.all_game_fields["kontra"][0].show()
        self.all_game_fields["kontra"][1].show()

        # Se Kontra está marcado, mostra Reh
        label_reh, check_reh = self.all_game_fields["reh"]
        if self.check_kontra.isChecked():
            label_reh.show()
            check_reh.show()
        else:
            label_reh.hide()
            check_reh.setChecked(False)
            check_reh.hide()

        # Se Reh está marcado, mostra Bock
        label_bock, check_bock = self.all_game_fields["bock"]
        if self.check_kontra.isChecked() and self.check_reh.isChecked():
            label_bock.show()
            check_bock.show()
        else:
            label_bock.hide()
            check_bock.setChecked(False)
            check_bock.hide()

        # Se Bock está marcado, mostra Rürsch
        label_rursch, check_rursch = self.all_game_fields["rursch"]
        if self.check_kontra.isChecked() and self.check_reh.isChecked() and self.check_bock.isChecked():
            label_rursch.show()
            check_rursch.show()
        else:
            label_rursch.hide()
            check_rursch.setChecked(False)
            check_rursch.hide()

    def atualizar_combo_jogador_que_empatou(self):
        jogador_principal = self.combo_jogador.currentText()

        # Limpar o combo de quem empatou
        self.combo_jogador_que_empatou.clear()

        # Adicionar apenas jogadores diferentes do jogador principal
        for i in range(self.combo_jogador.count()):
            nome = self.combo_jogador.itemText(i)
            if nome and nome != jogador_principal:
                self.combo_jogador_que_empatou.addItem(nome)

    def atualizar_visibilidade_empate(self):
        label, widget = self.all_game_fields["jogador_que_empatou"]
        if self.combo_jogo.currentText().lower() == "ramsch":
            houve_empate = self.check_houve_empate.isChecked()
            label.setVisible(houve_empate)
            widget.setVisible(houve_empate)

            if houve_empate:
                widget.clear()
                jogador_principal = self.combo_jogador.currentText()
                for i in range(self.combo_jogador.count()):
                    nome = self.combo_jogador.itemText(i)
                    if nome and nome != jogador_principal:
                        widget.addItem(nome)

        else:
            # Se não for Ramsch, oculta o campo de empate (segurança extra)
            label.setVisible(False)
            widget.setVisible(False)

    def atualizar_visibilidade_skat_empurrado(self):
        jogo_selecionado = self.combo_jogo.currentText().lower()
        rodada_atual = self.label_rodada.text().lower()
        
        label, widget = self.all_game_fields["skat_empurrado"]
        mostrar = jogo_selecionado in ["ramsch", "durchmarsch"] and "ramsch" in rodada_atual
        label.setVisible(mostrar)
        widget.setVisible(mostrar)

    def atualizar_campos_jogadores(self):
        quantos_jogadores = self.combo_quantos_jogadores.currentText()
        if quantos_jogadores == "3":
            self.line_jogador4.hide()
            self.label_jogador4.hide()
        else:
            self.line_jogador4.show()
            self.label_jogador4.show()

    def atualizar_dealer(self):
        if not self.scorekeeper:
            return
        dealer = self.scorekeeper.player_names[self.scorekeeper.dealer_index]
        self.label_dealer.setText(f"{dealer}")

    def configurar_colunas_tabela_resumo(self):
        nomes_jogadores = [
            self.line_jogador1.text(),
            self.line_jogador2.text(),
            self.line_jogador3.text(),
        ]

        if self.combo_quantos_jogadores.currentText() == "4":
            nomes_jogadores.append(self.line_jogador4.text())
        else:
            nomes_jogadores.append("")  # Placeholder para jogador 4 (será ocultado)

        # Adiciona a coluna "Spiel"
        nomes_jogadores.append("Spiel")

        # Sempre define 5 colunas
        self.tabela_resumo_partida.setColumnCount(5)
        self.tabela_resumo_partida.setHorizontalHeaderLabels(nomes_jogadores)

        if self.combo_quantos_jogadores.currentText() == "4":
            self.tabela_resumo_partida.setColumnHidden(3, False)
        else:
            self.tabela_resumo_partida.setColumnHidden(3, True)  # Oculta só o jogador 4

    def resetar_para_novo_jogo(self):
        # Limpa tabela de resumo
        self.tabela_resumo_partida.setRowCount(0)
        self.scorekeeper = None
        self.pontuacao_acumulada = {}
        self.label_log_ultima_jogada.setText("Aguardando a primeira jogada...")

        # Limpa campos de nome
        self.line_jogador1.clear()
        self.line_jogador2.clear()
        self.line_jogador3.clear()
        self.line_jogador4.clear()

        self.update_game_state("setup")

    def iniciar_jogo(self):
        quantos_jogadores = self.combo_quantos_jogadores.currentText()
        nomes = [
            self.line_jogador1.text().strip(),
            self.line_jogador2.text().strip(),
            self.line_jogador3.text().strip(),
        ]
        if quantos_jogadores == "4":
            nomes.append(self.line_jogador4.text().strip())

        if any(nome == "" for nome in nomes):
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os nomes dos jogadores.")
            return

        self.scorekeeper = RauberskatScorekeeper(nomes)

        # Salva os detalhes da partida
        self.game_date = self.date_edit.date().toString("dd/MM/yyyy")
        self.game_venue = self.venue_edit.text()
        self.game_table_name = self.table_name_edit.text()
        self.game_start_time = self.start_time_edit.time().toString("HH:mm")
        self.game_end_time = self.end_time_edit.time().toString("HH:mm")

        self.configurar_colunas_tabela_resumo()
        
        # Inicializa o acumulador de pontuação dos jogadores
        self.pontuacao_acumulada = {
            self.line_jogador1.text(): 0,
            self.line_jogador2.text(): 0,
            self.line_jogador3.text(): 0,
        }
        if self.combo_quantos_jogadores.currentText() == "4":
            self.pontuacao_acumulada[self.line_jogador4.text()] = 0

        self.atualizar_rodada_atual()
        self.atualizar_dealer()

        self.update_game_state("playing")
        self.atualizar_jogadores_pontuadores() # Atualiza a lista de jogadores que podem pontuar
        self.atualizar_campos_por_jogo()

    def atualizar_rodada_atual(self):
        if not self.scorekeeper:
            return
        rodada = self.scorekeeper.current_mode
        self.label_rodada.setText(f"{rodada}")
        self.atualizar_campos_por_jogo()
        self.atualizar_opcoes_jogo()
        self.atualizar_visibilidade_skat_empurrado()

    def atualizar_jogadores_pontuadores(self):
        """Atualiza o ComboBox de jogadores que podem pontuar, removendo o dealer em jogos de 4."""
        if not self.scorekeeper:
            return

        jogadores_ativos = list(self.scorekeeper.player_names)
        
        # Se for um jogo de 4 jogadores, remove o dealer da lista de jogadores ativos
        if self.scorekeeper.num_players == 4:
            dealer_atual = self.scorekeeper.get_current_dealer()
            if dealer_atual in jogadores_ativos:
                jogadores_ativos.remove(dealer_atual)

        self.combo_jogador.clear()
        self.combo_jogador.addItem("") # Placeholder
        self.combo_jogador.addItems(jogadores_ativos)

    def atualizar_opcoes_jogo(self):
        rodada_texto = self.label_rodada.text()

        jogos_bock = [
            "", "Ouros", "Copas", "Espadas", "Paus",
            "Null", "Grand", "Null Revolution", "Durchmarsch", "Ramsch"
        ]
        jogos_ramsch = [
            "", "Ramsch", "Grand Hand", "Durchmarsch"
        ]

        if "Bock" in rodada_texto:
            self.combo_jogo.clear()
            self.combo_jogo.addItems(jogos_bock)

        elif "Ramsch" in rodada_texto:
            self.combo_jogo.clear()
            self.combo_jogo.addItems(jogos_ramsch)

    def resetar_campos_jogo(self):
        self.line_quantos_pontos.clear()
        self.combo_com_sem.setCurrentIndex(0)
        self.combo_skat_empurrado.setCurrentIndex(0)
        
        for _, widget in self.all_game_fields.values():
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)

    def atualizar_campos_por_jogo(self):
        self.resetar_campos_jogo()
        jogo = self.combo_jogo.currentText().strip().lower()

        # Oculta todos os campos primeiro, usando o dicionário já existente
        for label, widget in self.all_game_fields.values():
            if label: label.hide()
            if widget: widget.hide()

        def show_fields(field_keys):
            for key in field_keys:
                if key in self.all_game_fields:
                    label, widget = self.all_game_fields[key]
                    if label: label.show()
                    if widget: widget.show()

        if jogo in ["ouros", "copas", "espadas", "paus", "grand"]:
            show_fields(["com_sem", "hand", "ouvert", "schneider", "kontra", "perdeu"])
            self.atualizar_visibilidade_schneider_e_schwartz()
            self.atualizar_visibilidade_multiplicadores()

        elif jogo == "null":
            show_fields(["hand", "ouvert", "kontra", "perdeu"])
            self.atualizar_visibilidade_multiplicadores()

        elif jogo == "null revolution":
            show_fields(["kontra", "perdeu"])
            self.atualizar_visibilidade_multiplicadores()

        elif jogo == "durchmarsch":
            rodada_texto = self.label_rodada.text()
            if "Ramsch" in rodada_texto:
                self.atualizar_visibilidade_skat_empurrado()

        elif jogo == "ramsch":
            show_fields(["pontos_ramsch", "jungfrau", "houve_empate"])
            self.atualizar_visibilidade_empate()
            self.atualizar_visibilidade_skat_empurrado()

        elif jogo == "grand hand":
            show_fields(["com_sem", "ouvert", "schneider", "kontra", "perdeu"])
            self.atualizar_visibilidade_schneider_e_schwartz()
            self.atualizar_visibilidade_multiplicadores()

    def adicionar_resultado_tabela_resumo(self, jogadores_pontuadores, pontos_rodada, rodada_atual):
        # Atualiza o acumulado para os jogadores que pontuaram
        for jogador in jogadores_pontuadores:
            if jogador in self.pontuacao_acumulada:
                self.pontuacao_acumulada[jogador] += pontos_rodada
            else:
                self.pontuacao_acumulada[jogador] = pontos_rodada

        linha = self.tabela_resumo_partida.rowCount()
        self.tabela_resumo_partida.insertRow(linha)

        # Define o número da jogada no cabeçalho vertical
        self.tabela_resumo_partida.setVerticalHeaderItem(linha, QTableWidgetItem(str(linha + 1)))

        jogadores = [
            self.line_jogador1.text(),
            self.line_jogador2.text(),
            self.line_jogador3.text(),
            self.line_jogador4.text()
        ]
        
        # Preenche as colunas dos jogadores com a pontuação acumulada
        for col, nome_jogador in enumerate(jogadores):
            # Verifica se a coluna não está oculta (para o caso de 3 jogadores)
            if not self.tabela_resumo_partida.isColumnHidden(col) and nome_jogador:
                acumulado = self.pontuacao_acumulada.get(nome_jogador, 0)
                texto_pontos = f"+{acumulado}" if acumulado > 0 else "0" if acumulado == 0 else str(acumulado)
                item = QTableWidgetItem(texto_pontos)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Define a cor baseada no valor acumulado
                if acumulado > 0:
                    item.setForeground(QBrush(QColor("#28a745")))  # Verde
                elif acumulado < 0:
                    item.setForeground(QBrush(QColor("#dc3545")))  # Vermelho
                else:
                    item.setForeground(QBrush(QColor("black"))) # Preto para zero

                # Destaca a célula do(s) jogador(es) que pontuou(aram) na rodada
                if nome_jogador in jogadores_pontuadores:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setBackground(QBrush(QColor("#fff3cd"))) # Amarelo bem claro para destaque

                self.tabela_resumo_partida.setItem(linha, col, item)
        
        # Coluna Spiel (coluna 4)
        texto_spiel = f"{pontos_rodada:+}" if pontos_rodada != 0 else "0"
        texto_extras = ""
        rodada_lower = self.label_rodada.text().lower() # Pega a rodada atual da label
        jogo = self.combo_jogo.currentText().lower()

        if "bock" in rodada_lower:
            texto_extras = " B"
        elif "ramsch" in rodada_lower:
            texto_extras = " R"

        item_spiel = QTableWidgetItem(f"{texto_spiel}{texto_extras}")
        item_spiel.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        item_spiel.setFont(font)

        # Define a cor da coluna "Spiel" com base nos pontos da rodada
        item_spiel.setForeground(QBrush(QColor("green")) if pontos_rodada >= 0 else QBrush(QColor("red")))

        self.tabela_resumo_partida.setItem(linha, 4, item_spiel)

    def calcular_pontuacao_e_avancar(self):
        try:
            # Evita validação desnecessária se o campo ainda não estiver pronto
            if not self.combo_jogador.isEnabled() or not self.combo_jogador.isVisible():
                return
            # Coletar os dados da interface
            jogador = self.combo_jogador.currentText()
            # Verifica se o jogador foi selecionado corretamente
            if not jogador:
                QMessageBox.warning(self, "Jogador não selecionado", "Por favor, selecione um jogador antes de calcular a pontuação.")
                return
            # Verifica se o jogador é apenas um campo em branco usado como estética
            if jogador == "":
                QMessageBox.warning(self, "Jogador inválido", "Selecione um jogador válido antes de continuar.")
                return
            jogo = self.combo_jogo.currentText().strip().lower()
            com_sem = self.combo_com_sem.currentText()
            # Verifica se o campo 'Com ou Sem' está visível (ou seja, aplicável ao jogo atual)
            if self.combo_com_sem.isVisible():
                com_sem_text = self.combo_com_sem.currentText().strip()

                if not com_sem_text:
                    QMessageBox.warning(self, "Campo obrigatório", "Por favor, selecione um valor para 'Com ou Sem'.")
                    return
            hand = self.check_hand.isChecked()
            ouvert = self.check_ouvert.isChecked()
            schneider = self.check_schneider.isChecked()
            schneider_anunciado = self.check_schneider_anunciado.isChecked()
            schwartz = self.check_schwartz.isChecked()
            schwartz_anunciado = self.check_schwartz_anunciado.isChecked()
            kontra = self.check_kontra.isChecked()
            reh = self.check_reh.isChecked()
            bock = self.check_bock.isChecked()
            rursch = self.check_rursch.isChecked()
            perdeu = self.check_jogador_perdeu.isChecked()
            pontos_ramsch = self.line_quantos_pontos.text()
            jungfrau = self.check_jungfrau.isChecked()
            houve_empate = self.check_houve_empate.isChecked()

            # Empacotar os dados
            dados = {
                "jogador": jogador,
                "jogo": jogo,
                "com_sem": com_sem,
                "hand": hand,
                "ouvert": ouvert,
                "schneider": schneider,
                "schneider_anunciado": schneider_anunciado,
                "schwartz": schwartz,
                "schwartz_anunciado": schwartz_anunciado,
                "kontra": kontra,
                "reh": reh,
                "bock": bock,
                "rursch": rursch,
                "perdeu": perdeu,
                "pontos_ramsch": pontos_ramsch,
                "jungfrau": jungfrau,
                "houve_empate": houve_empate,
                "empates": self.combo_jogador_que_empatou.currentText() if houve_empate else None,
            }
            info = {}

            # Adiciona skat_empurrado se jogo for ramsch ou durchmarsch durante rodada de Ramsch
            rodada_atual = self.label_rodada.text().strip().lower()
            if "ramsch" in rodada_atual and jogo in ["ramsch", "durchmarsch"]:
                skat_empurrado = self.combo_skat_empurrado.currentIndex()
                info["skat_empurrado"] = skat_empurrado

            if info:
                dados["info"] = info

            # Enviar para o backend calcular a pontuação e atualizar o estado
            resultado = self.scorekeeper.calculate_score(dados)
            if resultado is not None:
                pontuacao_final, fator_total, base_score = resultado
            else:
                pontuacao_final = self.scorekeeper.scores.get(dados["jogador"], 0)  # tenta usar placar atual
                fator_total = None
                base_score = None
            #Para os casos como Ramsch, Grand Hand ou Null onde não há retorno

            # Atualizar a tabela lateral
            self.exibir_log_ultima_jogada(dados, pontuacao_final, fator_total, base_score)

            # Adiciona o resultado do jogador principal primeiro
            jogadores_pontuadores = [jogador]

            # Se houve empate no Ramsch, ambos os jogadores pontuam negativamente
            if jogo == "ramsch" and houve_empate:
                jogador_empatado = self.combo_jogador_que_empatou.currentText()
                jogadores_pontuadores.append(jogador_empatado)
                # Atualiza a pontuação acumulada do jogador que empatou
                # A pontuação já é adicionada no backend, não precisa fazer aqui.

            self.adicionar_resultado_tabela_resumo(jogadores_pontuadores, pontuacao_final, rodada_atual)

            # Avançar para a próxima rodada e dealer
            self.scorekeeper.check_mode_transition()
            
            # Verificar se o backend está aguardando uma decisão sobre a rodada de Ramsch
            if self.scorekeeper.awaiting_ramsch_decision and self.scorekeeper.ramsch_candidates:
                # Itera sobre a cópia da lista de candidatos
                for candidato in list(self.scorekeeper.ramsch_candidates):
                    resposta = QMessageBox.question(
                        self,
                        "Nova Rodada de Ramsch?",
                        f"O jogador {candidato} perdeu todos os jogos de Ramsch nesta rodada.\n\n"
                        f"Deseja iniciar uma nova rodada completa de Ramsch?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No # Default para Não
                    )

                    deseja_nova_rodada = (resposta == QMessageBox.StandardButton.Yes)
                    self.scorekeeper.processar_decisao_ramsch(candidato, deseja_nova_rodada)

                    # Se um jogador recusou, o backend já mudou para Bock e limpou a lista.
                    if not self.scorekeeper.awaiting_ramsch_decision:
                        break # Interrompe o loop de perguntas

                # Se a decisão foi por uma nova rodada de Ramsch, a rodada atual não muda. Se não, o backend já terá mudado para Bock.
                # Apenas precisamos atualizar a interface.
                self.atualizar_rodada_atual()
                self.scorekeeper.next_dealer()
                self.atualizar_dealer()
                return # A lógica de avanço já foi tratada

            # Atualizar o dealer
            self.scorekeeper.next_dealer()
            # Atualizar exibição da rodada atual
            self.atualizar_rodada_atual()
            #Atualizar a exibição do dealer atual
            self.atualizar_dealer()
            # Atualiza a lista de jogadores que podem pontuar para a nova rodada
            self.atualizar_jogadores_pontuadores()
            # Limpar os campos da interface para a próxima jogada
            self.atualizar_campos_por_jogo()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao calcular a pontuação:\n{e}")

    def exibir_log_ultima_jogada(self, dados, pontuacao_final, fator_total, base_score):        
        texto_log = self.gerar_texto_log(dados, pontuacao_final, fator_total, base_score, html_format=True)
        self.label_log_ultima_jogada.setText(texto_log)

    def gerar_texto_log(self, dados, pontuacao_final, fator_total, base_score, html_format=False):
        header = "<b>Resultado da Última Jogada:</b>" if html_format else "Resultado da Última Jogada:"
        jogador_html = f"<b>{dados.get('jogador')}</b>" if html_format else dados.get('jogador')
        jogo_html = f"<b>{dados.get('jogo').title()}</b>" if html_format else dados.get('jogo').title()

        linhas = [
            header,
            f"Jogador: {jogador_html}",
            f"Jogo: {jogo_html}",
        ]

        if dados.get("com_sem"):
            linhas.append(f"Com ou Sem: {dados.get('com_sem')}")

        marcados = []
        for chave, label in [
            ("hand", "Hand"), ("ouvert", "Ouvert"), ("schneider", "Schneider"),
            ("schneider_anunciado", "Schneider Anunciado"), ("schwartz", "Schwartz"),
            ("schwartz_anunciado", "Schwartz Anunciado"), ("kontra", "Kontra"),
            ("reh", "Reh"), ("bock", "Bock"), ("rursch", "Rursch"),
            ("perdeu", "Perdeu"), ("jungfrau", "Jüngfrau"), ("houve_empate", "Empate")
        ]:
            if dados.get(chave):
                marcados.append(label)
        
        if marcados:
            linhas.append("Opções marcadas: " + ", ".join(marcados))

        if dados.get("pontos_ramsch"):
            linhas.append(f"Pontos Ramsch inseridos: {dados.get('pontos_ramsch')}")

        if dados.get("empates"):
            linhas.append(f"Empates com: {dados.get('empates')}")

        jogo = dados.get("jogo")
        skat_empurrado = dados.get("info", {}).get("skat_empurrado", 0)
        
        pontuacao_texto = f"{pontuacao_final} pontos"
        if html_format:
            cor = "green" if pontuacao_final >= 0 else "red"
            pontuacao_texto = f"<b>Pontuação aplicada: <span style='color:{cor}'>{pontuacao_final} pontos</span></b>"
        else:
            pontuacao_texto = f"Pontuação aplicada: {pontuacao_final} pontos"

        if jogo == "durchmarsch":
            linhas.append(f"Pontuação Base: {base_score}")
            if self.scorekeeper.current_mode == "Bock":
                linhas.append(f"Multiplicação do Bock: x2")
            else: 
                linhas.append(f"Vezes que o skat foi empurrado: {skat_empurrado}")

        elif jogo == "ramsch":
            if self.scorekeeper.current_mode == "Bock":
                linhas.append("Multiplicação do Bock: x2")
            if "ramsch" in self.scorekeeper.current_mode.lower():
                linhas.append(f"Vezes que o skat foi empurrado: {skat_empurrado}")

        elif jogo in ["null", "null revolution"]:
            linhas.append(f"Pontuação Base: {base_score}")
            if self.scorekeeper.current_mode == "Bock":
                linhas.append("Multiplicação do Bock: x2")

        else: # Jogos normais
            if fator_total is not None:
                linhas.append(f"Fator Total: {fator_total}")
            if base_score is not None:
                linhas.append(f"Pontuação Base: {base_score}")
            if self.scorekeeper.current_mode == "Bock":
                linhas.append("Multiplicação do Bock: x2")

        linhas.append(pontuacao_texto)
        
        return "<br>".join(linhas) if html_format else "\n".join(linhas)

    def desfazer_ultima_jogada(self):
        #Solicita confirmação antes de desfazer a última jogada
        resposta = QMessageBox.question(
            self,
            "Confirmar Desfazer",
            "Deseja mesmo desfazer a última jogada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if resposta == QMessageBox.StandardButton.Yes:
            sucesso = self.scorekeeper.undo_last_game()
            if sucesso:
                self.atualizar_rodada_atual()
                self.atualizar_dealer()
                # Remove a última linha da tabela lateral
                row_count = self.tabela_resumo_partida.rowCount()
                if row_count > 0:
                    self.tabela_resumo_partida.removeRow(row_count - 1)
                self.label_log_ultima_jogada.setText("Última jogada desfeita com sucesso.")
                self.atualizar_campos_por_jogo()
            else:
                self.label_log_ultima_jogada.setText("Não há jogadas anteriores para desfazer.")

    def finalizar_jogo(self):
        placares = self.scorekeeper.scores
        maior_pontuacao = max(placares.values())
        vencedores = [j for j, p in placares.items() if p == maior_pontuacao]

        texto_final = "<b>🏁 Fim de Jogo</b><br><br>"

        if len(vencedores) == 1:
            texto_final += f"<b>Parabéns, {vencedores[0]}! Você venceu!</b><br>"
        else:
            texto_final += f"<b>Empate entre: {', '.join(vencedores)}</b><br>"

        texto_final += "<br><b>Valores a pagar ao caixa:</b><br>"
        
        for jogador, pontos in placares.items():
            if jogador not in vencedores:
                diferenca = maior_pontuacao - pontos
                valor = diferenca * 0.05
                texto_final += f"{jogador} deve pagar R${valor:.2f}<br>"

        self.end_game_label.setText(texto_final)
        self.update_game_state("ended")

    def exportar_resultado(self):
        if not self.scorekeeper:
            QMessageBox.warning(self, "Erro", "Não há jogo finalizado para exportar.")
            return

        # Formata os dados para o nome do arquivo, substituindo caracteres inválidos
        date_str = getattr(self, 'game_date', 'sem_data').replace('/', '-')
        venue_str = getattr(self, 'game_venue', 'sem_sede').strip()
        table_name_str = getattr(self, 'game_table_name', 'sem_mesa').strip()
        start_time_str = getattr(self, 'game_start_time', 'sem_inicio').replace(':', 'h')
        end_time_str = getattr(self, 'game_end_time', 'sem_termino').replace(':', 'h')

        # Monta o nome do arquivo conforme o formato solicitado
        default_filename = (
            f"Resultado_Skat_Data_{date_str}"
            f"_Sede_{venue_str}"
            f"_Mesa_{table_name_str}"
            f"_Horario de inicio_{start_time_str}"
            f"_Horario de Termino_{end_time_str}.html"
        )
        
        # Abre o diálogo para salvar o arquivo
        filePath, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", default_filename, "HTML Files (*.html);;All Files (*)")

        if not filePath:
            return # Usuário cancelou

        # Gera o conteúdo HTML
        html_content = self.gerar_html_relatorio()

        # Salva o arquivo
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em:\n{filePath}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def gerar_html_relatorio(self):
        # Coleta os dados do placar final
        placares = self.scorekeeper.scores
        maior_pontuacao = max(placares.values())
        vencedores = [j for j, p in placares.items() if p == maior_pontuacao]

        # --- Início do HTML ---
        html = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório da Partida de Räuberskat</title>
            <style>
                body { font-family: sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
                h1, h2 { color: #4a4a4a; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
                .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .placar, .pagamentos { margin-bottom: 20px; }
                .placar-item, .pagamento-item { padding: 8px; border-bottom: 1px solid #eee; }
                .vencedor { font-weight: bold; color: #28a745; }
                .jogada { border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 15px; background-color: #fafafa; }
                .jogada-header { font-weight: bold; font-size: 1.1em; margin-bottom: 10px; }
                .detalhe { margin-left: 20px; }
                table.resumo { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                table.resumo th, table.resumo td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                table.resumo th { background-color: #e9e9e9; font-weight: bold; }
                .positive-score { color: green; }
                .negative-score { color: red; }
                .highlighted-cell { background-color: #FFFF99; }
                .bold-text { font-weight: bold; }

            </style>
        </head>
        <body>
            <div class="container">
                <h1>Relatório da Partida de Räuberskat</h1>
        """
        # --- Seção de Detalhes da Partida ---
        html += "<h2>Detalhes da Partida</h2>"
        html += "<div class='detalhes-partida'>"
        html += f"<div><strong>Data:</strong> {getattr(self, 'game_date', 'N/A')}</div>"
        html += f"<div><strong>Nome da Mesa:</strong> {getattr(self, 'game_table_name', 'N/A')}</div>"
        html += f"<div><strong>Sede:</strong> {getattr(self, 'game_venue', 'N/A')}</div>"
        html += f"<div><strong>Início:</strong> {getattr(self, 'game_start_time', 'N/A')}</div>"
        html += f"<div><strong>Término:</strong> {getattr(self, 'game_end_time', 'N/A')}</div>"
        html += "</div>"


        # Seção do Placar Final
        html += "<h2>Placar Final</h2><div class='placar'>"
        for jogador, pontos in sorted(placares.items(), key=lambda item: item[1], reverse=True):
            classe_vencedor = "vencedor" if jogador in vencedores else ""
            html += f"<div class='placar-item {classe_vencedor}'>{jogador}: {pontos} pontos</div>"
        html += "</div>"

        # Seção da Tabela de Resumo da Partida
        html += "<h2>Resumo da Partida</h2>"
        html += "<table class='resumo'>"
        
        # Cabeçalho da tabela
        html += "<thead><tr>"
        html += "<th>#</th>" # Adiciona cabeçalho para a coluna de números de linha
        for col in range(self.tabela_resumo_partida.columnCount()):
            if not self.tabela_resumo_partida.isColumnHidden(col):
                header_item = self.tabela_resumo_partida.horizontalHeaderItem(col)
                html += f"<th>{header_item.text()}</th>"
        html += "</tr></thead>"

        # Corpo da tabela
        html += "<tbody>"
        for row in range(self.tabela_resumo_partida.rowCount()):
            html += "<tr>"            
            # Adiciona o número da jogada (cabeçalho vertical)
            v_header_item = self.tabela_resumo_partida.verticalHeaderItem(row)
            if v_header_item and v_header_item.text():
                html += f"<td>{v_header_item.text()}</td>"
            else:
                html += f"<td>{row + 1}</td>" # Fallback

            for col in range(self.tabela_resumo_partida.columnCount()):
                if not self.tabela_resumo_partida.isColumnHidden(col):
                    item = self.tabela_resumo_partida.item(row, col)
                    if item and item.text():
                        text = item.text()
                        classes = []
                        
                        # Verifica a cor de fundo para destaque
                        if item.background().color() == QColor("#fff3cd"):
                            classes.append("highlighted-cell")
                        
                        # Verifica se o texto está em negrito
                        if item.font().bold():
                            classes.append("bold-text")
                        
                        # Verifica a cor do texto para pontuação positiva/negativa
                        foreground_color = item.foreground().color()
                        if foreground_color in (QColor("#28a745"), QColor("green")):
                            classes.append("positive-score")
                        elif foreground_color in (QColor("#dc3545"), QColor("red")):
                            classes.append("negative-score")

                        html += f"<td class='{' '.join(classes)}'>{text}</td>"
                    else:
                        html += "<td></td>"
            html += "</tr>"
        html += "</tbody></table>"

        # Seção de Pagamentos
        html += "<h2>Pagamentos ao Caixa</h2><div class='pagamentos'>"
        for jogador, pontos in placares.items():
            if jogador not in vencedores:
                diferenca = maior_pontuacao - pontos
                valor = diferenca * 0.05
                html += f"<div class='pagamento-item'>{jogador} deve pagar R${valor:.2f}</div>"
        html += "</div>"

        # Seção do Histórico de Jogadas
        html += "<h2>Histórico de Jogadas</h2>"
        for i, jogada_dados in enumerate(self.scorekeeper.game_history):
            if "erro" in jogada_dados: continue # Pula jogadas com erro

            # Precisamos recalcular a pontuação da jogada para o log, pois não é salva no histórico
            # Esta é uma simplificação. O ideal seria salvar o resultado no histórico.
            # Por agora, vamos apenas exibir os dados que temos.
            pontuacao_final = "N/A" # Placeholder
            fator_total = "N/A"
            base_score = "N/A"

            html += f"<div class='jogada'><div class='jogada-header'>Jogada {i+1}: {jogada_dados.get('jogador')} - {jogada_dados.get('jogo', '').title()}</div>"
            html += "<div class='detalhes'>"
            
            # Adiciona detalhes da jogada
            # A pontuação final não está no histórico, então não podemos passá-la.
            # Vamos adaptar a função para lidar com isso.
            detalhes_texto = self.gerar_texto_log(jogada_dados, 0, 0, 0, html_format=False)
            html += detalhes_texto.replace("\n", "<br>").replace("Pontuação aplicada: 0 pontos", "")

            html += "</div></div>"

        # --- Fim do HTML ---
        html += """
            </div>
        </body>
        </html>
        """
        return html

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
