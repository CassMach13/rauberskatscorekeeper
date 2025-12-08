# 📘 Räuberskat Scorekeeper

## 🎯 Visão Geral
O **Räuberskat Scorekeeper** é um aplicativo em **Python + PyQt6** para cálculo automatizado de pontuações do jogo **Räuberskat**, uma variante do Skat.  
O objetivo é reduzir erros manuais de contagem e tornar a experiência mais fluida, com interface clara e cálculos automáticos de multiplicadores, fatores e regras especiais.  

Este README unifica:  
- 📖 **Contexto** → Regras detalhadas do jogo.  
- 📝 **Backlog** → Funcionalidades planejadas e correções necessárias.  

---

## 🃏 Contexto do Jogo

### Estrutura da Partida
- **Rodadas**: Bock e Ramsch.  
- **Jogadores**: 3 ou 4.  
- **Dealer** rotativo.  
- Rodada Ramsch deve ser repetida até sair Ramsch/Durchmarsch válido.  
- Jogada bônus: **Grand Hand em Ramsch** repete dealer.  

### Tipos de Jogos
- **Bock**: Ouros, Copas, Espadas, Paus, Grand, Null, Null Revolution, Ramsch, Durchmarsch.  
- **Ramsch**: Ramsch, Grand Hand, Durchmarsch.  

### Pontuação Base
- Ouros = 9  
- Copas = 10  
- Espadas = 11  
- Paus = 12  
- Grand = 24 (36 se Ouvert)  
- Null = fixo (23 a 92 dependendo da variação)  
- Durchmarsch = 120  

### Ajustes e Multiplicadores
- **Somadores de fator**: Hand, Ouvert, Schneider, Schwarz (e anunciados).  
- **Multiplicadores**:  
  - Rodada Bock (x2)  
  - Kontra (x2), Reh (x2), Bock (x2), Rürsch (x2)
  - Jogador perdedor quando o jogo não é Hand (x-2)
  - Jüngfrau (x2, Ramsch)  
  - Skat empurrado (x2 por empurrada, até x8)  

### Ordem de Cálculo
1. Determina o jogo.
2. Determina o fator Com ou Sem.
3. Ajusta fator com Hand, Ouvert, Schneider, Schwarz e Anunciados.  
4. Aplica multiplicadores opcionais (Kontra, Reh, Bock, Rürsch).  
5. Aplica rodada especial (Bock ou Ramsch).  
6. Ajusta para derrota (sinal).
7. Determina a pontuação base.
8. Atualiza acumulado.  

### Casos Especiais
- **Empates no Ramsch** → pontuações integrais, sem divisão.  
- **Durchmarsch em Bock** → apenas multiplicação x2 da rodada.  
- **Durchmarsch em Ramsch** → apenas skat empurrado.  
- **Fim do jogo** → horário definido (ou número de rodadas, sempre acordado antes do ínicio).  
- **Pagamentos** → diferença para o vencedor × R$0,05.  

---

## 🖥️ Fluxo no Aplicativo

1. **Início do jogo**:  
   - Usuário define número de jogadores e nomes.  
   - App reseta estado e inicializa placar.  

2. **Durante o jogo**:  
   - Seleção de jogador + tipo de jogo.  
   - Inserção de variáveis (Hand, Ouvert, Kontra etc.).  
   - Cálculo da pontuação → resumo exibido em log.  
   - Adição da pontuação → tabela de resumo atualizada.  

3. **Fim do jogo**:  
   - Determina vencedor ou empate.  
   - Calcula valores a pagar ao caixa.  
   - Resumo permanece visível até novo jogo começar.  

4. **Novo jogo**:  
   - Reseta tabela, placares acumulados e log.  
   - Mantém interface limpa para recomeçar.  

---

## 📊 Tabela Resumo

- Linhas = jogadas.  
- Colunas = jogadores + coluna “Spiel”.  
- Valores acumulados exibidos.  
- **Cores**: verde (positivo), vermelho (negativo), preto (neutro).  

---

## 📝 Backlog de Desenvolvimento

### 🔧 Correções
- Ajustar bug de desfazer jogada (pontuação acumulada incorreta).  
- Corrigir log em jogos Grand Hand (não aparece corretamente).  

### 🆕 Funcionalidades sugeridas
- Jogador que atingir **-1000 pontos** joga em pé por 3 rodadas.  
- Jogador que perder **3 Ramsch na mesma rodada** pode solicitar nova rodada de Ramsch.  
- Mensurar **Überreights no leilão** em Bock:  
  - Caso detectado → jogo perdido automaticamente.  
  - Registrar motivo no log.  

---

## 🚀 Como Rodar o App

1. Instale dependências:
   ```bash
   pip install PyQt6
   ```
2. Converta interface caso alterada:
   ```bash
   pyuic6 -x rauberskat_interface_V2.ui -o rauberskat_interface_V2.py
   ```
3. Execute:
   ```bash
   python rauberskat_app_V1_5.py
   ```
4. O app abre em **tela cheia** automaticamente.  

---

## 📂 Estrutura de Arquivos
- `rauberskat_backend_oficial.py` → regras e cálculos.  
- `rauberskat_interface_V2.py` → interface (Qt Designer).  
- `rauberskat_app_V1_5.py` → integração frontend/backend.  
- `Contexto_Rauberskat_Scorekeeper.md` → regras detalhadas.  
- `Backlog_de_Desenvolvimento_App_Skat.md` → melhorias futuras.