''' 
By @tq3940
'''

import pygame as pg
import random
import time
import expectiminimax
import copy
import draw_tree

BLACK_PLAYER = 1
WHITE_PLAYER = 2
# player1: 1 -> 24
# player2: 24-> 1

pg.init()
# 初始化Rect对象用于点击

# 放棋子的堆 + 槽
stack_rects = []
stack_size = (57.5, 280)
# 从右上逆时针转
stack_pos = (820-stack_size[0], 30)
for i in range(6):
    stack_rects.append(pg.Rect(stack_pos, stack_size))
    stack_pos = (stack_pos[0]-stack_size[0], stack_pos[1])

stack_pos = (430-stack_size[0], 30)
for i in range(6):
    stack_rects.append(pg.Rect(stack_pos, stack_size))
    stack_pos = (stack_pos[0]-stack_size[0], stack_pos[1])

stack_pos = (85, 480)
for i in range(6):
    stack_rects.append(pg.Rect(stack_pos, stack_size))
    stack_pos = (stack_pos[0]+stack_size[0], stack_pos[1])

stack_pos = (475, 480)
for i in range(6):
    stack_rects.append(pg.Rect(stack_pos, stack_size))
    stack_pos = (stack_pos[0]+stack_size[0], stack_pos[1])

stack_rects.append(pg.Rect((838, 480), (54, 276)))      # 右上槽
stack_rects.insert(0, pg.Rect((838, 43), (54, 276)))    # 右下槽

bar_rects = [0, pg.Rect((430, 30), (45, 280)), pg.Rect((430, 480), (45, 280))]         # 中间横栏 
player_select_rects = [pg.Rect((0, 90), (56, 56)), pg.Rect((0, 155), (56, 56))]     # 选择玩家按钮
checker_setting_rects = [pg.Rect((0, 357), (56, 56)), pg.Rect((0, 419), (56, 56))]  # 选择摆放棋子按钮
dice_rects = [pg.Rect((3, 618), (46, 51)), pg.Rect((3, 675), (46, 51))]             # 骰子
random_button_rect = pg.Rect((841, 325), (50, 140))                                 # 随机骰子按钮
start_button_rect = pg.Rect((662, 357), (122, 122))                                  # 开始按钮

pg.display.set_caption('Backgammon')
screen_size = (900, 790)  # a tuple of size (width, height)
screen = pg.display.set_mode(screen_size)

# 加载图像
board_img = pg.image.load("img\\two_players_back.png")
black_checker_img = pg.image.load("img\\black_pawn.png")
white_checker_img = pg.image.load("img\\white_pawn.png")
black_outside_img = pg.image.load("img\\black_pawn_outside.png")
white_outside_img = pg.image.load("img\\white_pawn_outside.png")
black_selected_img = pg.image.load("img\\black_highlight.png") 
white_selected_img = pg.image.load("img\\white_highlight.png") 
random_button_img = pg.image.load("img\\active_player_dice_button.png")
start_button_img = pg.image.load("img\\start_button.png")
moved_from_img = pg.image.load("img\\moved_from.png")
moved_to_img = pg.image.load("img\\moved_to.png")
moved_to_outside_img = pg.image.load("img\\moved_to_outside.png")
eaten_from_img = pg.image.load("img\\eaten_from.png")
eaten_to_img = pg.image.load("img\\eaten_to.png")

dice_imgs = [None]
for i in range(1,7):
    path = "img\\player_dice"+str(i)+".png"
    dice_img = pg.image.load(path)
    dice_imgs.append(dice_img)

# 当前玩家
current_player = None

# 统计棋子
checker_num_dict = {i:0 for i in range(26)} # 玩家: 棋子数

# 摆放棋子
add_checker = WHITE_PLAYER  # 初始为白色

# 横栏棋子
bar_checker_num = [0,0,0]     # [0, 上(黑), 下(白)]

# 骰子点数
dice_nums = [1,1]

def render_line_text(lines, font, start_pos, font_color, backgrand_color=None):
    '''传入列表每个元素为一行，输出多行文字'''
    rendered_lines = []
    line_height = font.get_linesize()
    x,y = start_pos
    for line in lines:
        rendered_line = font.render(line, True, font_color, backgrand_color)
        rendered_lines.append((rendered_line, (x, y)))
        y += line_height

    # 渲染到屏幕上
    for rendered_line, position in rendered_lines:
        screen.blit(rendered_line, position)

def render_player_selector():
    '''渲染选择当前玩家按钮'''
    black_img = black_selected_img if current_player == BLACK_PLAYER else black_checker_img
    white_img = white_selected_img if current_player == WHITE_PLAYER else white_checker_img

    screen.blit(black_img, player_select_rects[0])
    screen.blit(white_img, player_select_rects[1]) 

    if current_player == None:
        text = ["请选择", "当前玩家"]
        font_color = (255,0,79)
        backgrand_color = (132,204,201)
    else:
        text = ["已选择"]
        font_color = (0,255,0)
        backgrand_color = None

    text_pos = (0,30)        
    font = pg.font.SysFont("SimHei", 20)
    render_line_text(text, font, text_pos, font_color, backgrand_color)

def render_checker_setting():
    '''渲染选择摆放棋子按钮'''
    black_img = black_selected_img if add_checker == BLACK_PLAYER else black_checker_img
    white_img = white_selected_img if add_checker == WHITE_PLAYER else white_checker_img

    screen.blit(black_img, checker_setting_rects[0])
    screen.blit(white_img, checker_setting_rects[1]) 

    font = pg.font.SysFont("SimHei", 28)
    text = ["棋子", "颜色"]
    font_color = (246,179,127)
    text_pos = (0,285)
    render_line_text(text, font, text_pos, font_color)

def render_dices(only_dices=False):
    '''渲染骰子'''
    dice1 = dice_nums[0]
    dice2 = dice_nums[1]
    screen.blit(dice_imgs[dice1], dice_rects[0])
    screen.blit(dice_imgs[dice2], dice_rects[1])  

    if only_dices==False:
        screen.blit(random_button_img, random_button_rect)  
        text = ["点击", "切换", "骰子"]
        font = pg.font.SysFont("SimHei", 28)
        font_color = (246,179,127)
        text_pos = (0,520)
        render_line_text(text, font, text_pos, font_color)

def render_all_checker():

    for i in range(26): # 堆的下标
        if checker_num_dict[i] == 0:
            continue
        checker_color = checker_num_dict[i][0]
        checker_num = checker_num_dict[i][1]

        if i==0  or i==25:
            checker_img = white_outside_img if checker_color == WHITE_PLAYER else black_outside_img
            checker_size = (50,18)
        else:
            checker_img = white_checker_img if checker_color == WHITE_PLAYER else black_checker_img
            checker_size = (56,56)
        
        checker_rect_list = []

        # 上边的从上往下画
        if 0<= i <= 12:     
            for j in range(checker_num):
                checker_rect = pg.Rect(0,0,checker_size[0],checker_size[1])
                if j==0:
                    checker_rect.midtop = stack_rects[i].midtop
                else:
                    checker_rect.midtop = checker_rect_list[j-1].midbottom
                checker_rect_list.append(checker_rect)

        # 下边的从下往上画
        else:  
            for j in range(checker_num):
                checker_rect = pg.Rect(0,0,checker_size[0],checker_size[1])
                if j==0:
                    checker_rect.midbottom = stack_rects[i].midbottom
                else:
                    checker_rect.midbottom = checker_rect_list[j-1].midtop
                checker_rect_list.append(checker_rect)

        for rect in checker_rect_list:
            screen.blit(checker_img, rect)


def render_bar_checkers():
    '''渲染横栏上棋子'''
    # 上边的从上往下画, 上面一般只放黑色
    checker_rect_list = []
    for j in range(bar_checker_num[BLACK_PLAYER]):
        checker_rect = pg.Rect(0,0,56,56)
        if j==0:
            checker_rect.midtop = bar_rects[BLACK_PLAYER].midtop
        else:
            checker_rect.midtop = checker_rect_list[j-1].midbottom
        checker_rect_list.append(checker_rect)

    for rect in checker_rect_list:
        screen.blit(black_checker_img, rect)    

    # 下边的从下往上画, 下面一半只放白色
    checker_rect_list = []
    for j in range(bar_checker_num[WHITE_PLAYER]):
        checker_rect = pg.Rect(0,0,56,56)
        if j==0:
            checker_rect.midbottom = bar_rects[WHITE_PLAYER].midbottom
        else:
            checker_rect.midbottom = checker_rect_list[j-1].midtop
        checker_rect_list.append(checker_rect)

    for rect in checker_rect_list:
        screen.blit(white_checker_img, rect)        
 

def render_all_screen():

    screen.fill((0, 0, 0))
    screen.blit(board_img, (0,0))
    
    render_player_selector()
    render_checker_setting()
    render_dices()
    render_all_checker()
    render_bar_checkers()


    text = "左键选择，右键删除"
    font = pg.font.SysFont("SimHei", 30)
    font_color = (19,181,177)
    text_img = font.render(text, True, font_color)
    text_rect = text_img.get_rect()
    text_rect.centerx =  pg.display.Info().current_w // 2
    screen.blit(text_img, text_rect)


    screen.blit(start_button_img, start_button_rect)
    text = ["开始", "按钮"]
    font = pg.font.SysFont("SimHei", 48)
    font_color = (68,191,124)
    text_pos = (563,366)
    render_line_text(text, font, text_pos, font_color)

def add_checker_fun(i):
    if i==0 or i==25:
        sp_add_checker = WHITE_PLAYER if i == 0 else BLACK_PLAYER 
        if checker_num_dict[i] == 0:
            checker_num_dict[i] = [sp_add_checker, 1]

        else:
            checker_num_dict[i][1] += 1

    else:
        if checker_num_dict[i] == 0:
            checker_num_dict[i] = [add_checker, 1]

        elif checker_num_dict[i][0] ==add_checker:
            checker_num_dict[i][1] += 1
        
        else:
            text = ["警告：", "一个堆只能放一种棋子！"]
            font = pg.font.SysFont("SimHei", 60)
            font_color = (255,0,0)
            text_pos = (185,300)
            render_line_text(text, font, text_pos, font_color)
            pg.display.flip()

            time.sleep(1)

def render_move_from_box(from_rect, num, up_or_down, box_color="red"):
    '''
    渲染虚线提示框
        from_rect: 堆/槽/横栏
        num: 本次移动前棋子数
        up_or_down: "up"/"down"
        box_color: "red"/"blue"
    '''
    if from_rect == stack_rects[0] or from_rect == stack_rects[-1]:
        box_size = (50,18)
    else:    
        box_size = (56,56)
    
    box_img = moved_from_img if box_color == "red" else eaten_from_img
    box_rect = pg.Rect(0,0,box_size[0],box_size[1])

    num -= 1
    if up_or_down == "up":
        x0,y0 = from_rect.midtop
        box_rect.midtop = (x0, y0 + num*box_size[1])
    else:
        x0,y0 = from_rect.midbottom
        box_rect.midbottom = (x0, y0 - num*box_size[1])        
    
    screen.blit(box_img, box_rect)        

def render_move_to_box(to_rect, num, up_or_down, box_color="red"):
    '''
    渲染实线提示框
        from_rect: 堆/槽/横栏
        num: 本次移动前棋子数
        up_or_down: "up"/"down"
        box_color: "red"/"blue"
    '''
    if to_rect == stack_rects[0] or to_rect == stack_rects[-1]:
        box_size = (50,18)
        box_img = moved_to_outside_img
    else:    
        box_size = (56,56)
        box_img = moved_to_img if box_color == "red" else eaten_to_img

    box_rect = pg.Rect(0,0,box_size[0],box_size[1])

    if up_or_down == "up":
        x0,y0 = to_rect.midtop
        box_rect.midtop = (x0, y0 + num*box_size[1])
    else:
        x0,y0 = to_rect.midbottom
        box_rect.midbottom = (x0, y0 - num*box_size[1])
    
    screen.blit(box_img, box_rect)
    

def render_box(last_bar_checker_num, last_checker_num_dict):
    "渲染移动提示框"
    # 堆和槽
    for i in range(26):

        now_checker_num = 0 if checker_num_dict[i] == 0 else checker_num_dict[i][1]
        last_checker_num = 0 if last_checker_num_dict[i] == 0 else last_checker_num_dict[i][1]
        up_or_down = "up"  if 0<= i <= 12 else "down"
        
        if now_checker_num != 0 and last_checker_num != 0:
            if checker_num_dict[i][0] != last_checker_num_dict[i][0]:
                render_move_from_box(stack_rects[i], 1, up_or_down, "blue")
          
        # 移走棋子提示框
        if last_checker_num > now_checker_num:
            moved_num = last_checker_num- now_checker_num

            for j in range(moved_num):
                render_move_from_box(stack_rects[i], last_checker_num-j, up_or_down)
                
        # 移入棋子提示框
        if now_checker_num > last_checker_num:
            moved_num = now_checker_num- last_checker_num

            for j in range(moved_num):
                render_move_to_box(stack_rects[i], last_checker_num+j, up_or_down)            

    # 横栏
    for i,up_or_down in [(1,"up"),(2,"down")]:
        
        # 移走棋子提示框
        if last_bar_checker_num[i] > bar_checker_num[i]:
            moved_num = last_bar_checker_num[i] - bar_checker_num[i]
            for j in range(moved_num):
                render_move_from_box(bar_rects[i], last_bar_checker_num[i]-j, up_or_down)    

        # 移入棋子提示框
        elif bar_checker_num[i] > last_bar_checker_num[i]:
            moved_num = bar_checker_num[i] - last_bar_checker_num[i]
            for j in range(moved_num):
                render_move_to_box(bar_rects[i], last_bar_checker_num[i]+j, up_or_down, "blue")



def display_result(moves):

    last_bar_checker_num = copy.deepcopy(bar_checker_num)
    last_checker_num_dict = copy.deepcopy(checker_num_dict)

    for u,v in moves:

        if u == -1:
            bar_checker_num[current_player] -= 1

        else:
            checker_num_dict[u][1] -= 1
            if checker_num_dict[u][1] == 0:
                checker_num_dict[u] = 0    

        if checker_num_dict[v] == 0:
            checker_num_dict[v] = [current_player, 1]

        elif checker_num_dict[v][0] == current_player:
            checker_num_dict[v][1] += 1

        else:
            opposed_player = checker_num_dict[v][0] 
            checker_num_dict[v] = [current_player, 1]
            bar_checker_num[opposed_player] += 1

    render_all_screen()
    render_box(last_bar_checker_num, last_checker_num_dict)
    pg.display.flip()
    time.sleep(5)


        


def run_expectiminimax():

    if current_player == None:    
        text = ["警告：", "你还没有选择当前玩家！"]
        font = pg.font.SysFont("SimHei", 60)
        font_color = (255,0,0)
        text_pos = (185,300)
        render_line_text(text, font, text_pos, font_color)
        pg.display.flip()

        time.sleep(1)
        return 
    
    board = []
    bar = bar_checker_num

    for i in range(26):
        x = checker_num_dict[i]
        if x == 0:
            board.append([])
        else:
           board.append([x[0]] * x[1]) 
 
    dice_rolls = copy.deepcopy(dice_nums)
    if dice_rolls[0] == dice_rolls[1]:
        dice_rolls = dice_rolls * 2

    dice_rolls.sort()
    expectiminimax.player = current_player
    game_state = expectiminimax.GameState(board, bar, current_player)
    game = expectiminimax.Backgammon()

    #print(game.actions(game_state, dice_rolls))
    root,moves = expectiminimax.get_best_move(game_state, game, dice_rolls)

    if moves is not None:
        print("\n".join(" ".join(str(m) for m in move) for move in moves))
    
    draw_tree.draw_tree(root)
    display_result(moves)


if __name__ == '__main__':

    add_log = []

    while True:
        
        for event in pg.event.get(): #  获取用户事件
            if event.type == pg.QUIT: # 如果事件为关闭窗口
                pg.quit() # 退出pygame

            render_all_screen()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键选择
                    
                    # 检测选中堆或槽
                    for i in range(26):
                        if stack_rects[i].collidepoint(event.pos):
                            add_checker_fun(i)  
                            add_log.append(i)

                    for i in [0,1]:
                        # 检测切换按钮
                        if checker_setting_rects[i].collidepoint(event.pos):
                            add_checker = WHITE_PLAYER if i==1 else BLACK_PLAYER                    

                        # 检测骰子
                        if dice_rects[i].collidepoint(event.pos):
                            if dice_nums[i] == 6:
                                dice_nums[i] = 1
                            else:
                                dice_nums[i] += 1
                        # 检测选中参与人
                        if  player_select_rects[i].collidepoint(event.pos):
                            current_player = WHITE_PLAYER if i==1 else BLACK_PLAYER                    
                        
                        if bar_rects[i+1].collidepoint(event.pos):
                            bar_checker_num[i+1] += 1

                    # 检测选中随机按钮
                    if random_button_rect.collidepoint(event.pos):
                        for i in range (1000):
                            dice_nums[0] = random.randint(1, 6)
                            dice_nums[1] = random.randint(1, 6)
                            render_dices(True)
                            pg.display.flip()
                    
                    # 检测选中开始按钮
                    if start_button_rect.collidepoint(event.pos):
                        if len(add_log) == 0:
                            break
                        run_expectiminimax()

                        
                
                if event.button == 3:  # 右键删除
                    # 检测选中堆或槽
                    for i in range(26):
                        if stack_rects[i].collidepoint(event.pos):
                            if checker_num_dict[i] != 0:
                                checker_num_dict[i][1] -= 1
                                if checker_num_dict[i][1] == 0:
                                    checker_num_dict[i] = 0

                    for i in [0,1]:
                        # 检测骰子
                        if dice_rects[i].collidepoint(event.pos):
                            if dice_nums[i] == 1:
                                dice_nums[i] = 6
                            else:
                                dice_nums[i] -= 1
                               
                        if bar_rects[i+1].collidepoint(event.pos):
                            if bar_checker_num[i+1] != 0:
                                bar_checker_num[i+1] -=1

        pg.display.flip()
