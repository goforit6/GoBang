 # coding: utf8

import sys
import time
import pygame

# 无论是获胜后重新开始还是中途重新开始, 没有工人对order值做改变, 正好可以轮换先手与后手

pygame.init()
bgpic = pygame.image.load('./bg.jpg')
black = pygame.image.load('./black.png')
white = pygame.image.load('./white.png')

audio = './audio.mp3'
pygame.mixer.init()
pygame.mixer.music.load(audio)
pygame.mixer.music.play(100, 2)

width, height = bgpic.get_size()  # 获取背景图片尺寸作为屏幕尺寸
litter = min(width, height)  # 取出较小者方便后面画棋盘
interval = litter // 14 - 3  # 计算每个小格子的空间  15x15的棋盘  -3是增加棋盘外边距,防止边界棋子出界
t = interval * 14  # 计算棋盘总宽度
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('五子棋')
ico = pygame.image.load('./ico.png')
pygame.display.set_icon(ico)
lis = list()  # 用于存放所有的交叉坐标点
order = 1  # 黑棋先手：0无棋/1黑棋/
iswin = False
win_img = ''


def draw_button():
    x1, y1, x2, y2 = get_four_port()
    x = x2 + 20
    chocolate = (210, 105, 30)
    start = pause = end = again = regret = pygame.font.Font('./simkai.ttf', 30)
    start_img = start.render('继续播放', True, chocolate)
    screen.blit(start_img, (x, interval*2))
    pause_img = pause.render('暂停音乐', True, chocolate)
    screen.blit(pause_img, (x, interval*3))
    end_img = end.render('停止音乐', True, chocolate)
    screen.blit(end_img, (x, interval*4))
    again_img = again.render('重新开始', True, chocolate)
    screen.blit(again_img, (x, interval*5))
    regret_img = regret.render('后退一步', True, chocolate)  # 140x40
    screen.blit(regret_img, (x, interval*6))


def get_four_port():
    """返回x, y的取值范围"""
    x1 = (width - t) / 2
    y1 = (height - t) / 2
    x2 = x1 + t
    y2 = y1 + t
    return x1, y1, x2, y2


def draw_chessboard():
    """绘制棋盘及计算出所有落棋点坐标"""
    border = 2  # 线的宽度
    x1, y1, x2, y2 = get_four_port()
    for i in range(15):
        border = border+2 if i == 0 else 2  # 边界线的宽度比中间大2
        pygame.draw.line(bgpic, (0, 0, 0), (x1, y1 + interval * i), (x2, y1 + interval * i), border)  # 绘制水平直线
        pygame.draw.line(bgpic, (210, 0, 0), (x1 + interval * i, y1), (x1 + interval * i, y2), border)  # 绘制垂直直线
    pygame.draw.line(bgpic, (0, 0, 0), (x1, y2), (x2, y2), border+2)  # 绘制最后一条水平直线
    pygame.draw.line(bgpic, (210, 0, 0), (x2, y1), (x2, y2), border+2)  # 绘制最后一条垂直直线
draw_chessboard()


def get_cross_point():
    """遍历出所有的交叉点坐标"""
    x1, y1, x2, y2 = get_four_port()
    while x1 <= x2:
        while y1 <= y2:
            lis.append((x1, y1))
            y1 += interval
        y1 = (height - t) / 2  # 重置y1的值
        x1 += interval
    return interval


scare = get_cross_point()
black = pygame.transform.smoothscale(black, (scare-1, scare-1))  # 棋子按棋格大小缩放后-1 防止相邻棋子出现粘贴现象
white = pygame.transform.smoothscale(white, (scare-1, scare-1))
widthq = black.get_size()[0]  # 缩放后的棋子宽度，便于后面定位棋子位置
poslis_black, poslis_white = [], []  # 预设一个列表，存放棋子标识与所有对应鼠标点击过的位置


def calc_distance(tup1, tup2):
    """计算鼠标点击位置与交叉点（两点）的距离"""
    dispow = (tup2[0] - tup1[0]) ** 2 + (tup2[1] - tup1[1]) ** 2
    return dispow ** 0.5


def who_win_action(who):
    global lis
    global win_img
    lis = []  # 锁定棋盘
    win = pygame.font.Font('./simkai.ttf', 40)
    win_img = win.render('%s获胜' % who, True, (255, 0, 0))
    sound = pygame.mixer.Sound('./{}.ogg'.format(who).encode())
    sound.play()


def judge_black_win():
    """判断黑棋是否获胜"""
    global iswin
    x1, y1, x2, y2 = get_four_port()
    resb = poslis_black
    lenb = len(resb)
    if lenb >= 5:  # 有5个及以上的点才开始寻找
        x, y = resb[-1]  # 得到最后下的一颗棋子的坐标，以此为中心向4个大方向搜索

        # 1. 横向搜索, y保持不变
        cnt = 0  # 对每个大方向上的两个小方向棋子计数
        for lor in [-1, 1]:
            tx = x
            while x1 <= tx <= x2:
                tx += interval * lor
                if (tx, y) in resb:
                    cnt += 1
                    if cnt == 4:  # 减掉自身
                        iswin = True
                        who_win_action('黑棋')
                        return
                else:
                    break

        # 2. 纵向搜索, x保持不变
        cnt = 0
        for uod in [-1, 1]:
            ty = y
            while y1 <= ty <= y2:
                ty += interval * uod
                if (x, ty) in resb:
                    cnt += 1
                    if cnt == 4:
                        iswin = True
                        who_win_action('黑棋')
                        return
                else:
                    break

        # 3. 左斜向搜索,  (x减,y加), (x加,y减)
        cnt = 0
        for ldru in [-1, 1]:
            tx, ty = x, y
            while x1 <= tx <= x2 and y1 <= ty <= y2:
                tx += interval * ldru
                ty -= interval * ldru
                if (tx, ty) in resb:
                    cnt += 1
                    if cnt == 4:
                        iswin = True
                        who_win_action('黑棋')
                        return
                else:
                    break

        # 4. 右斜向搜索, (x减,y减),(x加,y加)
        cnt = 0
        for lurd in [-1, 1]:
            tx, ty = x, y
            while x1 <= tx <= x2 and y1 <= ty <= y2:
                tx += interval * lurd
                ty += interval * lurd
                if (tx, ty) in resb:
                    cnt += 1
                    if cnt == 4:
                        iswin = True
                        who_win_action('黑棋')
                        return
                else:
                    break


def judge_white_win():
    """判断白棋是否获胜"""
    global iswin
    x1, y1, x2, y2 = get_four_port()
    resw = poslis_white
    lenw = len(resw)
    if lenw >= 5:  # 有5个及以上的点才开始寻找
        x, y = resw[-1]  # 得到最后下的一颗棋子的坐标，以此为中心向4个大方向搜索

        # 1. 横向搜索, y保持不变
        cnt = 0  # 对每个大方向上的两个小方向棋子计数
        for lor in [-1, 1]:
            tx = x
            while x1 <= tx <= x2:
                tx += interval * lor
                if (tx, y) in resw:
                    cnt += 1
                    if cnt == 4:  # 减掉自身
                        iswin = True
                        who_win_action('白棋')
                        return
                else:
                    break

        # 2. 纵向搜索, x保持不变
        cnt = 0
        for uod in [-1, 1]:
            ty = y
            while y1 <= ty <= y2:
                ty += interval * uod
                if (x, ty) in resw:
                    cnt += 1
                    if cnt == 4:
                        iswin = True
                        who_win_action('白棋')
                        return
                else:
                    break

        # 3. 左斜向搜索,  (x减,y加), (x加,y减)
        cnt = 0
        for ldru in [-1, 1]:
            tx, ty = x, y
            while x1 <= tx <= x2 and y1 <= ty <= y2:
                tx += interval * ldru
                ty -= interval * ldru
                if (tx, ty) in resw:
                    cnt += 1
                    if cnt == 4:
                        iswin = True
                        who_win_action('白棋')
                        return
                else:
                    break

        # 4. 右斜向搜索, (x减,y减),(x加,y加)
        cnt = 0
        for lurd in [-1, 1]:
            tx, ty = x, y
            while x1 <= tx <= x2 and y1 <= ty <= y2:
                tx += interval * lurd
                ty += interval * lurd
                if (tx, ty) in resw:
                    cnt += 1
                    if cnt == 4:
                        iswin = True
                        who_win_action('白棋')
                        return
                else:
                    break


while True:
    time.sleep(0.2)
    screen.blit(bgpic, (0, 0))  # 背景放最前面执行，防止遮挡其他绘制的图形
    draw_button()
    pos_b_center = [(x - widthq / 2, y - widthq / 2) for x, y in poslis_black]  # 将棋子中心定位于交互点
    pos_w_center = [(x - widthq / 2, y - widthq / 2) for x, y in poslis_white]
    if iswin:
        screen.blit(win_img, (15, interval*2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit('已退出游戏')
        elif event.type == pygame.MOUSEBUTTONDOWN:

            x, y = event.pos
            x1, y1, x2, y2 = get_four_port()
            if x2+20 < x < x2+140 and interval*2 < y < interval*2+30:
                pygame.mixer.music.unpause()
            elif x2+20 < x < x2+140 and interval*3 < y < interval*3+30:
                pygame.mixer.music.pause()
            elif x2+20 < x < x2+140 and interval*4 < y < interval*4+30:
                pygame.mixer.music.stop()
            elif x2 + 20 < x < x2 + 140 and interval*5 < y < interval*5+30:
                poslis_black.clear()
                poslis_white.clear()
                pos_b_center.clear()
                pos_w_center.clear()
                iswin = False
                lis = []  # 如果是中途点的重新开始, 要清空lis, 重新加载lis
                get_cross_point()  # 如果是获胜后(lis被清空了)点的重新开始, 要重新通过此方法建立lis;
            elif x2 + 20 < x < x2 + 140 and interval*6 < y < interval*6+30:
                if iswin is False:  # 获胜后不允许悔棋
                    if order == 1:  # 现在是黑棋下,表示刚才落子的是白棋
                        poslis_white.pop()
                        pos_w_center.pop()
                        order += 1
                    else:
                        poslis_black.pop()
                        pos_b_center.pop()
                        order -= 1

            for pos_rel in lis:
                if calc_distance(pos_rel, event.pos) < 15:  # 数值设定越小，要求点击精度越高, 绝对不能>= interval/2
                    if pos_rel not in (poslis_black + poslis_white):  # 防止出现棋子覆盖现象
                        if order == 1:
                            poslis_black.append(pos_rel)
                            print(poslis_black[-1])
                            judge_black_win()
                            order += 1
                        elif order == 2:
                            poslis_white.append(pos_rel)
                            print(poslis_white[-1])
                            judge_white_win()
                            order -= 1

    for pos_b in pos_b_center:
        screen.blit(black, pos_b)
    for pos_w in pos_w_center:
        screen.blit(white, pos_w)

    pygame.display.update()
