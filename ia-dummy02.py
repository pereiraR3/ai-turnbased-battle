import sys
import math

GRID_SIZE = 5

# --- Funções Auxiliares ---
def parse_board(board_str):
    """Converte a string do tabuleiro em uma lista 2D."""
    board_list = list(map(int, list(board_str)))
    matrix = []
    for i in range(0, GRID_SIZE):
        matrix.append(board_list[i * GRID_SIZE : (i + 1) * GRID_SIZE])
    return matrix

def find_positions(board_matrix, player_id):
    """Encontra as posições do jogador, inimigo, arma e coração."""
    enemy_id = 1 if player_id == 2 else 2
    pos = {'player': None, 'enemy': None, 'weapon': None, 'heart': None}
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board_matrix[r][c] == player_id:
                pos['player'] = (c, r) # Formato (x, y)
            elif board_matrix[r][c] == enemy_id:
                pos['enemy'] = (c, r)
            elif board_matrix[r][c] == 3: # ID da Arma
                pos['weapon'] = (c, r)
            elif board_matrix[r][c] == 4: # ID do Coração
                pos['heart'] = (c, r)
    return pos

def manhattan_distance(pos1, pos2):
    """Calcula a distância de Manhattan entre dois pontos."""
    if pos1 is None or pos2 is None:
        return float('inf') 
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_adjacent_positions(pos):
    """Retorna uma lista de posições adjacentes válidas (dentro da grade)."""
    x, y = pos
    adjacent = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                adjacent.append((nx, ny))
    return adjacent

def move_towards(my_pos, target_pos, occupied_pos=None):
    """Determina o melhor movimento único em direção ao alvo, evitando posições ocupadas."""
    if my_pos is None or target_pos is None:
        return "up" # Movimento padrão se algo estiver errado

    occupied = occupied_pos if occupied_pos else set()

    possible_moves = {}
    my_x, my_y = my_pos
    target_x, target_y = target_pos

    # Verifica todos os 8 movimentos possíveis
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            new_x, new_y = my_x + dx, my_y + dy
            new_pos = (new_x, new_y)

            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and new_pos not in occupied:
                possible_moves[(dx, dy)] = manhattan_distance(new_pos, target_pos)

    if not possible_moves:
        return "block" # Sem movimentos válidos, melhor defender

    best_move_diff = min(possible_moves.values())
    best_moves = [move for move, dist in possible_moves.items() if dist == best_move_diff]

    # Prioriza direções com base no alvo
    if best_moves:
        if target_x > my_x and (1, 0) in best_moves: return "right"
        if target_x < my_x and (-1, 0) in best_moves: return "left"
        if target_y > my_y and (0, 1) in best_moves: return "down"
        if target_y < my_y and (0, -1) in best_moves: return "up"
        # Se a diagonal for a melhor e estiver disponível
        if target_x > my_x and target_y > my_y and (1, 1) in best_moves: return "down" 
        if target_x < my_x and target_y > my_y and (-1, 1) in best_moves: return "down"
        if target_x > my_x and target_y < my_y and (1, -1) in best_moves: return "up"  
        if target_x < my_x and target_y < my_y and (-1, -1) in best_moves: return "up" 

        # Retorna o primeiro melhor movimento se não houver prioridade clara
        dx, dy = best_moves[0]
        if dx == 1: return "right"
        elif dx == -1: return "left"
        elif dy == 1: return "down"
        elif dy == -1: return "up"

    return "block" 

# --- Lógica Principal para ia-phost.py (Melhorado) ---

# 1. Estado dos parâmetros
player_id = int(sys.argv[1])
enemy_id = 1 if player_id == 2 else 2
board_str = sys.argv[2]
my_life = int(sys.argv[3]) if player_id == 1 else int(sys.argv[4])
enemy_life = int(sys.argv[4]) if player_id == 1 else int(sys.argv[3])
my_bullets = int(sys.argv[5]) if player_id == 1 else int(sys.argv[6])

# 2. Processa o estado
board_matrix = parse_board(board_str)
positions = find_positions(board_matrix, player_id)
pos_player = positions['player']
pos_enemy = positions['enemy']
pos_weapon = positions['weapon']
pos_heart = positions['heart']

# Segurança caso a posição do jogador não seja encontrada
if pos_player is None:
    print("up")
    sys.exit()

# 3. Analisa a situação

# Podemos atacar o inimigo?
can_attack = False
if pos_enemy:
    dist_to_enemy_diag = max(abs(pos_player[0] - pos_enemy[0]), abs(pos_player[1] - pos_enemy[1]))
    if dist_to_enemy_diag <= 1:
        can_attack = True

# Devemos priorizar pegar o coração?
low_health_threshold = 5
needs_heart = my_life < 9 and pos_heart is not None
very_low_health = my_life <= low_health_threshold

# Devemos priorizar pegar a arma?
needs_weapon = my_bullets == 0 and pos_weapon is not None

# O inimigo provavelmente nos atacará no próximo turno? (O dummy sempre se move para perto e depois ataca)
enemy_is_adjacent = can_attack

# 4. Lógica de Tomada de Decisão

# Prioridade 1: Vitória Imediata
if can_attack and enemy_life <= (2 if my_bullets > 0 else 1):
    print("attack")
    sys.exit()

# Prioridade 2: Curar se a vida estiver muito baixa e o coração estiver adjacente
if very_low_health and pos_heart and manhattan_distance(pos_player, pos_heart) == 1:
    print(move_towards(pos_player, pos_heart, {pos_enemy} if pos_enemy else {}))
    sys.exit()

# Prioridade 3: Pegar a arma se disponível e sem balas
if needs_weapon and manhattan_distance(pos_player, pos_weapon) == 1:
    print(move_towards(pos_player, pos_weapon, {pos_enemy} if pos_enemy else {}))
    sys.exit()

# Prioridade 4: Curar se a vida estiver baixa e o coração estiver por perto
if very_low_health and needs_heart:
    print(move_towards(pos_player, pos_heart, {pos_enemy} if pos_enemy else {}))
    sys.exit()

# Prioridade 5: Atacar se o inimigo estiver adjacente e tivermos vantagem tática (mais vida ou arma)
if can_attack and (my_life >= enemy_life or my_bullets > 0):
    print("attack")
    sys.exit()

# Prioridade 6: Pegar a arma se estiver mais perto do que o coração (e precisarmos dela)
if needs_weapon and (not needs_heart or manhattan_distance(pos_player, pos_weapon) < manhattan_distance(pos_player, pos_heart)):
    print(move_towards(pos_player, pos_weapon, {pos_enemy} if pos_enemy else {}))
    sys.exit()

# Prioridade 7: Pegar o coração se necessário
if needs_heart:
    print(move_towards(pos_player, pos_heart, {pos_enemy} if pos_enemy else {}))
    sys.exit()

# Prioridade 8: Mover em direção ao inimigo para engajar
if pos_enemy:
    print(move_towards(pos_player, pos_enemy, {pos_enemy} if pos_enemy else {}))
    sys.exit()

# Prioridade 9: Se não houver objetivo claro, mover para o centro (ou um local seguro) - menos crítico contra o dummy
center = (GRID_SIZE // 2, GRID_SIZE // 2)
print(move_towards(pos_player, center, {pos_enemy} if pos_enemy else {}))