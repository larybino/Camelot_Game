import pygame

from src.utils.config import SCREEN_W, SCREEN_H

def _epic_font(size):
    """Tenta uma fonte medieval/arcaica do sistema, com fallback serifado."""
    candidates = (
        "oldenglishtextmt,luminari,imfellenglish,cinzel,palatinolinotype,"
        "bookantiqua,constantia,georgia,timesnewroman,serif"
    )
    try:
        return pygame.font.SysFont(candidates, size, bold=True)
    except Exception:
        return pygame.font.Font(None, size)


class Tutorial:
    """Texto de treinamento exibido no comeco da partida.

    Cada dica aparece quando o jogador alcanca uma certa distancia (em blocos)
    OU quando o jogador aperta ENTER para pular para a proxima.
    """

    # ------------------------------------------------------------------
    # AJUSTES DE DISTANCIA
    # ------------------------------------------------------------------
    # Tamanho de um "bloco" em pixels (TILE_SIZE do jogo).
    BLOCK_SIZE = 16
    # Bloco a partir do qual cada dica correspondente em STEPS aparece.
    # Tem que ter o mesmo numero de itens que STEPS.
    # A distancia que CADA dica fica na tela = diferenca ate o proximo valor
    # (ex.: a dica 2 fica do bloco 100 ao 150 -> 50 blocos).
    STEP_DISTANCES = [0, 50, 100, 150, 220]
    # Bloco em que o tutorial inteiro some de vez (mesmo sem apertar ENTER).
    HIDE_AFTER_BLOCK = 320
    # ------------------------------------------------------------------

    STEPS = [
        "Usa as SETAS  ->  e  <-  para caminhar pelo reino",
        "Pressiona  ESPAÇO  ou  seta para cima  para saltar",
        "Pressiona  CONTROL  para correr mais rápido",
        "Pressiona  K  para usar a tua espada",
        "Que a tua jornada seja gloriosa, cavaleiro!",
    ]

    FADE = 0.5

    INK = (245, 232, 196)
    GOLD = (200, 170, 90)
    HINT = (205, 195, 165)

    # Posicao vertical do estandarte (mais para baixo para nao cobrir o HUD).
    CENTER_Y = SCREEN_H - 358

    def __init__(self):
        self.font = _epic_font(24)
        self.hint_font = _epic_font(15)
        self.index = 0          # dica mostrada agora
        self.enter_index = 0    # ate onde o jogador avancou com ENTER
        self.since_change = 0.0
        self.done = False

    def next(self):
        """Chamado quando o jogador aperta ENTER: pula para a proxima dica."""
        if self.done:
            return
        self.enter_index = max(self.enter_index, self.index) + 1
        self._resolve(self.index)

    def update(self, dt, player_x):
        if self.done:
            return

        self.since_change += dt

        blocks = player_x / self.BLOCK_SIZE

        if blocks >= self.HIDE_AFTER_BLOCK:
            self.done = True
            return

        distance_index = 0
        for i, threshold in enumerate(self.STEP_DISTANCES):
            if blocks >= threshold:
                distance_index = i

        self._resolve(max(distance_index, self.enter_index))

    def _resolve(self, new_index):
        if new_index >= len(self.STEPS):
            self.done = True
            return
        if new_index != self.index:
            self.index = new_index
            self.since_change = 0.0

    def _alpha(self):
        if self.since_change < self.FADE:
            return max(0, min(255, int(255 * self.since_change / self.FADE)))
        return 255

    def draw(self, screen):
        if self.done:
            return

        alpha = self._alpha()
        cy = self.CENTER_Y
        half_h = 24

        banner = pygame.Surface((SCREEN_W, half_h * 2), pygame.SRCALPHA)
        banner.fill((0, 0, 0, int(alpha * 0.55)))
        screen.blit(banner, (0, cy - half_h))

        for y in (cy - half_h, cy + half_h):
            line = pygame.Surface((SCREEN_W, 2), pygame.SRCALPHA)
            line.fill((*self.GOLD, alpha))
            screen.blit(line, (0, y))

        text = self.font.render(self.STEPS[self.index], True, self.INK)
        text.set_alpha(alpha)
        screen.blit(text, text.get_rect(center=(SCREEN_W // 2, cy)))

        hint = self.hint_font.render(
            "ENTER para a proxima dica", True, self.HINT
        )
        hint.set_alpha(int(alpha * 0.8))
        screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, cy + half_h + 14)))
