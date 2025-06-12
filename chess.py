import tkinter as tk
from collections import deque
import os

# --- Configurações Globais ---
BOARD_SIZE    = 8
SQUARE_SIZE   = 80
ANIM_STEPS    = 10  # quadros na animação
IMG_FOLDER    = os.path.join(os.path.dirname(__file__), "images")
PIECE_IMAGES  = {
    'wp': 'wp.png', 'wn': 'wn.png', 'wb': 'wb.png',
    'wr': 'wr.png', 'wq': 'wq.png', 'wk': 'wk.png',
    'bp': 'bp.png', 'bn': 'bn.png', 'bb': 'bb.png',
    'br': 'br.png', 'bq': 'bq.png', 'bk': 'bk.png',
}

# --- Classes de Peça e Regras ---
class Piece:
    def __init__(self, color):
        self.color = color  # 'w' ou 'b'
    def moves(self, board, r, c):
        return []

class Pawn(Piece):
    def moves(self, board, r, c):
        dirs = -1 if self.color=='w' else 1
        res = []
        # avanço simples
        if board.empty(r+dirs, c):
            res.append((r+dirs, c))
            # avanço duplo se na linha inicial
            start = 6 if self.color=='w' else 1
            if r == start and board.empty(r+2*dirs, c):
                res.append((r+2*dirs, c))
        # capturas
        for dc in (-1,1):
            if board.enemy(r+dirs, c+dc, self.color):
                res.append((r+dirs, c+dc))
        return res

class Knight(Piece):
    OFFSETS = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
    def moves(self, board, r, c):
        res = []
        for dr,dc in Knight.OFFSETS:
            nr, nc = r+dr, c+dc
            if board.valid(nr,nc) and not board.friendly(nr,nc,self.color):
                res.append((nr,nc))
        return res

class Bishop(Piece):
    def moves(self, board, r, c):
        return board._sliding(r, c, self.color, [(1,1),(1,-1),(-1,1),(-1,-1)])

class Rook(Piece):
    def moves(self, board, r, c):
        return board._sliding(r, c, self.color, [(1,0),(-1,0),(0,1),(0,-1)])

class Queen(Piece):
    def moves(self, board, r, c):
        return board._sliding(
            r, c, self.color,
            [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        )

class King(Piece):
    def moves(self, board, r, c):
        res = []
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==dc==0: continue
                nr, nc = r+dr, c+dc
                if board.valid(nr,nc) and not board.friendly(nr,nc,self.color):
                    res.append((nr,nc))
        return res

# --- Tabuleiro ---
class Board:
    def __init__(self, game):
        self.game = game
        self.grid = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self._setup_initial()

    def _setup_initial(self):
        # peões
        for c in range(8):
            self.grid[6][c] = Pawn('w')
            self.grid[1][c] = Pawn('b')
        # demais peças
        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c, cls in enumerate(order):
            self.grid[7][c] = cls('w')
            self.grid[0][c] = cls('b')

    def valid(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def empty(self, r, c):
        return self.valid(r, c) and self.grid[r][c] is None

    def friendly(self, r, c, color):
        return self.valid(r, c) and self.grid[r][c] and self.grid[r][c].color == color

    def enemy(self, r, c, color):
        return self.valid(r, c) and self.grid[r][c] and self.grid[r][c].color != color

    def _sliding(self, r, c, color, directions):
        res = []
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            while self.valid(nr, nc):
                if self.empty(nr, nc):
                    res.append((nr, nc))
                elif self.enemy(nr, nc, color):
                    res.append((nr, nc))
                    break
                else:
                    break
                nr += dr; nc += dc
        return res

# --- Lógica de Jogo e GUI ---
class Game:
    def __init__(self, canvas):
        self.canvas   = canvas
        self.board    = Board(self)
        self.images   = {}
        self._load_images()
        self.turns    = deque(['w','b'])  # fila de turnos
        self.history  = []                # pilha para undo
        self.selected = None

        self._draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def _load_images(self):
        for key, fn in PIECE_IMAGES.items():
            path = os.path.join(IMG_FOLDER, fn)
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Imagem não encontrada: {path}")
            self.images[key] = tk.PhotoImage(file=path)

    def _draw_board(self):
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                x0, y0 = c*SQUARE_SIZE, r*SQUARE_SIZE
                color = "#EEE" if (r+c)%2 else "#555"
                self.canvas.create_rectangle(
                    x0, y0, x0+SQUARE_SIZE, y0+SQUARE_SIZE,
                    fill=color, outline=""
                )
                p = self.board.grid[r][c]
                if p:
                    key = p.color + p.__class__.__name__[0].lower()
                    self.canvas.create_image(
                        x0, y0, anchor="nw", image=self.images[key]
                    )
        if self.selected:
            r, c = self.selected
            x0, y0 = c*SQUARE_SIZE, r*SQUARE_SIZE
            self.canvas.create_rectangle(
                x0, y0, x0+SQUARE_SIZE, y0+SQUARE_SIZE,
                outline="yellow", width=3
            )

    def on_click(self, event):
        c = event.x // SQUARE_SIZE
        r = event.y // SQUARE_SIZE
        if not self.board.valid(r, c): return

        cur = self.turns[0]
        p = self.board.grid[r][c]
        if self.selected is None:
            if p and p.color == cur:
                self.selected = (r, c)
                self._draw_board()
        else:
            r0, c0 = self.selected
            piece = self.board.grid[r0][c0]
            moves = piece.moves(self.board, r0, c0)
            if (r, c) in moves:
                # salva p/ undo
                self.history.append((
                    r0, c0, piece,
                    r, c, self.board.grid[r][c],
                    cur
                ))
                self._animate_move(r0, c0, r, c, piece)
                # move de fato
                self.board.grid[r0][c0] = None
                self.board.grid[r][c]   = piece
                self.turns.rotate(-1)
            self.selected = None
            self._draw_board()

    def _animate_move(self, r0, c0, r1, c1, piece):
        key = piece.color + piece.__class__.__name__[0].lower()
        img_obj = None
        for obj in self.canvas.find_all():
            if self.canvas.type(obj) == "image":
                x, y = self.canvas.coords(obj)
                if (round(y)//SQUARE_SIZE, round(x)//SQUARE_SIZE) == (r0, c0):
                    img_obj = obj
                    break
        if not img_obj:
            return
        dx = (c1 - c0)*SQUARE_SIZE/ANIM_STEPS
        dy = (r1 - r0)*SQUARE_SIZE/ANIM_STEPS
        def step(count=0):
            if count < ANIM_STEPS:
                self.canvas.move(img_obj, dx, dy)
                self.canvas.after(30, lambda: step(count+1))
        step()

    def undo(self):
        if not self.history:
            return
        r0, c0, piece, r1, c1, captured, prev_turn = self.history.pop()
        self.board.grid[r0][c0] = piece
        self.board.grid[r1][c1] = captured
        self.turns.rotate(1)
        self._draw_board()

# --- Início da Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Xadrez – Python Tkinter")
    canvas = tk.Canvas(
        root,
        width = SQUARE_SIZE * BOARD_SIZE,
        height= SQUARE_SIZE * BOARD_SIZE
    )
    canvas.pack()
    game = Game(canvas)

    # atalho para undo
    root.bind("<Control-z>", lambda e: game.undo())
    root.mainloop()
