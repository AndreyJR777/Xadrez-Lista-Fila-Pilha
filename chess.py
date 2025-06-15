from collections import deque

# Classe para representar uma peça
class Peca:
    def __init__(self, tipo, cor):
        self.tipo = tipo  # 'rei', 'rainha', 'bispo', 'cavalo', 'torre', 'peao'
        self.cor = cor    # 'branco' ou 'preto'
        self.simbolo = self.get_simbolo()

    def get_simbolo(self):
        simbolos = {
            'rei': {'branco': '♔', 'preto': '♚'},
            'rainha': {'branco': '♕', 'preto': '♛'},
            'bispo': {'branco': '♗', 'preto': '♝'},
            'cavalo': {'branco': '♘', 'preto': '♞'},
            'torre': {'branco': '♖', 'preto': '♜'},
            'peao': {'branco': '♙', 'preto': '♟'}
        }
        return simbolos[self.tipo][self.cor]

    def __str__(self):
        return self.simbolo

# Função para inicializar o tabuleiro
def inicializar_tabuleiro():
    tabuleiro = [[None for _ in range(8)] for _ in range(8)]
    # Peças brancas
    tabuleiro[0] = [Peca('torre', 'branco'), Peca('cavalo', 'branco'), Peca('bispo', 'branco'), 
                    Peca('rainha', 'branco'), Peca('rei', 'branco'), Peca('bispo', 'branco'), 
                    Peca('cavalo', 'branco'), Peca('torre', 'branco')]
    tabuleiro[1] = [Peca('peao', 'branco') for _ in range(8)]
    # Peças pretas
    tabuleiro[7] = [Peca('torre', 'preto'), Peca('cavalo', 'preto'), Peca('bispo', 'preto'), 
                    Peca('rainha', 'preto'), Peca('rei', 'preto'), Peca('bispo', 'preto'), 
                    Peca('cavalo', 'preto'), Peca('torre', 'preto')]
    tabuleiro[6] = [Peca('peao', 'preto') for _ in range(8)]
    return tabuleiro

# Função para exibir o tabuleiro
def exibir_tabuleiro(tabuleiro):
    print("  a b c d e f g h")
    for i in range(7, -1, -1):
        linha = f"{i+1} "
        for j in range(8):
            peca = tabuleiro[i][j]
            linha += f"{str(peca) if peca else '.'} "
        print(linha)

# Função para verificar se a posição está dentro do tabuleiro
def dentro_do_tabuleiro(x, y):
    return 0 <= x < 8 and 0 <= y < 8

# Função para verificar se o caminho está livre (para torre, bispo, rainha)
def caminho_livre(tabuleiro, origem, destino):
    ox, oy = origem
    dx, dy = destino
    if ox == dx:  # Movimento vertical
        step = 1 if oy < dy else -1
        for y in range(oy + step, dy, step):
            if tabuleiro[ox][y]:
                return False
    elif oy == dy:  # Movimento horizontal
        step = 1 if ox < dx else -1
        for x in range(ox + step, dx, step):
            if tabuleiro[x][oy]:
                return False
    else:  # Movimento diagonal
        step_x = 1 if ox < dx else -1
        step_y = 1 if oy < dy else -1
        x, y = ox + step_x, oy + step_y
        while x != dx and y != dy:
            if tabuleiro[x][y]:
                return False
            x += step_x
            y += step_y
    return True

# Função para verificar movimento válido para cada tipo de peça
def movimento_valido(tabuleiro, origem, destino, jogador):
    ox, oy = origem
    dx, dy = destino
    peca = tabuleiro[ox][oy]
    if not peca or peca.cor != jogador:
        return False
    alvo = tabuleiro[dx][dy]
    if alvo and alvo.cor == jogador:
        return False

    if peca.tipo == 'peao':
        direcao = 1 if peca.cor == 'branco' else -1
        if oy == dy:  # Movimento reto
            if dx == ox + direcao and not alvo:
                return True
            if (peca.cor == 'branco' and ox == 1) or (peca.cor == 'preto' and ox == 6):
                if dx == ox + 2 * direcao and not tabuleiro[ox + direcao][oy] and not alvo:
                    return True
        elif abs(oy - dy) == 1 and dx == ox + direcao and alvo and alvo.cor != jogador:
            return True
        return False

    elif peca.tipo == 'cavalo':
        mov_cavalo = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        return any((ox + dx, oy + dy) == destino for dx, dy in mov_cavalo if dentro_do_tabuleiro(ox + dx, oy + dy))

    elif peca.tipo == 'bispo':
        return abs(ox - dx) == abs(oy - dy) and caminho_livre(tabuleiro, origem, destino)

    elif peca.tipo == 'torre':
        return (ox == dx or oy == dy) and caminho_livre(tabuleiro, origem, destino)

    elif peca.tipo == 'rainha':
        return ((ox == dx or oy == dy) or abs(ox - dx) == abs(oy - dy)) and caminho_livre(tabuleiro, origem, destino)

    elif peca.tipo == 'rei':
        return max(abs(ox - dx), abs(oy - dy)) == 1

    return False

# Função para mover peça
def mover_peca(tabuleiro, origem, destino, historico):
    ox, oy = origem
    dx, dy = destino
    peca = tabuleiro[ox][oy]
    capturada = tabuleiro[dx][dy]
    tabuleiro[dx][dy] = peca
    tabuleiro[ox][oy] = None
    historico.append((origem, destino, capturada))

# Função para desfazer movimento
def desfazer_movimento(tabuleiro, historico):
    if historico:
        origem, destino, capturada = historico.pop()
        ox, oy = origem
        dx, dy = destino
        tabuleiro[ox][oy] = tabuleiro[dx][dy]
        tabuleiro[dx][dy] = capturada

# Função para converter entrada do usuário em coordenadas
def parse_posicao(pos):
    col = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    return int(pos[1]) - 1, col[pos[0]]

# Loop principal do jogo
def jogo_xadrez():
    tabuleiro = inicializar_tabuleiro()
    jogadores = ['branco', 'preto']
    turnos = deque(jogadores)
    historico = []

    while True:
        jogador_atual = turnos[0]
        exibir_tabuleiro(tabuleiro)
        print(f"Turno do jogador {jogador_atual.capitalize()}")

        entrada = input("Digite o movimento (ex: 'e2 e4') ou 'desfazer' para voltar: ").strip().lower()
        if entrada == 'desfazer':
            desfazer_movimento(tabuleiro, historico)
            continue
        elif entrada == 'sair':
            break

        try:
            origem_str, destino_str = entrada.split()
            origem = parse_posicao(origem_str)
            destino = parse_posicao(destino_str)

            if movimento_valido(tabuleiro, origem, destino, jogador_atual):
                mover_peca(tabuleiro, origem, destino, historico)
                turnos.rotate(-1)
            else:
                print("Movimento inválido!")
        except (ValueError, KeyError):
            print("Entrada inválida! Use o formato 'e2 e4'.")

if __name__ == "__main__":
    print("Bem-vindo ao Jogo de Xadrez!")
    jogo_xadrez()