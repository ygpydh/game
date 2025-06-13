# game_optimized.py - 炸弹迷宫小偷游戏优化版

import pygame # 导入 Pygame 库，用于游戏开发
import sys    # 导入 sys 库，用于程序退出
import time   # 导入 time 库，用于处理时间相关的逻辑，如炸弹计时
import random # 导入 random 库，用于随机选择背景音乐

# --- 1. 配置部分 (Configuration) ---
# 定义游戏窗口的宽度和高度
# 根据迷宫的实际尺寸 (10 行 x 20 列) 和瓦片大小 (32x32) 进行调整
TILE_SIZE = 32
COLS = 20 # 迷宫的列数
ROWS = 10 # 迷宫的行数

WIDTH = COLS * TILE_SIZE  # 游戏窗口宽度：20 * 32 = 640 像素
HEIGHT = ROWS * TILE_SIZE # 游戏窗口高度：10 * 32 = 320 像素

# 颜色定义 (RGB 值) - 使用常量命名规范，提高可读性
COLOR_BLACK = (0, 0, 0)         # 黑色 (背景色)
COLOR_WHITE = (255, 255, 255)   # 白色
COLOR_GRAY = (100, 100, 100)    # 灰色 (用于墙壁)
COLOR_GREEN = (0, 255, 0)       # 绿色 (用于玩家)
COLOR_RED = (255, 0, 0)         # 红色 (用于守卫)
COLOR_BLUE = (0, 100, 255)      # 蓝色 (用于出口)
COLOR_YELLOW = (255, 255, 0)    # 黄色 (用于宝藏和爆炸)
COLOR_LIGHT_RED = (255, 200, 200) # 浅红色 (用于守卫的视线范围)
COLOR_ORANGE = (255, 165, 0)    # 橙色 (用于炸弹)

# 迷宫地图定义
# 这是一个二维列表，代表游戏世界中的迷宫布局
# 每个数字代表不同类型的瓦片：
#   1: 墙壁 (不可通行，不可被爆炸摧毁)
#   0: 可通行路径 (玩家、守卫、爆炸可在此处)
#   2: 宝藏 (玩家需要收集，收集后变为 0)
#   3: 出口 (玩家收集所有宝藏后可从此逃脱)
#   9: 特殊标记 (目前行为与 '0' 相同，建议统一为 '0' 或为其赋予明确游戏意义)
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,2,0,0,3,1],
    [1,0,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,2,0,1,0,1],
    [1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,9,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1], # 优化：建议将此处的 '9' 统一为 '0'
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# 背景音乐文件列表 - 集中管理所有媒体文件路径是个好习惯
# 假设 bgm 文件与 game_optimized.py 在同一目录下
BGM_FILES = ["bgm0.wav", "bgm1.wav", "bgm2.wav"]


# --- 2. 游戏元素类定义 (Game Elements Classes) ---
# 虽然当前是函数式编程，但为了未来的扩展性，可以考虑将玩家、守卫、炸弹等封装成类。
# 在这个优化版本中，我们继续使用全局变量和函数，但保持结构清晰。

# 玩家的当前逻辑位置 [x, y]
player_pos = [1, 1]

# 守卫的当前逻辑位置 [x, y]
guard_pos = [1, 8]
# 守卫的巡逻路径点列表
guard_path = [(1, 8), (5, 8)]
# 当前守卫巡逻路径点在 guard_path 列表中的索引
guard_path_index = 0 # 优化：更清晰的变量名

# 存储当前激活的炸弹列表。每个炸弹项包含 (x坐标, y坐标, 放置时间戳)。
bombs = []
# 存储当前激活的爆炸区域列表。每个爆炸区域项包含 (x坐标, y坐标, 爆炸开始时间戳)。
explosions = []

# 游戏状态变量
got_treasures = 0
total_treasures = sum(row.count(2) for row in maze)


# --- 3. 游戏逻辑函数 (Game Logic Functions) ---

def draw_maze(screen):
    """
    在 Pygame 屏幕上绘制迷宫的各个瓦片。
    根据 'maze' 列表中瓦片的值，绘制对应颜色的方块。
    未明确处理的瓦片类型（如 '0' 和 '9'）将显示为屏幕背景色（黑色）。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象，所有绘图操作都将在此进行。
    """
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile_type = maze[y][x] # 优化：更清晰的变量名

            if tile_type == 1:
                pygame.draw.rect(screen, COLOR_GRAY, rect) # 绘制墙壁
            elif tile_type == 2:
                pygame.draw.rect(screen, COLOR_YELLOW, rect) # 绘制宝藏
            elif tile_type == 3:
                pygame.draw.rect(screen, COLOR_BLUE, rect) # 绘制出口
            # tile_type == 0 或 9 不绘制，将显示背景色 COLOR_BLACK


def draw_player(screen):
    """
    在屏幕上绘制玩家角色。玩家被绘制为一个绿色的方块。
    """
    x, y = player_pos
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, COLOR_GREEN, rect)


def move_player(dx, dy):
    """
    尝试将玩家移动到新的位置。
    移动前会检查新位置是否在迷宫边界内，并且不是墙壁。
    """
    new_x, new_y = player_pos[0] + dx, player_pos[1] + dy # 优化：更清晰的变量名

    # 边界和碰撞检测
    if (0 <= new_x < COLS and
        0 <= new_y < ROWS and
        maze[new_y][new_x] != 1): # 确保新位置不是墙壁
        player_pos[0], player_pos[1] = new_x, new_y


def draw_guard(screen):
    """
    在屏幕上绘制守卫及其下方的视线范围。
    守卫本体为红色方块，其视线范围为浅红色方块。
    守卫的视线固定向下延伸，最远 3 格，会被墙壁阻挡。
    """
    x, y = guard_pos
    # 绘制守卫本体
    guard_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, COLOR_RED, guard_rect)

    # 绘制守卫向下的视线范围
    for i in range(1, 4): # 视线延伸 1 到 3 格远的瓦片
        sight_y = y + i # 优化：更清晰的变量名
        # 如果超出迷宫底部边界或遇到墙壁，则停止绘制视线
        if sight_y >= ROWS or maze[sight_y][x] == 1:
            break
        # 绘制视线范围内的瓦片
        sight_rect = pygame.Rect(x * TILE_SIZE, sight_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_LIGHT_RED, sight_rect)

def check_guard_sight():
    """
    检查玩家是否在守卫的视线范围内。
    只检测玩家是否在守卫的正下方，且距离不超过 3 格，并且之间没有墙壁阻挡。

    Returns:
        bool: 如果玩家在守卫视线范围内则返回 True，否则返回 False。
    """
    guard_x, guard_y = guard_pos
    player_x, player_y = player_pos

    # 检查玩家是否在守卫正下方且距离合理
    if player_x == guard_x and player_y > guard_y and (player_y - guard_y) <= 3:
        # 检查守卫和玩家之间是否有墙壁阻挡视线
        for y_check in range(guard_y + 1, player_y):
            if maze[y_check][guard_x] == 1:
                return False # 视线被墙壁阻挡
        return True # 玩家被发现
    return False # 玩家不在视线范围内

def move_guard():
    """
    根据预设的 `guard_path` 路径点移动守卫。
    守卫每次向其当前目标点移动一个瓦片。当到达当前目标点后，它会切换到路径中的下一个目标点。
    """
    global guard_path_index, guard_pos # 声明全局变量以便修改

    current_guard_x, current_guard_y = guard_pos
    target_x, target_y = guard_path[guard_path_index]

    # 逐步向目标点移动
    if current_guard_x < target_x:
        guard_pos[0] += 1
    elif current_guard_x > target_x:
        guard_pos[0] -= 1
    elif current_guard_y < target_y:
        guard_pos[1] += 1
    elif current_guard_y > target_y:
        guard_pos[1] -= 1
    else:
        # 如果守卫已经到达了当前的目标点，则切换到下一个目标点
        guard_path_index = (guard_path_index + 1) % len(guard_path)

def draw_bombs(screen):
    """
    在屏幕上绘制所有激活的炸弹。炸弹被绘制为橙色方块。
    """
    for bomb_x, bomb_y, _ in bombs:
        bomb_rect = pygame.Rect(bomb_x * TILE_SIZE, bomb_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_ORANGE, bomb_rect)

def draw_explosions(screen):
    """
    在屏幕上绘制所有激活的爆炸区域。爆炸区域被绘制为黄色方块。
    """
    for exp_x, exp_y, _ in explosions:
        exp_rect = pygame.Rect(exp_x * TILE_SIZE, exp_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_YELLOW, exp_rect)

def explode(x, y):
    """
    计算炸弹爆炸的受影响区域。
    爆炸以 (x, y) 为中心点，向上下左右四个方向各延伸最多 2 格，
    但爆炸范围会被迷宫中的墙壁阻挡（墙壁后的区域不受影响）。

    Args:
        x (int): 炸弹爆炸中心的 x 坐标。
        y (int): 炸弹爆炸中心的 y 坐标。

    Returns:
        list: 一个列表，包含所有受爆炸影响的瓦片坐标 (nx, ny)。
    """
    affected_positions = [(x, y)] # 爆炸中心本身受影响

    # 定义四个基本方向的偏移量
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    EXPLOSION_RANGE = 2 # 爆炸延伸的最大距离 (瓦片数)

    for dx, dy in DIRECTIONS:
        for i in range(1, EXPLOSION_RANGE + 1): # 优化：使用常量
            nx, ny = x + dx * i, y + dy * i

            # 边界检查
            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                break # 超出迷宫边界，停止此方向延伸

            # 墙壁阻挡检查
            if maze[ny][nx] == 1:
                break # 遇到墙壁，此方向的爆炸被阻挡

            affected_positions.append((nx, ny))
    return affected_positions

def play_random_bgm():
    """
    随机选择一首背景音乐并播放。音乐会循环播放。
    """
    if not pygame.mixer.music.get_busy(): # 如果当前没有音乐正在播放
        selected_bgm = random.choice(BGM_FILES)
        try:
            pygame.mixer.music.load(selected_bgm)
            pygame.mixer.music.play(-1) # -1 表示无限循环
            # print(f"正在播放: {selected_bgm}") # 优化：游戏运行时可以考虑移除此打印，或用日志代替
        except pygame.error as e:
            print(f"错误: 无法加载或播放音乐文件 '{selected_bgm}': {e}") # 优化：更详细的错误信息


def show_end_screen(screen, message, color):
    """
    显示游戏结束画面（胜利或失败信息），并等待用户按键或关闭窗口以继续。
    在此画面中，背景音乐会停止播放。
    """
    pygame.mixer.music.stop() # 停止背景音乐

    font = pygame.font.SysFont("Arial", 48)
    text_surface = font.render(message, True, color) # 优化：更清晰的变量名
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.wait(1500) # 暂停 1.5 秒

    waiting_for_input = True # 优化：更清晰的变量名
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting_for_input = False # 退出等待循环


# --- 4. 游戏主循环 (Main Game Loop) ---

def run_game(): # 优化：函数名更具体
    """
    游戏的主运行函数。
    负责初始化 Pygame、设置游戏窗口、处理所有游戏事件、更新游戏状态以及绘制所有游戏元素。
    """
    global got_treasures # 声明全局变量以便在函数内部修改

    pygame.init() # 初始化所有 Pygame 模块
    pygame.mixer.init() # 初始化 Pygame 的混音器模块

    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # 创建游戏窗口
    pygame.display.set_caption("小偷游戏 - 炸弹迷宫") # 设置窗口标题
    clock = pygame.time.Clock() # 创建时钟对象，用于控制游戏帧率

    play_random_bgm() # 游戏开始时播放背景音乐

    game_running = True # 优化：使用布尔变量控制主循环
    while game_running:
        # 确保背景音乐持续播放
        play_random_bgm()

        # --- 绘图阶段 ---
        screen.fill(COLOR_BLACK) # 清除屏幕
        draw_maze(screen)
        draw_guard(screen)
        draw_player(screen)
        draw_bombs(screen)
        draw_explosions(screen)

        current_time = time.time() # 优化：更清晰的变量名

        # --- 炸弹和爆炸逻辑更新 ---
        # 使用列表切片进行安全迭代和移除
        for bomb_info in bombs[:]:
            bomb_x, bomb_y, bomb_placed_time = bomb_info
            if current_time - bomb_placed_time >= 2: # 炸弹爆炸计时
                explosion_area = explode(bomb_x, bomb_y)
                for pos in explosion_area:
                    explosions.append((pos[0], pos[1], current_time))
                bombs.remove(bomb_info) # 从炸弹列表中移除

        for explosion_info in explosions[:]:
            exp_x, exp_y, explosion_start_time = explosion_info
            if current_time - explosion_start_time >= 1: # 爆炸持续时间
                explosions.remove(explosion_info) # 从爆炸列表中移除

        # --- 胜利/失败条件检查 ---
        # 检查守卫是否被炸晕 (胜利条件之一)
        for exp_x, exp_y, _ in explosions:
            if (guard_pos[0], guard_pos[1]) == (exp_x, exp_y):
                show_end_screen(screen, "守卫被炸晕，胜利！", COLOR_GREEN)
                game_running = False # 结束游戏
                break # 退出当前循环

        if not game_running: # 如果游戏已结束，跳过后续检查
            continue

        # 检查玩家是否被守卫发现 (失败条件)
        if check_guard_sight():
            show_end_screen(screen, "你被发现了！游戏失败", COLOR_RED)
            game_running = False # 结束游戏
            continue # 跳过后续逻辑，直接进入下一次循环判断 game_running

        # --- 事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False # 用户关闭窗口，结束游戏
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_current_x, player_current_y = player_pos
                    if maze[player_current_y][player_current_x] == 0: # 只能在可通行区域放置炸弹
                        bombs.append((player_current_x, player_current_y, current_time))

        # --- 玩家移动输入处理 (按键状态检测) ---
        keys_pressed = pygame.key.get_pressed() # 优化：更清晰的变量名
        move_dx = move_dy = 0
        if keys_pressed[pygame.K_UP]: move_dy = -1
        if keys_pressed[pygame.K_DOWN]: move_dy = 1
        if keys_pressed[pygame.K_LEFT]: move_dx = -1
        if keys_pressed[pygame.K_RIGHT]: move_dx = 1

        if move_dx != 0 or move_dy != 0: # 只有当有实际移动时才调用
            move_player(move_dx, move_dy)

        # --- 游戏状态更新 ---
        # 检查玩家是否收集到宝藏
        player_current_x, player_current_y = player_pos
        if maze[player_current_y][player_current_x] == 2:
            got_treasures += 1
            maze[player_current_y][player_current_x] = 0 # 将宝藏从地图移除

        # 检查玩家是否到达出口并成功逃脱 (胜利条件)
        if maze[player_current_y][player_current_x] == 3:
            if got_treasures == total_treasures:
                show_end_screen(screen, "你成功逃脱了！胜利！", COLOR_GREEN)
                game_running = False # 结束游戏

        # 守卫移动
        move_guard()

        # --- 屏幕更新与帧率控制 ---
        pygame.display.flip() # 更新整个屏幕显示
        clock.tick(10) # 游戏帧率 10 FPS

    pygame.quit() # 游戏循环结束后退出 Pygame
    sys.exit() # 确保程序完全退出

# --- 程序入口点 ---
if __name__ == "__main__":
    run_game() # 运行游戏
