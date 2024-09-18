import pgzrun  # 导入pgzrun库，用于创建游戏窗口和处理游戏循环
import pygame  # 导入pygame库，用于处理图像和声音等
import random  # 导入random库，用于生成随机数
import math    # 导入math库，用于数学计算
import os      # 导入os库，用于操作系统相关功能

# 定义游戏相关属性
TITLE = '白了个白'  # 游戏标题
WIDTH = 600        # 游戏窗口宽度
HEIGHT = 720       # 游戏窗口高度
TIME_LIMIT = 180  # 设置游戏时间限制为180秒
# 自定义游戏常量
T_WIDTH = 60       # 每张牌的宽度
T_HEIGHT = 66      # 每张牌的高度

# 下方牌堆的位置
DOCK = pygame.Rect((90, 564), (T_WIDTH*7, T_HEIGHT))  # 创建一个pygame.Rect对象，表示牌堆的位置和大小

# 上方的所有牌
tiles = []  # 存储所有牌的列表
# 牌堆里的牌
docks = []  # 存储牌堆中牌的列表

# 初始化牌组，12*12张牌随机打乱
ts = list(range(1, 13))*12  # 创建一个包含12*12张牌的列表
random.shuffle(ts)           # 随机打乱牌的顺序
n = 0                        # 初始化计数器
for k in range(7):            # 7层
    for i in range(7-k):      # 每层减1行
        for j in range(7-k):  # 每层减1列
            t = ts[n]         # 获取排种类
            n += 1
            tile = Actor(f'tile{t}')  # 使用tileX图片创建Actor对象
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            tile.pos = 120 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9+offset_y+offset_x   # 设定位置
            tile.tag = t             # 记录种类
            tile.layer = k           # 记录层级
            tile.status = 1 if k == 6 else 0  # 除了最顶层，状态都设置为0（不可点）这里是个简化实现
            tiles.append(tile)       # 将牌添加到tiles列表中

for i in range(4):  # 剩余的4张牌放下面（为了凑整能通关）
    t = ts[n]
    n += 1
    tile = Actor(f'tile{t}')
    tile.pos = 210 + i * tile.width, 516  # 设定位置
    tile.tag = t
    tile.layer = 0
    tile.status = 1
    tiles.append(tile)

# 初始化倒计时
timer = TIME_LIMIT

# 游戏帧绘制函数
def draw():
    screen.clear()  # 清除屏幕
    screen.blit('back', (0, 0))  # 绘制背景图
    for tile in tiles:  # 绘制上方牌组
        tile.draw()  # 绘制每张牌
        if tile.status == 0:  # 如果牌的状态为0（不可点）
            screen.blit('mask', tile.topleft)  # 绘制遮罩
    for i, tile in enumerate(docks):  # 绘制牌堆
        tile.left = (DOCK.x + i * T_WIDTH)  # 调整位置
        tile.top = DOCK.y
        tile.draw()  # 绘制每张牌

    # 绘制倒计时
    minutes = int(timer // 60)
    seconds = int(timer % 60)
    screen.draw.text(f'{minutes:02d}:{seconds:02d}', (10, 10), color="red", fontsize=60)


    # 超过7张或超出时间，失败
    if len(docks) >= 7 or timer == 0:
        screen.blit('end', (0, 0))  # 显示结束画面
    # 没有剩牌，胜利
    if len(tiles) == 0:
        screen.blit('win', (0, 0))  # 显示胜利画面


def update(dt):
    global timer
    timer -= dt
    if timer <= 0:
        timer = 0
        screen.blit('end', (0, 0))

# 鼠标点击响应
def on_mouse_down(pos):
    global docks  # 使用全局变量docks
    if len(docks) >= 7 or len(tiles) == 0:  # 游戏结束不响应
        return
    for tile in reversed(tiles):  # 逆序循环是为了先判断上方的牌
        if tile.status == 1 and tile.collidepoint(pos):  # 状态1可点，并且鼠标在范围内
            tile.status = 2  # 改变状态为2（已点击）
            tiles.remove(tile)  # 从tiles列表中移除
            diff = [t for t in docks if t.tag != tile.tag]  # 获取牌堆内不相同的牌
            if len(docks) - len(diff) < 2:  # 如果相同的牌数量<2，就加进牌堆
                docks.append(tile)
            else:  # 否则用不相同的牌替换牌堆（即消除相同的牌）
                docks = diff
            for down in tiles:  # 遍历所有的牌
                if down.layer == tile.layer - 1 and down.colliderect(tile):  # 如果在此牌的下一层，并且有重叠
                    for up in tiles:  # 那就再反过来判断这种被覆盖的牌
                        if up.layer == down.layer + 1 and up.colliderect(down):  # 如果有就跳出
                            break
                    else:  # 如果全都没有，说明它变成了可点状态
                        down.status = 1
            return

music.play('bgm')  # 播放背景音乐

pgzrun.go()  # 开始游戏循环
