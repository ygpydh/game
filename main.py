import pygame
import sys
import time

# --- 配置部分 (原 config.py 内容) ---
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
ROWS = HEIGHT // TILE_SIZE  # 计算迷宫的行数
COLS = WIDTH // TILE_SIZE  # 计算迷宫的列数

# 颜色定义 (RGB 值)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
LIGHT_RED = (255, 200, 200)
ORANGE = (255, 165, 0)

# 迷宫地图定义
# 1: 墙壁 (不可通行)
# 0: 可通行路径
# 2: 宝藏 (需要收集)
# 3: 出口 (收集所有宝藏后可通行)
# 注意：在迷宫地图中发现一个'9'，如果它没有特殊的游戏逻辑，建议将其改为'0'或其他有明确含义的值。
# 当前游戏中'9'并没有被特殊处理，视为普通可通行区域可能导致意外行为。
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,2,0,0,3,1],
    [1,0,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,2,0,1,0,1],
    [1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,9,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1], # 建议将此处的'9'改为'0'，除非其有明确的游戏意义
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# --- 迷宫绘制部分 (原 maze.py 内容) ---
def draw_maze(screen):
    """
    在屏幕上绘制迷宫的各个瓦片。
    根据迷宫地图中瓦片的值绘制不同颜色：
    - 1: 墙壁 (灰色)
    - 2: 宝藏 (黄色)
    - 3: 出口 (蓝色)
    未处理的瓦片类型 (如 0: 可通行路径，以及 config 中存在的 9) 将保持屏幕的默认背景色。
    """
    for y in range(ROWS): # 遍历迷宫的每一行
        for x in range(COLS): # 遍历迷宫的每一列
            # 根据瓦片的逻辑坐标和尺寸创建 Pygame 矩形对象
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = maze[y][x] # 获取当前瓦片的类型

            if tile == 1: # 如果是墙壁
                pygame.draw.rect(screen, GRAY, rect) # 绘制灰色矩形
            elif tile == 2: # 如果是宝藏
                pygame.draw.rect(screen, YELLOW, rect) # 绘制黄色矩形
            elif tile == 3: # 如果是出口
                pygame.draw.rect(screen, BLUE, rect) # 绘制蓝色矩形
            # 对于 tile == 0 (可通行路径) 或其他未定义的 tile 值 (如 9)，不进行绘制，
            # 它们会显示为背景色 (main.py 中定义的黑色)。

# --- 玩家部分 (原 player.py 内容) ---
player_pos = [1, 1]

def draw_player(screen):
    """
    在屏幕上绘制玩家。
    """
    x, y = player_pos
    # 根据玩家的逻辑坐标和瓦片大小计算绘制矩形的位置和尺寸
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, GREEN, rect) # 使用绿色绘制玩家

def move_player(dx, dy): # 移除了 maze, COLS, ROWS 参数，因为它们现在是全局可访问的
    """
    尝试移动玩家到新的位置。
    Args:
        dx (int): x 轴方向的移动量 (-1, 0, 或 1)。
        dy (int): y 轴方向的移动量 (-1, 0, 或 1)。
    """
    nx, ny = player_pos[0] + dx, player_pos[1] + dy # 计算新的潜在位置

    # 检查新位置是否在迷宫边界内，并且不是墙壁 (maze 值为 1)
    if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
        player_pos[0], player_pos[1] = nx, ny # 更新玩家位置

# --- 守卫部分 (原 guard.py 内容) ---
guard_pos = [1, 8]
guard_path = [(1, 8), (5, 8)]
guard_index = 0

def draw_guard(screen):
    """
    在屏幕上绘制守卫及其下方的视线范围。
    守卫本体为红色，视线范围为浅红色。
    """
    x, y = guard_pos
    # 绘制守卫本体
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, RED, rect) # 绘制红色矩形

    # 绘制守卫向下的视线范围 (最多 3 格)
    for i in range(1, 4): # 视线延伸 1 到 3 格
        vy = y + i # 计算视线瓦片的 y 坐标
        # 如果超出迷宫底部边界或遇到墙壁，则停止绘制视线
        if vy >= ROWS or maze[vy][x] == 1:
            break
        # 绘制视线瓦片
        vrect = pygame.Rect(x * TILE_SIZE, vy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, LIGHT_RED, vrect) # 绘制浅红色矩形

def check_guard_sight(): # 移除了 player_pos, maze 参数，因为它们现在是全局可访问的
    """
    检查玩家是否在守卫的视线范围内。
    当前实现只检查玩家是否在守卫正下方，且在3格视线范围内，且中间没有墙壁阻挡。
    Returns:
        bool: 如果玩家在守卫视线范围内则返回 True，否则返回 False。
    """
    gx, gy = guard_pos # 守卫的当前位置
    px, py = player_pos # 玩家的当前位置

    # 检查玩家是否在守卫正下方 (x 坐标相同) 且在 3 格以内 (y 坐标在 gy+1 到 gy+3 之间)
    if px == gx and py > gy and py - gy <= 3:
        # 检查守卫和玩家之间是否有墙壁阻挡
        for y_check in range(gy + 1, py): # 避免变量名冲突，改为 y_check
            if maze[y_check][gx] == 1: # 如果路径中有墙壁
                return False # 视线被阻挡
        return True # 玩家在视线范围内且无阻挡
    return False # 玩家不在视线范围内

def move_guard():
    """
    根据预设的路径点移动守卫。
    守卫每次向目标点移动一个瓦片。到达目标点后，切换到路径中的下一个目标点。
    """
    global guard_index, guard_pos # 声明全局变量以便修改

    gx, gy = guard_pos # 守卫当前位置
    tx, ty = guard_path[guard_index] # 守卫目标位置

    # 逐步向目标点移动
    if gx < tx:
        guard_pos[0] += 1
    elif gx > tx:
        guard_pos[0] -= 1
    elif gy < ty:
        guard_pos[1] += 1
    elif gy > ty:
        guard_pos[1] -= 1
    else:
        # 如果守卫已经到达当前目标点，则切换到下一个目标点
        guard_index = (guard_index + 1) % len(guard_path)

# --- 炸弹部分 (原 bomb.py 内容) ---
# 存储当前激活的炸弹列表。每个炸弹项包含 (x, y, 放置时间戳)
bombs = []
# 存储当前激活的爆炸列表。每个爆炸区域项包含 (x, y, 爆炸开始时间戳)
explosions = []

def draw_bombs(screen):
    """
    在屏幕上绘制所有激活的炸弹。
    炸弹绘制为橙色方块。
    """
    for bx, by, _ in bombs: # 遍历所有炸弹，_ 表示忽略时间戳
        # 根据炸弹的逻辑坐标和瓦片尺寸计算绘制矩形的位置和尺寸
        rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, ORANGE, rect) # 绘制橙色矩形

def draw_explosions(screen):
    """
    在屏幕上绘制所有激活的爆炸区域。
    爆炸区域绘制为黄色方块。
    """
    for ex, ey, _ in explosions: # 遍历所有爆炸区域，_ 表示忽略时间戳
        # 根据爆炸区域的逻辑坐标和瓦片尺寸计算绘制矩形的位置和尺寸
        rect = pygame.Rect(ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, YELLOW, rect) # 绘制黄色矩形

def explode(x, y): # 移除了 maze 参数，因为它是全局可访问的
    """
    计算炸弹爆炸的受影响区域。
    爆炸以 (x, y) 为中心，向上下左右四个方向各延伸2格，但会被墙壁阻挡。
    Args:
        x (int): 炸弹爆炸中心的 x 坐标。
        y (int): 炸弹爆炸中心的 y 坐标。
    Returns:
        list: 包含所有受爆炸影响的瓦片坐标 (nx, ny) 的列表。
    """
    positions = [(x, y)] # 爆炸中心本身也受影响
    # 定义四个方向的偏移量
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        # 每个方向延伸 2 格 (i 为 1 或 2)
        for i in range(1, 3):
            nx, ny = x + dx * i, y + dy * i # 计算新位置
            # 检查新位置是否在迷宫边界内
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                # 如果遇到墙壁 (maze 值为 1)，则此方向的爆炸停止延伸
                if maze[ny][nx] == 1:
                    break
                positions.append((nx, ny)) # 将受影响位置添加到列表中
    return positions

# --- 主程序部分 (原 main.py 内容) ---
got_treasures = 0
total_treasures = sum(row.count(2) for row in maze)

def show_end_screen(screen, message, color):
    """
    显示游戏结束画面 (胜利或失败信息)，并等待用户输入或退出。
    Args:
        screen (pygame.Surface): Pygame 屏幕对象。
        message (str): 要显示的消息文本。
        color (tuple): 消息文本的颜色 (RGB)。
    """
    font = pygame.font.SysFont("Arial", 48) # 设置字体和大小
    text = font.render(message, True, color) # 渲染文本
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2)) # 获取文本矩形并居中
    screen.blit(text, rect) # 将文本绘制到屏幕
    pygame.display.flip() # 更新屏幕显示
    pygame.time.wait(1500) # 暂停 1.5 秒

    waiting = True
    while waiting: # 循环等待用户按键或关闭窗口
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting = False # 如果按键或关闭窗口，则退出等待

def run():
    """
    游戏主循环。
    初始化 Pygame，处理游戏事件，更新游戏状态，并绘制所有元素。
    """
    global got_treasures # 声明全局变量以便在函数内部修改

    pygame.init() # 初始化 Pygame 模块
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # 设置屏幕尺寸
    pygame.display.set_caption("小偷游戏 - 炸弹迷宫") # 设置窗口标题
    clock = pygame.time.Clock() # 创建时钟对象，用于控制游戏帧率

    while True: # 游戏主循环
        screen.fill(BLACK) # 用黑色填充屏幕背景

        # 绘制所有游戏元素
        draw_maze(screen) # 绘制迷宫
        draw_guard(screen) # 绘制守卫及其视线
        draw_player(screen) # 绘制玩家
        draw_bombs(screen) # 绘制所有激活的炸弹
        draw_explosions(screen) # 绘制所有激活的爆炸区域

        now = time.time() # 获取当前时间戳

        # 处理炸弹计时和爆炸
        for bx, by, t in bombs[:]: # 遍历炸弹列表的副本，允许在循环中修改原列表
            if now - t >= 2: # 如果炸弹放置时间超过 2 秒
                area = explode(bx, by) # 计算爆炸影响区域 (不再需要传入 maze)
                for pos in area:
                    explosions.append((pos[0], pos[1], now)) # 将爆炸区域添加到爆炸列表中，记录当前时间
                bombs.remove((bx, by, t)) # 移除已爆炸的炸弹

        # 处理爆炸持续时间
        for ex, ey, t in explosions[:]: # 遍历爆炸列表的副本
            if now - t >= 1: # 如果爆炸持续时间超过 1 秒
                explosions.remove((ex, ey, t)) # 移除爆炸效果

        # 检查守卫是否被炸晕 (胜利条件之一)
        for ex, ey, _ in explosions: # 遍历所有爆炸区域
            if (guard_pos[0], guard_pos[1]) == (ex, ey): # 如果守卫位置在爆炸区域内
                show_end_screen(screen, "守卫被炸晕，胜利！", (0, 255, 0)) # 显示胜利信息
                pygame.quit() # 退出 Pygame
                return # 退出游戏主循环和 run 函数

        # 检查玩家是否被守卫发现 (失败条件)
        if check_guard_sight(): # 调用守卫视线检测函数 (不再需要传入 player_pos, maze)
            show_end_screen(screen, "你被发现了！游戏失败", (255, 0, 0)) # 显示失败信息
            break # 退出游戏主循环

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 如果用户点击关闭按钮
                pygame.quit() # 退出 Pygame
                sys.exit() # 退出程序

            # 放置炸弹的事件检查
            if event.type == pygame.KEYDOWN: # 检查是否是键盘按下事件
                if event.key == pygame.K_SPACE: # 如果按下了空格键
                    x, y = player_pos # 获取玩家当前位置
                    if maze[y][x] == 0: # 只有在可通行区域 (0) 才能放置炸弹
                        bombs.append((x, y, now)) # 添加新炸弹，记录当前时间

        # 处理玩家移动 (使用按键状态检测，允许持续移动)
        keys = pygame.key.get_pressed() # 获取所有按键的当前状态
        dx = dy = 0
        if keys[pygame.K_UP]: dy = -1 # 向上移动
        if keys[pygame.K_DOWN]: dy = 1 # 向下移动
        if keys[pygame.K_LEFT]: dx = -1 # 向左移动
        if keys[pygame.K_RIGHT]: dx = 1 # 向右移动

        if dx or dy: # 如果有任何方向的移动输入
            move_player(dx, dy) # 移动玩家 (不再需要传入 maze, COLS, ROWS)

        # 检查玩家是否收集到宝藏
        x, y = player_pos # 获取玩家当前位置
        if maze[y][x] == 2: # 如果玩家在宝藏位置
            got_treasures += 1 # 收集宝藏数量增加
            maze[y][x] = 0 # 将宝藏从地图上移除 (变为可通行区域)

        # 检查玩家是否到达出口并成功逃脱
        if maze[y][x] == 3: # 如果玩家在出口位置
            if got_treasures == total_treasures: # 并且收集了所有宝藏
                show_end_screen(screen, "你成功逃脱了！胜利！", (0, 255, 0)) # 显示胜利信息
                break # 退出游戏主循环

        move_guard() # 移动守卫
        pygame.display.flip() # 更新整个屏幕显示
        clock.tick(10) # 控制游戏帧率为 10 FPS

    pygame.quit() # 游戏循环结束后退出 Pygame

if __name__ == "__main__":
    run() # 运行游戏
