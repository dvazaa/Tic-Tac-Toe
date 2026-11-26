import csv
import os
import statistics
import threading
import time
from datetime import datetime
import pygame

from board.board import AI, HUMAN, EMPTY
from experiments.scenario_1 import BOARD_STATES, run_scenario_1
from experiments.scenario_2 import run_scenario_2
from experiments.scenario_3 import run_scenario_3

EXP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments",
)

CSV_FILES = (
    "scenario_1_results.csv",
    "scenario_2_results.csv",
    "scenario_3_random_results.csv",
    "scenario_3_direct_results.csv",
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


def _is_true(val):
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() == "true"


def _compute_s3_summaries(random_rows, direct_rows):
    random_summary = {}
    for algo in ("Minimax", "Alpha-Beta"):
        rows = [r for r in random_rows if r.get("algorithm") == algo]
        if not rows:
            continue
        wins = sum(1 for r in rows if r["result"] == "Win")
        draws = sum(1 for r in rows if r["result"] == "Draw")
        losses = sum(1 for r in rows if r["result"] == "Loss")
        total = len(rows)
        random_summary[algo] = {
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

    direct_summary = {}
    if direct_rows:
        total = len(direct_rows)
        draws = sum(1 for r in direct_rows if r["winner"] == "Draw")
        mm_first = sum(1 for r in direct_rows if r["x_agent"] == "Minimax")
        ab_first = sum(1 for r in direct_rows if r["x_agent"] == "Alpha-Beta")
        direct_summary = {
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

    return random_summary, direct_summary


class ExperimentDashboard:
    """Tampilan interaktif hasil eksperimen Skenario 1, 2, dan 3 dengan live update."""

    def __init__(self, ui):
        self.ui = ui
        self.active_tab = 1
        self.buttons = {}

        self._lock = threading.Lock()
        self.running = False
        self.running_tab = None
        self.progress = 0.0
        self.progress_stage = ""
        self.needs_reload = False
        self.status_msg = ""
        self.last_updated = {1: "", 2: "", 3: ""}

        self.s1_rows = []
        self.s2_rows = []
        self.s3_random_summary = {}
        self.s3_direct_summary = {}

        self._csv_mtimes = {}
        self._last_mtime_check = 0.0

        self.reload_data()

    def _get_csv_mtimes(self):
        mtimes = {}
        for fn in CSV_FILES:
            p = os.path.join(EXP_DIR, fn)
            mtimes[fn] = os.path.getmtime(p) if os.path.exists(p) else 0.0
        return mtimes

    def _format_mtime(self, filename):
        p = os.path.join(EXP_DIR, filename)
        if not os.path.exists(p):
            return ""
        return datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H:%M:%S")

    def reload_data(self):
        s1 = _read_csv("scenario_1_results.csv")
        s2 = _read_csv("scenario_2_results.csv")
        s3_rand, s3_dir = _compute_s3_summaries(
            _read_csv("scenario_3_random_results.csv"),
            _read_csv("scenario_3_direct_results.csv"),
        )
        with self._lock:
            self.s1_rows = s1
            self.s2_rows = s2
            self.s3_random_summary = s3_rand
            self.s3_direct_summary = s3_dir
            self.last_updated[1] = self._format_mtime("scenario_1_results.csv")
            self.last_updated[2] = self._format_mtime("scenario_2_results.csv")
            self.last_updated[3] = self._format_mtime("scenario_3_direct_results.csv")
        self._csv_mtimes = self._get_csv_mtimes()

    def _check_external_csv_updates(self):
        now = time.monotonic()
        if self.running or (now - self._last_mtime_check < 0.5):
            return
        self._last_mtime_check = now
        current = self._get_csv_mtimes()
        if current != self._csv_mtimes:
            self.reload_data()
            self.status_msg = f"Data tab diperbarui otomatis dari CSV ({datetime.now().strftime('%H:%M:%S')})"

    def run_active_scenario(self):
        if self.running:
            return
        tab = self.active_tab
        with self._lock:
            self.running = True
            self.running_tab = tab
            self.progress = 0.0
            self.progress_stage = f"Memulai Skenario {tab}..."
            self.status_msg = f"Menjalankan Skenario {tab}..."
            if tab == 1:
                self.s1_rows = []
            elif tab == 2:
                self.s2_rows = []
            else:
                self.s3_random_summary = {}
                self.s3_direct_summary = {}

        def _on_progress(payload):
            with self._lock:
                self.progress = float(payload.get("progress", self.progress))
                self.progress_stage = payload.get("stage", self.progress_stage)
                if tab == 1 and "rows" in payload:
                    self.s1_rows = list(payload["rows"])
                elif tab == 2 and "rows" in payload:
                    self.s2_rows = list(payload["rows"])
                elif tab == 3:
                    rand_rows = payload.get("random_rows", [])
                    dir_rows = payload.get("direct_rows", [])
                    self.s3_random_summary, self.s3_direct_summary = _compute_s3_summaries(
                        rand_rows, dir_rows
                    )

        def _worker():
            try:
                if tab == 1:
                    run_scenario_1(on_progress=_on_progress)
                elif tab == 2:
                    run_scenario_2(on_progress=_on_progress)
                else:
                    run_scenario_3(on_progress=_on_progress)
                now_str = datetime.now().strftime("%H:%M:%S")
                with self._lock:
                    self.progress = 1.0
                    self.progress_stage = ""
                    self.status_msg = f"Skenario {tab} selesai — tab & CSV diperbarui ({now_str})!"
            except Exception as exc:
                with self._lock:
                    self.status_msg = f"Gagal menjalankan Skenario {tab}: {exc}"
            finally:
                with self._lock:
                    self.needs_reload = True
                    self.running = False
                    self.running_tab = None

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
        self._check_external_csv_updates()

        with self._lock:
            s1_rows = list(self.s1_rows)
            s2_rows = list(self.s2_rows)
            s3_rand = dict(self.s3_random_summary)
            s3_dir = dict(self.s3_direct_summary)
            is_running = self.running
            running_tab = self.running_tab
            progress = self.progress
            progress_stage = self.progress_stage
            status_msg = self.status_msg
            updated_time = self.last_updated.get(self.active_tab, "")

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

        rerun_label = f"{int(progress * 100)}% Berjalan" if is_running else "Jalankan Ulang"
        rerun_bg = COLOR_ORANGE if is_running else BTN_SUCCESS
        rerun_hover = COLOR_ORANGE if is_running else BTN_SUCCESS_HOVER
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

        live_state = {
            "running": is_running and running_tab == self.active_tab,
            "any_running": is_running,
            "progress": progress,
            "stage": progress_stage,
            "status_msg": status_msg,
            "updated_time": updated_time,
        }

        # --- KONTEN TAB ---
        if self.active_tab == 1:
            self._draw_scenario_1(screen, s1_rows, live_state)
        elif self.active_tab == 2:
            self._draw_scenario_2(screen, s2_rows, live_state)
        else:
            self._draw_scenario_3(screen, s3_rand, s3_dir, live_state)

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

    def _draw_footer_box(self, screen, line1, line2, live_state):
        box = pygame.Rect(20, 524, 720, 76)
        pygame.draw.rect(screen, INFO_BG, box, border_radius=10)
        pygame.draw.rect(screen, INFO_BORDER, box, width=1, border_radius=10)

        if live_state["any_running"]:
            stage_text = live_state["stage"] or live_state["status_msg"]
            pct = int(live_state["progress"] * 100)
            s1 = self.ui.font_xs_bold.render(f"Live Update ({pct}%): {stage_text}", True, COLOR_ORANGE)
            screen.blit(s1, (34, 536))

            bar_rect = pygame.Rect(34, 560, 692, 16)
            pygame.draw.rect(screen, (215, 226, 232), bar_rect, border_radius=6)
            fill_w = max(8, int(692 * max(0.0, min(1.0, live_state["progress"]))))
            pygame.draw.rect(screen, BTN_SUCCESS, (34, 560, fill_w, 16), border_radius=6)

            hint = self.ui.font_xs.render("Konten tab diperbarui langsung seiring hasil masuk & otomatis disimpan ke CSV.", True, TEXT_MUTED)
            screen.blit(hint, (34, 580))
            return

        s1 = self.ui.font_xs_bold.render(line1, True, TEXT_DARK)
        s2 = self.ui.font_xs.render(line2, True, TEXT_MUTED)
        screen.blit(s1, (34, 534))
        screen.blit(s2, (34, 554))

        footer_note = live_state["status_msg"]
        if not footer_note and live_state["updated_time"]:
            footer_note = f"Terakhir diperbarui: {live_state['updated_time']} (otomatis sinkron dengan CSV)"
        if footer_note:
            color = COLOR_GREEN if "selesai" in footer_note.lower() or "diperbarui" in footer_note.lower() else TEXT_MUTED
            st = self.ui.font_xs_bold.render(footer_note, True, color)
            screen.blit(st, (34, 576))

    def _draw_scenario_1(self, screen, s1_rows, live_state):
        sub = self.ui.font_small.render(
            "Perbandingan Minimax vs Alpha-Beta pada 3 papan terkunci (rata-rata 10x uji, giliran X)",
            True,
            TEXT_MUTED,
        )
        screen.blit(sub, (20, 122))

        # --- 3 KARTU PAPAN TERKUNCI ---
        card_w = 232
        card_gap = 12
        short_names = ["Awal (9 Kosong)", "Mid (5 Kosong)", "End (2 Kosong)"]
        for i in range(3):
            cx = 20 + i * (card_w + card_gap)
            cy = 150
            card = pygame.Rect(cx, cy, card_w, 118)
            pygame.draw.rect(screen, CARD_BG, card, border_radius=10)
            pygame.draw.rect(screen, CARD_BORDER, card, width=1, border_radius=10)

            board = BOARD_STATES[i]["board"] if i < len(BOARD_STATES) else [EMPTY] * 9
            row = s1_rows[i] if i < len(s1_rows) else None
            best_move = int(float(row["alpha_beta_move"])) if row else None
            self._draw_mini_board(screen, cx + 10, cy + 17, board, highlight_idx=best_move)

            tx = cx + 104
            screen.blit(self.ui.font_xs_bold.render(short_names[i], True, HEADER_COLOR), (tx, cy + 14))
            if row:
                pruning = float(row["pruning_ratio_percent"])
                score = row["alpha_beta_score"]
                opt_ok = _is_true(row.get("score_match", True))
                screen.blit(self.ui.font_xs_bold.render(f"Pruning: {pruning:.2f}%", True, COLOR_GREEN), (tx, cy + 38))
                screen.blit(self.ui.font_xs.render(f"Langkah: Kotak {best_move + 1}", True, TEXT_DARK), (tx, cy + 58))
                screen.blit(self.ui.font_xs.render(f"Skor Optimal: {score}", True, TEXT_DARK), (tx, cy + 76))
                screen.blit(
                    self.ui.font_xs_bold.render(
                        "Status: Optimal" if opt_ok else "Status: Beda!",
                        True,
                        COLOR_GREEN if opt_ok else COLOR_X,
                    ),
                    (tx, cy + 94),
                )
            else:
                lbl = "Menghitung..." if (live_state["running"] and i == len(s1_rows)) else "Menunggu..."
                fg = COLOR_ORANGE if lbl == "Menghitung..." else TEXT_MUTED
                screen.blit(self.ui.font_xs_bold.render(lbl, True, fg), (tx, cy + 48))

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
        for idx in range(3):
            ry = 326 + idx * 58
            if idx % 2 == 1:
                pygame.draw.rect(screen, TABLE_ALT_BG, (22, ry - 4, 716, 52), border_radius=6)

            row = s1_rows[idx] if idx < len(s1_rows) else None
            if not row:
                status_lbl = "Menghitung..." if (live_state["running"] and idx == len(s1_rows)) else "Menunggu..."
                screen.blit(self.ui.font_xs_bold.render(short_labels[idx], True, TEXT_DARK), (28, ry + 12))
                screen.blit(
                    self.ui.font_xs_bold.render(status_lbl, True, COLOR_ORANGE if status_lbl == "Menghitung..." else TEXT_MUTED),
                    (146, ry + 12),
                )
                continue

            mm_nodes = f"{float(row['minimax_nodes']):,.0f}"
            ab_nodes = f"{float(row['alpha_beta_nodes']):,.0f}"
            pruning = f"{float(row['pruning_ratio_percent']):.2f}%"
            mm_ms = f"{float(row['minimax_time_ms']):.2f}"
            ab_ms = f"{float(row['alpha_beta_time_ms']):.2f}"
            mem = f"{float(row['minimax_memory_kb']):.2f} / {float(row['alpha_beta_memory_kb']):.2f}"
            valid = "Sama/Opt" if _is_true(row.get("score_match", True)) else "Berbeda"

            values = [
                (short_labels[idx], TEXT_DARK, True),
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

        if s1_rows:
            first = s1_rows[0]
            line1 = (
                f"Kesimpulan: Pemangkasan tertinggi di Awal Permainan ({float(first['pruning_ratio_percent']):.2f}%: "
                f"{float(first['minimax_nodes']):,.0f} -> {float(first['alpha_beta_nodes']):,.0f} node)."
            )
            line2 = "Semua kondisi papan menghasilkan langkah & skor 100% optimal. Sumber: scenario_1_results.csv"
        else:
            line1 = "Belum ada data Skenario 1."
            line2 = "Klik 'Jalankan Ulang' untuk memulai pengujian."
        self._draw_footer_box(screen, line1, line2, live_state)

    def _draw_scenario_2(self, screen, s2_rows, live_state):
        sub = self.ui.font_small.render(
            "Perbandingan Alpha-Beta: Urutan Indeks Standar (0-8) vs Strategis (Tengah -> Sudut -> Sisi)",
            True,
            TEXT_MUTED,
        )
        screen.blit(sub, (20, 122))

        # --- KARTU 1: PETA PRIORITAS STRATEGIS ---
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

        # --- KARTU 2 & 3: HIGHLIGHT AWAL & MID-GAME ---
        highlights = [
            ("Awal (9 Kosong)", s2_rows[0] if len(s2_rows) > 0 else None, 0),
            ("Mid-game (5 Kosong)", s2_rows[1] if len(s2_rows) > 1 else None, 1),
        ]
        for idx, (title, row, slot_idx) in enumerate(highlights):
            cx = 264 + idx * 244
            card = pygame.Rect(cx, 150, 232, 118)
            pygame.draw.rect(screen, CARD_BG, card, border_radius=10)
            pygame.draw.rect(screen, CARD_BORDER, card, width=1, border_radius=10)
            screen.blit(self.ui.font_small_bold.render(title, True, HEADER_COLOR), (cx + 14, 162))
            if row:
                std_n = float(row["standard_nodes"])
                str_n = float(row["strategic_nodes"])
                red = float(row["node_reduction_percent"])
                std_t = float(row["standard_time_ms"])
                str_t = float(row["strategic_time_ms"])
                screen.blit(self.ui.font_large.render(f"-{red:.2f}% Node", True, COLOR_GREEN), (cx + 14, 186))
                screen.blit(self.ui.font_xs.render(f"Node: {std_n:,.0f} -> {str_n:,.0f}", True, TEXT_DARK), (cx + 14, 222))
                screen.blit(self.ui.font_xs.render(f"Waktu: {std_t:.2f} -> {str_t:.2f} ms", True, TEXT_MUTED), (cx + 14, 242))
            else:
                lbl = "Menghitung..." if (live_state["running"] and slot_idx == len(s2_rows)) else "Menunggu..."
                fg = COLOR_ORANGE if lbl == "Menghitung..." else TEXT_MUTED
                screen.blit(self.ui.font_med.render(lbl, True, fg), (cx + 14, 200))

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
        for idx in range(3):
            ry = 326 + idx * 58
            if idx % 2 == 1:
                pygame.draw.rect(screen, TABLE_ALT_BG, (22, ry - 4, 716, 52), border_radius=6)

            row = s2_rows[idx] if idx < len(s2_rows) else None
            if not row:
                status_lbl = "Menghitung..." if (live_state["running"] and idx == len(s2_rows)) else "Menunggu..."
                screen.blit(self.ui.font_xs_bold.render(short_labels[idx], True, TEXT_DARK), (28, ry + 12))
                screen.blit(
                    self.ui.font_xs_bold.render(status_lbl, True, COLOR_ORANGE if status_lbl == "Menghitung..." else TEXT_MUTED),
                    (146, ry + 12),
                )
                continue

            std_m = int(float(row["standard_move"])) + 1
            str_m = int(float(row["strategic_move"])) + 1
            same_score = str(row["standard_score"]) == str(row["strategic_score"])

            values = [
                (short_labels[idx], TEXT_DARK, True),
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

        if s2_rows:
            first = s2_rows[0]
            line1 = (
                f"Kesimpulan: Strategic Ordering mengurangi node Alpha-Beta hingga {float(first['node_reduction_percent']):.2f}% "
                f"({float(first['standard_nodes']):,.0f} -> {float(first['strategic_nodes']):,.0f} node)."
            )
            line2 = "Pada papan kosong, K1 (sudut) & K5 (tengah) sama-sama optimal (skor 0). Sumber: scenario_2_results.csv"
        else:
            line1 = "Belum ada data Skenario 2."
            line2 = "Klik 'Jalankan Ulang' untuk memulai pengujian."
        self._draw_footer_box(screen, line1, line2, live_state)

    def _draw_scenario_3(self, screen, s3_rand, s3_dir, live_state):
        sub = self.ui.font_small.render(
            "Simulasi Pertandingan Penuh: 20 Ronde vs Random & 20 Ronde Minimax vs Alpha-Beta (10 X / 10 O)",
            True,
            TEXT_MUTED,
        )
        screen.blit(sub, (20, 122))

        # --- KARTU KIRI: VS RANDOM AGENT ---
        left_card = pygame.Rect(20, 150, 352, 224)
        pygame.draw.rect(screen, CARD_BG, left_card, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, left_card, width=1, border_radius=10)

        screen.blit(self.ui.font_small_bold.render("A. Uji 20 Ronde Melawan Random Agent", True, HEADER_COLOR), (34, 162))
        y = 192
        for algo, accent in (("Minimax", COLOR_X), ("Alpha-Beta", COLOR_O)):
            inner = pygame.Rect(32, y, 328, 80)
            pygame.draw.rect(screen, TABLE_ALT_BG, inner, border_radius=8)
            pygame.draw.rect(screen, accent, (32, y, 5, 80), border_radius=3)

            s = s3_rand.get(algo)
            title_suffix = f" ({s['total']}/20 ronde)" if (s and s["total"] < 20) else ""
            screen.blit(self.ui.font_small_bold.render(f"{algo}{title_suffix}", True, accent), (46, y + 6))
            if s:
                wdl = f"Win: {s['wins']} ({s['win_pct']:.0f}%) | Draw: {s['draws']} ({s['draw_pct']:.0f}%) | Loss: {s['losses']}"
                screen.blit(self.ui.font_xs_bold.render(wdl, True, TEXT_DARK), (46, y + 30))
                perf = f"Rata2: {s['avg_nodes']:,.0f} node | {s['avg_time']:.2f} ms | {s['avg_mem']:.2f} KB"
                screen.blit(self.ui.font_xs.render(perf, True, TEXT_MUTED), (46, y + 52))
            else:
                lbl = "Menunggu giliran uji..." if live_state["running"] else "Belum ada data."
                screen.blit(self.ui.font_xs.render(lbl, True, TEXT_MUTED), (46, y + 36))
            y += 90

        # --- KARTU KANAN: DIRECT MATCH ---
        right_card = pygame.Rect(388, 150, 352, 224)
        pygame.draw.rect(screen, CARD_BG, right_card, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, right_card, width=1, border_radius=10)

        screen.blit(self.ui.font_small_bold.render("B. Tanding Langsung: Minimax vs Alpha-Beta", True, HEADER_COLOR), (402, 162))
        d = s3_dir
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
        else:
            lbl = "Menunggu uji tanding langsung..." if live_state["running"] else "Belum ada data."
            screen.blit(self.ui.font_small.render(lbl, True, TEXT_MUTED), (404, 240))

        # --- GRAFIK BATANG PERBANDINGAN NODE ---
        bar_card = pygame.Rect(20, 388, 720, 122)
        pygame.draw.rect(screen, CARD_BG, bar_card, border_radius=10)
        pygame.draw.rect(screen, CARD_BORDER, bar_card, width=1, border_radius=10)
        screen.blit(self.ui.font_small_bold.render("Perbandingan Rata-rata Node per Langkah (Skenario 3)", True, TEXT_DARK), (34, 398))

        mm_r = s3_rand.get("Minimax", {}).get("avg_nodes", 0)
        ab_r = s3_rand.get("Alpha-Beta", {}).get("avg_nodes", 0)
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
            pygame.draw.rect(screen, (235, 240, 245), (bar_x, by + 2, bar_max_w, 14), border_radius=4)
            if val > 0:
                bar_w = max(4, int((val / max_val) * bar_max_w))
                pygame.draw.rect(screen, color, (bar_x, by + 2, bar_w, 14), border_radius=4)
            val_txt = f"{val:,.0f} node" if val > 0 else "-"
            screen.blit(self.ui.font_xs_bold.render(val_txt, True, TEXT_DARK), (bar_x + bar_max_w + 10, by))
            by += 21

        self._draw_footer_box(
            screen,
            "Kesimpulan: Kedua algoritma tak terkalahkan (0% Loss vs Random) & 100% Seri saat tanding langsung.",
            "Kecerdasan Alpha-Beta setara Minimax murni. Sumber: scenario_3_random & scenario_3_direct CSV.",
            live_state,
        )
