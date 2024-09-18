import pygame
import random
import os

# 初始化pygame和音频混音器
pygame.init()
pygame.mixer.init()  # 初始化音频模块

# 定义游戏相关属性
TITLE = '白了个白'  # 游戏标题
WIDTH = 700         # 游戏窗口宽度
HEIGHT = 820        # 游戏窗口高度
TIME_LIMIT = 180    # 游戏时间限制

# 设置窗口大小并创建屏幕对象
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

# 自定义游戏常量
T_WIDTH = 68       # 每张牌的宽度
T_HEIGHT = 76      # 每张牌的高度
DOCK = pygame.Rect((107, 648), (T_WIDTH * 7, T_HEIGHT))  # 牌堆的位置

# 加载资源
def load_image(filename):
    return pygame.image.load(os.path.join('../images', filename))

# 加载和调整背景图
background = pygame.transform.scale(load_image('back.png'), (WIDTH, HEIGHT))
mask_image = pygame.transform.scale(load_image('mask.png'), (T_WIDTH, T_HEIGHT))
end_image = pygame.transform.scale(load_image('end.png'), (WIDTH, HEIGHT))
win_image = pygame.transform.scale(load_image('win.png'), (WIDTH, HEIGHT))

# 加载按钮图片
undo_button_image = pygame.transform.scale(load_image('undo.png'), (100, 50))  # 撤销按钮
restart_button_image = pygame.transform.scale(load_image('restart.png'), (100, 50))  # 重新开始按钮

# 定义按钮位置
undo_button_rect = undo_button_image.get_rect(bottomright=(WIDTH , HEIGHT - 150))  # 右下角撤销按钮
restart_button_rect = restart_button_image.get_rect(bottomright=(WIDTH , HEIGHT - 100))  # 右下角重新开始按钮

# 加载背景音乐
pygame.mixer.music.load(os.path.join('../music', 'bgm.mp3'))  # 替换为你音乐文件的路径
pygame.mixer.music.play(-1)  # 无限循环播放背景音乐 (-1 表示循环)

# 上方所有牌
tiles = []
# 牌堆里的牌
docks = []
# 记录最近点击的牌，用于撤销功能
undo_stack = []

# 初始化牌组，12*12张牌随机打乱
# 游戏主循环
def initialize_game():
    global tiles, docks, undo_stack, timer, start_ticks, ts, score
    tiles = []
    docks = []
    undo_stack = []

    ts = list(range(1, 13)) * 12
    random.shuffle(ts)
    n = 0

    for k in range(7):  # 7层
        for i in range(7 - k):
            for j in range(7 - k):
                t = ts[n]
                n += 1
                tile_image = load_image(f'tile{t}.png')
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                pos_x = 120 + (k * 0.5 + j) * tile_image.get_width()
                pos_y = 100 + (k * 0.5 + i) * tile_image.get_height() * 0.9 + offset_y + offset_x
                tile = {
                    'image': tile_image,
                    'pos': (pos_x, pos_y),
                    'tag': t,
                    'layer': k,
                    'status': 1 if k == 6 else 0  # 顶层可点击，其他不可点击
                }
                tiles.append(tile)

    # 剩余4张牌
    for i in range(4):
        t = ts[n]
        n += 1
        tile_image = load_image(f'tile{t}.png')
        tile = {
            'image': tile_image,
            'pos': (210 + i * tile_image.get_width(), 546),
            'tag': t,
            'layer': 0,
            'status': 1
        }
        tiles.append(tile)

    timer = TIME_LIMIT
    start_ticks = pygame.time.get_ticks()
    score = 0

# 初始化倒计时
clock = pygame.time.Clock()

#分数设计
def display_leaderboard(victory):
    # 这里假设排行榜数据存储在一个JSON文件中
    import json

    leaderboard_file = '../leaderboard.json'
    try:
        with open(leaderboard_file, 'r') as file:
            leaderboard = json.load(file)
    except FileNotFoundError:
        leaderboard = []

    # 如果是胜利，添加到排行榜中
    if victory:
        new_entry = {'score': score, 'time': TIME_LIMIT - timer}
        leaderboard.append(new_entry)
        leaderboard.sort(key=lambda x: (-x['score'], x['time']))  # 按分数降序，时间升序
        with open(leaderboard_file, 'w') as file:
            json.dump(leaderboard, file)

    # 绘制排行榜
    font = pygame.font.Font(None, 40)
    y_offset = HEIGHT // 2 - 150
    leaderboard_text = font.render('Leaderboard:', True, (255, 255, 255))
    screen.blit(leaderboard_text, (WIDTH // 2 - 100, y_offset))
    for entry in leaderboard[:10]:  # 显示前10名
        y_offset += 50
        entry_text = font.render(f'Score: {entry["score"]} Time: {entry["time"]}', True, (255, 255, 255))
        screen.blit(entry_text, (WIDTH // 2 - 150, y_offset))

# 绘制函数
def draw():
    screen.blit(background, (0, 0))  # 绘制背景

    # 绘制上方牌组
    for tile in tiles:
        screen.blit(tile['image'], tile['pos'])
        if tile['status'] == 0:
            screen.blit(mask_image, tile['pos'])  # 不可点击的牌绘制遮罩

    # 绘制牌堆
    for i, tile in enumerate(docks):
        pos = (DOCK.x + i * T_WIDTH, DOCK.y)
        screen.blit(tile['image'], pos)

    # 绘制倒计时
    minutes = int(timer // 60)
    seconds = int(timer % 60)
    font = pygame.font.Font(None, 60)
    time_text = font.render(f'{minutes:02d}:{seconds:02d}', True, (255, 0, 0))
    screen.blit(time_text, (10, 10))

    # 绘制分数
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - 200, 10))

    # 绘制按钮
    screen.blit(undo_button_image, undo_button_rect)
    screen.blit(restart_button_image, restart_button_rect)

    # 超过7张或超时，游戏失败
    if len(docks) >= 7 or timer <= 0:
        screen.blit(end_image, (0, 0))
        display_leaderboard(False)
    # 没有剩余牌，游戏胜利
    elif len(tiles) == 0:
        screen.blit(win_image, (0, 0))
        display_leaderboard(True)

# 更新函数
def update():
    global timer
    current_ticks = pygame.time.get_ticks()
    timer = TIME_LIMIT - (current_ticks - start_ticks) // 1000
    if timer <= 0:
        timer = 0
        # 游戏失败处理逻辑
        if len(docks) >= 7:
            display_leaderboard(False)
        elif len(tiles) == 0:
            display_leaderboard(True)


# 鼠标点击响应
def handle_mouse_down(pos):
    global docks, score
    if undo_button_rect.collidepoint(pos):
        handle_undo()
        return
    elif restart_button_rect.collidepoint(pos):
        initialize_game()
        return

    if len(docks) >= 7 or len(tiles) == 0:
        return
    for tile in reversed(tiles):
        rect = tile['image'].get_rect(topleft=tile['pos'])
        if tile['status'] == 1 and rect.collidepoint(pos):
            tile['status'] = 2  # 已点击
            tiles.remove(tile)
            undo_stack.append(tile)  # 将牌放入撤销栈

            # 处理牌堆
            non_matching_tiles = [t for t in docks if t['tag'] != tile['tag']]
            if len(docks) - len(non_matching_tiles) < 2:
                docks.append(tile)
                score += 10  # 每次消除成功的牌获得10分
            else:
                docks = non_matching_tiles

            # 处理牌层级状态
            for down in tiles:
                if down['layer'] == tile['layer'] - 1:
                    rect_down = down['image'].get_rect(topleft=down['pos'])
                    for up in tiles:
                        rect_up = up['image'].get_rect(topleft=up['pos'])
                        if up['layer'] == down['layer'] + 1 and rect_down.colliderect(rect_up):
                            break
                    else:
                        down['status'] = 1
            break

# 撤销功能
def handle_undo():
    global score
    if undo_stack:
        tile = undo_stack.pop()  # 取出最后一次操作的牌
        tiles.append(tile)  # 放回tiles中
        docks.remove(tile)  # 从docks中移除

        # 恢复牌的状态为可点击
        tile['status'] = 1

        # 每次撤销减少10分
        score = max(score - 10, 0)

        # 重新更新牌的层级状态
        for down in tiles:
            if down['layer'] == tile['layer'] - 1:
                rect_down = down['image'].get_rect(topleft=down['pos'])
                for up in tiles:
                    rect_up = up['image'].get_rect(topleft=up['pos'])
                    if up['layer'] == down['layer'] + 1 and rect_down.colliderect(rect_up):
                        break
                else:
                    down['status'] = 1


# 游戏主循环
initialize_game()
running = True
while running:
    screen.fill((0, 0, 0))  # 清屏
    draw()  # 绘制内容
    update()  # 更新游戏状态
    pygame.display.flip()  # 刷新屏幕

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_down(event.pos)

    clock.tick(60)  # 控制帧率

pygame.quit()
#成功版本