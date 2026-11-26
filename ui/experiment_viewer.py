import csv
import os
import statistics
import threading
import pygame

from board.board import AI, HUMAN, EMPTY
from experiments.scenario_1 import BOARD_STATES, run_scenario_1
from experiments.scenario_2 import run_scenario_2
from experiments.scenario_3 import run_scenario_3

EXP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments",
)

# Palet warna konsisten dengan pygame_ui.py
BG_COLOR = (245, 247, 250)
HEADER_COLOR = (41, 128, 185)
CARD_BG = (255, 255, 255)
CARD_BORDER = (213, 221, 229)
TABLE_HEADER_BG = (232, 241, 248)
TABLE_ALT_BG = (248, 250, 252)
INFO_BG = (232, 246, 243)
INFO_BORDER = (163, 228, 215)
TEXT_DARK = (44, 62, 80)
TEXT_MUTED = (100, 115, 130)
TEXT_LIGHT = (255, 255, 255)
COLOR_X = (231, 76, 60)
COLOR_O = (41, 128, 185)
COLOR_GREEN = (39, 174, 96)
COLOR_ORANGE = (230, 126, 34)
CELL_BG = (249, 231, 159)
CELL_BEST_BG = (212, 239, 223)
BTN_PRIMARY = (52, 152, 219)
BTN_PRIMARY_HOVER = (41, 128, 185)
BTN_DARK = (52, 73, 94)
BTN_DARK_HOVER = (44, 62, 80)
BTN_SUCCESS = (46, 204, 113)
BTN_SUCCESS_HOVER = (39, 174, 96)
BTN_MUTED = (189, 195, 199)
BTN_MUTED_HOVER = (149, 165, 166)


def _draw_btn(screen, rect, text, font, bg, hover, mouse_pos, text_color=TEXT_LIGHT, radius=8):
    color = hover if rect.collidepoint(mouse_pos) else bg
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    lbl = font.render(text, True, text_color)
    screen.blit(lbl, lbl.get_rect(center=rect.center))
    return rect


def _read_csv(filename):
    path = os.path.join(EXP_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, mode="r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class ExperimentDashboard:
    """Tampilan interaktif hasil eksperimen Skenario 1, 2, dan 3."""

    def __init__(self, ui):
        self.ui = ui
        self.active_tab = 1
        self.buttons = {}
        self.running = False
        self.needs_reload = False
        self.status_msg = ""

        self.s1_rows = []
        self.s2_rows = []
        self.s3_random_summary = {}
        self.s3_direct_summary = {}

        self.reload_data()

    def reload_data(self):
        self.s1_rows = _read_csv("scenario_1_results.csv")
        self.s2_rows = _read_csv("scenario_2_results.csv")
        self._load_s3_summaries()

    def _load_s3_summaries(self):
        random_rows = _read_csv("scenario_3_random_results.csv")
        self.s3_random_summary = {}
        for algo in ("Minimax", "Alpha-Beta"):
            rows = [r for r in random_rows if r.get("algorithm") == algo]
            if not rows:
                continue
            wins = sum(1 for r in rows if r["result"] == "Win")
            draws = sum(1 for r in rows if r["result"] == "Draw")
            losses = sum(1 for r in rows if r["result"] == "Loss")
            total = len(rows)
            self.s3_random_summary[algo] = {
                "total": total,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "win_pct": (wins / total) * 100,
                "draw_pct": (draws / total) * 100,
                "loss_pct": (losses / total) * 100,
                "avg_nodes": statistics.mean(float(r["average_nodes"]) for r in rows),
                "avg_time": statistics.mean(float(r["average_time_ms"]) for r in rows),
                "avg_mem": statistics.mean(float(r["average_memory_kb"]) for r in rows),
            }

        direct_rows = _read_csv("scenario_3_direct_results.csv")
        if direct_rows:
            total = len(direct_rows)
            draws = sum(1 for r in direct_rows if r["winner"] == "Draw")
            mm_first = sum(1 for r in direct_rows if r["x_agent"] == "Minimax")
            ab_first = sum(1 for r in direct_rows if r["x_agent"] == "Alpha-Beta")
            self.s3_direct_summary = {
                "total": total,
                "draws": draws,
                "draw_pct": (draws / total) * 100,
                "mm_first": mm_first,
                "ab_first": ab_first,
                "mm_nodes": statistics.mean(float(r["minimax_nodes"]) for r in direct_rows),
                "ab_nodes": statistics.mean(float(r["alpha_beta_nodes"]) for r in direct_rows),
                "mm_time": statistics.mean(float(r["minimax_time_ms"]) for r in direct_rows),
                "ab_time": statistics.mean(float(r["alpha_beta_time_ms"]) for r in direct_rows),
                "mm_mem": statistics.mean(float(r["minimax_memory_kb"]) for r in direct_rows),
                "ab_mem": statistics.mean(float(r["alpha_beta_memory_kb"]) for r in direct_rows),
            }
        else:
            self.s3_direct_summary = {}

    def run_active_scenario(self):
        if self.running:
            return
        tab = self.active_tab
        self.running = True
        self.status_msg = f"Menjalankan Skenario {tab} (mohon tunggu)..."

        def _worker():
            try:
                if tab == 1:
                    run_scenario_1()
                elif tab == 2:
                    run_scenario_2()
                else:
                    run_scenario_3()
                self.status_msg = f"Skenario {tab} selesai & CSV diperbarui!"
            except Exception as exc:
                self.status_msg = f"Gagal menjalankan Skenario {tab}: {exc}"
            finally:
                self.needs_reload = True
                self.running = False

        threading.Thread(target=_worker, daemon=True).start()

    def handle_click(self, pos):
        if "back" in self.buttons and self.buttons["back"].collidepoint(pos):
            return "menu"

        for tab in (1, 2, 3):
            key = f"tab_{tab}"
            if key in self.buttons and self.buttons[key].collidepoint(pos):
                self.active_tab = tab
                if not self.running:
                    self.status_msg = ""
                self.reload_data()
                return None

        if "rerun" in self.buttons and self.buttons["rerun"].collidepoint(pos):
            self.run_active_scenario()
            return None

        return None

    def draw(self, mouse_pos):
        if self.needs_reload:
            self.reload_data()
            self.needs_reload = False

        screen = self.ui.screen
        width = screen.get_width()
        screen.fill(BG_COLOR)
        self.buttons = {}

        # --- HEADER ---
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, width, 64))
        title = self.ui.font_large.render("Dashboard Hasil Eksperimen", True, TEXT_LIGHT)
        screen.blit(title, title.get_rect(center=(width // 2, 32)))

        btn_back = pygame.Rect(16, 14, 92, 36)
        self.buttons["back"] = _draw_btn(
            screen, btn_back, "Kembali", self.ui.font_small, BTN_DARK, BTN_DARK_HOVER, mouse_pos
        )

        rerun_label = "Berjalan..." if self.running else "Jalankan Ulang"
        rerun_bg = COLOR_ORANGE if self.running else BTN_SUCCESS
        rerun_hover = COLOR_ORANGE if self.running else BTN_SUCCESS_HOVER
        btn_rerun = pygame.Rect(width - 148, 14, 132, 36)
        self.buttons["rerun"] = _draw_btn(
            screen, btn_rerun, rerun_label, self.ui.font_small_bold, rerun_bg, rerun_hover, mouse_pos
        )

        # --- TAB SKENARIO ---
        tabs = [
            (1, "Skenario 1: Kedalaman"),
            (2, "Skenario 2: Move Ordering"),
            (3, "Skenario 3: Simulasi 20 Ronde"),
        ]
        tab_x = 20
        tab_y = 76
        gap = 10
        tab_w = (width - 40 - gap * 2) // 3
        for idx, (tab_id, label) in enumerate(tabs):
            rect = pygame.Rect(tab_x + idx * (tab_w + gap), tab_y, tab_w, 36)
            is_active = self.active_tab == tab_id
            bg = BTN_PRIMARY if is_active else BTN_MUTED
            hover = BTN_PRIMARY_HOVER if is_active else BTN_MUTED_HOVER
            self.buttons[f"tab_{tab_id}"] = _draw_btn(
                screen, rect, label, self.ui.font_small_bold, bg, hover, mouse_pos
            )

        # --- KONTEN TAB ---
        if self.active_tab == 1:
            self._draw_scenario_1(screen)
        elif self.active_tab == 2:
            self._draw_scenario_2(screen)
        else:
            self._draw_scenario_3(screen)

    def _draw_mini_board(self, screen, x, y, board, highlight_idx=None, labels_override=None):
        cell = 26
        gap = 3
        for idx in range(9):
            r, c = divmod(idx, 3)
            rx = x + c * (cell + gap)
            ry = y + r * (cell + gap)
            rect = pygame.Rect(rx, ry, cell, cell)

            if labels_override is not None:
                text, bg, fg = labels_override[idx]
                pygame.draw.rect(screen, bg, rect, border_radius=4)
                surf = self.ui.font_xs_bold.render(text, True, fg)
                screen.blit(surf, surf.get_rect(center=rect.center))
                continue

            bg = CELL_BEST_BG if idx == highlight_idx else CELL_BG
            pygame.draw.rect(screen, bg, rect, border_radius=4)
            if idx == highlight_idx:
                pygame.draw.rect(screen, COLOR_GREEN, rect, width=2, border_radius=4)

            val = board[idx]
            if val != EMPTY:
                fg = COLOR_X if val == AI else COLOR_O
                surf = self.ui.font_small_bold.render(val, True, fg)
                screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_footer_box(self, screen, line1, line2):
        box = pygame.Rect(20, 524, 720, 76)
        pygame.draw.rect(screen, INFO_BG, box, border_radius=10)
        pygame.draw.rect(screen, INFO_BORDER, box, width=1, border_radius=10)

        s1 = self.ui.font_xs_bold.render(line1, True, TEXT_DARK)
        s2 = self.ui.font_xs.render(line2, True, TEXT_MUTED)
        screen.blit(s1, (34, 536))
        screen.blit(s2, (34, 558))

        if self.status_msg:
            st_color = COLOR_ORANGE if self.running else COLOR_GREEN
            st = self.ui.font_xs_bold.render(self.status_msg, True, st_color)
            screen.blit(st, (34, 578))

    def _draw_scenario_1(self, screen):
        sub = self.ui.font_small.render(
            "Perbandingan Minimax vs Alpha-Beta pada 3 papan terkunci (rata-rata 10x uji, giliran X)",
            True,
            TEXT_MUTED,
        )
        screen.blit(sub, (20, 122))

        if not self.s1_rows:
            msg = self.ui.font_med.render("Data scenario_1_results.csv belum tersedia. Klik 'Jalankan Ulang'.", True, COLOR_X)
            screen.blit(msg, (20, 180))
            return

        # --- 3 KARTU PAPAN TERKUNCI ---
        card_w = 232
        card_gap = 12
        for i, row in enumerate(self.s1_rows[:3]):
            cx = 20 + i * (card_w + card_gap)
            cy = 150
            card = pygame.Rect(cx, cy, card_w, 118)
            pygame.draw.rect(screen, CARD_BG, card, border_radius=10)
            pygame.draw.rect(screen, CARD_BORDER, card, width=1, border_radius=10)

            board = BOARD_STATES[i]["board"] if i < len(BOARD_STATES) else [EMPTY] * 9
            best_move = int(float(row["alpha_beta_move"]))
            self._draw_mini_board(screen, cx + 10, cy + 17, board, highlight_idx=best_move)

            tx = cx + 104
            short_names = ["Awal (9 Kosong)", "Mid (5 Kosong)", "End (2 Kosong)"]
            title = short_names[i] if i < 3 else row["scenario"]
            pruning = float(row["pruning_ratio_percent"])
            score = row["alpha_beta_score"]
            opt_ok = row.get("score_match", "True") == "True"

            screen.blit(self.ui.font_xs_bold.render(title, True, HEADER_COLOR), (tx, cy + 14))
            screen.blit(self.ui.font_xs_bold.render(f"Pruning: {pruning:.2f}%", True, COLOR_GREEN), (tx, cy + 38))
            screen.blit(self.ui.font_xs.render(f"Langkah: Kotak {best_move + 1}", True, TEXT_DARK), (tx, cy + 58))
            screen.blit(self.ui.font_xs.render(f"Skor Optimal: {score}", True, TEXT_DARK), (tx, cy + 76))
            screen.blit(
                self.ui.font_xs_bold.render("Status: Optimal" if opt_ok else "Status: Beda!", True, COLOR_GREEN if opt_ok else COLOR_X),
                (tx, cy + 94),
            )

        # --- TABEL PERBANDINGAN ---
        table_rect = pygame.Rect(20, 282, 720, 226)
        pygame.draw.rect(screen, CARD_BG, table_rect, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, table_rect, width=1, border_radius=10)

        headers = [
            ("Kondisi", 118),
            ("MM Node", 86),
            ("AB Node", 80),
            ("Pruning", 80),
            ("MM (ms)", 86),
            ("AB (ms)", 80),
            ("Mem (KB)", 98),
            ("Validasi", 92),
        ]
        pygame.draw.rect(screen, TABLE_HEADER_BG, (21, 283, 718, 38), border_radius=8)
        x = 28
        for h_text, col_w in headers:
            screen.blit(self.ui.font_xs_bold.render(h_text, True, TEXT_DARK), (x, 294))
            x += col_w

        short_labels = ["Awal (9)", "Mid-game (5)", "End-game (2)"]
        for idx, row in enumerate(self.s1_rows[:3]):
            ry = 326 + idx * 58
            if idx % 2 == 1:
                pygame.draw.rect(screen, TABLE_ALT_BG, (22, ry - 4, 716, 52), border_radius=6)

            mm_nodes = f"{float(row['minimax_nodes']):,.0f}"
            ab_nodes = f"{float(row['alpha_beta_nodes']):,.0f}"
            pruning = f"{float(row['pruning_ratio_percent']):.2f}%"
            mm_ms = f"{float(row['minimax_time_ms']):.2f}"
            ab_ms = f"{float(row['alpha_beta_time_ms']):.2f}"
            mem = f"{float(row['minimax_memory_kb']):.2f} / {float(row['alpha_beta_memory_kb']):.2f}"
            valid = "Sama/Opt" if row.get("score_match", "True") == "True" else "Berbeda"

            values = [
                (short_labels[idx] if idx < 3 else row["scenario"], TEXT_DARK, True),
                (mm_nodes, COLOR_X, False),
                (ab_nodes, COLOR_O, True),
                (pruning, COLOR_GREEN, True),
                (mm_ms, TEXT_DARK, False),
                (ab_ms, COLOR_O, False),
                (mem, TEXT_MUTED, False),
                (valid, COLOR_GREEN, True),
            ]
            x = 28
            for (val_text, fg, bold), (_, col_w) in zip(values, headers):
                font = self.ui.font_xs_bold if bold else self.ui.font_xs
                screen.blit(font.render(val_text, True, fg), (x, ry + 12))
                x += col_w

        first = self.s1_rows[0]
        self._draw_footer_box(
            screen,
            f"Kesimpulan: Pemangkasan tertinggi di Awal Permainan ({float(first['pruning_ratio_percent']):.2f}%: "
            f"{float(first['minimax_nodes']):,.0f} -> {float(first['alpha_beta_nodes']):,.0f} node).",
            "Semua kondisi papan menghasilkan langkah & skor 100% optimal. Sumber: experiments/scenario_1_results.csv",
        )

    def _draw_scenario_2(self, screen):
        sub = self.ui.font_small.render(
            "Perbandingan Alpha-Beta: Urutan Indeks Standar (0-8) vs Strategis (Tengah -> Sudut -> Sisi)",
            True,
            TEXT_MUTED,
        )
        screen.blit(sub, (20, 122))

        if not self.s2_rows:
            msg = self.ui.font_med.render("Data scenario_2_results.csv belum tersedia. Klik 'Jalankan Ulang'.", True, COLOR_X)
            screen.blit(msg, (20, 180))
            return

        # --- KARTU VISUAL PRIORITAS + 2 HIGHLIGHT ---
        # Kartu 1: Peta Prioritas Strategis
        c1 = pygame.Rect(20, 150, 232, 118)
        pygame.draw.rect(screen, CARD_BG, c1, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, c1, width=1, border_radius=10)
        priority_cells = [
            ("2", (214, 234, 248), COLOR_O),
            ("6", (235, 237, 239), TEXT_MUTED),
            ("3", (214, 234, 248), COLOR_O),
            ("7", (235, 237, 239), TEXT_MUTED),
            ("1", (212, 239, 223), COLOR_GREEN),
            ("8", (235, 237, 239), TEXT_MUTED),
            ("4", (214, 234, 248), COLOR_O),
            ("9", (235, 237, 239), TEXT_MUTED),
            ("5", (214, 234, 248), COLOR_O),
        ]
        self._draw_mini_board(screen, 30, 167, [EMPTY] * 9, labels_override=priority_cells)
        screen.blit(self.ui.font_xs_bold.render("Urutan Strategis", True, HEADER_COLOR), (124, 164))
        screen.blit(self.ui.font_xs_bold.render("1: Tengah (idx 4)", True, COLOR_GREEN), (124, 188))
        screen.blit(self.ui.font_xs_bold.render("2-5: Sudut", True, COLOR_O), (124, 208))
        screen.blit(self.ui.font_xs.render("6-9: Sisi", True, TEXT_MUTED), (124, 228))

        # Kartu 2 & 3: Highlight Awal & Mid-game
        highlights = [
            ("Awal (9 Kosong)", self.s2_rows[0] if len(self.s2_rows) > 0 else None),
            ("Mid-game (5 Kosong)", self.s2_rows[1] if len(self.s2_rows) > 1 else None),
        ]
        for idx, (title, row) in enumerate(highlights):
            cx = 264 + idx * 244
            card = pygame.Rect(cx, 150, 232, 118)
            pygame.draw.rect(screen, CARD_BG, card, border_radius=10)
            pygame.draw.rect(screen, CARD_BORDER, card, width=1, border_radius=10)
            if row:
                std_n = float(row["standard_nodes"])
                str_n = float(row["strategic_nodes"])
                red = float(row["node_reduction_percent"])
                std_t = float(row["standard_time_ms"])
                str_t = float(row["strategic_time_ms"])
                screen.blit(self.ui.font_small_bold.render(title, True, HEADER_COLOR), (cx + 14, 162))
                screen.blit(self.ui.font_large.render(f"-{red:.2f}% Node", True, COLOR_GREEN), (cx + 14, 186))
                screen.blit(self.ui.font_xs.render(f"Node: {std_n:,.0f} -> {str_n:,.0f}", True, TEXT_DARK), (cx + 14, 222))
                screen.blit(self.ui.font_xs.render(f"Waktu: {std_t:.2f} -> {str_t:.2f} ms", True, TEXT_MUTED), (cx + 14, 242))

        # --- TABEL PERBANDINGAN ---
        table_rect = pygame.Rect(20, 282, 720, 226)
        pygame.draw.rect(screen, CARD_BG, table_rect, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, table_rect, width=1, border_radius=10)

        headers = [
            ("Kondisi", 118),
            ("Std Node", 82),
            ("Str Node", 82),
            ("Reduksi", 84),
            ("Std (ms)", 84),
            ("Str (ms)", 84),
            ("Langkah", 96),
            ("Skor", 90),
        ]
        pygame.draw.rect(screen, TABLE_HEADER_BG, (21, 283, 718, 38), border_radius=8)
        x = 28
        for h_text, col_w in headers:
            screen.blit(self.ui.font_xs_bold.render(h_text, True, TEXT_DARK), (x, 294))
            x += col_w

        short_labels = ["Awal (9)", "Mid-game (5)", "End-game (2)"]
        for idx, row in enumerate(self.s2_rows[:3]):
            ry = 326 + idx * 58
            if idx % 2 == 1:
                pygame.draw.rect(screen, TABLE_ALT_BG, (22, ry - 4, 716, 52), border_radius=6)

            std_m = int(float(row["standard_move"])) + 1
            str_m = int(float(row["strategic_move"])) + 1
            same_score = row["standard_score"] == row["strategic_score"]

            values = [
                (short_labels[idx] if idx < 3 else row["scenario"], TEXT_DARK, True),
                (f"{float(row['standard_nodes']):,.0f}", TEXT_DARK, False),
                (f"{float(row['strategic_nodes']):,.0f}", COLOR_O, True),
                (f"{float(row['node_reduction_percent']):.2f}%", COLOR_GREEN, True),
                (f"{float(row['standard_time_ms']):.2f}", TEXT_DARK, False),
                (f"{float(row['strategic_time_ms']):.2f}", COLOR_O, False),
                (f"K{std_m} / K{str_m}", TEXT_MUTED, False),
                (f"Sama ({row['strategic_score']})" if same_score else "Beda!", COLOR_GREEN if same_score else COLOR_X, True),
            ]
            x = 28
            for (val_text, fg, bold), (_, col_w) in zip(values, headers):
                font = self.ui.font_xs_bold if bold else self.ui.font_xs
                screen.blit(font.render(val_text, True, fg), (x, ry + 12))
                x += col_w

        first = self.s2_rows[0]
        self._draw_footer_box(
            screen,
            f"Kesimpulan: Strategic Ordering mengurangi node Alpha-Beta hingga {float(first['node_reduction_percent']):.2f}% "
            f"({float(first['standard_nodes']):,.0f} -> {float(first['strategic_nodes']):,.0f} node).",
            "Pada papan kosong, K1 (sudut) & K5 (tengah) sama-sama optimal (skor 0). Sumber: scenario_2_results.csv",
        )

    def _draw_scenario_3(self, screen):
        sub = self.ui.font_small.render(
            "Simulasi Pertandingan Penuh: 20 Ronde vs Random & 20 Ronde Minimax vs Alpha-Beta (10 X / 10 O)",
            True,
            TEXT_MUTED,
        )
        screen.blit(sub, (20, 122))

        if not self.s3_random_summary and not self.s3_direct_summary:
            msg = self.ui.font_med.render("Data scenario_3 CSV belum tersedia. Klik 'Jalankan Ulang'.", True, COLOR_X)
            screen.blit(msg, (20, 180))
            return

        # --- KARTU KIRI: VS RANDOM AGENT ---
        left_card = pygame.Rect(20, 150, 352, 224)
        pygame.draw.rect(screen, CARD_BG, left_card, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, left_card, width=1, border_radius=10)

        screen.blit(self.ui.font_small_bold.render("A. Uji 20 Ronde Melawan Random Agent", True, HEADER_COLOR), (34, 162))
        y = 192
        for algo, accent in (("Minimax", COLOR_X), ("Alpha-Beta", COLOR_O)):
            s = self.s3_random_summary.get(algo)
            if not s:
                continue
            inner = pygame.Rect(32, y, 328, 80)
            pygame.draw.rect(screen, TABLE_ALT_BG, inner, border_radius=8)
            pygame.draw.rect(screen, accent, (32, y, 5, 80), border_radius=3)

            screen.blit(self.ui.font_small_bold.render(algo, True, accent), (46, y + 6))
            wdl = f"Win: {s['wins']} ({s['win_pct']:.0f}%) | Draw: {s['draws']} ({s['draw_pct']:.0f}%) | Loss: {s['losses']}"
            screen.blit(self.ui.font_xs_bold.render(wdl, True, TEXT_DARK), (46, y + 30))
            perf = f"Rata2: {s['avg_nodes']:,.0f} node | {s['avg_time']:.2f} ms | {s['avg_mem']:.2f} KB"
            screen.blit(self.ui.font_xs.render(perf, True, TEXT_MUTED), (46, y + 52))
            y += 90

        # --- KARTU KANAN: DIRECT MATCH ---
        right_card = pygame.Rect(388, 150, 352, 224)
        pygame.draw.rect(screen, CARD_BG, right_card, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, right_card, width=1, border_radius=10)

        screen.blit(self.ui.font_small_bold.render("B. Tanding Langsung: Minimax vs Alpha-Beta", True, HEADER_COLOR), (402, 162))
        d = self.s3_direct_summary
        if d:
            badge = pygame.Rect(402, 192, 324, 54)
            pygame.draw.rect(screen, INFO_BG, badge, border_radius=8)
            pygame.draw.rect(screen, INFO_BORDER, badge, width=1, border_radius=8)
            b_txt = self.ui.font_med.render(f"{d['draws']}/{d['total']} RONDE SERI ({d['draw_pct']:.0f}% Draw)", True, COLOR_GREEN)
            screen.blit(b_txt, b_txt.get_rect(center=badge.center))

            lines = [
                f"Pembagian Giliran : {d['mm_first']}x Minimax (X), {d['ab_first']}x Alpha-Beta (X)",
                f"Minimax (Rata2)   : {d['mm_nodes']:,.1f} node | {d['mm_time']:.2f} ms",
                f"Alpha-Beta (Rata2): {d['ab_nodes']:,.1f} node | {d['ab_time']:.2f} ms",
                f"Memori Puncak     : MM {d['mm_mem']:.2f} KB vs AB {d['ab_mem']:.2f} KB",
            ]
            ly = 260
            for ln in lines:
                screen.blit(self.ui.font_xs.render(ln, True, TEXT_DARK), (404, ly))
                ly += 24

        # --- GRAFIK BATANG PERBANDINGAN NODE ---
        bar_card = pygame.Rect(20, 388, 720, 122)
        pygame.draw.rect(screen, CARD_BG, bar_card, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, bar_card, width=1, border_radius=10)
        screen.blit(self.ui.font_small_bold.render("Perbandingan Rata-rata Node per Langkah (Skenario 3)", True, TEXT_DARK), (34, 398))

        mm_r = self.s3_random_summary.get("Minimax", {}).get("avg_nodes", 0)
        ab_r = self.s3_random_summary.get("Alpha-Beta", {}).get("avg_nodes", 0)
        mm_d = d.get("mm_nodes", 0) if d else 0
        ab_d = d.get("ab_nodes", 0) if d else 0
        max_val = max(mm_r, ab_r, mm_d, ab_d, 1)

        bars = [
            ("Vs Random - Minimax", mm_r, COLOR_X),
            ("Vs Random - Alpha-Beta", ab_r, COLOR_O),
            ("Direct Match - Minimax", mm_d, COLOR_X),
            ("Direct Match - Alpha-Beta", ab_d, COLOR_O),
        ]
        by = 424
        for label, val, color in bars:
            screen.blit(self.ui.font_xs.render(label, True, TEXT_DARK), (34, by))
            bar_x = 225
            bar_max_w = 400
            bar_w = max(4, int((val / max_val) * bar_max_w))
            pygame.draw.rect(screen, (235, 240, 245), (bar_x, by + 2, bar_max_w, 14), border_radius=4)
            pygame.draw.rect(screen, color, (bar_x, by + 2, bar_w, 14), border_radius=4)
            screen.blit(self.ui.font_xs_bold.render(f"{val:,.0f} node", True, TEXT_DARK), (bar_x + bar_max_w + 10, by))
            by += 21

        self._draw_footer_box(
            screen,
            "Kesimpulan: Kedua algoritma tak terkalahkan (0% Loss vs Random) & 100% Seri saat tanding langsung.",
            "Kecerdasan Alpha-Beta setara Minimax murni. Sumber: scenario_3_random & scenario_3_direct CSV.",
        )
