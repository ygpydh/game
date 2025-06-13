# game.py - 炸弹迷宫小偷游戏主程序

import pygame # 导入 Pygame 库，用于游戏开发
import sys    # 导入 sys 库，用于程序退出
import time   # 导入 time 库，用于处理时间相关的逻辑，如炸弹计时

# --- 1. 配置部分 (Configuration) ---
# 定义游戏窗口的宽度和高度
WIDTH, HEIGHT = 640, 320 # 屏幕宽度 640 像素，高度 320 像素

# 瓦片（Tile）的大小，所有游戏元素都基于这个尺寸进行绘制
TILE_SIZE = 32 # 每个瓦片 32x32 像素

# 根据屏幕尺寸和瓦片大小计算迷宫的行数和列数
# 注意：这里 HEIGHT 调整为 320 是为了与下方 maze 数组的实际行数 (10行) 匹配
ROWS = HEIGHT // TILE_SIZE  # 迷宫的行数：320 / 32 = 10
COLS = WIDTH // TILE_SIZE   # 迷宫的列数：640 / 32 = 20

# 颜色定义 (RGB 值)
# 定义游戏中使用的各种颜色，方便统一管理和修改
BLACK = (0, 0, 0)         # 黑色
WHITE = (255, 255, 255)   # 白色
GRAY = (100, 100, 100)    # 灰色 (用于墙壁)
GREEN = (0, 255, 0)       # 绿色 (用于玩家)
RED = (255, 0, 0)         # 红色 (用于守卫)
BLUE = (0, 100, 255)      # 蓝色 (用于出口)
YELLOW = (255, 255, 0)    # 黄色 (用于宝藏和爆炸)
LIGHT_RED = (255, 200, 200) # 浅红色 (用于守卫的视线范围)
ORANGE = (255, 165, 0)    # 橙色 (用于炸弹)

# 迷宫地图定义
# 这是一个二维列表，代表游戏世界中的迷宫布局
# 每个数字代表不同类型的瓦片：
#   1: 墙壁 (不可通行，不可被爆炸摧毁)
#   0: 可通行路径 (玩家、守卫、爆炸可在此处)
#   2: 宝藏 (玩家需要收集，收集后变为 0)
#   3: 出口 (玩家收集所有宝藏后可从此逃脱)
#   9: 特殊标记 (在此迷宫中，'9' 与 '0' 行为相同，但建议为其赋予明确意义或改为 '0' 以避免混淆)
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,2,0,0,3,1],
    [1,0,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,0,0,1],
    [1,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,2,0,1,0,1],
    [1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,9,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1], # 此处的 '9' 在当前游戏逻辑中被视为普通路径
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# --- 2. 迷宫绘制功能 (Maze Drawing) ---
def draw_maze(screen):
    """
    在 Pygame 屏幕上绘制迷宫的各个瓦片。
    根据 'maze' 列表中瓦片的值，绘制对应颜色的方块。
    未明确处理的瓦片类型（如 '0' 和 '9'）将显示为屏幕背景色（黑色）。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象，所有绘图操作都将在此进行。
    """
    for y in range(ROWS): # 遍历迷宫的每一行 (从 0 到 ROWS-1)
        for x in range(COLS): # 遍历迷宫的每一列 (从 0 到 COLS-1)
            # 根据当前瓦片的逻辑坐标 (x, y) 和瓦片大小 (TILE_SIZE)
            # 计算其在屏幕上的像素位置和尺寸，创建 Pygame 矩形对象
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = maze[y][x] # 获取当前瓦片的类型值

            if tile == 1: # 如果瓦片是墙壁
                pygame.draw.rect(screen, GRAY, rect) # 绘制灰色矩形
            elif tile == 2: # 如果瓦片是宝藏
                pygame.draw.rect(screen, YELLOW, rect) # 绘制黄色矩形
            elif tile == 3: # 如果瓦片是出口
                pygame.draw.rect(screen, BLUE, rect) # 绘制蓝色矩形
            # 对于 tile == 0 (可通行路径) 或其他未定义的 tile 值 (如 9)，不进行额外绘制，
            # 它们会默认显示为在主循环中设置的屏幕背景色 (BLACK)。


# --- 3. 玩家功能 (Player) ---
# 玩家的当前逻辑位置 [x, y]
player_pos = [1, 1]

def draw_player(screen):
    """
    在屏幕上绘制玩家角色。
    玩家被绘制为一个绿色的方块。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象。
    """
    x, y = player_pos # 获取玩家当前位置的 x 和 y 坐标
    # 根据玩家的逻辑坐标和瓦片大小计算绘制矩形的位置和尺寸
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, GREEN, rect) # 使用绿色绘制玩家方块

def move_player(dx, dy):
    """
    尝试将玩家移动到新的位置。
    移动前会检查新位置是否在迷宫边界内，并且不是墙壁。

    Args:
        dx (int): x 轴方向的移动量 (-1 表示左，1 表示右，0 表示不变)。
        dy (int): y 轴方向的移动量 (-1 表示上，1 表示下，0 表示不变)。
    """
    nx, ny = player_pos[0] + dx, player_pos[1] + dy # 计算玩家的潜在新位置

    # 检查新位置是否合法：
    # 1. 0 <= nx < COLS：新 x 坐标必须在迷宫的列范围内
    # 2. 0 <= ny < ROWS：新 y 坐标必须在迷宫的行范围内
    # 3. maze[ny][nx] != 1：新位置不能是墙壁
    if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1:
        player_pos[0], player_pos[1] = nx, ny # 如果合法，更新玩家的当前位置


# --- 4. 守卫功能 (Guard) ---
# 守卫的当前逻辑位置 [x, y]
guard_pos = [1, 8]
# 守卫的巡逻路径点列表
guard_path = [(1, 8), (5, 8)] # 守卫会在 (1,8) 和 (5,8) 之间往返移动
# 当前守卫巡逻路径点在 guard_path 列表中的索引
guard_index = 0

def draw_guard(screen):
    """
    在屏幕上绘制守卫及其下方的视线范围。
    守卫本体为红色方块，其视线范围为浅红色方块。
    守卫的视线固定向下延伸，最远 3 格，会被墙壁阻挡。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象。
    """
    x, y = guard_pos # 获取守卫当前位置的 x 和 y 坐标
    # 绘制守卫本体
    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, RED, rect) # 绘制红色矩形代表守卫

    # 绘制守卫向下的视线范围 (最多 3 格)
    for i in range(1, 4): # 视线延伸 1 到 3 格远的瓦片
        vy = y + i # 计算视线范围内瓦片的 y 坐标
        # 检查视线瓦片是否超出迷宫底部边界，或者是否遇到墙壁 (maze 值为 1)
        if vy >= ROWS or maze[vy][x] == 1:
            break # 如果超出边界或遇到墙壁，此方向的视线停止延伸
        # 绘制视线范围内的瓦片
        vrect = pygame.Rect(x * TILE_SIZE, vy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, LIGHT_RED, vrect) # 绘制浅红色矩形

def check_guard_sight():
    """
    检查玩家是否在守卫的视线范围内。
    此函数只检测玩家是否在守卫的正下方，且距离不超过 3 格，并且之间没有墙壁阻挡。

    Returns:
        bool: 如果玩家在守卫视线范围内则返回 True，否则返回 False。
    """
    gx, gy = guard_pos # 守卫的当前位置
    px, py = player_pos # 玩家的当前位置

    # 检查玩家是否满足以下条件：
    # 1. px == gx：玩家与守卫在同一列 (正下方)
    # 2. py > gy：玩家在守卫下方
    # 3. py - gy <= 3：玩家与守卫的垂直距离不超过 3 格
    if px == gx and py > gy and py - gy <= 3:
        # 进一步检查守卫和玩家之间是否有墙壁阻挡视线
        # 遍历从守卫下方一格到玩家上方一格的所有瓦片
        for y_check in range(gy + 1, py):
            if maze[y_check][gx] == 1: # 如果路径中有墙壁
                return False # 视线被墙壁阻挡，玩家未被发现
        return True # 玩家在视线范围内且无阻挡，被发现
    return False # 玩家不在守卫的视线范围内


def move_guard():
    """
    根据预设的 `guard_path` 路径点移动守卫。
    守卫每次向其当前目标点移动一个瓦片。当到达当前目标点后，它会切换到路径中的下一个目标点。
    """
    global guard_index, guard_pos # 声明为全局变量以便在函数内部修改

    gx, gy = guard_pos # 守卫的当前 (x, y) 位置
    tx, ty = guard_path[guard_index] # 守卫的当前目标 (x, y) 位置

    # 根据当前位置和目标位置的差异，更新守卫的坐标
    if gx < tx: # 如果守卫在目标点的左边，则向右移动
        guard_pos[0] += 1
    elif gx > tx: # 如果守卫在目标点的右边，则向左移动
        guard_pos[0] -= 1
    elif gy < ty: # 如果守卫在目标点的上方，则向下移动
        guard_pos[1] += 1
    elif gy > ty: # 如果守卫在目标点的下方，则向上移动
        guard_pos[1] -= 1
    else:
        # 如果守卫已经到达了当前的目标点
        # 切换到路径中的下一个目标点，使用模运算符实现路径循环
        guard_index = (guard_index + 1) % len(guard_path)


# --- 5. 炸弹和爆炸功能 (Bomb and Explosion) ---
# 存储当前激活的炸弹列表。每个炸弹项包含 (x坐标, y坐标, 放置时间戳)。
bombs = []
# 存储当前激活的爆炸区域列表。每个爆炸区域项包含 (x坐标, y坐标, 爆炸开始时间戳)。
explosions = []

def draw_bombs(screen):
    """
    在屏幕上绘制所有激活的炸弹。
    炸弹被绘制为橙色方块。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象。
    """
    for bx, by, _ in bombs: # 遍历所有炸弹，'_' 表示我们只关心位置，忽略时间戳
        # 根据炸弹的逻辑坐标和瓦片尺寸计算绘制矩形的位置和尺寸
        rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, ORANGE, rect) # 绘制橙色矩形

def draw_explosions(screen):
    """
    在屏幕上绘制所有激活的爆炸区域。
    爆炸区域被绘制为黄色方块。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象。
    """
    for ex, ey, _ in explosions: # 遍历所有爆炸区域，'_' 表示我们只关心位置，忽略时间戳
        # 根据爆炸区域的逻辑坐标和瓦片尺寸计算绘制矩形的位置和尺寸
        rect = pygame.Rect(ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, YELLOW, rect) # 绘制黄色矩形

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
    positions = [(x, y)] # 爆炸中心本身也受影响，首先将其添加到列表中
    
    # 定义四个基本方向的偏移量 (左, 右, 上, 下)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        # 每个方向的爆炸延伸范围为 1 格和 2 格 (即 i 取 1 和 2)
        for i in range(1, 3):
            nx, ny = x + dx * i, y + dy * i # 计算潜在的爆炸影响位置

            # 检查潜在位置是否在迷宫边界内
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                # 如果当前位置是墙壁 (maze 值为 1)，则此方向的爆炸被阻挡，不再向外延伸
                if maze[ny][nx] == 1:
                    break # 停止此方向的循环
                positions.append((nx, ny)) # 将受影响的位置添加到列表中
    return positions


# --- 6. 主游戏逻辑 (Main Game Logic) ---
# 玩家已收集的宝藏数量
got_treasures = 0
# 迷宫中所有宝藏的总数，通过遍历 maze 列表统计所有值为 '2' 的瓦片数量
total_treasures = sum(row.count(2) for row in maze)

def show_end_screen(screen, message, color):
    """
    显示游戏结束画面（胜利或失败信息），并等待用户按键或关闭窗口以继续。

    Args:
        screen (pygame.Surface): Pygame 的屏幕 Surface 对象。
        message (str): 要在屏幕上显示的消息文本。
        color (tuple): 消息文本的颜色 (RGB 值)。
    """
    font = pygame.font.SysFont("Arial", 48) # 设置字体为 Arial，大小 48
    text = font.render(message, True, color) # 渲染文本，True 表示抗锯齿
    # 获取文本矩形，并将其中心设置在屏幕中央
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect) # 将渲染好的文本绘制到屏幕上
    pygame.display.flip() # 更新整个屏幕显示，使文本可见
    pygame.time.wait(1500) # 暂停游戏 1.5 秒，让玩家有时间阅读信息

    waiting = True
    while waiting: # 进入一个循环，等待用户输入或关闭窗口
        for event in pygame.event.get():
            # 如果检测到键盘按下事件或用户点击了关闭窗口按钮
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting = False # 退出等待循环

def run():
    """
    游戏的主运行函数。
    负责初始化 Pygame、设置游戏窗口、处理所有游戏事件、更新游戏状态以及绘制所有游戏元素。
    """
    global got_treasures # 声明 got_treasures 为全局变量，因为函数内部会修改它

    pygame.init() # 初始化所有导入的 Pygame 模块
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # 创建游戏窗口
    pygame.display.set_caption("小偷游戏 - 炸弹迷宫") # 设置窗口标题
    clock = pygame.time.Clock() # 创建 Pygame 时钟对象，用于控制游戏帧率

    # 游戏主循环
    while True:
        screen.fill(BLACK) # 每次循环开始时，用黑色填充整个屏幕，清除上一帧的绘图

        # --- 绘制所有游戏元素 ---
        draw_maze(screen) # 绘制迷宫地图
        draw_guard(screen) # 绘制守卫及其视线
        draw_player(screen) # 绘制玩家
        draw_bombs(screen) # 绘制所有激活的炸弹
        draw_explosions(screen) # 绘制所有激活的爆炸区域

        now = time.time() # 获取当前系统时间戳，用于计时

        # --- 炸弹和爆炸管理 ---
        # 遍历 bombs 列表的副本 ([:])，这样在迭代时可以安全地移除元素
        for bx, by, t in bombs[:]:
            if now - t >= 2: # 如果炸弹放置时间超过 2 秒 (即爆炸计时结束)
                area = explode(bx, by) # 调用 explode 函数计算爆炸影响区域
                for pos in area: # 遍历爆炸区域中的每个瓦片坐标
                    explosions.append((pos[0], pos[1], now)) # 将这些瓦片添加到爆炸列表中，并记录当前时间
                bombs.remove((bx, by, t)) # 从激活炸弹列表中移除已爆炸的炸弹

        # 遍历 explosions 列表的副本，管理爆炸效果的持续时间
        for ex, ey, t in explosions[:]:
            if now - t >= 1: # 如果爆炸效果持续时间超过 1 秒
                explosions.remove((ex, ey, t)) # 移除此爆炸效果

        # --- 胜利条件：守卫被炸晕 ---
        for ex, ey, _ in explosions: # 遍历当前所有爆炸区域
            if (guard_pos[0], guard_pos[1]) == (ex, ey): # 如果守卫的位置在某个爆炸区域内
                show_end_screen(screen, "守卫被炸晕，胜利！", (0, 255, 0)) # 显示胜利信息 (绿色文本)
                pygame.quit() # 退出 Pygame 模块
                return # 退出 run 函数，结束游戏

        # --- 失败条件：玩家被守卫发现 ---
        if check_guard_sight(): # 调用守卫视线检测函数
            show_end_screen(screen, "你被发现了！游戏失败", (255, 0, 0)) # 显示失败信息 (红色文本)
            break # 退出游戏主循环

        # --- 事件处理 ---
        for event in pygame.event.get(): # 遍历所有 Pygame 事件
            if event.type == pygame.QUIT: # 如果用户点击了窗口关闭按钮
                pygame.quit() # 退出 Pygame 模块
                sys.exit() # 彻底退出 Python 程序

            # 处理键盘按键事件
            if event.type == pygame.KEYDOWN: # 如果是键盘按键按下事件
                if event.key == pygame.K_SPACE: # 如果按下的键是空格键
                    x, y = player_pos # 获取玩家当前位置
                    if maze[y][x] == 0: # 只有当玩家位于可通行路径 (0) 时才能放置炸弹
                        bombs.append((x, y, now)) # 在玩家当前位置放置一个新炸弹，并记录时间

        # --- 玩家移动处理 (持续按键移动) ---
        keys = pygame.key.get_pressed() # 获取所有键盘按键的当前按下状态
        dx = dy = 0 # 初始化移动量
        if keys[pygame.K_UP]: dy = -1    # 如果按下上箭头，y 轴向上移动
        if keys[pygame.K_DOWN]: dy = 1   # 如果按下下箭头，y 轴向下移动
        if keys[pygame.K_LEFT]: dx = -1  # 如果按下左箭头，x 轴向左移动
        if keys[pygame.K_RIGHT]: dx = 1  # 如果按下右箭头，x 轴向右移动

        if dx or dy: # 如果玩家有任何方向的移动输入
            move_player(dx, dy) # 调用移动玩家函数

        # --- 收集宝藏逻辑 ---
        x, y = player_pos # 获取玩家当前位置
        if maze[y][x] == 2: # 如果玩家当前站在宝藏 (2) 上
            got_treasures += 1 # 增加已收集宝藏的数量
            maze[y][x] = 0 # 将该宝藏从地图上移除 (将其变为可通行区域 0)

        # --- 胜利条件：成功逃脱 ---
        if maze[y][x] == 3: # 如果玩家当前站在出口 (3) 上
            if got_treasures == total_treasures: # 并且已经收集了所有宝藏
                show_end_screen(screen, "你成功逃脱了！胜利！", (0, 255, 0)) # 显示胜利信息
                break # 退出游戏主循环

        # --- 守卫移动 ---
        move_guard() # 调用守卫移动函数，更新守卫位置

        # --- 游戏帧率控制与屏幕更新 ---
        pygame.display.flip() # 更新整个屏幕的内容，显示所有绘制的元素
        clock.tick(10) # 控制游戏帧率为 10 帧每秒 (FPS)，防止游戏运行过快

    pygame.quit() # 当游戏主循环结束后 (游戏结束)，退出 Pygame 模块

# --- 程序入口点 ---
if __name__ == "__main__":
    run() # 如果此脚本作为主程序运行，则调用 run() 函数启动游戏
