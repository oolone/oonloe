import pygame
import random
import os
import json
#程序部分函数由AI生成，且其他函数经过AI的修改
# 初始化pygame和音频混音器
pygame.init()
pygame.mixer.init()  # 初始化音频模块

# 定义游戏相关属性
TITLE = '秀了又秀'  # 游戏标题
WIDTH = 700  # 游戏窗口宽度
HEIGHT = 820  # 游戏窗口高度
TIME_LIMIT = 300  # 游戏时间限制

# 设置窗口大小并创建屏幕对象
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

# 自定义游戏常量
T_WIDTH = 68  # 每张牌的宽度
T_HEIGHT = 76  # 每张牌的高度
DOCK = pygame.Rect((107, 648), (T_WIDTH * 7, T_HEIGHT))  # 牌堆的位置


# 加载资源
def load_image(filename):
    return pygame.image.load(os.path.join('images', filename))


# 加载和调整背景图
background = pygame.transform.scale(load_image('back.png'), (WIDTH, HEIGHT))
mask_image = pygame.transform.scale(load_image('mask.png'), (T_WIDTH, T_HEIGHT))
end_image = pygame.transform.scale(load_image('loser.png'), (WIDTH, HEIGHT))
win_image = pygame.transform.scale(load_image('win.png'), (WIDTH, HEIGHT))

# 加载按钮图片
undo_button_image = pygame.transform.scale(load_image('undo.jpg'), (100, 80))  # 撤销按钮
restart_button_image = pygame.transform.scale(load_image('restart.jpg'), (100, 80))  # 重新开始按钮

# 定义按钮位置
undo_button_rect = undo_button_image.get_rect(bottomright=(WIDTH - 8, HEIGHT - 280))  # 右下角撤销按钮
restart_button_rect = restart_button_image.get_rect(bottomright=(WIDTH - 8, HEIGHT - 190))  # 右下角重新开始按钮

# 加载背景音乐
pygame.mixer.music.load(os.path.join('music', 'bgm.mp3'))  # 替换为你音乐文件的路径
pygame.mixer.music.play(-1)  # 无限循环播放背景音乐 (-1 表示循环)

# 游戏名、分数和状态
game_name = ''
score = 0
victory = False
game_name_input_active = True  # 初始时激活输入界面
input_box_active = False  # 跟踪输入框是否被激活

# 上方所有牌
tiles = []
# 牌堆里的牌
docks = []
# 记录最近点击的牌，用于撤销功能
undo_stack = []


# 初始化牌组，12*12张牌随机打乱
def initialize_game():
    global tiles, docks, undo_stack, timer, start_ticks, ts, score
    tiles = []
    docks = []
    undo_stack = []
    score = 0

    ts = list(range(1, 13)) * 12
    random.shuffle(ts)
    n = 0

    for k in range(7):  # 7层
        for i in range(7 - k):
            for j in range(7 - k):
                t = ts[n]
                n += 1
                tile_image = pygame.transform.scale(load_image(f'tile{t}.jpg'), (60, 66))
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
        tile_image = pygame.transform.scale(load_image(f'tile{t}.jpg'), (60, 66))
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


# 初始化倒计时
clock = pygame.time.Clock()


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

    # 绘制按钮
    screen.blit(undo_button_image, undo_button_rect)
    screen.blit(restart_button_image, restart_button_rect)

    # 绘制分数
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - 100, 10))

    # 超过7张或超时，游戏失败
    if len(docks) >= 7 or timer <= 0:
        screen.blit(end_image, (0, 0))
    # 没有剩余牌，游戏胜利
    elif len(tiles) == 0:
        screen.blit(win_image, (0, 0))


# 更新函数
def update():
    global timer
    current_ticks = pygame.time.get_ticks()
    timer = TIME_LIMIT - (current_ticks - start_ticks) // 1000
    if timer <= 0:
        timer = 0


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

            # 更新分数
            score += 10
            break


# 撤销功能（该部分由AI生成）
def handle_undo():
    global score
    if undo_stack:
        tile = undo_stack.pop()  # 取出最后一次操作的牌
        tile['status'] = 1  # 撤销后状态为可点击
        tiles.append(tile)  # 放回tiles中
        docks.remove(tile)  # 从docks中移除
        score = max(score - 10, 0)  # 每次撤销分数减少10分，确保分数不为负


# 游戏名输入（该部分由AI生成）
def get_username():
    global game_name
    game_name = ''

    input_box = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 30, 320, 60)  # 增大输入框尺寸
    color_inactive = pygame.Color('lightskyblue3')  # 非激活状态颜色
    color_active = pygame.Color('blue')  # 激活状态颜色（蓝色）
    color = color_inactive
    font = pygame.font.Font(None, 50)  # 调整字体大小以匹配更大的输入框
    active = False  # 输入框是否激活
    done = False  # 标志输入是否完成
    prompt_shown = True  # 是否显示提示文本
    input_cursor = "|"  # 光标显示
    cursor_blink = pygame.USEREVENT + 1  # 自定义事件，用于光标闪烁
    pygame.time.set_timer(cursor_blink, 500)  # 每500ms触发一次光标闪烁

    clock = pygame.time.Clock()
    # 定义查看排行榜按钮
    leaderboard_button_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 40)
    button_color = pygame.Color('dodgerblue')  # 改为蓝色
    leaderboard_active = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return ''
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查是否点击了查看排行榜按钮
                if leaderboard_button_rect.collidepoint(event.pos):
                    leaderboard_active = True  # 点击后激活排行榜显示

                # 检查是否点击了输入框
                if input_box.collidepoint(event.pos):
                    active = True
                    prompt_shown = False  # 点击输入框后隐藏提示文本
                else:
                    active = False
                color = color_active if active else color_inactive  # 改变输入框颜色
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True  # 按下 Enter 键时结束输入
                    elif event.key == pygame.K_BACKSPACE:
                        game_name = game_name[:-1]  # 删除字符
                    else:
                        # 处理英文字符和常规字符输入，包括字母、数字及一些常见符号
                        if event.unicode.isprintable() and len(game_name) < 20:  # 允许的字符必须是可打印的
                            game_name += event.unicode

            elif event.type == cursor_blink and active:
                input_cursor = '' if input_cursor else '|'  # 切换光标显示

        screen.blit(background, (0, 0))  # 保持原背景图

        # 绘制输入提示文本
        prompt_text = font.render('Please input your playname:', True, (0, 0, 255))
        screen.blit(prompt_text, (WIDTH // 2 - 200, HEIGHT // 2 - 100))

        # 绘制输入框及其内容
        display_name = game_name + (input_cursor if active else '')  # 显示光标
        txt_surface = font.render(display_name, True, (0, 0, 255))  # 白色文字
        width = max(320, txt_surface.get_width() + 10)  # 动态调整输入框宽度
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))  # 调整文字位置
        pygame.draw.rect(screen, (0, 0, 255), input_box, 5)  # 绘制加粗边框，设置为5像素的蓝色边框

        # 如果用户未点击输入框且尚未输入，显示输入提示词
        if prompt_shown and not active and game_name == '':
            hint_text = font.render('Enter your name...', True, (0, 0, 255))  # 灰色提示
            screen.blit(hint_text, (input_box.x + 10, input_box.y + 10))

        # 绘制“查看排行榜”按钮
        pygame.draw.rect(screen, button_color, leaderboard_button_rect)
        leaderboard_text = font.render('Leaderboard', True, (255, 255, 255))
        screen.blit(leaderboard_text, (leaderboard_button_rect.x + 10, leaderboard_button_rect.y + 5))
        if leaderboard_active:
            display_leaderboard_in_input()
        pygame.display.flip()
        clock.tick(30)  # 控制帧率

    pygame.time.set_timer(cursor_blink, 0)  # 停止光标闪烁计时器
    return game_name
# 显示排行榜在输入用户名界面，并添加返回按钮
def display_leaderboard_in_input():
    leaderboard = []
    if os.path.exists('leaderboard.json'):
        with open('leaderboard.json', 'r') as file:
            leaderboard = json.load(file)

    # 返回按钮
    return_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 100, 100, 40)
    button_color = pygame.Color('dodgerblue')  # 返回按钮改为蓝色
    font = pygame.font.Font(None, 36)

    # 显示排行榜
    while True:
        screen.blit(background, (0, 0))  # 保持原背景图
        title_text = font.render('Leaderboard', True, (255, 0, 0))  # 蓝色排行榜标题
        screen.blit(title_text, (WIDTH // 2 - 100, 50))

        for i, entry in enumerate(leaderboard):
            rank_text = font.render(f'{i + 1}. {entry["name"]} - Score: {entry["score"]}, Time: {entry["time"]}', True, (255, 0, 0))  # 蓝色内容
            screen.blit(rank_text, (50, 100 + i * 40))

        # 绘制返回按钮
        pygame.draw.rect(screen, button_color, return_button_rect)
        return_text = font.render('Return', True, (255, 255, 255))
        screen.blit(return_text, (return_button_rect.x + 10, return_button_rect.y + 5))

        pygame.display.flip()

        # 事件处理，返回到用户名输入界面
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if return_button_rect.collidepoint(event.pos):
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # 按下 ESC 键也可以返回
                    return
# 显示排行榜（该部分由AI生成）
def display_leaderboard(victory):
    leaderboard = []
    if os.path.exists('leaderboard.json'):
        with open('leaderboard.json', 'r') as file:
            leaderboard = json.load(file)

    if victory:
        leaderboard.append({
            'name': game_name,
            'score': score,
            'time': TIME_LIMIT - timer
        })
        leaderboard = sorted(leaderboard, key=lambda x: (-x['score'], x['time']))[:10]  # 排序并限制前10名

        with open('leaderboard.json', 'w') as file:
            json.dump(leaderboard, file, indent=4)

    # 显示排行榜
    screen.blit(background, (0, 0))  # 保持原背景图
    font = pygame.font.Font(None, 36)
    title_text = font.render('Leaderboard', True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - 100, 50))

    for i, entry in enumerate(leaderboard):
        rank_text = font.render(f'{i + 1}. {entry["name"]} - Score: {entry["score"]}, Time: {entry["time"]}', True,
                                (255, 255, 255))
        screen.blit(rank_text, (50, 100 + i * 40))

    pygame.display.flip()
    pygame.time.wait(5000)  # 显示5秒


def main():
    global game_name_input_active, victory

    # 获取用户名
    game_name = get_username()
    if not game_name:
        return  # 如果未输入游戏名，则退出游戏

    # 游戏初始化
    initialize_game()
    running = True
    victory = False

    while running:
        screen.fill((0, 0, 0))  # 清屏
        draw()  # 绘制内容
        update()  # 更新游戏状态
        pygame.display.flip()  # 刷新屏幕

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_down(event.pos)
            elif event.type == pygame.KEYDOWN:
                # 处理其他键盘输入（如撤销功能）
                pass

        if len(tiles) == 0:
            victory = True
            display_leaderboard(True)  # 显示排行榜

        clock.tick(60)  # 控制帧率

    pygame.quit()


if __name__ == '__main__':
    main()
# 最终版本
