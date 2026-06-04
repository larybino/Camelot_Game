class Health:
    def __init__(self, max_lives=3, invuln_duration=0.8):
        self.max_lives = max_lives
        self.lives = max_lives
        self.invuln_duration = invuln_duration
        self.invuln_timer = 0.0

    def update(self, dt):
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)

    def take_damage(self, amount=1, ignore_invuln=False):
        if self.lives <= 0:
            return False
        if self.invuln_timer > 0 and not ignore_invuln:
            return False

        self.lives = max(0, self.lives - amount)
        self.invuln_timer = self.invuln_duration
        return True

    def reset(self):
        self.lives = self.max_lives
        self.invuln_timer = 0.0
