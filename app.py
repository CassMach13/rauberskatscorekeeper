import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from rauberskat_backend_oficial import RauberskatScorekeeper
from flask_cors import CORS

# --- Inicialização do Firebase ---
db = None  # Inicializa db como None para evitar NameError
try:
    # Tenta carregar as credenciais da variável de ambiente (Vercel/Produção)
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')

    if firebase_creds_json:
        print(f"DEBUG: Encontrei FIREBASE_CREDENTIALS (len={len(firebase_creds_json)})")
        # Carrega do JSON na variável de ambiente
        cred_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(cred_dict)
    elif os.path.exists("firebase-credentials.json"):
        print("DEBUG: Usando arquivo local firebase-credentials.json")
        # Fallback para arquivo local (Desenvolvimento)
        cred = credentials.Certificate("firebase-credentials.json")
    else:
        print("CRÍTICO: Nenhuma credencial do Firebase encontrada (Env ou Arquivo)!")
        cred = None

    if cred:
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("SUCESSO: Firebase conectado!")
except Exception as e:
    print(f"ERRO FATAL ao iniciar Firebase: {str(e)}")
    import traceback
    traceback.print_exc()

# --- Inicialização do Flask ---
# --- Inicialização do Flask ---
# Na Vercel, o Flask serve apenas a API. Arquivos estáticos são servidos pela CDN.
app = Flask(__name__)

# --- Configuração do CORS ---
# Isso permite que requisições de qualquer origem acessem sua API.
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- Rotas da API ---
# A rota '/' (index) foi removida pois o Vercel servirá o index.html da pasta public automaticamente.

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """
    Cria uma nova partida no Firestore.
    Recebe: {"player_names": ["Nome1", ...], "date": "...", "venue": "...", ...}
    Retorna: {"game_id": "ID_DA_NOVA_PARTIDA"}
    """
    data = request.get_json()
    player_names = data.get('player_names')

    if not player_names or len(player_names) not in [3, 4]:
        return jsonify({"error": "A lista de jogadores é inválida."}), 400

    # Cria o estado inicial do jogo
    initial_state = {
        "player_names": player_names,
        "num_players": len(player_names),
        "scores": {name: 0 for name in player_names},
        "current_mode": "Bock",
        "dealer_index": 0,
        "game_history": [],
        "previous_states": [],
        # Novos campos de detalhes da partida
        "date": data.get("date"),
        "venue": data.get("venue"),
        "table": data.get("table"),
        "start_time": data.get("start_time"),
        "end_time": data.get("end_time"),
        # Outros campos de estado do jogo
        "bock_rounds_played": 0,
        "ramsch_rounds_played": 0,
        "last_game_name": "",
        "ramsch_losses": {name: 0 for name in player_names},
        "ramsch_scores_count": {name: 0 for name in player_names},
        "ramsch_ramsch_count": 0,
        "dealer_turns_count": {name: 0 for name in player_names},
        "last_scoring_player": None,
        "awaiting_ramsch_decision": False,
        "ramsch_candidates": [],
        "last_was_bonus": False,
    }

    # Adiciona o novo documento de partida ao Firestore
    update_time, game_ref = db.collection('partidas').add(initial_state)
    
    # --- Log de Confirmação no Terminal ---
    print("\n" + "="*60)
    print("🎮 JOGO INICIADO!")
    print(f"👥 Jogadores: {', '.join(initial_state['player_names'])}")
    print(f"🔄 Rodada inicial: {initial_state['current_mode']}")
    # O dealer inicial é sempre o jogador no índice 0
    print(f"🎯 Dealer inicial: {initial_state['player_names'][0]}")
    print("="*60 + "\n")

    return jsonify({"game_id": game_ref.id}), 201

@app.route('/api/game/<game_id>/calculate', methods=['POST'])
def calculate(game_id):
    """
    Calcula a pontuação para uma jogada.
    Recebe: dados da jogada (mesmo formato que o frontend enviava antes)
    Retorna: estado atualizado do jogo.
    """
    try:
        scorekeeper = RauberskatScorekeeper(db, game_id)
        dados_jogada = request.get_json()
        
        # 1. Calcula a pontuação da jogada
        scorekeeper.calculate_score(dados_jogada)
        # 2. Verifica se a rodada deve mudar (ou se deve esperar uma decisão)
        scorekeeper.check_mode_transition()
        # 3. Avança o dealer (a menos que uma decisão esteja pendente)
        if not scorekeeper.awaiting_ramsch_decision:
            scorekeeper.next_dealer()
        
        scorekeeper._save_state() # Salva todas as alterações no banco de dados
        # Carrega o estado final para retornar ao frontend
        final_state = scorekeeper.game_ref.get().to_dict()
        return jsonify(final_state), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404 # Jogo não encontrado
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/game/<game_id>/undo', methods=['POST'])
def undo(game_id):
    """
    Desfaz a última jogada.
    Retorna: estado atualizado do jogo.
    """
    try:
        scorekeeper = RauberskatScorekeeper(db, game_id)
        if scorekeeper.undo_last_game():
            restored_state = scorekeeper.game_ref.get().to_dict()
            return jsonify(restored_state), 200
        else:
            return jsonify({"error": "Não há jogadas para desfazer."}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game_state(game_id):
    """
    Obtém o estado atual de uma partida.
    Retorna: estado atual do jogo.
    """
    try:
        game_ref = db.collection('partidas').document(game_id)
        game_data = game_ref.get().to_dict()
        if not game_data:
            return jsonify({"error": "Partida não encontrada."}), 404
        return jsonify(game_data), 200
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/api/game/<game_id>/decide_ramsch', methods=['POST'])
def decide_ramsch(game_id):
    """
    Processa a decisão de um jogador sobre iniciar uma nova rodada de Ramsch.
    Recebe: {"jogador": "NomeDoJogador", "deseja_nova_rodada": true/false}
    Retorna: estado atualizado do jogo.
    """
    try:
        scorekeeper = RauberskatScorekeeper(db, game_id)
        data = request.get_json()
        decisao_em_grupo = data.get('decisao_em_grupo', False)

        scorekeeper.processar_decisao_ramsch(jogador, deseja_nova_rodada, decisao_em_grupo)
        
        # O método processar_decisao_ramsch já salva o estado, então apenas o retornamos.
        final_state = scorekeeper.game_ref.get().to_dict()
        return jsonify(final_state), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    # O host='0.0.0.0' torna o servidor acessível na sua rede local
    app.run(host='0.0.0.0', port=5000, debug=True)
