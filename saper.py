import array
import json
import math
import os
import random
import sys
from collections import deque

import pygame

CELL = 32 # rozmiar jednego pol planszy w pikselach
HUD_H = 86 # wysokość górnego paska (licznik min, czas, życia)
BAR_H = 62 # wysokość dolnego paska z supermocami (tryby rozszerzone)
FOOTER_H = 30 # wysokość dolnej stopki z podpowiedzią (tryb klasyczny)
MARGIN = 16 # margines wokół planszy
MIN_W = 600 # minimalna szerokość okna gry
MENU_SIZE = (760, 660) # rozmiar okna menu (szer., wys.)
FPS = 60 # ile klatek na sekundę rysujemy

# poziomy trudności
# (nazwa, kolumny, wiersze, liczba min)
DIFFICULTIES = [
    ("Łatwy", 9, 9, 10),
    ("Średni", 16, 16, 40),
    ("Trudny", 30, 16, 99),
]

# Zapis do plików
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "profil.json")
OLD_RECORDS_FILE = os.path.join(BASE_DIR, "rekordy.json")

# Tryby gry
MODE_CLASSIC, MODE_ADVENTURE, MODE_TIME, MODE_CAMPAIGN = range(4)
MODES = [
    ("Klasyczny", "1 życie", "Tradycyjny saper. Jedno życie, liczy się czas."),
    ("Przygoda", "3 życia + bonusy", "3 życia, power-upy, pola specjalne, punkty i combo."),
    ("Na czas", "odliczanie", "Czas ucieka! Każde odkryte pole daje sekundy. 2 życia."),
    ("Kampania", "10 poziomów", "Seria plansz o różnych kształtach.")
]

class Fonts:
    def __init__(self):
        self.cache = {}

    def __call__(self, size, bold=True):
        key = (size, bold)
        if key not in self.cache:
            self.cache[key] = pygame.font.SysFont("segoeui,arial,dejavusans", size, bold=bold)
        return self.cache[key]

    def fit(self, text, size, max_w, color, bold=True):
        while size > 9:
            img = self(size, bold).render(text, True, color)
            if img.get_width() <= max_w:
                return img
            size -= 1
        return self(size, bold).render(text, True, color)
        

class Menu:
    def __init__(self, app):
        self.app = app
        app.set_size(*MENU_SIZE)
        self.diff, self.mode = app.last_diff, app.last_mode
        self.t = 0.0
        W, H = MENU_SIZE
        bw, bh, gap = 210, 64, 18
        x0 = (W - (3 * bw + 2 * gap)) // 2
        self.diff_btn = [pygame.Rect(x0 + i * (bw + gap), 178, bw, bh) for i in range(3)]
        self.mode_btn = [pygame.Rect(x0 + i * (bw + gap), 288, bw, bh) for i in range(3)]
        self.start_btn = pygame.Rect(W // 2 - 140, 498, 280, 56)
        sw, sg = 160, 12
        sx = (W - (4 * sw + 3 * sg)) // 2
        self.sub_btn = [(pygame.Rect(sx + i * (sw + sg), 572, sw, 42), label, scr)
                        for i, (label, scr) in enumerate([("Kampania", ""), ("Sklep", ""), ("Osiągnięcia", ""), ("Motywy", "")])]

        self.deco = [[random.uniform(0, W), random.uniform(0, H), random.uniform(10, 26),
                      random.uniform(8, 26), random.random() < 0.3] for _ in range(36)]

    def draw(self, surf):
       f = self.app.fonts
       W, H = MENU_SIZE
       surf.fill(BG) 

class App:
    def __init__(self):
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Saper+")
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.display.set_icon(icon)
        self.fonts = Fonts()
        self.screen = pygame.display.set_mode(MENU_SIZE)
        self.clock = pygame.time.Clock()
        self.profile = self.load_profile()
        # self.records = self.profile["records"]
        self.last_diff, self.last_mode = 0, MODE_ADVENTURE
        self.scene = Menu(self)
        


    def load_profile(self):
        prof = {}
        try:
            with open(SAVE_FILE, encoding="utf-8") as fh:
                prof = json.load(fh)
                if not isinstance(prof, dict):
                    prof = {}
        except (OSError, ValueError):
            try:
                with open(OLD_RECORDS_FILE, encoding="utf-8") as fh:
                    old = json.load(fh)
                    if isinstance(old, dict):
                        prof["records"] = old
            except (OSError, ValueError):
                pass
        prof.setdefault("record", {})
        prof.setdefault("coins", 0)
        prof.setdefault("upgrades", {})
        prof.setdefault("achievements", [])
        prof.setdefault("stats", {})
        prof.setdefault("theme", "Nocny")
        camp = prof.setdefault("campaign", {})
        camp.setdefault("unlocked", 1)
        camp.setdefault("stars", {})
        return prof

    def save(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as fh:
                json.dump(self.profile, fh, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def quit(self):
        self.save()
        pygame.quit()
        sys.exit()

    def set_size(self, w, h):
        if self.screen.get_size() != (w, h):
            self.screen = pygame.display.set_mode((w, h))

    def start_game(self, diff, mode):
        self.last_diff, self.last_mode = diff, mode


    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.quit()
                # self.scene.handle(e)

            self.scene.draw(self.screen)
                    
if __name__ == "__main__":
    App().run()