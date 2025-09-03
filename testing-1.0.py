# file: aim_trainer.py
import pygame, random, time, math

pygame.init()
W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mini Aim Trainer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# settings
target_min_r, target_max_r = 16, 32
spawn_interval = 0.9     # seconds
target_speed = 140       # px/s (random direction)
session_time = 60        # seconds

class Target:
    def __init__(self):
        self.r = random.randint(target_min_r, target_max_r)
        self.x = random.randint(self.r, W - self.r)
        self.y = random.randint(self.r, H - self.r)
        ang = random.uniform(0, 2*math.pi)
        self.vx = math.cos(ang) * target_speed
        self.vy = math.sin(ang) * target_speed
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # bounce
        if self.x < self.r and self.vx < 0: self.vx *= -1
        if self.x > W - self.r and self.vx > 0: self.vx *= -1
        if self.y < self.r and self.vy < 0: self.vy *= -1
        if self.y > H - self.r and self.vy > 0: self.vy *= -1

    def draw(self, s):
        pygame.draw.circle(s, (200,200,200), (int(self.x), int(self.y)), self.r+4)
        pygame.draw.circle(s, (220,70,70), (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(s, (230,230,230), (int(self.x), int(self.y)), max(2, self.r//3))

    def hit(self, mx, my):
        return (self.x - mx)**2 + (self.y - my)**2 <= self.r**2

def main():
    running = True
    targets = []
    last_spawn = 0
    start = time.time()
    score = 0
    total_shots = 0
    hits = 0

    while running:
        dt = clock.tick(240) / 1000.0
        t = time.time() - start
        if t >= session_time:
            running = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                total_shots += 1
                mx, my = pygame.mouse.get_pos()
                # prefer closest target if overlapping
                hit_any = None
                best_d = 1e9
                for tg in targets:
                    if tg.alive and tg.hit(mx, my):
                        d = (tg.x - mx)**2 + (tg.y - my)**2
                        if d < best_d:
                            best_d = d; hit_any = tg
                if hit_any:
                    hits += 1
                    score += max(10, 50 - int(math.sqrt(best_d)/3))
                    hit_any.alive = False

        # spawn
        last_spawn += dt
        if last_spawn >= spawn_interval:
            last_spawn = 0
            targets.append(Target())

        # update
        for tg in targets:
            if tg.alive: tg.update(dt)

        # draw
        screen.fill((18, 18, 22))
        for tg in targets:
            if tg.alive: tg.draw(screen)

        acc = (hits / total_shots * 100) if total_shots else 0.0
        time_left = max(0, int(session_time - (time.time() - start)))
        hud = f"Score: {score}   Hits: {hits}/{total_shots} ({acc:.1f}%)   Time: {time_left}s"
        screen.blit(font.render(hud, True, (230,230,230)), (16, 12))
        pygame.display.flip()

    # end screen
    screen.fill((18,18,22))
    acc = (hits / total_shots * 100) if total_shots else 0.0
    lines = [
        "Session Complete!",
        f"Score: {score}",
        f"Accuracy: {acc:.1f}%  ({hits}/{total_shots})",
        "Tekan tombol apa saja untuk keluar..."
    ]
    y = H//2 - 60
    for L in lines:
        text = font.render(L, True, (230,230,230))
        screen.blit(text, (W//2 - text.get_width()//2, y))
        y += 36
    pygame.display.flip()
    wait = True
    while wait:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN):
                wait = False
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()