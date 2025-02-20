import pygame
import sys

import threading
import cv2
import mediapipe as mp
import math

from anglespeed import *
from Screen import *
from Stone import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
SELECTED = (200, 100, 50)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# Movement substeps at the given timestep
movement_substeps = 1
# Target FPS
FPS = 60.0
# dt (should be 1.0/FPS for realtime, but you can change it to speed up or slow down time)
dt = 1.0 / FPS
turn = 0
num_of_stone = 10  # 돌의 개수
now_select = 0  # 현재 선택된 돌의 번호

"""
realmain의 구조와 movement_substpes, FPS, dt 등의 상수는 Gravity 4 코드에서 일부 참조했다.
<Gravity Simulation - 4.0.0> 
https://www.pygame.org/project/617/4587 
http://geometrian.com/programming/index.php 
http://www.geometrian.com/data/programming/projects/Gravitation/Simulation%204.0.0/Gravity4.zip

pygame에서 한글 출력하는 방법은 빗자루네 블로그에서 참조했다.
<pygame 한글 출력>
http://imp17.com/tc/myevan/133?fbclid=IwAR3C8PL16p5Vr0D5wMpNGFKSnfzTk6UNK8OM2sCO2iihFXXONeofkA03yPQ

anglespeed의 구조는 일부 pygame-physics-simulation에서 가져왔다.
<pygame-physics-simulation>
http://www.petercollingridge.co.uk/tutorials/pygame-physics-simulation/
"""


def textprint(printobj, xcord=400, ycord=30):
    textSurfaceObj = fontObj.render(str(printobj), True, WHITE, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (xcord, ycord)
    window.blit(textSurfaceObj, textRectObj)


def score():
    scored = dict()
    for stone in stones:
        scored.setdefault(stone.team, 0)
        sum = stone.visible
        scored[stone.team] = scored[stone.team] + sum

    if scored[0] == 0:
        return "GRAY WIN"
    elif scored[1] == 0:
        return "WHITE WIN"
    else:
        return "White : " + str(scored[0]) + " vs Gray :" + str(scored[1]) + "\n" + "Selection :" + str(now_select + 1)


icon = pygame.Surface((1, 1))
icon.set_alpha(0)
pygame.display.set_icon(icon)
pygame.display.set_caption("OOP_LIGHTBULB")
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.init()

fontObj = pygame.font.Font("NanumSquareRoundB.ttf", 16)

# team 0
stones = [Stone(start_x=i * 78 + 244, start_y=144, mass=i, team=0, surface=surface) for i in range(5)]
# team 1
stones += [Stone(start_x=i * 78 + 244, start_y=457, mass=i + 5, team=1, surface=surface) for i in range(5)]


# 화면 생성
# screen = Screen("lightbulb", 1000, 600, (0, 0, 0))
window = Screen("lightbulb", 1000, 600, (0, 0, 0)).screen  # 게임화면

# 바둑판
board_img = pygame.image.load("board.png").convert()
board_img = pygame.transform.scale(board_img, (500, 500))
window.blit(board_img, (150, 50))  # 바둑판 위치

# 화살표
arrow_img = pygame.image.load("arrow4.png").convert_alpha()
# arrow4_img = pygame.image.load("arrow4.png").convert_alpha()
# arrow5_img = pygame.image.load("arrow5.png").convert_alpha()
# a3 (614, 195)
# a4 (633, 102)
# a5 (569, 302)

arrow_img = pygame.transform.scale(arrow_img, (60, 15))
offset = pygame.math.Vector2(arrow_img.get_width() // 2, 0)  # 벡터


def new_draw():  # 돌 클래스에서 게임판을 전달받았으므로 draw에서 surface안써줘도됨
    window.fill((0, 0, 0))
    window.blit(board_img, (150, 50))
    # arrow(-stones[now_select].angle)
    # arrow2(stones[now_select].x, stones[now_select].y, -stones[now_select].angle)
    arrow(arrow_img, stones[now_select].angle, (stones[now_select].x, stones[now_select].y))
    for stone in stones:  # 바둑 돌
        if stone.visible:
            stone.draw()
    textprint(score())
    textprint("선택한 돌의 방향", 800, 530)
    if turn == 0:
        textprint("WHITE TURN", 800, 400)
    else:
        textprint("GRAY TURN", 800, 400)

    for stone in stones:
        if stone.mass == 0:
            textprint("------- WHITE -------", 800, 100)
        if stone.mass == 5:
            textprint("-------  GRAY -------", 800, 230)
        if not stone.visible:
            textprint("%d 은 죽었습니다." % (stone.mass + 1), 800, 120 + stone.mass * 20 + (stone.mass // 5) * 30)
        else:
            textprint("%d 은 살아있습니다." % (stone.mass + 1), 800, 120 + stone.mass * 20 + (stone.mass // 5) * 30)

    pygame.display.flip()


def new_move():
    for i in range(movement_substeps):
        for p in stones:
            if p.visible:
                p.move(dt / float(movement_substeps))  # 보일 때만 움직임
            for q in stones:
                if p != q:
                    collide(p, q)
                    if not q.visible and p.bycon == q.mass:
                        stones[q.bycon].check_alive(q.mass)
                    if not p.visible and q.bycon == p.mass:
                        stones[p.bycon].check_alive(p.mass)


def arrow(surface, angle, pivot):

    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.

    rect = rotated_image.get_rect(center=pivot + rotated_offset)
    window.blit(rotated_image, rect)  # Blit the rotated image.
    pygame.draw.circle(window, (30, 250, 70), pivot, 3)  # Pivot point.
    # pygame.draw.rect(window, (30, 250, 70), rect, 1)  # The rect.


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)


def cvgame():
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        results = hands.process(image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 즉, 업지손가락 끝은 landmark[4]에, 검지 손가락 끝은 landmark[8]에 좌표값이 반환되는데,
        # 좌표값은 image상의 x,y위치값을 0.0~1.0 사이의 값으로 표시한다. 즉 image 좌측 최상단은 x=0.0 y=0.0  우측최하단은 x=1.0, y=1.0이 된다.
        # 따라서int(hand_landmarks.landmark[4].x * 100)은 엄지손가락 끝의 x좌표를 100분율로 표시한 것이 된다.
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # finger1 = int(hand_landmarks.landmark[4].x * 100 )
                # finger2 = int(hand_landmarks.landmark[8].x * 100 )
                dist = abs(
                    math.dist(
                        [hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y],
                        [hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y],
                    )
                )
                cv2.putText(
                    # image, text='f1=%d f2=%d dist=%d ' % (finger1,finger2,dist), org=(10, 30),
                    image,
                    text="dist=%f " % (dist),
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=255,
                    thickness=3,
                )

                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("image", image)
        if cv2.waitKey(1) == ord("q"):
            break


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    t = threading.Thread(target=cvgame)
    t.start()

    clock = pygame.time.Clock()
    while True:
        # print(pygame.mouse.get_pos())  # 마우스 위치
        temp = now_select

        key_event = pygame.key.get_pressed()
        # 방향조절
        if key_event[pygame.K_LEFT]:
            stones[now_select].angle += -5
        elif key_event[pygame.K_RIGHT]:
            stones[now_select].angle -= -5
        stones[now_select].angle %= 360

        vel, now_select, newturn = stoneshooting(stones[now_select], now_select, turn)

        if vel == -111 and now_select == -111:  # 종료
            break

        if stones[now_select].is_dead():
            now_select += 1
            now_select %= 10

        stones[now_select].color = SELECTED
        turn = newturn
        if now_select != temp:
            if stones[temp].team == 0:
                stones[temp].color = WHITE
            else:
                stones[temp].color = GRAY

        stones[now_select].vel = stones[now_select].vel + vel
        new_move()
        new_draw()
        if abs(turn * 9 - now_select) >= 5:
            for p in stones:
                if turn == 1:
                    if p.mass > 4 and p.visible:
                        now_select = p.mass
                        break
                else:
                    if p.mass <= 4 and p.visible:
                        now_select = p.mass
                        break
            if now_select != temp:
                if stones[temp].team == 0:
                    stones[temp].color = WHITE
                else:
                    stones[temp].color = GRAY

        game_result = score()
        if game_result == "GRAY WIN" or game_result == "WHITE WIN":
            # 게임 오버 메시지
            game_font = pygame.font.Font(None, 40)
            msg = game_font.render(game_result, True, YELLOW)  # 노란색
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            window.blit(msg, msg_rect)
            pygame.time.delay(2000)
            break

        clock.tick(FPS)

    pygame.display.update()
    pygame.quit()
    sys.exit()
