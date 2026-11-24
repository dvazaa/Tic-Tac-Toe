import csv
import os
import sys
import time
import tracemalloc
from datetime import datetime
import pygame

from board.board import (
    AI,
    HUMAN,
    EMPTY,
    create_board,
    make_move,
    check_winner,
    is_game_over,
)
from algorithms.minimax import find_best_move as minimax_move
from algorithms.alpha_beta import find_best_move as alpha_beta_move

# --- KONFIGURASI WARNA & LAYAR ---
GAME_AREA_W = 480
STATS_PANEL_W = 280
WIDTH = GAME_AREA_W + STATS_PANEL_W  # 760
HEIGHT = 620
FPS = 60

BG_COLOR = (245, 247, 250)
PANEL_BG = (235, 240, 245)
HEADER_COLOR = (41, 128, 185)
YELLOW_CELL = (241, 196, 15)
YELLOW_HOVER = (247, 215, 75)
TEXT_DARK = (44, 62, 80)
TEXT_MUTED = (100, 115, 130)
TEXT_LIGHT = (255, 255, 255)
COLOR_X = (231, 76, 60)
COLOR_O = (41, 128, 185)
BTN_COLOR = (52, 152, 219)
BTN_HOVER = (41, 128, 185)
BTN_DANGER = (231, 76, 60)
BTN_SUCCESS = (46, 204, 113)
OVERLAY_BG = (0, 0, 0, 150)

LOG_FILE = "game_metrics_log.csv"

ALGO_MAP = {
    "Minimax": minimax_move,
    "Alpha-Beta": alpha_beta_move,
}


def draw_button(screen, rect, text, font, bg_color, hover_color, mouse_pos, text_color=TEXT_LIGHT):
    color = hover_color if rect.collidepoint(mouse_pos) else bg_color
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect


class TicTacToeUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe - Minimax & Alpha-Beta Pruning")
        self.clock = pygame.time.Clock()

        # Font
        self.font_title = pygame.font.SysFont("segoeui", 30, bold=True)
        self.font_large = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_med = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 15)
        self.font_small_bold = pygame.font.SysFont("segoeui", 15, bold=True)
        self.font_symbol = pygame.font.SysFont("segoeui", 64, bold=True)

        # State Navigasi
        self.screen_state = "menu"

        # Pengaturan Mode & Algoritma
        self.mode = "Human vs AI"
        self.algo_p1 = "Minimax"
        self.algo_p2 = "Alpha-Beta"

        # State Permainan
        self.board = create_board()
        self.current_player = HUMAN
        self.score_o = 0
        self.score_x = 0
        self.round_num = 1
        self.popup = None
        self.result_text = ""
        self.last_ai_time = 0

        # Data Statistik Pengukuran Terakhir & Riwayat Sesi
        self.last_metrics = {
            "algo": "-",
            "player": "-",
            "move": "-",
            "nodes": 0,
            "time_ms": 0.0,
            "peak_kb": 0.0,
            "quality": "-",
        }
        self.total_nodes_session = 0
        self.total_moves_ai = 0

        # Layout Papan 3x3 (di sisi kiri)
        self.cell_size = 110
        self.cell_gap = 12
        grid_total = self.cell_size * 3 + self.cell_gap * 2
        self.grid_start_x = (GAME_AREA_W - grid_total) // 2
        self.grid_start_y = 215

        self._init_csv_log()

    def _init_csv_log(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp",
                    "Mode",
                    "Ronde",
                    "Pemain",
                    "Algoritma",
                    "Indeks_Langkah",
                    "Jumlah_Node",
                    "Waktu_Eksekusi_ms",
                    "Peak_Memory_KB",
                    "Kualitas_Keputusan",
                ])

    def _save_metrics_to_csv(self, player, algo_name, move, nodes, time_ms, peak_kb, quality):
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.mode,
                self.round_num,
                player,
                algo_name,
                move,
                nodes,
                f"{time_ms:.4f}",
                f"{peak_kb:.4f}",
                quality,
            ])

    def start_new_session(self):
        self.score_o = 0
        self.score_x = 0
        self.round_num = 1
        self.total_nodes_session = 0
        self.total_moves_ai = 0
        self.last_metrics = {
            "algo": "-",
            "player": "-",
            "move": "-",
            "nodes": 0,
            "time_ms": 0.0,
            "peak_kb": 0.0,
            "quality": "-",
        }
        self.reset_board_only()
        self.screen_state = "game"

    def reset_board_only(self):
        self.board = create_board()
        self.current_player = HUMAN if self.round_num % 2 == 1 else AI
        self.popup = None
        self.result_text = ""
        self.last_ai_time = pygame.time.get_ticks()

    def get_player_controller(self, player):
        if self.mode == "Human vs Human":
            return None, None
        elif self.mode == "Human vs AI":
            if player == HUMAN:
                return None, None
            return ALGO_MAP[self.algo_p2], self.algo_p2
        else:
            if player == HUMAN:
                return ALGO_MAP[self.algo_p1], self.algo_p1
            return ALGO_MAP[self.algo_p2], self.algo_p2

    def check_end_state(self):
        if not is_game_over(self.board):
            return False

        winner = check_winner(self.board)
        if winner == HUMAN:
            self.score_o += 1
            self.result_text = "Pemain O Menang!"
        elif winner == AI:
            self.score_x += 1
            self.result_text = "Pemain X Menang!"
        else:
            self.result_text = "Permainan Seri!"

        self.popup = "gameover"
        return True

    def handle_ai_turn(self):
        if self.screen_state != "game" or self.popup is not None:
            return

        algo_fn, algo_name = self.get_player_controller(self.current_player)
        if algo_fn is None:
            return

        now = pygame.time.get_ticks()
        if now - self.last_ai_time < 400:
            return

        # --- PENGUKURAN WAKTU, MEMORI, & NODE ---
        tracemalloc.start()
        t_start = time.perf_counter()
        result = algo_fn(self.board, self.current_player)
        exec_time_ms = (time.perf_counter() - t_start) * 1000
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_kb = peak_mem / 1024

        # Ekstrak hasil (move, nodes) dari return fungsi algoritma
        move = result[0]
        nodes = result[1] if len(result) > 1 else 0

        # --- PENGUKURAN KUALITAS KEPUTUSAN ---
        # Bandingkan dengan langkah optimal Minimax (jika pakai Alpha-Beta)
        if algo_name == "Minimax":
            quality = "Optimal"
        else:
            opt_res = minimax_move(self.board.copy(), self.current_player)
            opt_move = opt_res[0]
            quality = "Optimal" if move == opt_move else "Optimal (Alternatif)"

        if move is not None:
            make_move(self.board, move, self.current_player)

            # Simpan ke state UI & CSV
            self.total_nodes_session += nodes
            self.total_moves_ai += 1
            self.last_metrics = {
                "algo": algo_name,
                "player": self.current_player,
                "move": f"Kotak {move + 1}",
                "nodes": nodes,
                "time_ms": exec_time_ms,
                "peak_kb": peak_kb,
                "quality": quality,
            }
            self._save_metrics_to_csv(
                self.current_player,
                algo_name,
                move,
                nodes,
                exec_time_ms,
                peak_kb,
                quality,
            )

            if not self.check_end_state():
                self.current_player = AI if self.current_player == HUMAN else HUMAN
                self.last_ai_time = pygame.time.get_ticks()

    # ---------------- RENDER MENU ----------------
    def draw_menu(self, mouse_pos):
        self.screen.fill(BG_COLOR)

        pygame.draw.rect(self.screen, HEADER_COLOR, (0, 0, WIDTH, 90))
        title = self.font_title.render("TIC-TAC-TOE", True, TEXT_LIGHT)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 45)))

        self.menu_buttons = {}
        menu_w = 420
        menu_x = (WIDTH - menu_w) // 2

        lbl_mode = self.font_med.render("1. Pilih Mode Permainan:", True, TEXT_DARK)
        self.screen.blit(lbl_mode, (menu_x, 115))

        modes = ["Human vs Human", "Human vs AI", "AI vs AI"]
        for i, m in enumerate(modes):
            rect = pygame.Rect(menu_x, 150 + i * 50, menu_w, 40)
            bg = BTN_SUCCESS if self.mode == m else (189, 195, 199)
            hover = BTN_SUCCESS if self.mode == m else (149, 165, 166)
            self.menu_buttons[f"mode_{m}"] = draw_button(self.screen, rect, m, self.font_med, bg, hover, mouse_pos)

        y_algo = 320
        half_w = (menu_w - 15) // 2
        if self.mode == "Human vs AI":
            lbl = self.font_med.render("2. Pilih Algoritma AI (X):", True, TEXT_DARK)
            self.screen.blit(lbl, (menu_x, y_algo))
            for i, algo in enumerate(["Minimax", "Alpha-Beta"]):
                rect = pygame.Rect(menu_x + i * (half_w + 15), y_algo + 35, half_w, 42)
                bg = BTN_COLOR if self.algo_p2 == algo else (189, 195, 199)
                self.menu_buttons[f"algo2_{algo}"] = draw_button(self.screen, rect, algo, self.font_med, bg, BTN_HOVER, mouse_pos)

        elif self.mode == "AI vs AI":
            lbl1 = self.font_med.render("2. Algoritma AI 1 (O):", True, TEXT_DARK)
            self.screen.blit(lbl1, (menu_x, y_algo))
            for i, algo in enumerate(["Minimax", "Alpha-Beta"]):
                rect = pygame.Rect(menu_x + i * (half_w + 15), y_algo + 30, half_w, 38)
                bg = BTN_COLOR if self.algo_p1 == algo else (189, 195, 199)
                self.menu_buttons[f"algo1_{algo}"] = draw_button(self.screen, rect, algo, self.font_med, bg, BTN_HOVER, mouse_pos)

            lbl2 = self.font_med.render("3. Algoritma AI 2 (X):", True, TEXT_DARK)
            self.screen.blit(lbl2, (menu_x, y_algo + 80))
            for i, algo in enumerate(["Minimax", "Alpha-Beta"]):
                rect = pygame.Rect(menu_x + i * (half_w + 15), y_algo + 110, half_w, 38)
                bg = BTN_COLOR if self.algo_p2 == algo else (189, 195, 199)
                self.menu_buttons[f"algo2_{algo}"] = draw_button(self.screen, rect, algo, self.font_med, bg, BTN_HOVER, mouse_pos)

        start_rect = pygame.Rect(menu_x, HEIGHT - 85, menu_w, 50)
        self.menu_buttons["start"] = draw_button(self.screen, start_rect, "MULAI PERMAINAN", self.font_large, HEADER_COLOR, (31, 97, 141), mouse_pos)

    # ---------------- RENDER GAME & PANEL STATISTIK ----------------
    def draw_game(self, mouse_pos):
        self.screen.fill(BG_COLOR)
        self.game_buttons = {}

        # Header
        pygame.draw.rect(self.screen, HEADER_COLOR, (0, 0, WIDTH, 70))
        title = self.font_large.render("Tic Tac Toe", True, TEXT_LIGHT)
        self.screen.blit(title, title.get_rect(center=(GAME_AREA_W // 2, 35)))

        btn_back = pygame.Rect(15, 17, 90, 36)
        btn_reset = pygame.Rect(GAME_AREA_W - 105, 17, 90, 36)
        self.game_buttons["back"] = draw_button(self.screen, btn_back, "Kembali", self.font_small, (52, 73, 94), (44, 62, 80), mouse_pos)
        self.game_buttons["reset"] = draw_button(self.screen, btn_reset, "Reset", self.font_small, BTN_DANGER, (192, 57, 43), mouse_pos)

        # Panel Skor & Indikator Giliran (Sisi Kiri)
        turn_o_bg = (214, 234, 248) if self.current_player == HUMAN else (235, 237, 239)
        turn_x_bg = (250, 219, 216) if self.current_player == AI else (235, 237, 239)

        pygame.draw.rect(self.screen, turn_o_bg, (35, 95, 140, 85), border_radius=12)
        pygame.draw.rect(self.screen, turn_x_bg, (GAME_AREA_W - 175, 95, 140, 85), border_radius=12)

        lbl_o = self.font_med.render("Pemain O", True, COLOR_O)
        lbl_x = self.font_med.render("Pemain X", True, COLOR_X)
        self.screen.blit(lbl_o, lbl_o.get_rect(center=(105, 120)))
        self.screen.blit(lbl_x, lbl_x.get_rect(center=(GAME_AREA_W - 105, 120)))

        score_text = self.font_title.render(f"{self.score_o} : {self.score_x}", True, TEXT_DARK)
        self.screen.blit(score_text, score_text.get_rect(center=(GAME_AREA_W // 2, 138)))

        lbl_turn = self.font_small.render(f"Giliran: {self.current_player} (Ronde {self.round_num})", True, TEXT_DARK)
        self.screen.blit(lbl_turn, lbl_turn.get_rect(center=(GAME_AREA_W // 2, 185)))

        # Papan 3x3
        self.cell_rects = []
        for idx in range(9):
            row, col = divmod(idx, 3)
            x = self.grid_start_x + col * (self.cell_size + self.cell_gap)
            y = self.grid_start_y + row * (self.cell_size + self.cell_gap)
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            self.cell_rects.append(rect)

            is_hover = rect.collidepoint(mouse_pos) and self.board[idx] == EMPTY and self.popup is None
            color = YELLOW_HOVER if is_hover else YELLOW_CELL
            pygame.draw.rect(self.screen, color, rect, border_radius=12)

            if self.board[idx] != EMPTY:
                sym_color = COLOR_O if self.board[idx] == HUMAN else COLOR_X
                sym = self.font_symbol.render(self.board[idx], True, sym_color)
                self.screen.blit(sym, sym.get_rect(center=rect.center))

        # --- PANEL STATISTIK (SISI KANAN) ---
        self.draw_stats_panel()

        if self.popup is not None:
            self.draw_popup(mouse_pos)

    def draw_stats_panel(self):
        panel_rect = pygame.Rect(GAME_AREA_W, 70, STATS_PANEL_W, HEIGHT - 70)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, (200, 210, 220), (GAME_AREA_W, 70), (GAME_AREA_W, HEIGHT), 2)

        x = GAME_AREA_W + 20
        y = 95

        header_lbl = self.font_med.render("Pengukuran Performa AI", True, HEADER_COLOR)
        self.screen.blit(header_lbl, (x, y))
        y += 35

        m = self.last_metrics
        items = [
            ("Algoritma Terakhir", f"{m['algo']} ({m['player']})"),
            ("Langkah Dipilih", str(m["move"])),
            ("Jumlah Node", f"{m['nodes']:,}"),
            ("Waktu Eksekusi", f"{m['time_ms']:.3f} ms"),
            ("Peak Memory", f"{m['peak_kb']:.2f} KB"),
            ("Kualitas Keputusan", str(m["quality"])),
        ]

        for label, value in items:
            card = pygame.Rect(x, y, STATS_PANEL_W - 40, 56)
            pygame.draw.rect(self.screen, TEXT_LIGHT, card, border_radius=8)
            lbl_surf = self.font_small.render(label, True, TEXT_MUTED)
            val_surf = self.font_small_bold.render(value, True, TEXT_DARK)
            self.screen.blit(lbl_surf, (x + 12, y + 7))
            self.screen.blit(val_surf, (x + 12, y + 28))
            y += 66

        # Info Ringkasan & Log CSV
        y += 5
        summary = self.font_small.render(f"Total Node Sesi: {self.total_nodes_session:,}", True, TEXT_DARK)
        self.screen.blit(summary, (x, y))
        log_info = self.font_small.render(f"Log: {LOG_FILE}", True, BTN_SUCCESS)
        self.screen.blit(log_info, (x, y + 22))

    def draw_popup(self, mouse_pos):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect((WIDTH - 380) // 2, 200, 380, 200)
        pygame.draw.rect(self.screen, TEXT_LIGHT, box, border_radius=15)

        if self.popup == "gameover":
            msg = self.font_large.render(self.result_text, True, TEXT_DARK)
            self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 255)))

            btn_again = pygame.Rect(box.x + 35, 315, 145, 45)
            btn_menu = pygame.Rect(box.x + 200, 315, 145, 45)
            self.game_buttons["play_again"] = draw_button(self.screen, btn_again, "Main Lagi", self.font_med, BTN_SUCCESS, (39, 174, 96), mouse_pos)
            self.game_buttons["to_menu"] = draw_button(self.screen, btn_menu, "Menu Utama", self.font_med, BTN_COLOR, BTN_HOVER, mouse_pos)

        elif self.popup == "exit_confirm":
            msg = self.font_med.render("Yakin ingin kembali ke menu?", True, TEXT_DARK)
            self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 255)))

            btn_yes = pygame.Rect(box.x + 45, 315, 130, 45)
            btn_no = pygame.Rect(box.x + 205, 315, 130, 45)
            self.game_buttons["confirm_yes"] = draw_button(self.screen, btn_yes, "Ya", self.font_med, BTN_DANGER, (192, 57, 43), mouse_pos)
            self.game_buttons["confirm_no"] = draw_button(self.screen, btn_no, "Tidak", self.font_med, (149, 165, 166), (127, 140, 141), mouse_pos)

    # ---------------- EVENT HANDLER ----------------
    def handle_click(self, pos):
        if self.screen_state == "menu":
            for key, rect in self.menu_buttons.items():
                if rect.collidepoint(pos):
                    if key.startswith("mode_"):
                        self.mode = key.replace("mode_", "")
                    elif key.startswith("algo1_"):
                        self.algo_p1 = key.replace("algo1_", "")
                    elif key.startswith("algo2_"):
                        self.algo_p2 = key.replace("algo2_", "")
                    elif key == "start":
                        self.start_new_session()
            return

        if self.popup == "gameover":
            if self.game_buttons["play_again"].collidepoint(pos):
                self.round_num += 1
                self.reset_board_only()
            elif self.game_buttons["to_menu"].collidepoint(pos):
                self.screen_state = "menu"
            return

        if self.popup == "exit_confirm":
            if self.game_buttons["confirm_yes"].collidepoint(pos):
                self.screen_state = "menu"
                self.popup = None
            elif self.game_buttons["confirm_no"].collidepoint(pos):
                self.popup = None
            return

        if self.game_buttons["back"].collidepoint(pos):
            self.popup = "exit_confirm"
            return
        if self.game_buttons["reset"].collidepoint(pos):
            self.start_new_session()
            return

        algo_fn, _ = self.get_player_controller(self.current_player)
        if algo_fn is None:
            for idx, rect in enumerate(self.cell_rects):
                if rect.collidepoint(pos):
                    if make_move(self.board, idx, self.current_player):
                        if not self.check_end_state():
                            self.current_player = AI if self.current_player == HUMAN else HUMAN
                            self.last_ai_time = pygame.time.get_ticks()
                    break

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.handle_ai_turn()

            if self.screen_state == "menu":
                self.draw_menu(mouse_pos)
            else:
                self.draw_game(mouse_pos)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = TicTacToeUI()
    app.run()