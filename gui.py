"""Antarmuka grafis (UI) Tic-Tac-Toe berbasis Pygame.

Mengacu pada desain antarmuka, alur permainan, dan skenario pengujian jurnal:
"Penerapan Algoritma Minimax dengan Alpha-Beta Pruning pada Permainan
Tic-Tac-Toe Menggunakan Framework Flutter" (Pradana & Litanianda, JATI 2024),
serta mendukung 3 mode permainan (Human vs Human, Human vs AI, AI vs AI),
pemilihan algoritma (Alpha-Beta, AB Strategic, Minimax), dan statistik performa.
"""

import math
import pygame

from board.board import (
    EMPTY,
    check_winner,
    create_board,
    is_draw,
    make_move,
)
from algorithms.minimax import find_best_move as find_best_move_minimax
from algorithms.alpha_beta import find_best_move as find_best_move_alpha_beta


# ----------,-----------------------------------------------------------------
# Konstanta Jendela & Warna (disesuaikan dengan Gambar 5-8 pada jurnal)
# ---------------------------------------------------------------------------
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 720
FPS = 60

# Palet warna dari acuan jurnal
COLOR_BG = (255, 135, 135)           # #FF8787 - Latar belakang coral
COLOR_BG_DARK = (232, 114, 114)      # #E87272 - Kontainer sekunder
COLOR_BG_CARD = (224, 104, 104)      # #E06868 - Kartu statistik / menu
COLOR_TILE = (255, 201, 60)          # #FFC93C - Kotak papan kuning
COLOR_TILE_HOVER = (255, 215, 102)   # #FFD766 - Kotak papan saat hover
COLOR_TILE_WIN = (255, 226, 122)     # #FFE27A - Kotak garis kemenangan
COLOR_TILE_SHADOW = (224, 110, 110)  # Bayangan halus di bawah kotak
COLOR_WHITE = (255, 255, 255)        # #FFFFFF - Simbol X, teks utama, dialog
COLOR_WHITE_SOFT = (255, 236, 236)   # Teks sekunder terang
COLOR_O_TEAL = (23, 107, 135)        # #176B87 - Simbol O & skor komputer
COLOR_O_TEAL_DARK = (16, 82, 105)    # Label sekunder komputer
COLOR_COLON = (255, 201, 60)         # #FFC93C - Tanda ':' pada papan skor
COLOR_BTN_RED = (255, 75, 75)        # #FF4B4B - Tombol aksi utama dialog
COLOR_BTN_RED_HOVER = (235, 58, 58)
COLOR_BTN_GRAY = (189, 189, 189)     # #BDBDBD - Tombol sekunder dialog
COLOR_BTN_GRAY_HOVER = (168, 168, 168)
COLOR_TEXT_DARK = (33, 33, 33)       # Teks gelap pada kartu/dialog putih
COLOR_TEXT_MUTED = (105, 105, 105)   # Subteks pada kartu/dialog putih
COLOR_WIN_RING = (255, 255, 255)     # Garis penanda 3 kotak pemenang

# Pemetaan simbol sesuai jurnal (Pemain 1 = X, Pemain 2 / Komputer = O)
SYMBOL_X = "X"
SYMBOL_O = "O"

# Mode permainan
MODE_HVH = "hvh"
MODE_HVAI = "hvai"
MODE_AIVAI = "aivai"

GAME_MODES = (
    {
        "key": MODE_HVAI,
        "title": "Human vs AI",
        "subtitle": "Pemain (X) melawan Komputer (O)",
    },
    {
        "key": MODE_HVH,
        "title": "Human vs Human",
        "subtitle": "Player 1 (X) melawan Player 2 (O)",
    },
    {
        "key": MODE_AIVAI,
        "title": "AI vs AI",
        "subtitle": "Komputer 1 (X) melawan Komputer 2 (O)",
    },
)

# Jeda visual sebelum AI bergerak agar pergantian giliran mudah diikuti
AI_DELAY_MS = 320
AI_VS_AI_DELAY_MS = 520

WINNING_COMBINATIONS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

# Pilihan algoritma yang terhubung ke modul algorithms/
ALGORITHMS = (
    {
        "key": "alpha_beta_standard",
        "label": "Alpha-Beta",
        "full_name": "Alpha-Beta Pruning",
        "fn": lambda board, player: find_best_move_alpha_beta(
            board, player=player, move_order="standard"
        ),
    },
    {
        "key": "alpha_beta_strategic",
        "label": "AB Strategic",
        "full_name": "Alpha-Beta (Strategic)",
        "fn": lambda board, player: find_best_move_alpha_beta(
            board, player=player, move_order="strategic"
        ),
    },
    {
        "key": "minimax",
        "label": "Minimax",
        "full_name": "Minimax",
        "fn": lambda board, player: find_best_move_minimax(
            board, player=player
        ),
    },
)


def find_winning_line(board):
    """Mengembalikan tuple 3 indeks garis pemenang jika ada, else None."""
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return (a, b, c)
    return None


def load_font(size, bold=False):
    """Memuat font sans-serif yang bersih dengan fallback default Pygame."""
    preferred = ("freesans", "dejavusans", "liberationsans", "nimbussans")
    for name in preferred:
        matched = pygame.font.match_font(name, bold=bold)
        if matched:
            return pygame.font.Font(matched, size)
    return pygame.font.SysFont(None, size, bold=bold)


def _draw_capsule(surf, color, p1, p2, radius):
    """Menggambar garis berkepala bulat presisi dengan ketebalan seragam."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length == 0:
        pygame.draw.circle(surf, color, (int(p1[0]), int(p1[1])), int(radius))
        return
    nx = -dy / length * radius
    ny = dx / length * radius
    quad = (
        (p1[0] + nx, p1[1] + ny),
        (p2[0] + nx, p2[1] + ny),
        (p2[0] - nx, p2[1] - ny),
        (p1[0] - nx, p1[1] - ny),
    )
    pygame.draw.polygon(surf, color, quad)
    pygame.draw.circle(
        surf, color, (int(round(p1[0])), int(round(p1[1]))), int(round(radius))
    )
    pygame.draw.circle(
        surf, color, (int(round(p2[0])), int(round(p2[1]))), int(round(radius))
    )


def create_x_surface(size, color):
    """Membuat simbol X tebal membulat dengan supersampling anti-aliasing."""
    scale = 4
    hi = size * scale
    surf = pygame.Surface((hi, hi), pygame.SRCALPHA)
    surf.fill((color[0], color[1], color[2], 0))
    pad = hi * 0.31
    radius = hi * 0.068

    p1 = (pad, pad)
    p2 = (hi - pad, hi - pad)
    p3 = (hi - pad, pad)
    p4 = (pad, hi - pad)

    _draw_capsule(surf, color, p1, p2, radius)
    _draw_capsule(surf, color, p3, p4, radius)

    return pygame.transform.smoothscale(surf, (size, size))


def create_o_surface(size, color):
    """Membuat simbol O tebal (gaya jurnal) dengan supersampling anti-aliasing."""
    scale = 4
    hi = size * scale
    surf = pygame.Surface((hi, hi), pygame.SRCALPHA)
    surf.fill((color[0], color[1], color[2], 0))
    center = (hi // 2, hi // 2)
    outer_rx = int(hi * 0.23)
    outer_ry = int(hi * 0.26)
    inner_rx = int(hi * 0.09)
    inner_ry = int(hi * 0.12)

    outer_rect = pygame.Rect(
        center[0] - outer_rx,
        center[1] - outer_ry,
        outer_rx * 2,
        outer_ry * 2,
    )
    inner_rect = pygame.Rect(
        center[0] - inner_rx,
        center[1] - inner_ry,
        inner_rx * 2,
        inner_ry * 2,
    )
    pygame.draw.ellipse(surf, color, outer_rect)
    pygame.draw.ellipse(surf, (color[0], color[1], color[2], 0), inner_rect)

    return pygame.transform.smoothscale(surf, (size, size))


def create_back_icon(size, color):
    """Membuat ikon panah kembali '<' dengan supersampling anti-aliasing."""
    scale = 4
    hi = size * scale
    surf = pygame.Surface((hi, hi), pygame.SRCALPHA)
    surf.fill((color[0], color[1], color[2], 0))
    radius = hi * 0.048

    top = (hi * 0.62, hi * 0.20)
    mid = (hi * 0.32, hi * 0.50)
    bot = (hi * 0.62, hi * 0.80)

    _draw_capsule(surf, color, top, mid, radius)
    _draw_capsule(surf, color, mid, bot, radius)

    return pygame.transform.smoothscale(surf, (size, size))


def create_refresh_icon(size, color):
    """Membuat ikon refresh melingkar dengan supersampling anti-aliasing."""
    scale = 4
    hi = size * scale
    surf = pygame.Surface((hi, hi), pygame.SRCALPHA)
    surf.fill((color[0], color[1], color[2], 0))
    cx, cy = hi / 2, hi / 2
    arc_radius = hi * 0.31
    stroke_r = hi * 0.048

    steps = 40
    start_deg = 35
    end_deg = 315
    points = []
    for i in range(steps + 1):
        deg = start_deg + (end_deg - start_deg) * (i / steps)
        rad = math.radians(deg)
        points.append(
            (cx + arc_radius * math.cos(rad), cy + arc_radius * math.sin(rad))
        )

    for i in range(len(points) - 1):
        _draw_capsule(surf, color, points[i], points[i + 1], stroke_r)

    end_x, end_y = points[-1]
    arrow = hi * 0.20
    tip = (end_x + arrow * 0.45, end_y + arrow * 0.45)
    wing1 = (end_x - arrow * 0.68, end_y + arrow * 0.38)
    wing2 = (end_x + arrow * 0.40, end_y - arrow * 0.68)
    pygame.draw.polygon(surf, color, [tip, wing1, wing2])

    return pygame.transform.smoothscale(surf, (size, size))


def _make_segmented_rects(container, count, pad=4):
    """Membagi rect kontainer menjadi `count` tab pill sejajar."""
    inner_w = container.width - pad * 2
    tab_w = inner_w / count
    rects = []
    for i in range(count):
        x = int(round(container.x + pad + i * tab_w))
        next_x = int(round(container.x + pad + (i + 1) * tab_w))
        rects.append(
            pygame.Rect(
                x,
                container.y + pad,
                next_x - x,
                container.height - pad * 2,
            )
        )
    return rects


class TicTacToeUI:
    """Aplikasi Pygame Tic-Tac-Toe dengan menu mode & desain acuan jurnal."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tic Tac Toe - Minimax & Alpha-Beta Pruning")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Font
        self.font_hero = load_font(34, bold=True)
        self.font_hero_sub = load_font(14, bold=False)
        self.font_section = load_font(13, bold=True)
        self.font_mode_title = load_font(17, bold=True)
        self.font_mode_sub = load_font(12, bold=False)
        self.font_cta = load_font(17, bold=True)
        self.font_title = load_font(24, bold=True)
        self.font_turn = load_font(22, bold=True)
        self.font_round = load_font(19, bold=True)
        self.font_score = load_font(44, bold=True)
        self.font_score_sub = load_font(12, bold=True)
        self.font_pill = load_font(13, bold=True)
        self.font_stat_title = load_font(12, bold=True)
        self.font_stat_val = load_font(17, bold=True)
        self.font_stat_lbl = load_font(11, bold=False)
        self.font_dialog_title = load_font(20, bold=True)
        self.font_dialog_body = load_font(15, bold=False)
        self.font_dialog_btn = load_font(15, bold=True)

        # Layout rect layar permainan
        self.back_btn_rect = pygame.Rect(16, 12, 42, 42)
        self.refresh_btn_rect = pygame.Rect(WINDOW_WIDTH - 58, 12, 42, 42)
        self.control_bar_rect = pygame.Rect(27, 200, WINDOW_WIDTH - 54, 36)
        self.algo_tab_rects = _make_segmented_rects(
            self.control_bar_rect, len(ALGORITHMS)
        )
        self.pause_btn_rect = pygame.Rect(
            self.control_bar_rect.right - 92,
            self.control_bar_rect.y + 4,
            88,
            self.control_bar_rect.height - 8,
        )
        self.change_mode_btn_rect = pygame.Rect(
            self.control_bar_rect.right - 104,
            self.control_bar_rect.y + 4,
            100,
            self.control_bar_rect.height - 8,
        )

        # Layout rect layar menu
        self.menu_mode_rects = [
            pygame.Rect(32, 198 + i * 74, WINDOW_WIDTH - 64, 62)
            for i in range(len(GAME_MODES))
        ]
        self.menu_algo1_bar = pygame.Rect(32, 456, WINDOW_WIDTH - 64, 36)
        self.menu_algo1_tabs = _make_segmented_rects(
            self.menu_algo1_bar, len(ALGORITHMS)
        )
        self.menu_algo2_bar = pygame.Rect(32, 522, WINDOW_WIDTH - 64, 36)
        self.menu_algo2_tabs = _make_segmented_rects(
            self.menu_algo2_bar, len(ALGORITHMS)
        )
        self.menu_start_rect = pygame.Rect(32, 586, WINDOW_WIDTH - 64, 52)
        self.menu_exit_rect = pygame.Rect(32, 650, WINDOW_WIDTH - 64, 42)

        # Papan 3x3
        self.tile_size = 110
        self.tile_gap = 12
        board_total = self.tile_size * 3 + self.tile_gap * 2
        board_x = (WINDOW_WIDTH - board_total) // 2
        board_y = 250
        self.tile_rects = []
        for idx in range(9):
            row, col = divmod(idx, 3)
            x = board_x + col * (self.tile_size + self.tile_gap)
            y = board_y + row * (self.tile_size + self.tile_gap)
            self.tile_rects.append(
                pygame.Rect(x, y, self.tile_size, self.tile_size)
            )

        # Kartu statistik / ringkasan di bawah papan
        self.stats_card_rect = pygame.Rect(27, 616, WINDOW_WIDTH - 54, 88)

        # Aset vektor anti-aliased
        self.icon_back = create_back_icon(24, COLOR_WHITE)
        self.icon_refresh = create_refresh_icon(24, COLOR_WHITE)
        self.sym_x = create_x_surface(self.tile_size, COLOR_WHITE)
        self.sym_x_ghost = create_x_surface(self.tile_size, (255, 255, 255, 95))
        self.sym_o = create_o_surface(self.tile_size, COLOR_O_TEAL)
        self.sym_o_ghost = create_o_surface(self.tile_size, (23, 107, 135, 95))
        self.badge_x = create_x_surface(38, COLOR_WHITE)
        self.badge_o = create_o_surface(38, COLOR_O_TEAL)

        # State layar & konfigurasi menu
        self.screen_state = "menu"  # "menu" | "game"
        self.game_mode = MODE_HVAI
        self.algo_x_idx = 0  # Digunakan oleh AI 1 (X) pada mode AI vs AI
        self.algo_o_idx = 0  # Digunakan oleh AI (O) pada Human vs AI & AI vs AI

        # State permainan
        self.board = create_board()
        self.score_x = 0
        self.score_o = 0
        self.draw_count = 0
        self.move_count = 0
        self.round_num = 1
        self.current_turn = SYMBOL_X
        self.winning_line = None
        self.last_stats = None
        self.last_stat_badge = ""
        self.ai_scheduled_at = None
        self.ai_computing = False
        self.ai_paused = False

        # State dialog: None | "win" | "draw" | "exit"
        self.active_dialog = None
        self.previous_dialog = None
        self.winner_symbol = None

        # Rect tombol dialog (diisi saat render dialog)
        self.dialog_play_again_rect = pygame.Rect(0, 0, 0, 0)
        self.dialog_menu_rect = pygame.Rect(0, 0, 0, 0)
        self.dialog_yes_rect = pygame.Rect(0, 0, 0, 0)
        self.dialog_no_rect = pygame.Rect(0, 0, 0, 0)

    # -----------------------------------------------------------------------
    # Helper Mode & Pemain
    # -----------------------------------------------------------------------
    def is_ai_turn(self, symbol=None):
        """Mengembalikan True jika pemain untuk simbol tertentu adalah AI."""
        sym = self.current_turn if symbol is None else symbol
        if self.game_mode == MODE_HVH:
            return False
        if self.game_mode == MODE_HVAI:
            return sym == SYMBOL_O
        return True  # MODE_AIVAI

    def get_algo_idx_for_symbol(self, symbol):
        return self.algo_x_idx if symbol == SYMBOL_X else self.algo_o_idx

    def get_player_labels(self):
        if self.game_mode == MODE_HVH:
            return ("Player 1 (X)", "Player 2 (O)")
        if self.game_mode == MODE_HVAI:
            return ("Pemain (X)", "Komputer (O)")
        return ("AI 1 (X)", "AI 2 (O)")

    def _schedule_ai_if_needed(self):
        if self.is_ai_turn() and not self.ai_paused:
            delay = (
                AI_VS_AI_DELAY_MS
                if self.game_mode == MODE_AIVAI
                else AI_DELAY_MS
            )
            self.ai_scheduled_at = pygame.time.get_ticks() + delay
        else:
            self.ai_scheduled_at = None

    # -----------------------------------------------------------------------
    # Transisi Layar & Logika Permainan
    # -----------------------------------------------------------------------
    def start_game(self, mode=None):
        """Masuk dari menu ke layar permainan dengan state bersih."""
        if mode is not None:
            self.game_mode = mode
        self.screen_state = "game"
        self.reset_all()

    def return_to_menu(self):
        """Kembali ke layar menu pemilihan mode."""
        self.screen_state = "menu"
        self.active_dialog = None
        self.previous_dialog = None
        self.ai_scheduled_at = None
        self.ai_computing = False
        self.ai_paused = False

    def reset_all(self):
        """Tombol Refresh: kosongkan papan, reset skor ke 0, ronde ke 1."""
        self.board = create_board()
        self.score_x = 0
        self.score_o = 0
        self.draw_count = 0
        self.move_count = 0
        self.round_num = 1
        self.current_turn = SYMBOL_X
        self.winning_line = None
        self.winner_symbol = None
        self.active_dialog = None
        self.previous_dialog = None
        self.last_stats = None
        self.last_stat_badge = ""
        self.ai_computing = False
        self.ai_paused = False
        self._schedule_ai_if_needed()

    def start_next_round(self):
        """Tombol Main Lagi: kosongkan papan, naikkan ronde, giliran bergantian.

        Aturan Tabel 3 No. 10:
        - Ronde ganjil (1, 3, 5, ...): Pemain X bergerak pertama.
        - Ronde genap  (2, 4, 6, ...): Pemain O bergerak pertama.
        """
        self.board = create_board()
        self.move_count = 0
        self.round_num += 1
        self.winning_line = None
        self.winner_symbol = None
        self.active_dialog = None
        self.previous_dialog = None
        self.ai_computing = False
        self.ai_paused = False

        self.current_turn = SYMBOL_X if self.round_num % 2 == 1 else SYMBOL_O
        self._schedule_ai_if_needed()

    def open_exit_dialog(self):
        """Tampilkan dialog konfirmasi keluar (Gambar 8)."""
        if self.active_dialog != "exit":
            self.previous_dialog = self.active_dialog
            self.active_dialog = "exit"

    def close_exit_dialog(self):
        """Tombol 'Tidak' pada dialog keluar: kembali ke kondisi sebelumnya."""
        self.active_dialog = self.previous_dialog
        self.previous_dialog = None
        if self.screen_state == "game" and self.active_dialog is None:
            self._schedule_ai_if_needed()

    def toggle_ai_pause(self):
        """Jeda atau lanjutkan permainan otomatis pada mode AI vs AI."""
        if self.game_mode != MODE_AIVAI or self.active_dialog is not None:
            return
        self.ai_paused = not self.ai_paused
        if self.ai_paused:
            self.ai_scheduled_at = None
        else:
            self._schedule_ai_if_needed()

    def _check_post_move(self):
        """Periksa kondisi menang atau seri setelah sebuah langkah dilakukan."""
        winner = check_winner(self.board)
        if winner is not None:
            self.winner_symbol = winner
            self.winning_line = find_winning_line(self.board)
            if winner == SYMBOL_X:
                self.score_x += 1
            else:
                self.score_o += 1
            self.active_dialog = "win"
            self.ai_scheduled_at = None
            return True

        if is_draw(self.board):
            self.winner_symbol = None
            self.winning_line = None
            self.draw_count += 1
            self.active_dialog = "draw"
            self.ai_scheduled_at = None
            return True

        return False

    def handle_human_move(self, cell_idx):
        """Menangani klik pemain manusia pada kotak 0..8."""
        if (
            self.screen_state != "game"
            or self.active_dialog is not None
            or self.is_ai_turn()
        ):
            return

        if not make_move(self.board, cell_idx, self.current_turn):
            return

        self.move_count += 1
        if not self._check_post_move():
            self.current_turn = (
                SYMBOL_O if self.current_turn == SYMBOL_X else SYMBOL_X
            )
            self._schedule_ai_if_needed()

    def execute_ai_move(self):
        """Menjalankan algoritma terpilih untuk menentukan langkah AI."""
        if (
            self.screen_state != "game"
            or self.active_dialog is not None
            or not self.is_ai_turn()
        ):
            return

        active_symbol = self.current_turn
        algo = ALGORITHMS[self.get_algo_idx_for_symbol(active_symbol)]
        self.ai_computing = True
        self.render()
        pygame.display.flip()

        move, score, stats = algo["fn"](self.board, active_symbol)
        self.ai_computing = False
        self.ai_scheduled_at = None

        self.last_stats = stats
        if self.game_mode == MODE_AIVAI:
            ai_tag = "AI 1 (X)" if active_symbol == SYMBOL_X else "AI 2 (O)"
            self.last_stat_badge = f"{ai_tag} • {algo['label']} | Skor: {score}"
        else:
            self.last_stat_badge = f"{algo['label']} | Skor: {score}"

        if move is not None and make_move(self.board, move, active_symbol):
            self.move_count += 1

        if not self._check_post_move():
            self.current_turn = (
                SYMBOL_O if active_symbol == SYMBOL_X else SYMBOL_X
            )
            self._schedule_ai_if_needed()

    # -----------------------------------------------------------------------
    # Penanganan Input / Event
    # -----------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.active_dialog == "exit":
                    self.close_exit_dialog()
                elif self.screen_state == "game":
                    self.return_to_menu()
                else:
                    self.open_exit_dialog()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.active_dialog in ("win", "draw"):
                    self.start_next_round()
                elif self.active_dialog == "exit":
                    self.running = False
                elif self.screen_state == "menu":
                    self.start_game()
                elif (
                    self.screen_state == "game"
                    and self.game_mode == MODE_AIVAI
                    and event.key == pygame.K_SPACE
                ):
                    self.toggle_ai_pause()
            elif (
                event.key == pygame.K_r
                and self.screen_state == "game"
                and self.active_dialog is None
            ):
                self.reset_all()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Interaksi dialog modal
            if self.active_dialog in ("win", "draw"):
                if self.dialog_play_again_rect.collidepoint(pos):
                    self.start_next_round()
                elif self.dialog_menu_rect.collidepoint(pos):
                    self.return_to_menu()
                return

            if self.active_dialog == "exit":
                if self.dialog_yes_rect.collidepoint(pos):
                    self.running = False
                elif self.dialog_no_rect.collidepoint(pos):
                    self.close_exit_dialog()
                return

            if self.screen_state == "menu":
                self._handle_menu_click(pos)
            else:
                self._handle_game_click(pos)

    def _handle_menu_click(self, pos):
        for mode_cfg, rect in zip(GAME_MODES, self.menu_mode_rects):
            if rect.collidepoint(pos):
                self.game_mode = mode_cfg["key"]
                return

        if self.game_mode == MODE_HVAI:
            for idx, rect in enumerate(self.menu_algo1_tabs):
                if rect.collidepoint(pos):
                    self.algo_o_idx = idx
                    return
        elif self.game_mode == MODE_AIVAI:
            for idx, rect in enumerate(self.menu_algo1_tabs):
                if rect.collidepoint(pos):
                    self.algo_x_idx = idx
                    return
            for idx, rect in enumerate(self.menu_algo2_tabs):
                if rect.collidepoint(pos):
                    self.algo_o_idx = idx
                    return

        if self.menu_start_rect.collidepoint(pos):
            self.start_game()
            return

        if self.menu_exit_rect.collidepoint(pos):
            self.open_exit_dialog()
            return

    def _handle_game_click(self, pos):
        if self.back_btn_rect.collidepoint(pos):
            self.return_to_menu()
            return

        if self.refresh_btn_rect.collidepoint(pos):
            self.reset_all()
            return

        if self.game_mode == MODE_HVAI:
            for idx, rect in enumerate(self.algo_tab_rects):
                if rect.collidepoint(pos):
                    self.algo_o_idx = idx
                    return
        elif self.game_mode == MODE_HVH:
            if self.change_mode_btn_rect.collidepoint(pos):
                self.return_to_menu()
                return
        elif self.game_mode == MODE_AIVAI:
            if self.pause_btn_rect.collidepoint(pos):
                self.toggle_ai_pause()
                return

        for idx, rect in enumerate(self.tile_rects):
            if rect.collidepoint(pos):
                self.handle_human_move(idx)
                return

    def update(self):
        if (
            self.screen_state == "game"
            and self.active_dialog is None
            and not self.ai_paused
            and self.is_ai_turn()
            and self.ai_scheduled_at is not None
            and pygame.time.get_ticks() >= self.ai_scheduled_at
        ):
            self.execute_ai_move()

    # -----------------------------------------------------------------------
    # Rendering Layar Menu
    # -----------------------------------------------------------------------
    def _draw_segmented_bar(self, bar_rect, tab_rects, selected_idx, mouse_pos):
        pygame.draw.rect(self.screen, COLOR_BG_DARK, bar_rect, border_radius=18)

        for idx, (algo, rect) in enumerate(zip(ALGORITHMS, tab_rects)):
            is_selected = idx == selected_idx
            is_hover = self.active_dialog is None and rect.collidepoint(mouse_pos)

            if is_selected:
                pygame.draw.rect(self.screen, COLOR_WHITE, rect, border_radius=14)
                txt_color = COLOR_BTN_RED
            else:
                if is_hover:
                    hover_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(
                        hover_surf,
                        (255, 255, 255, 38),
                        hover_surf.get_rect(),
                        border_radius=14,
                    )
                    self.screen.blit(hover_surf, rect.topleft)
                txt_color = COLOR_WHITE

            lbl = self.font_pill.render(algo["label"], True, txt_color)
            self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_menu(self, mouse_pos):
        # Ikon mini dekoratif X & O di bagian atas
        badge_size = 44
        gap = 12
        bx = WINDOW_WIDTH // 2 - badge_size - gap // 2
        by = 34
        for i, sym_surf in enumerate((self.badge_x, self.badge_o)):
            r = pygame.Rect(bx + i * (badge_size + gap), by, badge_size, badge_size)
            pygame.draw.rect(
                self.screen, COLOR_TILE_SHADOW, r.move(0, 3), border_radius=11
            )
            pygame.draw.rect(self.screen, COLOR_TILE, r, border_radius=11)
            self.screen.blit(sym_surf, sym_surf.get_rect(center=r.center))

        # Judul & subjudul
        title_surf = self.font_hero.render("Tic Tac Toe", True, COLOR_WHITE)
        self.screen.blit(
            title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 108))
        )
        sub_surf = self.font_hero_sub.render(
            "Minimax & Alpha-Beta Pruning", True, COLOR_WHITE_SOFT
        )
        self.screen.blit(
            sub_surf, sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 136))
        )

        # Label bagian mode permainan
        sec_mode = self.font_section.render(
            "PILIH MODE PERMAINAN", True, COLOR_WHITE_SOFT
        )
        self.screen.blit(sec_mode, (34, 174))

        # Kartu pilihan mode (Human vs AI, Human vs Human, AI vs AI)
        for mode_cfg, rect in zip(GAME_MODES, self.menu_mode_rects):
            is_selected = self.game_mode == mode_cfg["key"]
            is_hover = self.active_dialog is None and rect.collidepoint(mouse_pos)

            # Bayangan halus
            pygame.draw.rect(
                self.screen,
                COLOR_TILE_SHADOW,
                rect.move(0, 3),
                border_radius=16,
            )

            if is_selected:
                bg = COLOR_WHITE
                title_col = COLOR_O_TEAL
                sub_col = COLOR_TEXT_MUTED
            else:
                bg = COLOR_BG_DARK if not is_hover else (240, 124, 124)
                title_col = COLOR_WHITE
                sub_col = COLOR_WHITE_SOFT

            pygame.draw.rect(self.screen, bg, rect, border_radius=16)

            if is_selected:
                pygame.draw.rect(
                    self.screen, COLOR_TILE, rect, width=3, border_radius=16
                )

            # Indikator radio di kiri
            radio_center = (rect.x + 26, rect.centery)
            if is_selected:
                pygame.draw.circle(self.screen, COLOR_BTN_RED, radio_center, 9)
                pygame.draw.circle(self.screen, COLOR_WHITE, radio_center, 4)
            else:
                pygame.draw.circle(
                    self.screen, COLOR_WHITE_SOFT, radio_center, 9, width=2
                )

            t_surf = self.font_mode_title.render(
                mode_cfg["title"], True, title_col
            )
            s_surf = self.font_mode_sub.render(
                mode_cfg["subtitle"], True, sub_col
            )
            self.screen.blit(t_surf, (rect.x + 48, rect.y + 11))
            self.screen.blit(s_surf, (rect.x + 48, rect.y + 36))

        # Konfigurasi algoritma sesuai mode terpilih
        if self.game_mode == MODE_HVAI:
            lbl = self.font_section.render(
                "ALGORITMA KOMPUTER (O)", True, COLOR_WHITE_SOFT
            )
            self.screen.blit(lbl, (34, 434))
            self._draw_segmented_bar(
                self.menu_algo1_bar,
                self.menu_algo1_tabs,
                self.algo_o_idx,
                mouse_pos,
            )

        elif self.game_mode == MODE_AIVAI:
            lbl1 = self.font_section.render(
                "ALGORITMA AI 1 (X)", True, COLOR_WHITE_SOFT
            )
            self.screen.blit(lbl1, (34, 434))
            self._draw_segmented_bar(
                self.menu_algo1_bar,
                self.menu_algo1_tabs,
                self.algo_x_idx,
                mouse_pos,
            )

            lbl2 = self.font_section.render(
                "ALGORITMA AI 2 (O)", True, COLOR_WHITE_SOFT
            )
            self.screen.blit(lbl2, (34, 502))
            self._draw_segmented_bar(
                self.menu_algo2_bar,
                self.menu_algo2_tabs,
                self.algo_o_idx,
                mouse_pos,
            )

        else:  # MODE_HVH
            info_card = pygame.Rect(32, 444, WINDOW_WIDTH - 64, 72)
            pygame.draw.rect(
                self.screen, COLOR_BG_CARD, info_card, border_radius=16
            )
            info_t = self.font_pill.render(
                "Mode 2 Pemain Lokal", True, COLOR_TILE
            )
            info_s = self.font_mode_sub.render(
                "Player 1 (X) & Player 2 (O) bermain bergantian.",
                True,
                COLOR_WHITE_SOFT,
            )
            self.screen.blit(
                info_t, info_t.get_rect(center=(info_card.centerx, info_card.y + 24))
            )
            self.screen.blit(
                info_s, info_s.get_rect(center=(info_card.centerx, info_card.y + 48))
            )

        # Tombol utama "Mulai Permainan" (kuning cerah dengan teks teal gelap)
        start_hover = (
            self.active_dialog is None
            and self.menu_start_rect.collidepoint(mouse_pos)
        )
        pygame.draw.rect(
            self.screen,
            COLOR_TILE_SHADOW,
            self.menu_start_rect.move(0, 4),
            border_radius=16,
        )
        pygame.draw.rect(
            self.screen,
            COLOR_TILE_HOVER if start_hover else COLOR_TILE,
            self.menu_start_rect,
            border_radius=16,
        )
        start_txt = self.font_cta.render("Mulai Permainan", True, COLOR_O_TEAL_DARK)
        self.screen.blit(
            start_txt, start_txt.get_rect(center=self.menu_start_rect.center)
        )

        # Tombol sekunder "Keluar"
        exit_hover = (
            self.active_dialog is None
            and self.menu_exit_rect.collidepoint(mouse_pos)
        )
        exit_bg = COLOR_BTN_RED if exit_hover else COLOR_BG_CARD
        pygame.draw.rect(
            self.screen, exit_bg, self.menu_exit_rect, border_radius=14
        )
        exit_txt = self.font_dialog_btn.render("Keluar", True, COLOR_WHITE)
        self.screen.blit(
            exit_txt, exit_txt.get_rect(center=self.menu_exit_rect.center)
        )

    # -----------------------------------------------------------------------
    # Rendering Layar Permainan
    # -----------------------------------------------------------------------
    def _draw_top_bar(self, mouse_pos):
        for rect, icon in (
            (self.back_btn_rect, self.icon_back),
            (self.refresh_btn_rect, self.icon_refresh),
        ):
            if self.active_dialog is None and rect.collidepoint(mouse_pos):
                hover_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.circle(
                    hover_surf,
                    (255, 255, 255, 45),
                    (rect.width // 2, rect.height // 2),
                    rect.width // 2,
                )
                self.screen.blit(hover_surf, rect.topleft)
            icon_rect = icon.get_rect(center=rect.center)
            self.screen.blit(icon, icon_rect)

        title_surf = self.font_title.render("Tic Tac Toe", True, COLOR_WHITE)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 33))
        self.screen.blit(title_surf, title_rect)

    def _draw_status_and_score(self):
        if self.ai_computing:
            turn_label = f"Turn: {self.current_turn} (Berpikir...)"
        elif self.ai_paused:
            turn_label = f"Turn: {self.current_turn} (Dijeda)"
        else:
            turn_label = f"Turn: {self.current_turn}"

        turn_surf = self.font_turn.render(turn_label, True, COLOR_WHITE)
        self.screen.blit(
            turn_surf, turn_surf.get_rect(center=(WINDOW_WIDTH // 2, 74))
        )

        round_surf = self.font_round.render(
            f"Round: {self.round_num}", True, COLOR_WHITE
        )
        self.screen.blit(
            round_surf, round_surf.get_rect(center=(WINDOW_WIDTH // 2, 103))
        )

        score_y = 148
        colon_surf = self.font_score.render(":", True, COLOR_COLON)
        self.screen.blit(
            colon_surf, colon_surf.get_rect(center=(WINDOW_WIDTH // 2, score_y - 3))
        )

        sx_surf = self.font_score.render(str(self.score_x), True, COLOR_WHITE)
        self.screen.blit(
            sx_surf, sx_surf.get_rect(center=(WINDOW_WIDTH // 2 - 48, score_y))
        )

        so_surf = self.font_score.render(str(self.score_o), True, COLOR_O_TEAL)
        self.screen.blit(
            so_surf, so_surf.get_rect(center=(WINDOW_WIDTH // 2 + 48, score_y))
        )

        label_x, label_o = self.get_player_labels()
        lbl_x = self.font_score_sub.render(label_x, True, COLOR_WHITE_SOFT)
        self.screen.blit(
            lbl_x, lbl_x.get_rect(center=(WINDOW_WIDTH // 2 - 48, 179))
        )
        lbl_o = self.font_score_sub.render(label_o, True, COLOR_O_TEAL_DARK)
        self.screen.blit(
            lbl_o, lbl_o.get_rect(center=(WINDOW_WIDTH // 2 + 48, 179))
        )

    def _draw_game_control_bar(self, mouse_pos):
        if self.game_mode == MODE_HVAI:
            self._draw_segmented_bar(
                self.control_bar_rect,
                self.algo_tab_rects,
                self.algo_o_idx,
                mouse_pos,
            )
            return

        pygame.draw.rect(
            self.screen, COLOR_BG_DARK, self.control_bar_rect, border_radius=18
        )

        if self.game_mode == MODE_HVH:
            txt = self.font_pill.render(
                "Mode: Human vs Human", True, COLOR_WHITE
            )
            self.screen.blit(
                txt,
                txt.get_rect(
                    midleft=(
                        self.control_bar_rect.x + 16,
                        self.control_bar_rect.centery,
                    )
                ),
            )
            btn = self.change_mode_btn_rect
            is_hover = self.active_dialog is None and btn.collidepoint(mouse_pos)
            pygame.draw.rect(
                self.screen,
                COLOR_TILE_HOVER if is_hover else COLOR_WHITE,
                btn,
                border_radius=14,
            )
            btxt = self.font_pill.render("Ganti Mode", True, COLOR_BTN_RED)
            self.screen.blit(btxt, btxt.get_rect(center=btn.center))

        elif self.game_mode == MODE_AIVAI:
            algo_x = ALGORITHMS[self.algo_x_idx]["label"]
            algo_o = ALGORITHMS[self.algo_o_idx]["label"]
            info = f"X: {algo_x}  vs  O: {algo_o}"
            txt = self.font_pill.render(info, True, COLOR_WHITE)
            self.screen.blit(
                txt,
                txt.get_rect(
                    midleft=(
                        self.control_bar_rect.x + 14,
                        self.control_bar_rect.centery,
                    )
                ),
            )
            btn = self.pause_btn_rect
            is_hover = self.active_dialog is None and btn.collidepoint(mouse_pos)
            btn_bg = (
                COLOR_TILE_HOVER
                if (self.ai_paused or is_hover)
                else COLOR_WHITE
            )
            pygame.draw.rect(self.screen, btn_bg, btn, border_radius=14)
            btn_label = "Lanjut" if self.ai_paused else "Jeda"
            btxt = self.font_pill.render(btn_label, True, COLOR_BTN_RED)
            self.screen.blit(btxt, btxt.get_rect(center=btn.center))

    def _draw_board(self, mouse_pos):
        can_hover = (
            self.active_dialog is None and not self.is_ai_turn()
        )
        ghost_sym = (
            self.sym_x_ghost if self.current_turn == SYMBOL_X else self.sym_o_ghost
        )

        for idx, rect in enumerate(self.tile_rects):
            cell = self.board[idx]
            is_win_tile = (
                self.winning_line is not None and idx in self.winning_line
            )
            is_hover = can_hover and cell == EMPTY and rect.collidepoint(mouse_pos)

            shadow_rect = rect.move(0, 4)
            pygame.draw.rect(
                self.screen, COLOR_TILE_SHADOW, shadow_rect, border_radius=14
            )

            if is_win_tile:
                tile_color = COLOR_TILE_WIN
            elif is_hover:
                tile_color = COLOR_TILE_HOVER
            else:
                tile_color = COLOR_TILE

            pygame.draw.rect(self.screen, tile_color, rect, border_radius=14)

            if is_win_tile:
                pygame.draw.rect(
                    self.screen,
                    COLOR_WIN_RING,
                    rect,
                    width=3,
                    border_radius=14,
                )

            if cell == SYMBOL_X:
                self.screen.blit(self.sym_x, rect.topleft)
            elif cell == SYMBOL_O:
                self.screen.blit(self.sym_o, rect.topleft)
            elif is_hover:
                self.screen.blit(ghost_sym, rect.topleft)

    def _draw_stats_card(self):
        pygame.draw.rect(
            self.screen, COLOR_BG_CARD, self.stats_card_rect, border_radius=14
        )

        header_y = self.stats_card_rect.y + 16
        sep_y = self.stats_card_rect.y + 30

        if self.game_mode == MODE_HVH:
            title = self.font_stat_title.render(
                "Ringkasan Pertandingan", True, COLOR_WHITE_SOFT
            )
            self.screen.blit(title, (self.stats_card_rect.x + 14, header_y - 7))

            badge = self.font_stat_title.render(
                "Human vs Human", True, COLOR_TILE
            )
            self.screen.blit(
                badge,
                badge.get_rect(
                    midright=(self.stats_card_rect.right - 14, header_y)
                ),
            )
            metrics = (
                ("Langkah", f"{self.move_count} / 9"),
                ("Total Seri", str(self.draw_count)),
                ("Giliran", f"Player {'1 (X)' if self.current_turn == SYMBOL_X else '2 (O)'}"),
            )
        else:
            title = self.font_stat_title.render(
                "Statistik Langkah AI Terakhir", True, COLOR_WHITE_SOFT
            )
            self.screen.blit(title, (self.stats_card_rect.x + 14, header_y - 7))

            if self.last_stats is not None:
                badge_text = self.last_stat_badge
            elif self.game_mode == MODE_AIVAI:
                badge_text = "AI vs AI"
            else:
                badge_text = ALGORITHMS[self.algo_o_idx]["label"]

            badge = self.font_stat_title.render(badge_text, True, COLOR_TILE)
            self.screen.blit(
                badge,
                badge.get_rect(
                    midright=(self.stats_card_rect.right - 14, header_y)
                ),
            )

            if self.last_stats is not None:
                nodes_str = f"{self.last_stats['nodes']:,}"
                time_str = f"{self.last_stats['execution_time_ms']:.3f} ms"
                mem_str = f"{self.last_stats['peak_memory_kb']:.2f} KB"
            else:
                nodes_str = "-"
                time_str = "-"
                mem_str = "-"

            metrics = (
                ("Jumlah Node", nodes_str),
                ("Waktu Eksekusi", time_str),
                ("Peak Memory", mem_str),
            )

        pygame.draw.line(
            self.screen,
            COLOR_WHITE,
            (self.stats_card_rect.x + 14, sep_y),
            (self.stats_card_rect.right - 14, sep_y),
            1,
        )

        col_w = self.stats_card_rect.width / 3
        val_y = self.stats_card_rect.y + 52
        lbl_y = self.stats_card_rect.y + 73

        for i, (label, value) in enumerate(metrics):
            cx = int(self.stats_card_rect.x + col_w * (i + 0.5))
            val_surf = self.font_stat_val.render(value, True, COLOR_WHITE)
            self.screen.blit(val_surf, val_surf.get_rect(center=(cx, val_y)))

            lbl_surf = self.font_stat_lbl.render(label, True, COLOR_WHITE_SOFT)
            self.screen.blit(lbl_surf, lbl_surf.get_rect(center=(cx, lbl_y)))

    # -----------------------------------------------------------------------
    # Rendering Dialog Modal
    # -----------------------------------------------------------------------
    def _win_subtitle(self):
        if self.game_mode == MODE_HVH:
            return (
                "Player 1 (X) Menang!"
                if self.winner_symbol == SYMBOL_X
                else "Player 2 (O) Menang!"
            )
        if self.game_mode == MODE_HVAI:
            return (
                "Selamat, Anda Menang!"
                if self.winner_symbol == SYMBOL_X
                else "Komputer Menang!"
            )
        algo_name = ALGORITHMS[self.get_algo_idx_for_symbol(self.winner_symbol)][
            "label"
        ]
        ai_num = "AI 1" if self.winner_symbol == SYMBOL_X else "AI 2"
        return f"{ai_num} ({algo_name}) Menang!"

    def _draw_dialog_overlay(self, mouse_pos):
        if self.active_dialog is None:
            return

        backdrop = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 145))
        self.screen.blit(backdrop, (0, 0))

        if self.active_dialog in ("win", "draw"):
            card = pygame.Rect(0, 0, 324, 162)
            card.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
            pygame.draw.rect(self.screen, COLOR_WHITE, card, border_radius=22)

            if self.active_dialog == "win":
                headline = f"Pemenangnya : Player {self.winner_symbol}"
                subline = self._win_subtitle()
            else:
                headline = "Hasilnya Seri!"
                subline = "Semua kotak terisi tanpa pemenang."

            head_surf = self.font_dialog_title.render(
                headline, True, COLOR_TEXT_DARK
            )
            self.screen.blit(head_surf, (card.x + 24, card.y + 24))

            sub_surf = self.font_dialog_body.render(
                subline, True, COLOR_TEXT_MUTED
            )
            self.screen.blit(sub_surf, (card.x + 24, card.y + 56))

            # Tombol "Menu" (abu-abu) & "Main Lagi" (merah seperti Gambar 6 & 7)
            btn_play = pygame.Rect(card.right - 134, card.bottom - 58, 110, 38)
            btn_menu = pygame.Rect(btn_play.x - 96, card.bottom - 58, 84, 38)
            self.dialog_play_again_rect = btn_play
            self.dialog_menu_rect = btn_menu

            menu_color = (
                COLOR_BTN_GRAY_HOVER
                if btn_menu.collidepoint(mouse_pos)
                else COLOR_BTN_GRAY
            )
            pygame.draw.rect(self.screen, menu_color, btn_menu, border_radius=10)
            m_txt = self.font_dialog_btn.render("Menu", True, COLOR_TEXT_DARK)
            self.screen.blit(m_txt, m_txt.get_rect(center=btn_menu.center))

            play_color = (
                COLOR_BTN_RED_HOVER
                if btn_play.collidepoint(mouse_pos)
                else COLOR_BTN_RED
            )
            pygame.draw.rect(self.screen, play_color, btn_play, border_radius=10)
            p_txt = self.font_dialog_btn.render("Main Lagi", True, COLOR_WHITE)
            self.screen.blit(p_txt, p_txt.get_rect(center=btn_play.center))

        elif self.active_dialog == "exit":
            card = pygame.Rect(0, 0, 324, 182)
            card.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
            pygame.draw.rect(self.screen, COLOR_WHITE, card, border_radius=22)

            head_surf = self.font_dialog_title.render(
                "Peringatan !!", True, COLOR_TEXT_DARK
            )
            self.screen.blit(head_surf, (card.x + 24, card.y + 24))

            msg_surf = self.font_dialog_body.render(
                "Apakah Anda yakin ingin keluar?", True, COLOR_TEXT_DARK
            )
            self.screen.blit(msg_surf, (card.x + 24, card.y + 66))

            btn_w, btn_h = 84, 38
            gap = 14
            start_x = card.centerx - (btn_w * 2 + gap) // 2 + 18
            btn_y = card.bottom - 58

            yes_rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
            no_rect = pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h)
            self.dialog_yes_rect = yes_rect
            self.dialog_no_rect = no_rect

            yes_color = (
                COLOR_BTN_RED_HOVER
                if yes_rect.collidepoint(mouse_pos)
                else COLOR_BTN_RED
            )
            pygame.draw.rect(self.screen, yes_color, yes_rect, border_radius=10)
            yes_txt = self.font_dialog_btn.render("Ya", True, COLOR_WHITE)
            self.screen.blit(yes_txt, yes_txt.get_rect(center=yes_rect.center))

            no_color = (
                COLOR_BTN_GRAY_HOVER
                if no_rect.collidepoint(mouse_pos)
                else COLOR_BTN_GRAY
            )
            pygame.draw.rect(self.screen, no_color, no_rect, border_radius=10)
            no_txt = self.font_dialog_btn.render(
                "Tidak", True, COLOR_TEXT_DARK
            )
            self.screen.blit(no_txt, no_txt.get_rect(center=no_rect.center))

    def render(self):
        mouse_pos = pygame.mouse.get_pos()
        self.screen.fill(COLOR_BG)
        if self.screen_state == "menu":
            self._draw_menu(mouse_pos)
        else:
            self._draw_top_bar(mouse_pos)
            self._draw_status_and_score()
            self._draw_game_control_bar(mouse_pos)
            self._draw_board(mouse_pos)
            self._draw_stats_card()
        self._draw_dialog_overlay(mouse_pos)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    app = TicTacToeUI()
    app.run()


if __name__ == "__main__":
    main()
