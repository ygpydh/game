import pygame
import sys
import time

from config import WIDTH, HEIGHT, ROWS, COLS, BLACK, maze
from maze import draw_maze
from player import player_pos, draw_player, move_player
from guard import guard_pos, draw_guard, move_guard, check_guard_sight
from bomb import bombs, explosions, draw_bombs, draw_explosions, explode

got_treasures = 0
total_treasures = sum(row.count(2) for row in maze)

def show_end_screen(screen, message, color):
    font = pygame.font.SysFont("Arial", 48)
    text = font.render(message, True, color)
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(1500)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting = False

def run():
    global got_treasures
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("小偷游戏 - 炸弹迷宫")
    clock = pygame.time.Clock()

    while True:
        screen.fill(BLACK)
        draw_maze(screen)
        draw_guard(screen)
        draw_player(screen)
        draw_bombs(screen)
        draw_explosions(screen)

        now = time.time()

        for bx, by, t in bombs[:]:
            if now - t >= 2:
                area = explode(bx, by, maze)
                for pos in area:
                    explosions.append((pos[0], pos[1], now))
                bombs.remove((bx, by, t))

        for ex, ey, t in explosions[:]:
            if now - t >= 1:
                explosions.remove((ex, ey, t))

        for ex, ey, _ in explosions:
            if (guard_pos[0], guard_pos[1]) == (ex, ey):
                show_end_screen(screen, "守卫被炸晕，胜利！", (0,255,0))
                pygame.quit()
                return

        if check_guard_sight(player_pos, maze):
            show_end_screen(screen, "你被发现了！游戏失败", (255,0,0))
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    x, y = player_pos
                    if maze[y][x] == 0:
                        bombs.append((x, y, now))

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1

        if dx or dy:
            move_player(dx, dy, maze, COLS, ROWS)

        x, y = player_pos
        if maze[y][x] == 2:
            got_treasures += 1
            maze[y][x] = 0

        if maze[y][x] == 3:
            if got_treasures == total_treasures:
                show_end_screen(screen, "你成功逃脱了！胜利！", (0,255,0))
                break

        move_guard()
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    run()
