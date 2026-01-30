class RauberskatScorekeeper:
    # Modificado para integração com Firebase
    def __init__(self, db, game_id):
        """
        Inicializa o Scorekeeper com uma referência ao banco de dados e um ID de partida.
        O estado do jogo será carregado do Firestore.
        """
        self.db = db
        self.game_id = game_id
        self.game_ref = self.db.collection('partidas').document(self.game_id)
        
        # Carrega os dados do jogo do Firestore.
        # Os atributos da classe (self.scores, self.current_mode, etc.)
        # serão definidos pelo método _load_state().
        self._load_state()

        self.base_scores = {
                "ouros": 9,
                "grand hand": 24,
                "copas": 10,
                "espadas": 11,
                "paus": 12,
                "null": 23,
                "grand": 24,
                "null hand": 35,
                "null ouvert": 46,
                "null hand ouvert": 59,
                "null revolution": 92,
                "durchmarsch": 120
            }

    def _load_state(self):
        """Carrega o estado do jogo do Firestore para os atributos da classe."""
        game_data = self.game_ref.get().to_dict()
        if not game_data:
            raise ValueError(f"Partida com ID '{self.game_id}' não encontrada no Firestore.")
        
        # Define os atributos da instância com base nos dados do DB
        self.scores = game_data.get("scores", {})
        self.player_names = game_data.get("player_names", [])
        self.num_players = game_data.get("num_players", 0)
        self.current_mode = game_data.get("current_mode", "Bock")
        self.dealer_index = game_data.get("dealer_index", 0)
        self.bock_rounds_played = game_data.get("bock_rounds_played", 0)
        self.ramsch_rounds_played = game_data.get("ramsch_rounds_played", 0)
        self.last_game_name = game_data.get("last_game_name", "")
        self.previous_states = game_data.get("previous_states", [])
        self.ramsch_losses = game_data.get("ramsch_losses", {})
        self.ramsch_scores_count = game_data.get("ramsch_scores_count", {})
        self.ramsch_ramsch_count = game_data.get("ramsch_ramsch_count", 0)
        self.dealer_turns_count = game_data.get("dealer_turns_count", {})
        self.last_scoring_player = game_data.get("last_scoring_player", None)
        self.game_history = game_data.get("game_history", [])
        self.awaiting_ramsch_decision = game_data.get("awaiting_ramsch_decision", False)
        self.ramsch_candidates = game_data.get("ramsch_candidates", [])
        self.last_was_bonus = game_data.get("last_was_bonus", False)

    def _save_state(self):
        """Salva o estado atual da instância da classe de volta no Firestore."""
        current_state = self.__dict__.copy()
        # Remove atributos que não devem ser serializados (referência ao DB)
        del current_state['db']
        del current_state['game_ref']
        del current_state['base_scores'] # É constante, não precisa salvar
        self.game_ref.set(current_state)

    @staticmethod
    def iniciar_jogo(db, nome_jogadores):
        num_players = len(nome_jogadores)
        if num_players not in [3, 4]:
            raise ValueError("Número de jogadores deve ser 3 ou 4.")

    def get_winners(self):
        max_score = max(self.scores.values())
        winners = [player for player, score in self.scores.items() if score == max_score]
        return winners, max_score
    
    def add_players(self, player_names):
        self.num_players = len(player_names)
        if self.num_players not in [3, 4]:
            raise ValueError("Número de jogadores deve ser 3 ou 4.")

        self.player_names = [name.strip() for name in player_names]
        self.scores = {player: 0 for player in self.player_names}
        self.ramsch_losses = {player: 0 for player in self.player_names}
        self.ramsch_scores_count = {player: 0 for player in self.player_names}
        self.ramsch_ramsch_count = 0
        self.dealer_turns_count = {player: 0 for player in self.player_names}
            
    def save_previous_state(self):
        state = {
            "scores": self.scores.copy(),
            "current_mode": self.current_mode,
            "bock_rounds_played": self.bock_rounds_played,
            "ramsch_rounds_played": self.ramsch_rounds_played,
            "last_game_name": self.last_game_name,
            "last_scoring_player": self.last_scoring_player,
            "dealer_index": self.dealer_index,
            "awaiting_ramsch_decision": self.awaiting_ramsch_decision,
            "ramsch_candidates": self.ramsch_candidates.copy(),
            "ramsch_losses": self.ramsch_losses.copy(),
            "ramsch_scores_count": self.ramsch_scores_count.copy(),
            "ramsch_ramsch_count": self.ramsch_ramsch_count,
            "dealer_turns_count": self.dealer_turns_count.copy(),
            "bonus_turns": getattr(self, "bonus_turns", 0),
            "last_was_bonus": getattr(self, "last_was_bonus", False),
            "game_history": self.game_history.copy(),  # Salva histórico            
        }
        self.previous_states.append(state)

    def undo_last_game(self):
        if not self.previous_states:
            print("❌ Não há jogos para desfazer!")            
            return False
        
        last_state = self.previous_states.pop()

        self.scores = last_state["scores"]
        self.current_mode = last_state["current_mode"]
        self.bock_rounds_played = last_state["bock_rounds_played"]
        self.ramsch_rounds_played = last_state["ramsch_rounds_played"]
        self.last_game_name = last_state["last_game_name"]
        self.last_scoring_player = last_state["last_scoring_player"]
        self.dealer_index = last_state["dealer_index"]
        self.awaiting_ramsch_decision = last_state.get("awaiting_ramsch_decision", False)
        self.ramsch_candidates = last_state.get("ramsch_candidates", [])
        self.ramsch_losses = last_state.get("ramsch_losses", {})
        self.ramsch_scores_count = last_state.get("ramsch_scores_count", {})
        self.ramsch_ramsch_count = last_state.get("ramsch_ramsch_count", 0)
        self.dealer_turns_count = last_state.get("dealer_turns_count", {})
        self.bonus_turns = last_state.get("bonus_turns", 0)
        self.last_was_bonus = last_state.get("last_was_bonus", False)
        self.game_history = last_state.get("game_history", [])  # Restaura histórico

        print("↩️  JOGO DESFEITO! Estado anterior restaurado.")
        self.display_scoreboard() # Mostra placar após desfazer
        self._save_state() # Salva o estado restaurado no DB
        return True

    def add_empate(self, jogador_que_empatou, jogador_principal):
        self.empates.append((jogador_que_empatou, jogador_principal))

    def print_scores(self):
        print("\n" + "="*50)
        print("📊 PLACAR ATUAL:")
        print("="*50)
        for player, score in self.scores.items():
            status = "🏆" if score == max(self.scores.values()) else "  "
            print(f"{status} {player}: {score:+d} pontos")
        print("="*50)
        self.display_scoreboard()
            
    def calculate_score(self, dados):
        jogador_nome = dados.get("jogador")
        game_name = dados.get("jogo", "").lower().strip()
        pontos = 0
        multiplicador = 1
        base_score = 0
        fator_total = 1

        print(f"🎯 Dealer: {self.get_current_dealer()}")
        print(f"🔄 Rodada: {self.current_mode}")
        print(f"👤 Jogador: {jogador_nome}")
        print(f"🃏 Jogo: {game_name.upper()}")

        if not dados:
            # Se não houver dados, não há o que salvar no histórico.
            # Adiciona um registro de erro ao histórico para depuração.
            self.game_history.append({"erro": "Nenhum dado recebido para calcular pontuação."})
            self.save_previous_state() # Salva o estado mesmo em erro para poder desfazer.
            raise ValueError("Nenhum dado recebido para calcular pontuação.")
        
        # Jogos Ouros, Copas, Espadas, Paus, Grand
        kontra = dados.get("kontra", False)
        reh = dados.get("reh", False)
        bock = dados.get("bock", False)
        rursch = dados.get("rursch", False)
        is_hand = dados.get("hand", False)
        jogador_perdedor = dados.get("perdeu", False)

        multiplicadores = 1
        if kontra:
            multiplicadores *= 2
        if reh:
            multiplicadores *= 2

        # Bock (independente do Bock declarado)
        if self.current_mode == "Bock":
            multiplicadores *= 2
        
        # O estado é carregado na inicialização.
        # A lógica de salvar o estado anterior agora é feita dentro do calculate_score
        # e o estado final é salvo no final do método.
        self.save_previous_state()

        jogador_nome = dados.get("jogador")
        if jogador_nome not in self.scores:
            raise ValueError(f"Jogador '{jogador_nome}' não encontrado nos jogadores cadastrados.")

        player_index = self.player_names.index(jogador_nome)
        game_name = str(dados.get("jogo", "")).strip().lower()
        
        # RAMSCH - Tratamento especial
        if game_name == "ramsch":           
            info = dados.get("info", {})
            skat_empurrado = info.get("skat_empurrado", 0)
            multiplicador = 2 ** skat_empurrado  # 0 → 1, 1 → 2, 2 → 4, 3 → 8
            
            try:
                pontos_ramsch = int(dados.get("pontos_ramsch", 0))
            except ValueError:
                pontos_ramsch = 0
            
            #Armazenar os pontos inseridos para exibição
            pontos_inseridos = pontos_ramsch

            jungfrau = dados.get("jungfrau", False)

            print(f"   📝 Pontos inseridos: {pontos_inseridos}")
            print(f"   📤 Skat empurrado: {skat_empurrado}x (multiplicador: {multiplicador})")            

            # Calcular os multiplicadores totais para exibição
            multiplicadores_totais = multiplicador  # Skat empurrado
            if jungfrau:
                pontos_ramsch *= 2
                multiplicadores_totais *= 2
                print("   👩 Jüngfrau (x2)")

            if self.current_mode == "Bock":
                pontos_ramsch *= 2
                multiplicadores_totais *= 2
                print("   🔥 Bock ativo (x2)")                

            pontos_ramsch *= multiplicador #Quantidade de vezes que o skat foi empurrado
            pontos_ramsch *= -1  # Sempre negativo

            self.scores[jogador_nome] += pontos_ramsch

            print(f"   🔢 Multiplicadores: {multiplicadores_totais}")
            print(f"   ➡️  Pontos finais para {jogador_nome}: {pontos_ramsch}")

            # Incrementa contador de derrotas para o jogador principal
            self.ramsch_scores_count[jogador_nome] = self.ramsch_scores_count.get(jogador_nome, 0) + 1

            # Tratamento de empates no Ramsch
            empates = dados.get("empates", [])
            if empates is None:
                empates = []
            elif isinstance(empates, str):
                empates = [empates]

            for jogador_empatado in empates:
                if jogador_empatado in self.scores:
                    if self.scores[jogador_empatado] == 0:
                        self.scores[jogador_empatado] = pontos_ramsch
                    else:
                        self.scores[jogador_empatado] += pontos_ramsch
                    
                    # Incrementa contador de derrotas para quem empatou também
                    self.ramsch_scores_count[jogador_empatado] = self.ramsch_scores_count.get(jogador_empatado, 0) + 1
                    
                    print(f"   🤝 Empate aplicado para {jogador_empatado}: {pontos_ramsch}")

            self.last_game_name = "ramsch"

            self.last_scoring_player = jogador_nome
            self.display_scoreboard()

            # Salva o resultado no histórico
            log_entry = dados.copy()
            log_entry['round_mode'] = self.current_mode
            log_entry['dealer'] = self.get_current_dealer() # Add Dealer
            log_entry['result'] = {'points': pontos_ramsch, 'total_factor': multiplicadores_totais, 'base_score': pontos_inseridos}
            self.game_history.append(log_entry)

            # Retornar os valores para o frontend (pontos_ramsch já é negativo)
            return pontos_ramsch, multiplicadores_totais, pontos_inseridos
        
        if game_name == "durchmarsch":          
            try:
                base_score = 120
                info = dados.get("info", {})
                skat_empurrado = info.get("skat_empurrado", 0)  # default 0 se não existir

                if self.current_mode == "Ramsch":
                    multiplicador = 2 ** skat_empurrado
                else:
                    multiplicador = skat_empurrado if skat_empurrado > 0 else 1

                pontos = base_score * multiplicador

                print(f"   📝 Pontos base: {base_score}")
                print(f"   📤 Skat empurrado: {skat_empurrado} (multiplicador: {multiplicador})")

                # Aplicar Bock se estiver em Bock
                if self.current_mode == "Bock":
                    multiplicador *= 2 # Atualiza o multiplicador total
                    print("   🔥 Bock ativo (x2)")
                
                pontos = base_score * multiplicador
                self.scores[jogador_nome] += pontos

                print(f"   ➡️  Pontos finais para {jogador_nome}: {pontos}")

                self.last_game_name = "durchmarsch"
                self.last_scoring_player = jogador_nome
                self.last_was_bonus = False
                self.display_scoreboard()

                # Salva o resultado no histórico
                log_entry = dados.copy()
                log_entry['round_mode'] = self.current_mode
                log_entry['result'] = {'points': pontos, 'total_factor': multiplicador, 'base_score': base_score}
                self.game_history.append(log_entry)

                return pontos, multiplicador, base_score
            # O estado final será salvo no final do método calculate_score
            
            except Exception as e:
                print(f"[ERROR] Erro no cálculo do Durchmarsch: {e}")
                # Em caso de erro, definir valores padrão
                base_score = 120
                multiplicador = 1
                pontos = base_score
                
                self.scores[jogador_nome] += pontos
                self.last_game_name = "durchmarsch"
                self.last_scoring_player = jogador_nome
                self.last_was_bonus = False
                self.display_scoreboard()

                # Salva o resultado no histórico
                log_entry = dados.copy()
                log_entry['round_mode'] = self.current_mode
                log_entry['result'] = {'points': pontos, 'total_factor': multiplicador, 'base_score': base_score}
                self.game_history.append(log_entry)
                
                return pontos, multiplicador, base_score
            # O estado final será salvo no final do método calculate_score

        # Jogos Ouros, Copas, Espadas, Paus, Grand
        com_sem = dados.get("com_sem")
        schneider = dados.get("schneider", False)
        schneider_announced = dados.get("schneider_anunciado", False)
        schwarz = dados.get("schwartz", False)
        schwarz_announced = dados.get("schwartz_anunciado", False)
        is_ouvert = dados.get("ouvert", False)

        if game_name == "grand" and is_ouvert:
            base_score = 36
        else:
            base_score = self.base_scores.get(game_name, 0)

        # Tratamento especial para jogos NULL
        if game_name in ["null", "null revolution"]:
            if game_name == "null revolution":
                base_score = 92
                game_type_log = "NULL REVOLUTION"
                print(f"   🎯 Tipo: {game_type_log}")
            else: # Jogo "null" normal
                is_hand = dados.get("hand", False)
                is_ouvert = dados.get("ouvert", False)
            # Definir pontuação base correta para Null
                if is_hand and is_ouvert:
                    base_score = 59
                    game_type_log = "NULL HAND OUVERT"
                    print(f"   🎯 Tipo: {game_type_log}")
                elif is_hand:
                    base_score = 35
                    game_type_log = "NULL HAND"
                    print(f"   🎯 Tipo: {game_type_log}")
                elif is_ouvert:
                    base_score = 46
                    game_type_log = "NULL OUVERT"
                    print(f"   🎯 Tipo: {game_type_log}")
                else:
                    base_score = 23
                    game_type_log = "NULL"
                    print(f"   🎯 Tipo: {game_type_log}")

            # Multiplicadores aplicáveis (Kontra, Reh, Rursch, Bock)
            multiplicador = 1
            if dados.get("kontra", False): 
                multiplicador *= 2
                print("   ⚔️  KONTRA!")
            if dados.get("reh", False): 
                multiplicador *= 2
                print("   🔥 REH!")
            if dados.get("bock", False):
                multiplicador *= 2
                print("   💥 BOCK!")
            if dados.get("rursch", False):
                multiplicador *= 2
                print("   🌪️  RURSCH!")

            #Multiplicação pela rodada de Bock
            if self.current_mode == "Bock":
                multiplicador *= 2
                print("   🔥 Bock ativo (x2)")

            # Se o jogador perdeu, a pontuação vira negativa
            if jogador_perdedor:
                is_hand = dados.get("hand", False) # Precisamos verificar o hand aqui também
                if is_hand:
                    multiplicador *= -1 #Se perdeu com Hand, multiplica por -1
                    print("   ❌ PERDEU (Hand: x-1)")
                else:
                    multiplicador *= -2 #Se perdeu sem Hand, multiplica por -2
                    print("   ❌ PERDEU (Sem Hand: x-2)")
            else:
                print("   ✅ GANHOU!")

            pontos = base_score * multiplicador

            print(f"   🔢 Multiplicadores: {multiplicador}")
            print(f"   📝 Pontos base: {base_score}")                         

            self.scores[jogador_nome] += pontos
            print(f"   ➡️  Pontos finais para {jogador_nome}: {pontos}")

            self.last_game_name = "null"
            self.last_scoring_player = jogador_nome
            self.display_scoreboard()

            # Salva o resultado no histórico
            log_entry = dados.copy()
            log_entry['game_type_log'] = game_type_log # Salva o tipo específico de Null
            log_entry['round_mode'] = self.current_mode
            log_entry['result'] = {'points': pontos, 'total_factor': multiplicador, 'base_score': base_score}
            self.game_history.append(log_entry)
            
            return pontos, multiplicador, base_score
        # O estado final será salvo no final do método calculate_score
        
        if game_name == "grand hand":
            # Ajustes especiais para Grand Hand
            base_score = 24  # Base de Grand normal
            is_hand = True  # Sempre Hand
            is_ouvert = dados.get("ouvert", False)  # Ouvert ainda pode ser perguntado
            jogador_perdedor = dados.get("perdeu", False)

            if is_ouvert:
                base_score = 36  # Se foi Ouvert, base é 36
                print("   🎯 GRAND HAND OUVERT")

            try:
                com_sem = int(dados.get("com_sem", 1))
            except (TypeError, ValueError):
                com_sem = 1

            factor = com_sem + 1 #Exemplo com_sem = 1 - Factor 2
            factor += 1 #Hand automático

            print(f"   📝 Com/Sem: {com_sem}")
            print(f"   ✋ Hand automático (+1)")

            # Adicionar fatores de Schneider e Schwarz
            if dados.get("schneider", False):
                factor += 1
                print("   🎯 Schneider (+1)")
            if dados.get("schneider_anunciado", False):
                factor += 1
                print("   📢 Schneider anunciado (+1)")
            if dados.get("schwartz", False):
                factor += 1
                print("   ⚫ Schwarz (+1)")
            if dados.get("schwartz_anunciado", False):
                factor += 1
                print("   📢 Schwarz anunciado (+1)")

            multiplicadores = 1
            if dados.get("kontra", False): 
                multiplicadores *= 2
                print("   ⚔️  KONTRA!")
            if dados.get("reh", False): 
                multiplicadores *= 2
                print("   🔥 REH!")
            if dados.get("bock", False): 
                multiplicadores *= 2 # Bock declarado
                print("   💥 BOCK (declarado)!")
            if dados.get("rursch", False): 
                multiplicadores *= 2
                print("   🌪️  RURSCH!")

            # Cálculo final
            pontos = base_score * factor * multiplicadores
            fator_total = factor * multiplicadores

            # Se perdeu, multiplica apenas por -1 (nunca -2 para Grand Hand)
            if jogador_perdedor:
                pontos *= -1
                fator_total *= -1 # Aplica a penalidade ao fator total também
                print("   ❌ PERDEU (x-1)")
            else:
                print("   ✅ GANHOU!")
            print(f"   📝 Pontos base: {base_score}")

            self.scores[jogador_nome] += pontos

            print(f"   ➡️  Pontos finais para {jogador_nome}: {pontos}")

            self.last_game_name = "grand hand"
            self.last_scoring_player = jogador_nome
            self.last_was_bonus = True #Garante que o contador de rodada de Ramsch não avance
            # Se for Grand Hand durante uma rodada de Ramsch, o dealer não muda.
            if self.current_mode == "Ramsch":
                print("Grand Hand em rodada de Ramsch. Dealer não avança.")
                self.last_was_bonus = True

            # Salva o resultado no histórico
            log_entry = dados.copy()
            log_entry['round_mode'] = self.current_mode
            log_entry['result'] = {'points': pontos, 'total_factor': fator_total, 'base_score': base_score}
            self.game_history.append(log_entry)

            self.display_scoreboard()
            
            return pontos, fator_total, base_score
        # O estado final será salvo no final do método calculate_score

        else:
            # Validação para jogos que exigem 'com_sem'
            if not com_sem:
                raise ValueError("Para este tipo de jogo, o valor 'Com ou Sem' é obrigatório.")

            try:
                factor = int(com_sem) + 1
            except (TypeError, ValueError):
                factor = 1

        print(f"   📝 Com/Sem: {com_sem} (fator base: {factor})")

        if is_hand:
            factor += 1
            print("   ✋ Hand (+1)")

        if is_ouvert and game_name != "grand":
            factor += 1
            print("   👁️  Ouvert (+1)")
        elif is_ouvert and game_name == "grand":
            print("   👁️  grand ouvert: Apenas base muda para 36 (sem +1 no fator).")

        if schneider:
            factor += 1
            print("   🎯 Schneider (+1)")

        if schneider_announced:
            factor += 1
            print("   📢 Schneider anunciado (+1)")

        if schwarz:
            factor += 1
            print("   ⚫ Schwarz (+1)")

        if schwarz_announced:
            factor += 1
            print("   📢 Schwarz anunciado (+1)")
        
        # APLICANDO A NOVA LÓGICA DE CÁLCULO SEQUENCIAL
        # Os multiplicadores agora afetam o 'factor' diretamente em cadeia.
        if kontra:
            factor *= 2
            print("   ⚔️  KONTRA!")
        if reh:
            factor *= 2
            print("   🔥 REH!")
        if bock:
            factor *= 2
            print("   💥 BOCK!")
        if rursch:
            factor *= 2
            print("   🌪️  RURSCH!")

        # Bock (independente do Bock declarado)
        if self.current_mode == "Bock":
            factor *= 2
            print("   🔥 Bock ativo (x2)")

        # Se o jogador perdeu, aplicamos o fator negativo
        if jogador_perdedor:
            if is_hand:
                factor *= -1
                print("   ❌ PERDEU (Hand: x-1)")                
            else:
                factor *= -2
                print("   ❌ PERDEU (Sem Hand: x-2)")
        else:
            print("   ✅ GANHOU!")

        # O fator total agora é o próprio 'factor' após todas as operações
        fator_total = factor
        pontos = base_score * fator_total

        print(f"   📝 Pontos base: {base_score}")
        print(f"   🔢 Fator Total: {fator_total}")        

        # Salva nos scores
        self.scores[jogador_nome] += pontos

        print(f"   ➡️  Pontos finais para {jogador_nome}: {pontos}")

        # Marcar jogo como último jogado
        self.last_game_name = game_name
        self.last_scoring_player = jogador_nome
        self.last_was_bonus = False
        self.display_scoreboard()

        # Salva o resultado no histórico para jogos normais
        log_entry = dados.copy()
        log_entry['round_mode'] = self.current_mode
        log_entry['dealer'] = self.get_current_dealer() # Add Dealer
        log_entry['result'] = {'points': pontos, 'total_factor': fator_total, 'base_score': base_score}
        self.game_history.append(log_entry)

        # Retornar valores finais ao frontend
        return pontos, fator_total, base_score

    def apply_empates(self, dados, pontos_ramsch):
        """
        Atualiza o placar dos jogadores que empataram no Ramsch.

        :param dados: dicionário com informações da jogada atual.
        :param pontos_ramsch: pontuação a ser somada no placar dos jogadores empatados.
        """
        self.scores[jogador_nome] += pontos_ramsch

        # Tratar empate no Ramsch (se existir)
        empates = dados.get("empates", [])

        # Corrigir caso venha uma string e não lista
        if isinstance(empates, str):
            empates = [empates]
        print(f"Empates após conversão: {empates}")
        for jogador_empatado in empates:
            print(f"Verificando empate para o jogador: {jogador_empatado}")
            if jogador_empatado in self.scores:
                if self.scores[jogador_empatado] == 0:
                    self.scores[jogador_empatado] = pontos_ramsch
                else:
                    self.scores[jogador_empatado] += pontos_ramsch
        else:
            print(f"{jogador_empatado} não encontrado em self.scores")

    def increment_turn_count(self):
        """Incrementa contador de jogadas com debug"""
        if not hasattr(self, 'turn_count'):
            print("⚠️  AVISO: turn_count não existe, criando com valor 1")
            self.turn_count = 1
        else:
            self.turn_count += 1
            print(f"✅ turn_count incrementado para: {self.turn_count}")

    # Método para inicializar turn_count se não existir
    def initialize_turn_count(self):
        """Inicializa turn_count se não existir"""
        if not hasattr(self, 'turn_count'):
            self.turn_count = 0
            print("✅ turn_count inicializado com 0")

    def display_scoreboard(self):
        """Mostra o placar atualizado após cada jogada"""
        # Incrementa o contador
        if not hasattr(self, 'manual_turn_count'):
            self.manual_turn_count = 0
        self.manual_turn_count += 1
        
        print("\n" + "=" * 50)
        print("📊 PLACAR ATUAL")
        print("=" * 50)
        print(f"📝 Jogada: {self.manual_turn_count}")
        
        # Exibe todos os jogadores
        for i, jogador in enumerate(self.player_names):
            try:
                pontos = self.scores[jogador]
                
                # Indica se é o dealer atual
                if i == self.dealer_index:
                    emoji = "🎯"  # Dealer atual
                else:
                    emoji = "👤"  # Jogador normal
                    
                # Formata pontos: 0 sem sinal, outros com sinal
                if pontos == 0:
                    print(f"{emoji} {jogador}: 0 pontos")
                else:
                    print(f"{emoji} {jogador}: {pontos:+d} pontos")
                    
            except KeyError:
                print(f"❌ ERRO: Jogador '{jogador}' não encontrado nos scores")
            except Exception as e:
                print(f"❌ ERRO inesperado para '{jogador}': {e}")
        
        # Mostra informações adicionais do jogo
        
        if hasattr(self, 'current_mode') and self.current_mode:
            print(f"🔄 Rodada: {self.current_mode}")
        
        if hasattr(self, 'dealer_index') and hasattr(self, 'player_names'):
            print(f"🎲 Dealer: {self.player_names[self.dealer_index]}")
        
        print("=" * 50)

    def check_mode_transition(self):
        """Verifica e faz a transição automática entre Bock e Ramsch."""
        print("\n[DEBUG] Iniciando verificação de transição de modo...")
        if self.current_mode == "Ramsch":
            # Se não foi uma jogada bônus, avança o contador de rodadas
            if not getattr(self, 'last_was_bonus', False):
                self.ramsch_rounds_played += 1
                # Se o último jogo foi um "ramsch", incrementa os contadores da regra especial
                if self.last_game_name == "ramsch":
                    self.ramsch_ramsch_count += 1
                    # A contagem de perdas agora é feita diretamente no calculate_score para incluir empates
            # Zera o indicador de bônus após o tratamento
            if getattr(self, 'last_was_bonus', False):
                self.last_was_bonus = False

            # Quando o número de rodadas de Ramsch for igual ao número de jogadores, a rodada acaba.
            print(f"[DEBUG] Rodadas de Ramsch jogadas: {self.ramsch_rounds_played}/{self.num_players}")
            if self.ramsch_rounds_played >= self.num_players:
                print("[DEBUG] Fim da rodada de Ramsch. Verificando regra especial...")
                # Verifica a condição para a regra especial de nova rodada de Ramsch.
                # Agora procuramos por uma lista de candidatos.
                self.ramsch_candidates = []
                # A regra só se aplica se houver pelo menos um jogo "ramsch" na rodada
                print(f"[DEBUG] Total de jogos 'ramsch' na rodada: {self.ramsch_ramsch_count}")
                if self.ramsch_ramsch_count > 0:
                    for player, loss_count in self.ramsch_scores_count.items():
                        print(f"[DEBUG] Verificando jogador: {player}...")
                        print(f"[DEBUG]   > Perdas em Ramsch (incluindo empates): {loss_count}")
                        
                        # A condição agora é simples: se perdeu 3 ou mais vezes.
                        if loss_count >= 3:
                            print(f"[DEBUG]   > CONDIÇÃO ATINGIDA! {player} perdeu {loss_count} vezes.")
                            self.ramsch_candidates.append(player)

                if self.ramsch_candidates:
                    print("[DEBUG] Backend em modo de espera pela decisão do(s) candidato(s).")
                    # Encontrou um candidato. O backend agora espera a decisão do frontend.
                    self.awaiting_ramsch_decision = True
                    print(f"Candidatos para nova rodada de Ramsch: {', '.join(self.ramsch_candidates)}")
                    return  # Espera decisão do frontend

                # Se não houver candidato para a regra especial, transita para Bock normalmente.
                self._reset_to_bock_round()
        
        elif self.current_mode == "Bock":
            if not getattr(self, 'last_was_bonus', False):
                self.bock_rounds_played += 1
                print(f"[DEBUG] Rodadas de Bock jogadas: {self.bock_rounds_played}/{self.num_players}")

                if self.bock_rounds_played >= self.num_players:
                    self.bock_rounds_played = 0
                    self.current_mode = "Ramsch"
                    # Zera os contadores para a nova rodada de Ramsch
                    self.ramsch_rounds_played = 0
                    self.ramsch_ramsch_count = 0
                    self.ramsch_scores_count = {p: 0 for p in self.scores.keys()}
                    self.dealer_turns_count = {p: 0 for p in self.scores.keys()}
                    
                    print("Mudança para a rodada de Ramsch.")
            
            if getattr(self, 'last_was_bonus', False):
                self.last_was_bonus = False
        self._save_state() # Salva o estado após a transição

    def processar_decisao_ramsch(self, jogador, deseja_nova_rodada, decisao_em_grupo=False):
        if not self.awaiting_ramsch_decision or not self.ramsch_candidates:
            return  # Não está aguardando decisão

        if not deseja_nova_rodada:
            # Se qualquer jogador recusar, a rodada de Bock começa imediatamente.
            print(f"{jogador} recusou a nova rodada de Ramsch. Mudando para Bock.")
            
            # Avança o dealer manualmente pois next_dealer() foi pulado na espera
            self.dealer_index = (self.dealer_index + 1) % self.num_players
            print(f"Dealer avançado manualmente para: {self.player_names[self.dealer_index]}")

            self._reset_to_bock_round()
            self.awaiting_ramsch_decision = False
            self.ramsch_candidates = []
            self._save_state() # Salva a mudança para Bock
            return

        # Decisão em grupo (Atomicidade) - Se todos aceitaram via flag ou jogador especial
        if (decisao_em_grupo or jogador == 'todos') and deseja_nova_rodada:
            print("Decisão em grupo recebida: Todos aceitaram. Esvaziando lista.")
            self.ramsch_candidates = [] # Esvazia a lista para forçar o início imediato
        
        # Remove o jogador que aceitou da lista de pendentes (fluxo normal)
        elif jogador in self.ramsch_candidates:
            self.ramsch_candidates.remove(jogador)

        # Se todos os candidatos aceitaram (lista ficou vazia), inicia nova rodada de Ramsch.
        if not self.ramsch_candidates:
            print("Todos os candidatos aceitaram. Iniciando nova rodada completa de Ramsch.")
            
            # Avança o dealer manualmente pois next_dealer() foi pulado na espera
            self.dealer_index = (self.dealer_index + 1) % self.num_players
            print(f"Dealer avançado manualmente para: {self.player_names[self.dealer_index]}")

            # Reinicia os contadores para uma nova rodada de Ramsch
            self.ramsch_rounds_played = 0
            self.ramsch_ramsch_count = 0
            self.ramsch_scores_count = {p: 0 for p in self.scores.keys()}
            self.dealer_turns_count = {p: 0 for p in self.scores.keys()} # Zera também o contador de turnos de dealer
            self.awaiting_ramsch_decision = False
            self._save_state() # Salva o reinício da rodada Ramsch

    def _reset_to_bock_round(self):
        self.current_mode = "Bock"
        self.ramsch_turns = 0
        self.ramsch_rounds_played = 0
        self.ramsch_ramsch_count = 0
        self.ramsch_losses = {p: 0 for p in self.scores.keys()}
        self.ramsch_scores_count = {p: 0 for p in self.scores.keys()}
        self.dealer_turns_count = {p: 0 for p in self.scores.keys()}
        print("Mudança para a rodada de Bock.")

    def exibir_info(self):
        print(f"Rodada atual: {self.current_mode}")
        print(f"Dealer: {self.player_names[self.dealer_index]}")

    def get_current_dealer(self):
        """Retorna o nome do dealer atual."""
        if not self.scores or self.dealer_index >= len(self.scores):
            return "Desconhecido"
        return self.player_names[self.dealer_index]

    def next_dealer(self):
        """Ajusta o dealer para a próxima rodada."""
        if self.current_mode == "Ramsch" and self.last_game_name == "grand hand":
            print("A próxima jogada será distribuída pelo mesmo dealer (jogada bônus).")
            self.last_game_name = None #usa para resetar a rodada bônus e poder seguir em frente
        else:
            # Incrementa o contador de turnos do dealer ANTES de mudar para o próximo
            current_dealer_name = self.get_current_dealer()
            if current_dealer_name in self.dealer_turns_count:
                self.dealer_turns_count[current_dealer_name] += 1

            self.dealer_index = (self.dealer_index + 1) % len(self.scores)
            print(f"Novo dealer: {self.player_names[self.dealer_index]}")
        self._save_state() # Adicionado para garantir que a mudança do dealer seja salva no DB
        #Se o jogo atual não for Grand Hand, resetar last_game_name
        if self.last_game_name != "grand hand":
            self.last_game_name = ""
                
def obter_nome_jogo(current_mode):
    if current_mode == "Ramsch":
        jogos_validos = ["grand hand", "durchmarsch", "ramsch"]
    else:
        jogos_validos = ["ouros", "copas", "espadas", "paus", "null", "grand", "null revolution", "durchmarsch", "ramsch"]
    print("Jogos válidos para a rodada atual:")
    for jogo in jogos_validos:
        print(jogo)

    while True:
        nome_jogo = input("Nome do jogo: ").strip().lower()
        if nome_jogo in jogos_validos:
            return nome_jogo
        else:
            print("Entrada inválida. Por favor, digite um nome de jogo válido.")

def obter_fator():
    while True:
        try:
            fator = int(input("Com ou Sem (1 a 4)? "))
            if fator not in [1, 2, 3, 4]:
                raise ValueError("O fator deve ser entre 1 e 4.")
            return fator
        except ValueError as e:
            print(e)

def obter_booleano(prompt):
    while True:
        resposta = input(prompt + " (true/false): ").strip().lower()
        if resposta in ['true', 'false']:
            return resposta == 'true'
        else:
            print("Entrada inválida. Por favor, digite 'true' ou 'false'.")
    
def main():
    scorekeeper = RauberskatScorekeeper()
    scorekeeper.add_players()
    
    while True:
        print("\n1. Adicionar nova pontuação")
        print("2. Desfazer última jogada")
        print("3. Fim de jogo")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            scorekeeper.exibir_info()
            scorekeeper.calculate_score()
            scorekeeper.increment_turn_count()
            scorekeeper.check_mode_transition()
            scorekeeper.next_dealer()
            scorekeeper.print_scores()
        elif opcao == "2":
            scorekeeper.undo_last_game()
        elif opcao == "3":
            print("Placar final:")
            scorekeeper.print_scores()
            winners, winner_score = scorekeeper.get_winners()
            if len(winners) == 1:
                print(f"PARABÉNS!! {winners[0]} ganhou com {winner_score} pontos!")
            else:
                print(f"PARABÉNS!! {' e '.join(winners)} ganharam com {winner_score} pontos!")
            max_pontos = max(scorekeeper.scores[jogador] for jogador in winners)
            arrecadacao_total = 0
            # Calcula a taxa de caixa para os não-ganhadores
            for jogador, pontos in scorekeeper.scores.items():
                if jogador not in winners:
                    diferenca = max_pontos - pontos
                    taxa_caixa = diferenca * 0.05 #valor cobrado por ponto de diferença do jogador ganhardor
                    arrecadacao_total += taxa_caixa
                    print(f"Taxa de caixa para {jogador}: R${taxa_caixa:.2f} (Diferença de {diferenca} pontos)")
                    print(f"\nArrecadação total deste jogo: R${arrecadacao_total:.2f}")
                
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()