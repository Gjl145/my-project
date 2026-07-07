import pygame
import sys
import random

pygame.init()

# ===== 常量 =====
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
BASE_MOVE_DELAY = 150
MIN_MOVE_DELAY = 60
SPEED_PER_SCORE = 5
FOOD_COUNT = 3

# ===== 颜色 =====
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 70, 200)
RED = (200, 0, 0)
WHITE = (255, 255, 255)

# ===== 窗口 =====
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("双人贪吃蛇")
clock = pygame.time.Clock()
font = pygame.font.SysFont("simhei", 24)

# ===== 方向 =====
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# ===== 生成食物 =====
def spawn_food():
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake1 and pos not in snake2 and pos not in foods:
            return pos

# ===== 初始化游戏 =====
def init_game():
    global snake1, direction1, snake2, direction2, foods, game_over
    global direction_changed1, direction_changed2, score1, score2, last_move_time

    snake1 = [(5, 15), (4, 15), (3, 15)]
    direction1 = DIR_RIGHT
    direction_changed1 = False

    snake2 = [(25, 15), (26, 15), (27, 15)]
    direction2 = DIR_LEFT
    direction_changed2 = False

    score1 = 0
    score2 = 0
    game_over = False
    last_move_time = pygame.time.get_ticks()

    foods = []
    for _ in range(FOOD_COUNT):
        foods.append(spawn_food())

init_game()

# ===== 绘制函数 =====
def draw_snake(snake, head_color, body_color):
    for i, segment in enumerate(snake):
        x = segment[0] * CELL_SIZE
        y = segment[1] * CELL_SIZE
        color = head_color if i == 0 else body_color
        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

def draw_foods():
    for food in foods:
        x = food[0] * CELL_SIZE
        y = food[1] * CELL_SIZE
        pygame.draw.rect(screen, RED, (x, y, CELL_SIZE, CELL_SIZE))

# ===== 计算速度 =====
def get_move_delay():
    speed_bonus = (max(score1, score2) // SPEED_PER_SCORE) * 10
    delay = BASE_MOVE_DELAY - speed_bonus
    return max(delay, MIN_MOVE_DELAY)

# ===== 移动蛇 =====
def move_snake(snake, direction):
    """返回 (new_snake, new_head, alive)"""
    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    # 穿墙
    new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)

    # 撞自己
    if new_head in snake:
        return snake, new_head, False

    new_snake = [new_head] + snake
    return new_snake, new_head, True

# ===== 检查碰撞 =====
def check_collision(head, snake_a, snake_b):
    """head 撞到 snake_a 或 snake_b 的身体"""
    return head in snake_a or head in snake_b

# ===== 主循环 =====
while True:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_over and (event.key == pygame.K_r or event.key == pygame.K_SPACE):
                init_game()

    if not game_over:
        # ===== 蛇1（WASD）=====
        if not direction_changed1:
            keys = pygame.key.get_pressed()
            new_dir = None
            if keys[pygame.K_w]:
                new_dir = DIR_UP
            elif keys[pygame.K_s]:
                new_dir = DIR_DOWN
            elif keys[pygame.K_a]:
                new_dir = DIR_LEFT
            elif keys[pygame.K_d]:
                new_dir = DIR_RIGHT

            if new_dir and not (new_dir[0] == -direction1[0] and new_dir[1] == -direction1[1]):
                direction1 = new_dir
                direction_changed1 = True

        # ===== 蛇2（方向键）=====
        if not direction_changed2:
            keys = pygame.key.get_pressed()
            new_dir = None
            if keys[pygame.K_UP]:
                new_dir = DIR_UP
            elif keys[pygame.K_DOWN]:
                new_dir = DIR_DOWN
            elif keys[pygame.K_LEFT]:
                new_dir = DIR_LEFT
            elif keys[pygame.K_RIGHT]:
                new_dir = DIR_RIGHT

            if new_dir and not (new_dir[0] == -direction2[0] and new_dir[1] == -direction2[1]):
                direction2 = new_dir
                direction_changed2 = True

        # ===== 定时移动 =====
        move_delay = get_move_delay()
        if current_time - last_move_time > move_delay:
            # 先各自计算新位置
            new_snake1, head1, alive1 = move_snake(snake1, direction1)
            new_snake2, head2, alive2 = move_snake(snake2, direction2)

            # 检查蛇1是否撞蛇2的身体
            if alive1 and head1 in snake2:
                alive1 = False

            # 检查蛇2是否撞蛇1的身体
            if alive2 and head2 in snake1:
                alive2 = False

            # 检查两条蛇头对头
            if head1 == head2:
                alive1 = False
                alive2 = False

            if not alive1:
                game_over = True
                winner = 2
            elif not alive2:
                game_over = True
                winner = 1
            else:
                # 都活着，应用移动
                snake1 = new_snake1
                snake2 = new_snake2

                # 吃食物
                if head1 in foods:
                    foods.remove(head1)
                    foods.append(spawn_food())
                    score1 += 1
                else:
                    snake1.pop()

                if head2 in foods:
                    foods.remove(head2)
                    foods.append(spawn_food())
                    score2 += 1
                else:
                    snake2.pop()

            direction_changed1 = False
            direction_changed2 = False
            last_move_time = current_time

    # ===== 绘制 =====
    screen.fill(BLACK)
    draw_snake(snake1, (0, 255, 0), GREEN)
    draw_snake(snake2, (50, 150, 255), BLUE)
    draw_foods()

    # 分数
    score1_text = font.render(f"P1 (WASD): {score1}", True, GREEN)
    score2_text = font.render(f"P2 (Arrow): {score2}", True, BLUE)
    screen.blit(score1_text, (5, 5))
    screen.blit(score2_text, (WIDTH - score2_text.get_width() - 5, 5))

    hint = font.render("WASD / Arrow | R Restart", True, (150, 150, 150))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

    if game_over:
        over = font.render(f"Game Over! Player {winner} Wins!", True, WHITE)
        rect = over.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(over, rect)

        restart = font.render("Press R to Restart", True, WHITE)
        rect2 = restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
        screen.blit(restart, rect2)

    pygame.display.flip()
    clock.tick(60)