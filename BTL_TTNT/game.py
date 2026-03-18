import pygame
import random
import json
import os

# --- Cấu hình màu sắc hiện đại ---
COLOR_BG = (25, 25, 35)
COLOR_PANEL = (35, 35, 50)
COLOR_TEXT = (240, 240, 240)
COLOR_ACCENT = (0, 255, 150)
COLOR_RED = (255, 80, 80)
COLOR_BLUE = (0, 150, 255)
COLOR_GRAY = (100, 100, 110)

WIDTH, HEIGHT = 900, 700
GRID_SIZE = 25
GAME_AREA = (600, 600)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Pro: Luxury Edition")
        self.clock = pygame.time.Clock()
        
        self.font_main = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 45, bold=True)
        
        self.state = "MENU"
        self.difficulty = "Normal"
        self.fps = 15
        self.map_type = "Classic"
        self.ai_active = False
        self.obstacles = []
        
        self.reset_game_data()

    def reset_game_data(self):
        self.snake = [(300, 300), (275, 300), (250, 300)]
        self.direction = (GRID_SIZE, 0)
        self.score = 0
        self.game_over = False
        self.death_reason = ""   # ✅ THÊM
        self.setup_map()
        self.spawn_food()

    def setup_map(self):
        self.obstacles = []
        if self.map_type == "Obstacles":
            for i in range(5, 15):
                self.obstacles.append((i * GRID_SIZE, 150))
                self.obstacles.append(((24 - i) * GRID_SIZE, 450))

    def spawn_food(self):
        while True:
            self.food = (random.randint(0, (GAME_AREA[0]-GRID_SIZE)//GRID_SIZE) * GRID_SIZE,
                         random.randint(0, (GAME_AREA[1]-GRID_SIZE)//GRID_SIZE) * GRID_SIZE)
            if self.food not in self.snake and self.food not in self.obstacles:
                break

    # --- AI ---
    def get_ai_move(self):
        head = self.snake[0]
        possible_moves = [(GRID_SIZE, 0), (-GRID_SIZE, 0), (0, GRID_SIZE), (0, -GRID_SIZE)]
        possible_moves = [m for m in possible_moves if (m[0]*-1, m[1]*-1) != self.direction]

        body_except_tail = set(self.snake[:-1])

        best_move = self.direction
        min_dist = 9999

        for move in possible_moves:
            nxt = (head[0] + move[0], head[1] + move[1])
            in_bounds = (0 <= nxt[0] < GAME_AREA[0] and 0 <= nxt[1] < GAME_AREA[1])
            safe_from_body = nxt not in body_except_tail
            safe_from_obstacles = nxt not in self.obstacles

            if in_bounds and safe_from_body and safe_from_obstacles:
                dist = abs(nxt[0] - self.food[0]) + abs(nxt[1] - self.food[1])
                if dist < min_dist:
                    min_dist = dist
                    best_move = move
        return best_move

    # --- UI ---
    def draw_button(self, text, x, y, w, h, color, selected=False):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        rect = pygame.Rect(x, y, w, h)
        
        is_hover = rect.collidepoint(mouse)
        draw_color = COLOR_ACCENT if selected else (color if not is_hover else (min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255)))
        
        pygame.draw.rect(self.screen, draw_color, rect, border_radius=12)
        if selected:
            pygame.draw.rect(self.screen, (255,255,255), rect, 2, border_radius=12)
            
        txt = self.font_main.render(text, True, (255,255,255))
        self.screen.blit(txt, (x + (w - txt.get_width())//2, y + (h - txt.get_height())//2))
        
        return is_hover and click[0]

    def draw_sidebar(self):
        panel_rect = pygame.Rect(650, 20, 230, 660)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect, border_radius=20)
        
        self.screen.blit(self.font_main.render("DASHBOARD", True, COLOR_GRAY), (670, 50))
        self.screen.blit(self.font_main.render(f"Score: {self.score}", True, COLOR_ACCENT), (670, 100))
        
        if self.draw_button("AI: " + ("ON" if self.ai_active else "OFF"), 670, 200, 190, 45, COLOR_BLUE, self.ai_active):
            self.ai_active = not self.ai_active
            pygame.time.delay(150)

        if self.draw_button("VỀ MENU", 670, 600, 190, 45, COLOR_RED):
            self.state = "MENU"
            pygame.time.delay(150)

    def menu_screen(self):
        self.screen.fill(COLOR_BG)
        title = self.font_title.render("SNAKE LUXURY", True, COLOR_ACCENT)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        self.screen.blit(self.font_main.render("CHỌN ĐỘ KHÓ:", True, COLOR_GRAY), (100, 180))
        if self.draw_button("EASY", 100, 220, 120, 45, COLOR_PANEL, self.difficulty == "Easy"):
            self.difficulty = "Easy"; self.fps = 10
        if self.draw_button("NORMAL", 240, 220, 120, 45, COLOR_PANEL, self.difficulty == "Normal"):
            self.difficulty = "Normal"; self.fps = 15
        if self.draw_button("HARD", 380, 220, 120, 45, COLOR_PANEL, self.difficulty == "Hard"):
            self.difficulty = "Hard"; self.fps = 25

        self.screen.blit(self.font_main.render("CHỌN MÀN CHƠI:", True, COLOR_GRAY), (100, 320))
        if self.draw_button("CLASSIC", 100, 360, 150, 45, COLOR_PANEL, self.map_type == "Classic"):
            self.map_type = "Classic"
        if self.draw_button("OBSTACLES", 270, 360, 150, 45, COLOR_PANEL, self.map_type == "Obstacles"):
            self.map_type = "Obstacles"

        if self.draw_button("BẮT ĐẦU CHƠI", WIDTH//2 - 150, 550, 300, 60, COLOR_ACCENT):
            self.reset_game_data()
            self.state = "PLAYING"
            pygame.time.delay(200)

    def play_screen(self):
        self.screen.fill(COLOR_BG)
        pygame.draw.rect(self.screen, (20,20,30), (20,20, GAME_AREA[0], GAME_AREA[1]), border_radius=10)

        for obs in self.obstacles:
            pygame.draw.rect(self.screen, COLOR_GRAY, (obs[0]+20, obs[1]+20, GRID_SIZE-2, GRID_SIZE-2), border_radius=4)

        for i, p in enumerate(self.snake):
            color = COLOR_ACCENT if i == 0 else (0,180,100)
            pygame.draw.rect(self.screen, color, (p[0]+20, p[1]+20, GRID_SIZE-2, GRID_SIZE-2), border_radius=6)

        pygame.draw.circle(self.screen, COLOR_RED, (self.food[0]+20+GRID_SIZE//2, self.food[1]+20+GRID_SIZE//2), 10)

        self.draw_sidebar()

        if not self.game_over:
            if self.ai_active:
                self.direction = self.get_ai_move()

            new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

            # ✅ PHÂN LOẠI NGUYÊN NHÂN CHẾT
            if new_head in self.snake:
                self.death_reason = "CẮN VÀO ĐUÔI!"
                self.game_over = True

            elif new_head in self.obstacles:
                self.death_reason = "ĐÂM VÀO TƯỜNG!"
                self.game_over = True

            elif (new_head[0] < 0 or new_head[0] >= GAME_AREA[0] or 
                  new_head[1] < 0 or new_head[1] >= GAME_AREA[1]):
                self.death_reason = "RA NGOÀI BẢN ĐỒ!"
                self.game_over = True

            else:
                self.snake.insert(0, new_head)
                if new_head == self.food:
                    self.score += 10
                    self.spawn_food()
                else:
                    self.snake.pop()

        else:
            # ✅ Overlay mờ (vẫn thấy rắn)
            overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (20, 20))

            font_big = pygame.font.SysFont("Segoe UI", 60, bold=True)
            font_small = pygame.font.SysFont("Segoe UI", 25)

            text_reason = font_big.render(self.death_reason, True, COLOR_RED)
            self.screen.blit(text_reason, (320 - text_reason.get_width()//2, 220))

            text_score = font_small.render(f"Score: {self.score}", True, COLOR_TEXT)
            self.screen.blit(text_score, (320 - text_score.get_width()//2, 300))

            text_restart = font_small.render("Nhấn SPACE để chơi lại", True, COLOR_ACCENT)
            self.screen.blit(text_restart, (320 - text_restart.get_width()//2, 340))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()

                if event.type == pygame.KEYDOWN:

                    # restart khi chết
                    if self.game_over and event.key == pygame.K_SPACE:
                        self.reset_game_data()
                        self.game_over = False

                    if not self.ai_active:
                        if event.key == pygame.K_UP and self.direction != (0, GRID_SIZE): self.direction = (0, -GRID_SIZE)
                        if event.key == pygame.K_DOWN and self.direction != (0, -GRID_SIZE): self.direction = (0, GRID_SIZE)
                        if event.key == pygame.K_LEFT and self.direction != (GRID_SIZE, 0): self.direction = (-GRID_SIZE, 0)
                        if event.key == pygame.K_RIGHT and self.direction != (-GRID_SIZE, 0): self.direction = (GRID_SIZE, 0)

            if self.state == "MENU":
                self.menu_screen()
            elif self.state == "PLAYING":
                self.play_screen()
            
            pygame.display.update()
            self.clock.tick(self.fps)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()

