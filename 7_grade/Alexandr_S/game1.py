import pygame
import math

# --- настройки ---
WIDTH, HEIGHT = 900, 600
HALF_HEIGHT = HEIGHT // 2

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 200
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS

TILE = 64

# карта
game_map = [
    "111111111111",
    "100000000001",
    "100000000001",
    "100000000001",
    "101000010001",
    "100000000001",
    "111111111111"
]

# игрок
player_pos = [160, 160]
player_angle = 0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# текстура стены
wall_texture = pygame.image.load("wall.png").convert()
wall_texture = pygame.transform.scale(wall_texture, (TILE, TILE))

# оружие
gun_idle = pygame.Surface((200, 120))
gun_idle.fill((80, 80, 80))

gun_shoot = pygame.Surface((200, 120))
gun_shoot.fill((200, 200, 200))

shooting = False
shoot_timer = 0

# --- пули ---
bullets = []


def ray_casting():
    ox, oy = player_pos
    cur_angle = player_angle - HALF_FOV

    for ray in range(NUM_RAYS):
        sin_a = math.sin(cur_angle)
        cos_a = math.cos(cur_angle)

        for depth in range(1, MAX_DEPTH):
            x = ox + depth * cos_a
            y = oy + depth * sin_a

            map_x = int(x // TILE)
            map_y = int(y // TILE)

            if game_map[map_y][map_x] == '1':
                depth *= math.cos(player_angle - cur_angle)
                proj_height = min(int(40000 / (depth + 0.0001)), HEIGHT)

                hit_x = x % TILE
                hit_y = y % TILE

                if abs(hit_x - TILE) < 1 or abs(hit_x) < 1:
                    texture_x = int(hit_y)
                else:
                    texture_x = int(hit_x)

                texture_column = wall_texture.subsurface(texture_x, 0, 1, TILE)
                texture_column = pygame.transform.scale(texture_column, (SCALE, proj_height))

                shade = 255 / (1 + depth * depth * 0.00002)
                texture_column.fill((shade, shade, shade), special_flags=pygame.BLEND_MULT)

                screen.blit(texture_column, (ray * SCALE, HALF_HEIGHT - proj_height // 2))
                break

        cur_angle += DELTA_ANGLE


def draw_weapon():
    global shoot_timer, shooting

    if shooting:
        screen.blit(gun_shoot, (WIDTH // 2 - 100, HEIGHT - 120))
        shoot_timer -= 1
        if shoot_timer <= 0:
            shooting = False
    else:
        screen.blit(gun_idle, (WIDTH // 2 - 100, HEIGHT - 120))


def shoot():
    global shooting, shoot_timer

    shooting = True
    shoot_timer = 5

    # создаём пулю
    bullets.append({
        "x": player_pos[0],
        "y": player_pos[1],
        "angle": player_angle
    })


def update_bullets():
    speed = 10
    for bullet in bullets[:]:
        bullet["x"] += math.cos(bullet["angle"]) * speed
        bullet["y"] += math.sin(bullet["angle"]) * speed

        map_x = int(bullet["x"] // TILE)
        map_y = int(bullet["y"] // TILE)

        # если попала в стену — удаляем
        if game_map[map_y][map_x] == '1':
            bullets.remove(bullet)
            continue

        # рисуем пулю (2D сверху)
        pygame.draw.circle(screen, (255, 200, 0), (int(bullet["x"]), int(bullet["y"])), 4)


def movement():
    global player_angle

    keys = pygame.key.get_pressed()

    # поворот
    if keys[pygame.K_LEFT]:
        player_angle -= 0.04
    if keys[pygame.K_RIGHT]:
        player_angle += 0.04

    speed = 3

    dx = math.cos(player_angle) * speed
    dy = math.sin(player_angle) * speed

    # вперёд / назад
    if keys[pygame.K_w]:
        player_pos[0] += dx
        player_pos[1] += dy
    if keys[pygame.K_s]:
        player_pos[0] -= dx
        player_pos[1] -= dy

    # --- СТРЕЙФ (влево / вправо) ---
    if keys[pygame.K_a]:
        player_pos[0] += math.cos(player_angle - math.pi/2) * speed
        player_pos[1] += math.sin(player_angle - math.pi/2) * speed

    if keys[pygame.K_d]:
        player_pos[0] += math.cos(player_angle + math.pi/2) * speed
        player_pos[1] += math.sin(player_angle + math.pi/2) * speed


# --- главный цикл ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        ):
            shoot()

    movement()

    # фон
    screen.fill("black")
    pygame.draw.rect(screen, (25, 25, 40), (0, 0, WIDTH, HALF_HEIGHT))
    pygame.draw.rect(screen, (40, 40, 40), (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    ray_casting()

    update_bullets()

    # прицел
    pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 3)

    draw_weapon()

    pygame.display.flip()
    clock.tick(60)