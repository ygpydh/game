# game.py - 炸弹迷宫小偷游戏主程序

import pygame  # 导入 Pygame 库，用于游戏开发
import sys     # 导入 sys 库，用于程序退出
import time    # 导入 time 库，用于处理时间相关的逻辑，如炸弹计时
import random  # 导入 random 库，用于随机选择背景音乐和迷宫生成

# --- 1. 配置部分 (Configuration) ---
# 定义游戏窗口的宽度和高度
TILE_SIZE = 32  # 每个瓦片 32x32 像素
PLAYER_SPEED = 3.0 # 玩家每帧移动的像素数 (用于平滑移动)
GUARD_SPEED = 1.0 # 守卫每帧移动的像素数 (比玩家慢，用于平滑移动)

COLS = 20       # 迷宫的列数
ROWS = 10       # 迷宫的行数

WIDTH = COLS * TILE_SIZE    # 游戏窗口宽度：20 * 32 = 640 像素
HEIGHT = ROWS * TILE_SIZE   # 游戏窗口高度：10 * 32 = 320 像素

# 颜色定义 (RGB 值) - 使用常量命名规范，提高可读性
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 100, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_LIGHT_RED = (255, 200, 200)
COLOR_ORANGE = (255, 165, 0)
COLOR_BROWN = (139, 69, 19) # 棕色 (用于可炸开的障碍物)
COLOR_HEALTH_GREEN = (0, 200, 0) # 血量条绿色
COLOR_HEALTH_RED = (200, 0, 0)   # 血量条红色背景

# 迷宫地图定义 (在多关卡/随机地图模式下，此硬编码地图将被动态生成所替代)
# 瓦片类型：
#   0: 可通行路径 (例如，草地)
#   1: 墙壁 (不可通行，不可被爆炸摧毁，例如，房子、树)
#   2: 宝藏 (例如，金币)
#   3: 出口 (例如，蓝色传送门)
#   4: 可炸开的障碍物 (例如，木箱、砖块)
#   9: 特殊标记 (目前行为与 '0' 相同，建议统一为 '0' 或为其赋予明确游戏意义)
maze = [] # 初始设置为空，将在 run_game_loop 中生成

# 背景音乐文件列表 (假设在 'music' 子文件夹中)
BGM_FILES = ["music/bgm0.wav", "music/bgm1.wav", "music/bgm2.wav"]

# 游戏图片资源路径 (假设在 'assets' 子文件夹中)
IMAGE_PATHS = {
    'tile_grass': 'assets/map/tile_grass.png',
    'tile_wall': 'assets/map/tile_wall.png',
    'tile_box': 'assets/map/tile_box.png', # 可炸开的障碍物
    'tile_treasure': 'assets/item/tile_treasure.png',
    'tile_exit': 'assets/map/tile_exit.png',
    'player': 'assets/player/player.png',
    'guard': 'assets/computer/guard.png',
    'bomb': 'assets/boom/bomb.png',
    'explosion': 'assets/boom/explosion.png',
}
GAME_IMAGES = {} # 存储加载后的图片对象

# --- 2. 游戏元素变量定义 (Game Elements Variables) ---
# 玩家的逻辑瓦片位置和像素位置
player_tile_pos = [1, 1] # 玩家所在的瓦片坐标 (整数)
player_pixel_pos = [player_tile_pos[0] * TILE_SIZE, player_tile_pos[1] * TILE_SIZE] # 玩家的精确像素坐标 (浮点数)
player_current_speed_x = 0
player_current_speed_y = 0

PLAYER_MAX_HP = 3
player_hp = PLAYER_MAX_HP

# 守卫的逻辑瓦片位置和像素位置
guard_tile_pos = [1, 8] # 守卫所在的瓦片坐标 (整数)
guard_pixel_pos = [guard_tile_pos[0] * TILE_SIZE, guard_tile_pos[1] * TILE_SIZE] # 守卫的精确像素坐标 (浮点数)
guard_current_speed_x = 0
guard_current_speed_y = 0

GUARD_MAX_HP = 2
guard_hp = GUARD_MAX_HP
guard_path = []
guard_path_index = 0
GUARD_BOMB_COOLDOWN = 5
last_guard_bomb_time = 0

bombs = []
explosions = []
EXPLOSION_RANGE = 2 # 炸弹爆炸范围常量

got_treasures = 0
total_treasures = 0


# --- 3. 游戏逻辑函数 (Game Logic Functions) ---

def load_images():
    """
    加载所有游戏图片资源。
    """
    for key, path in IMAGE_PATHS.items():
        try:
            image = pygame.image.load(path).convert_alpha()
            GAME_IMAGES[key] = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            print(f"错误: 无法加载图片 '{path}'. 请确保文件存在且路径正确。错误信息: {e}")
            GAME_IMAGES[key] = None

def draw_maze(screen):
    """
    在 Pygame 屏幕上绘制迷宫的各个瓦片，使用图片资源。
    如果图片加载失败，则使用颜色作为备用。
    """
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile_type = maze[y][x]
            
            image_to_draw = None
            color_to_draw = None

            if tile_type == 0 or tile_type == 9: # 可通行路径
                image_to_draw = GAME_IMAGES.get('tile_grass')
                color_to_draw = COLOR_BLACK
            elif tile_type == 1: # 墙壁
                image_to_draw = GAME_IMAGES.get('tile_wall')
                color_to_draw = COLOR_GRAY
            elif tile_type == 2: # 宝藏
                image_to_draw = GAME_IMAGES.get('tile_treasure')
                color_to_draw = COLOR_YELLOW
            elif tile_type == 3: # 出口
                image_to_draw = GAME_IMAGES.get('tile_exit')
                color_to_draw = COLOR_BLUE
            elif tile_type == 4: # 可炸开的障碍物
                image_to_draw = GAME_IMAGES.get('tile_box')
                color_to_draw = COLOR_BROWN
            
            if image_to_draw:
                screen.blit(image_to_draw, rect)
            elif color_to_draw:
                pygame.draw.rect(screen, color_to_draw, rect)


def draw_player(screen):
    """
    在屏幕上绘制玩家角色，使用图片资源。
    使用 player_pixel_pos 进行绘制，实现平滑移动。
    """
    player_image = GAME_IMAGES.get('player')
    if player_image:
        screen.blit(player_image, (player_pixel_pos[0], player_pixel_pos[1]))
    else:
        rect = pygame.Rect(player_pixel_pos[0], player_pixel_pos[1], TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_GREEN, rect)


def get_tile_at_pixel(pixel_x, pixel_y):
    """根据像素坐标获取所在的瓦片坐标。"""
    return int(pixel_x // TILE_SIZE), int(pixel_y // TILE_SIZE)

def get_pixel_center_of_tile(tile_x, tile_y):
    """获取瓦片中心的像素坐标。"""
    return tile_x * TILE_SIZE + TILE_SIZE / 2, tile_y * TILE_SIZE + TILE_SIZE / 2

def check_collision_with_map(target_pixel_rect):
    """
    检查矩形是否与迷宫中的墙壁 (1) 或不可炸开障碍物 (4) 发生碰撞。
    Returns: bool
    """
    # 获取矩形覆盖的瓦片范围
    start_col = int(target_pixel_rect.left // TILE_SIZE)
    end_col = int(target_pixel_rect.right // TILE_SIZE)
    start_row = int(target_pixel_rect.top // TILE_SIZE)
    end_row = int(target_pixel_rect.bottom // TILE_SIZE)

    # 遍历受影响的瓦片
    for r in range(max(0, start_row), min(ROWS, end_row + 1)):
        for c in range(max(0, start_col), min(COLS, end_col + 1)):
            if maze[r][c] == 1 or maze[r][c] == 4: # 墙壁或可炸开障碍物
                tile_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if target_pixel_rect.colliderect(tile_rect):
                    return True # 发生碰撞
    return False

def move_player_smooth():
    """
    玩家平滑移动逻辑，处理像素级移动和碰撞。
    dx, dy 作为 player_current_speed_x/y 在主循环中设置。
    """
    global player_pixel_pos, player_tile_pos, player_current_speed_x, player_current_speed_y

    # 计算目标像素位置
    new_pixel_x = player_pixel_pos[0] + player_current_speed_x
    new_pixel_y = player_pixel_pos[1] + player_current_speed_y

    # 创建玩家的下一个位置的矩形
    player_rect = pygame.Rect(new_pixel_x, new_pixel_y, TILE_SIZE, TILE_SIZE)

    # 如果没有碰撞，则直接移动
    if not check_collision_with_map(player_rect):
        player_pixel_pos[0] = new_pixel_x
        player_pixel_pos[1] = new_pixel_y
        player_tile_pos[0], player_tile_pos[1] = get_tile_at_pixel(player_pixel_pos[0], player_pixel_pos[1])
        return

    # --- 平滑碰撞处理（拐角滑动）---
    # 如果发生碰撞，尝试只在X或Y方向上移动
    can_move_x = True
    temp_rect_x = pygame.Rect(new_pixel_x, player_pixel_pos[1], TILE_SIZE, TILE_SIZE)
    if check_collision_with_map(temp_rect_x):
        can_move_x = False

    can_move_y = True
    temp_rect_y = pygame.Rect(player_pixel_pos[0], new_pixel_y, TILE_SIZE, TILE_SIZE)
    if check_collision_with_map(temp_rect_y):
        can_move_y = False

    if can_move_x:
        player_pixel_pos[0] = new_pixel_x
    if can_move_y:
        player_pixel_pos[1] = new_pixel_y

    # 如果两个方向都不能移动，则尝试进行“滑动”调整
    # 当玩家紧贴着墙移动，但目标瓦片侧面是通畅时，可以轻微调整
    # 这里的滑动逻辑可以更复杂，目前简化为：如果当前方向被阻挡，尝试向侧面一个像素进行微调
    # 核心思想：当一个方向被堵住时，检查另外一个方向是否有微小的移动空间
    if player_current_speed_x != 0 and not can_move_x: # 尝试水平移动被阻挡
        # 尝试沿Y轴微调
        current_tile_center_y = player_tile_pos[1] * TILE_SIZE + TILE_SIZE / 2
        
        # 如果玩家Y轴不在瓦片中心，尝试归位
        if abs(player_pixel_pos[1] - current_tile_center_y) > 1: # 允许1像素误差
             if player_pixel_pos[1] < current_tile_center_y:
                 player_pixel_pos[1] += min(PLAYER_SPEED, current_tile_center_y - player_pixel_pos[1])
             else:
                 player_pixel_pos[1] -= min(PLAYER_SPEED, player_pixel_pos[1] - current_tile_center_y)

    elif player_current_speed_y != 0 and not can_move_y: # 尝试垂直移动被阻挡
        # 尝试沿X轴微调
        current_tile_center_x = player_tile_pos[0] * TILE_SIZE + TILE_SIZE / 2
        if abs(player_pixel_pos[0] - current_tile_center_x) > 1:
            if player_pixel_pos[0] < current_tile_center_x:
                player_pixel_pos[0] += min(PLAYER_SPEED, current_tile_center_x - player_pixel_pos[0])
            else:
                player_pixel_pos[0] -= min(PLAYER_SPEED, player_pixel_pos[0] - current_tile_center_x)

    # 最终更新瓦片位置
    player_tile_pos[0], player_tile_pos[1] = get_tile_at_pixel(player_pixel_pos[0], player_pixel_pos[1])


def draw_guard(screen):
    """
    在屏幕上绘制守卫及其下方的视线范围。
    守卫本体使用图片资源，视线范围为浅红色方块。
    守卫的视线固定向下延伸，最远 3 格，会被墙壁或可炸开障碍物阻挡。
    """
    guard_image = GAME_IMAGES.get('guard')
    if guard_image:
        screen.blit(guard_image, (guard_pixel_pos[0], guard_pixel_pos[1]))
    else:
        guard_rect = pygame.Rect(guard_pixel_pos[0], guard_pixel_pos[1], TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_RED, guard_rect)

    # 绘制守卫向下的视线范围
    x, y = guard_tile_pos # 视线检测仍基于瓦片位置
    for i in range(1, 4):
        sight_y = y + i
        if sight_y >= ROWS or maze[sight_y][x] == 1 or maze[sight_y][x] == 4:
            break
        sight_rect = pygame.Rect(x * TILE_SIZE, sight_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLOR_LIGHT_RED, sight_rect)

def check_guard_sight():
    """
    检查玩家是否在守卫的视线范围内。
    只检测玩家是否在守卫的正下方，且距离不超过 3 格，并且之间没有墙壁或可炸开障碍物阻挡。
    """
    guard_x, guard_y = guard_tile_pos
    player_x, player_y = player_tile_pos # 使用玩家的瓦片位置进行视线检测

    if player_x == guard_x and player_y > guard_y and (player_y - guard_y) <= 3:
        for y_check in range(guard_y + 1, player_y):
            if maze[y_check][guard_x] == 1 or maze[y_check][guard_x] == 4:
                return False
        return True
    return False

def move_guard_smooth():
    """
    守卫平滑移动逻辑。
    守卫向目标瓦片中心移动，并在到达后切换目标。
    如果守卫无法移动（被困），它可能会尝试放置炸弹。
    """
    global guard_tile_pos, guard_pixel_pos, guard_path_index, last_guard_bomb_time
    global guard_current_speed_x, guard_current_speed_y

    # 获取当前目标瓦片
    target_x_tile, target_y_tile = guard_path[guard_path_index]
    # 获取目标瓦片的中心像素坐标
    target_x_pixel, target_y_pixel = get_pixel_center_of_tile(target_x_tile, target_y_tile)

    # 计算移动方向和距离
    dx = target_x_pixel - (guard_pixel_pos[0] + TILE_SIZE / 2)
    dy = target_y_pixel - (guard_pixel_pos[1] + TILE_SIZE / 2)

    distance = (dx**2 + dy**2)**0.5

    if distance < GUARD_SPEED: # 如果接近目标中心，则直接对齐并切换目标
        guard_pixel_pos[0] = target_x_pixel - TILE_SIZE / 2
        guard_pixel_pos[1] = target_y_pixel - TILE_SIZE / 2
        guard_tile_pos[0], guard_tile_pos[1] = target_x_tile, target_y_tile
        guard_path_index = (guard_path_index + 1) % len(guard_path)
        guard_current_speed_x = 0 # 停止移动
        guard_current_speed_y = 0
        return # 成功移动并对齐，返回

    # 计算标准化速度
    guard_current_speed_x = GUARD_SPEED * (dx / distance)
    guard_current_speed_y = GUARD_SPEED * (dy / distance)

    # 尝试移动
    new_pixel_x = guard_pixel_pos[0] + guard_current_speed_x
    new_pixel_y = guard_pixel_pos[1] + guard_current_speed_y

    guard_rect = pygame.Rect(new_pixel_x, new_pixel_y, TILE_SIZE, TILE_SIZE)
    collided = check_collision_with_map(guard_rect)

    if not collided:
        guard_pixel_pos[0] = new_pixel_x
        guard_pixel_pos[1] = new_pixel_y
        guard_tile_pos[0], guard_tile_pos[1] = get_tile_at_pixel(guard_pixel_pos[0], guard_pixel_pos[1])
    else:
        # 如果发生碰撞，守卫被困
        guard_current_speed_x = 0 # 停止移动
        guard_current_speed_y = 0

        current_time = time.time()
        # 守卫放置炸弹尝试脱困或攻击
        if current_time - last_guard_bomb_time >= GUARD_BOMB_COOLDOWN:
            # 守卫所在位置是可通行区域 (0) 或可炸开障碍物 (4)
            if maze[guard_tile_pos[1]][guard_tile_pos[0]] in [0, 4]:
                distance_to_player = abs(player_tile_pos[0] - guard_tile_pos[0]) + abs(player_tile_pos[1] - guard_tile_pos[1])
                # 如果玩家在守卫的潜在炸弹攻击范围内，或者守卫被困时随机放炸弹
                if distance_to_player <= EXPLOSION_RANGE + 2 or random.random() < 0.5:
                    bombs.append((guard_tile_pos[0], guard_tile_pos[1], current_time, 'guard'))
                    last_guard_bomb_time = current_time


def draw_bombs(screen):
    """
    在屏幕上绘制所有激活的炸弹，使用图片资源。
    """
    bomb_image = GAME_IMAGES.get('bomb')
    for bomb_x, bomb_y, _, _ in bombs:
        if bomb_image:
            screen.blit(bomb_image, (bomb_x * TILE_SIZE, bomb_y * TILE_SIZE))
        else:
            bomb_rect = pygame.Rect(bomb_x * TILE_SIZE, bomb_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_ORANGE, bomb_rect)


def draw_explosions(screen):
    """
    在屏幕上绘制所有激活的爆炸区域，使用图片资源。
    """
    explosion_image = GAME_IMAGES.get('explosion')
    for exp_x, exp_y, _ in explosions:
        if explosion_image:
            screen.blit(explosion_image, (exp_x * TILE_SIZE, exp_y * TILE_SIZE))
        else:
            exp_rect = pygame.Rect(exp_x * TILE_SIZE, exp_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_YELLOW, exp_rect)


def explode(x, y):
    """
    计算炸弹爆炸的受影响区域，并处理可炸开障碍物。
    爆炸以 (x, y) 为中心点，向上下左右四个方向各延伸最多 `EXPLOSION_RANGE` 格。
    墙壁 (1) 阻挡爆炸。可炸开的障碍物 (4) 会在爆炸后变为可通行路径 (0)。
    """
    affected_positions = [(x, y)] # 爆炸中心本身受影响

    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in DIRECTIONS:
        for i in range(1, EXPLOSION_RANGE + 1):
            nx, ny = x + dx * i, y + dy * i

            if not (0 <= nx < COLS and 0 <= ny < ROWS): # 边界检查
                break

            if maze[ny][nx] == 1: # 墙壁 (1) 阻挡爆炸，且不会被炸毁
                break
            
            if maze[ny][nx] == 4: # 可炸开障碍物 (4) 会被炸毁，但爆炸不会穿透它
                affected_positions.append((nx, ny))
                maze[ny][nx] = 0 # 障碍物被炸毁，变为可通行路径
                break
            
            affected_positions.append((nx, ny))
    return affected_positions

def play_random_bgm():
    """
    随机选择一首背景音乐并播放。音乐会循环播放。
    """
    if not pygame.mixer.music.get_busy():
        selected_bgm = random.choice(BGM_FILES)
        try:
            pygame.mixer.music.load(selected_bgm)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"错误: 无法加载或播放音乐文件 '{selected_bgm}'. "
                  f"请检查文件是否存在且路径正确，以及文件格式是否受支持。错误信息: {e}")

def draw_health_bar(screen, current_hp, max_hp, x, y, width, height, color_full, color_empty):
    """
    绘制血量条。
    """
    if max_hp <= 0:
        return

    pygame.draw.rect(screen, color_empty, (x, y, width, height))

    fill_width = (current_hp / max_hp) * width
    pygame.draw.rect(screen, color_full, (x, y, fill_width, height))

    pygame.draw.rect(screen, COLOR_WHITE, (x, y, width, height), 1)


def show_end_screen(screen, message, color):
    """
    显示游戏结束画面（胜利或失败信息），并等待用户按键或关闭窗口以继续。
    在此画面中，背景音乐会停止播放。
    """
    pygame.mixer.music.stop()

    font = pygame.font.SysFont("Arial", 48)
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.wait(1500)

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting_for_input = False


# --- 5. 迷宫生成与游戏状态管理函数 (Maze Generation & Game State Management) ---

def generate_maze(rows, cols):
    """
    生成一个简单的随机迷宫。
    注意：此函数仅为占位符，生成的是带有随机墙壁和可炸开障碍物的网格，
    而不是一个保证可解的复杂迷宫。若要生成复杂迷宫，需引入专门算法。
    """
    new_maze = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # 边缘墙壁
    for r in range(rows):
        new_maze[r][0] = 1
        new_maze[r][cols - 1] = 1
    for c in range(cols):
        new_maze[0][c] = 1
        new_maze[rows - 1][c] = 1
    
    # 随机放置内部墙壁 (1) 和可炸开障碍物 (4)
    num_walls = int(rows * cols * 0.15)
    num_breakable_obstacles = int(rows * cols * 0.10)

    for _ in range(num_walls):
        rand_x = random.randint(1, cols - 2)
        rand_y = random.randint(1, rows - 2)
        if new_maze[rand_y][rand_x] == 0:
            new_maze[rand_y][rand_x] = 1

    for _ in range(num_breakable_obstacles):
        rand_x = random.randint(1, cols - 2)
        rand_y = random.randint(1, rows - 2)
        if new_maze[rand_y][rand_x] == 0:
            new_maze[rand_y][rand_x] = 4
            
    return new_maze

def place_game_elements(current_maze):
    """
    在当前生成的迷宫上放置玩家、守卫、宝藏和出口。
    确保这些元素放置在可通行或可炸开的区域，并且不会彼此重叠。
    """
    global player_tile_pos, player_pixel_pos, guard_tile_pos, guard_pixel_pos, guard_path

    # 收集所有可用的瓦片（0或4），用于放置元素
    available_tiles = []
    for r in range(1, ROWS - 1):
        for c in range(1, COLS - 1):
            if current_maze[r][c] == 0 or current_maze[r][c] == 4:
                available_tiles.append((c, r))
    random.shuffle(available_tiles)

    # 放置玩家
    if available_tiles:
        px, py = available_tiles.pop(0)
        player_tile_pos[0], player_tile_pos[1] = px, py
        player_pixel_pos[0], player_pixel_pos[1] = px * TILE_SIZE, py * TILE_SIZE
        current_maze[py][px] = 0 # 确保玩家起点是通路
    else:
        print("警告: 未能在迷宫中找到玩家的起始点。")
        player_tile_pos[0], player_tile_pos[1] = 1, 1 
        player_pixel_pos[0], player_pixel_pos[1] = 1 * TILE_SIZE, 1 * TILE_SIZE

    # 放置守卫
    guard_placed = False
    for i in range(len(available_tiles) -1, -1, -1):
        gx, gy = available_tiles[i]
        # 确保守卫周围有通路或可炸开障碍物，以便它能够移动或脱困
        has_open_neighbor = False
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and (current_maze[ny][nx] == 0 or current_maze[ny][nx] == 4):
                has_open_neighbor = True
                break
        
        if has_open_neighbor:
            guard_tile_pos[0], guard_tile_pos[1] = gx, gy
            guard_pixel_pos[0], guard_pixel_pos[1] = gx * TILE_SIZE, gy * TILE_SIZE
            current_maze[gy][gx] = 0 # 确保守卫起点是通路
            available_tiles.pop(i)
            guard_placed = True
            break
    
    if not guard_placed:
        print("警告: 未能在迷宫中找到守卫的非封闭起始点。守卫可能被困。")
        if available_tiles:
            gx, gy = available_tiles.pop(0)
            guard_tile_pos[0], guard_tile_pos[1] = gx, gy
            guard_pixel_pos[0], guard_pixel_pos[1] = gx * TILE_SIZE, gy * TILE_SIZE
            current_maze[gy][gx] = 0
        else:
            guard_tile_pos[0], guard_tile_pos[1] = COLS - 2, ROWS - 2
            guard_pixel_pos[0], guard_pixel_pos[1] = (COLS - 2) * TILE_SIZE, (ROWS - 2) * TILE_SIZE

    # 简化守卫路径：当前位置和随机选择的另一个通路作为路径
    guard_path_options = [p for p in available_tiles if p != tuple(guard_tile_pos)] # 避免守卫路径与自身起点重叠
    guard_path = [tuple(guard_tile_pos)]
    if len(guard_path_options) >= 1:
        second_point = random.choice(guard_path_options)
        guard_path.append(second_point)
    elif len(guard_path_options) == 0 and len(available_tiles) > 0:
        guard_path.append(available_tiles[0])


    # 放置宝藏
    treasures_to_place = 3
    placed_treasures = 0
    treasure_coords = []
    
    for _ in range(treasures_to_place):
        if available_tiles:
            tx, ty = available_tiles.pop(0)
            current_maze[ty][tx] = 2 # 放置宝藏
            treasure_coords.append((tx,ty))
            placed_treasures += 1
        else:
            print("警告: 可放置宝藏的瓦片不足。")
            break
            
    # 放置出口
    exit_placed = False
    exit_options = [p for p in available_tiles if p not in treasure_coords]
    
    if exit_options:
        ex, ey = available_tiles.pop(0)
        current_maze[ey][ex] = 3
        exit_placed = True
    else:
        print("警告: 未能在迷宫中找到合适的出口位置。")
        for r_check in range(ROWS):
            for c_check in range(COLS):
                if current_maze[r_check][c_check] == 0:
                    current_maze[r_check][c_check] = 3
                    exit_placed = True
                    break
            if exit_placed: break

    return current_maze, placed_treasures


def reset_game_variables():
    """
    重置所有游戏状态变量，准备新的一轮游戏或新地图。
    """
    global bombs, explosions, got_treasures, guard_path_index, last_guard_bomb_time
    global player_hp, guard_hp
    global player_current_speed_x, player_current_speed_y
    global guard_current_speed_x, guard_current_speed_y
    
    bombs.clear()
    explosions.clear()
    got_treasures = 0
    guard_path_index = 0
    last_guard_bomb_time = 0
    player_hp = PLAYER_MAX_HP
    guard_hp = GUARD_MAX_HP
    player_current_speed_x = 0
    player_current_speed_y = 0
    guard_current_speed_x = 0
    guard_current_speed_y = 0


# --- 6. 游戏主循环 (Main Game Loop) ---

def run_game_loop(screen, clock): # 传入 clock
    """
    处理一轮游戏的核心逻辑，包括事件处理、状态更新和绘图。
    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象。
        clock (pygame.time.Clock): Pygame 时钟对象。
    Returns:
        str: 游戏结果 ("won", "lost", "quit")。
    """
    global got_treasures, maze, total_treasures, player_hp, guard_hp
    global player_current_speed_x, player_current_speed_y

    # 在每次新的游戏循环开始时重新生成地图并放置元素
    current_maze, new_total_treasures = place_game_elements(generate_maze(ROWS, COLS))
    maze[:] = current_maze
    total_treasures = new_total_treasures
    reset_game_variables()

    play_random_bgm()

    game_active = True
    while game_active:
        if not pygame.mixer.music.get_busy():
            play_random_bgm()

        # --- 绘图阶段 ---
        screen.fill(COLOR_BLACK)
        draw_maze(screen)
        draw_guard(screen)
        draw_player(screen)
        draw_bombs(screen)
        draw_explosions(screen)

        # 绘制血量条
        draw_health_bar(screen, player_hp, PLAYER_MAX_HP, 5, 5, 100, 15, COLOR_HEALTH_GREEN, COLOR_HEALTH_RED)
        draw_health_bar(screen, guard_hp, GUARD_MAX_HP, WIDTH - 105, 5, 100, 15, COLOR_HEALTH_GREEN, COLOR_HEALTH_RED)

        current_time = time.time()

        # --- 炸弹和爆炸逻辑更新 ---
        hit_player_this_frame = False
        hit_guard_this_frame = False

        for bomb_info in bombs[:]:
            bomb_x, bomb_y, bomb_placed_time, bomb_owner = bomb_info
            if current_time - bomb_placed_time >= 2:
                explosion_area = explode(bomb_x, bomb_y)
                
                for pos in explosion_area:
                    explosions.append((pos[0], pos[1], current_time))
                    
                    # 检查玩家是否在爆炸区域
                    # 玩家位置为瓦片坐标，需要转换为像素坐标进行精确碰撞检测
                    player_rect = pygame.Rect(player_pixel_pos[0], player_pixel_pos[1], TILE_SIZE, TILE_SIZE)
                    explosion_tile_rect = pygame.Rect(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    if player_rect.colliderect(explosion_tile_rect) and not hit_player_this_frame:
                        player_hp -= 1
                        hit_player_this_frame = True

                    # 检查守卫是否在爆炸区域
                    guard_rect = pygame.Rect(guard_pixel_pos[0], guard_pixel_pos[1], TILE_SIZE, TILE_SIZE)
                    if guard_rect.colliderect(explosion_tile_rect) and not hit_guard_this_frame:
                        guard_hp -= 1
                        hit_guard_this_frame = True

                bombs.remove(bomb_info)

        for explosion_info in explosions[:]:
            exp_x, exp_y, explosion_start_time = explosion_info
            if current_time - explosion_start_time >= 1:
                explosions.remove(explosion_info)

        # --- 碰撞检测与胜负判断 ---
        if player_hp <= 0:
            show_end_screen(screen, "你被炸弹炸死了！游戏失败", COLOR_RED)
            return "lost"
            
        if guard_hp <= 0:
            show_end_screen(screen, "守卫被炸晕，胜利！", COLOR_GREEN)
            return "won"

        if check_guard_sight():
            show_end_screen(screen, "你被发现了！游戏失败", COLOR_RED)
            return "lost"

        # --- 事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 玩家放置炸弹的位置基于其当前的瓦片坐标
                    player_current_tile_x, player_current_tile_y = player_tile_pos
                    if maze[player_current_tile_y][player_current_tile_x] in [0, 4]:
                        bombs.append((player_current_tile_x, player_current_tile_y, current_time, 'player'))

        # --- 玩家移动输入处理 (按键状态检测，允许持续移动) ---
        keys_pressed = pygame.key.get_pressed()
        player_current_speed_x = 0
        player_current_speed_y = 0

        if keys_pressed[pygame.K_UP]: player_current_speed_y = -PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN]: player_current_speed_y = PLAYER_SPEED
        if keys_pressed[pygame.K_LEFT]: player_current_speed_x = -PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]: player_current_speed_x = PLAYER_SPEED

        # 如果同时按了水平和垂直方向，将速度对角线移动（可以根据需要调整，例如限制为单一方向）
        if player_current_speed_x != 0 and player_current_speed_y != 0:
            # 例如，只允许单一方向移动
            if abs(player_current_speed_x) > abs(player_current_speed_y):
                player_current_speed_y = 0
            else:
                player_current_speed_x = 0

        move_player_smooth() # 调用平滑移动函数

        # --- 游戏状态更新 ---
        # 检查玩家是否收集到宝藏 (基于瓦片位置)
        if maze[player_tile_pos[1]][player_tile_pos[0]] == 2:
            got_treasures += 1
            maze[player_tile_pos[1]][player_tile_pos[0]] = 0

        # 检查玩家是否到达出口并成功逃脱 (基于瓦片位置)
        if maze[player_tile_pos[1]][player_tile_pos[0]] == 3:
            if got_treasures == total_treasures:
                show_end_screen(screen, "你成功逃脱了！胜利！", COLOR_GREEN)
                return "won"

        move_guard_smooth() # 守卫平滑移动

        # --- 屏幕更新与帧率控制 ---
        pygame.display.flip()
        clock.tick(60) # 提高帧率到 60 FPS，让平滑移动更流畅

    return "quit"


# --- 7. 程序入口点 (Entry Point) ---

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("小偷游戏 - 炸弹迷宫")
    clock = pygame.time.Clock() # 时钟对象在外部创建，每次循环传入

    load_images() # 在游戏主循环前加载所有图片

    # 游戏主循环，处理多关卡逻辑
    while True:
        game_result = run_game_loop(screen, clock) # 传入 screen 和 clock

        if game_result == "won":
            print("恭喜！进入下一关！")
            pass
        elif game_result == "lost":
            print("游戏失败。尝试重玩本关卡。")
            pass
        elif game_result == "quit":
            print("游戏退出。")
            break

    pygame.quit()
    sys.exit()
