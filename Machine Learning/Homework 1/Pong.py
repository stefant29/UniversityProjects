import pygame
import random
from pygame.locals import *
from copy import copy
import sys
from time import sleep
import time

RUNNING = True

TOP = 0
BOTTOM = 1

ACTIONS = ["UP", "DOWN"]

TIMEOUT = 60
EPSILON = 0.05
ALPHA = 0.9
BETA = 0.1
SCORE = {"enemy": 0, "player": 0}

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

TEXT_HEIGHT = 15
SPACE = 10
global BAR_SIZE

class Game(object):
    #      Game(screensize, speed, ball_position, ball_size, ball_direct, bar_size, colors):
    def __init__(self, screensize, speed, ball_position, ball_size, ball_direct, bar_size, colors):
        # initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((int(screensize[0]*1.25), screensize[1]))
        self.clock = pygame.time.Clock()
        self.game_state = RUNNING
        self.speed = speed
        self.width = screensize[0]
        self.height = screensize[1]

        # create game elements
        self.ball = Ball(screensize, speed, ball_position, ball_size, ball_direct, colors["ball"])
        self.enemyBar = Bar(screensize, speed, bar_size[0], bar_size[1], TOP, colors["enemyBar"])
        self.playerBar = Bar(screensize, speed, bar_size[0], bar_size[1], BOTTOM, colors["playerBar"])

        self.menuRect = pygame.Rect(self.width, 0, self.width*0.25, self.height)

        text1_y = self.menuRect.top + TEXT_HEIGHT+SPACE
        text2_y = self.menuRect.top + (TEXT_HEIGHT+SPACE)*2
        text3_y = self.menuRect.top + (TEXT_HEIGHT+SPACE)*3
        text4_y = self.menuRect.top + (TEXT_HEIGHT+SPACE)*4
        self.text5_y = self.menuRect.top + (TEXT_HEIGHT+SPACE)*5
        self.text6_y = self.menuRect.top + (TEXT_HEIGHT+SPACE)*6
        self.text7_y = self.menuRect.top + (TEXT_HEIGHT+SPACE)*7

        self.arrowUp1 = ArrowUp((self.menuRect.center[0] - self.menuRect.width/2 + TEXT_HEIGHT, text1_y), TEXT_HEIGHT, red)
        self.arrowUp2 = ArrowUp((self.menuRect.center[0] - self.menuRect.width/2 + TEXT_HEIGHT, text2_y), TEXT_HEIGHT, red)
        self.arrowUp3 = ArrowUp((self.menuRect.center[0] - self.menuRect.width/2 + TEXT_HEIGHT, text3_y), TEXT_HEIGHT, red)
        self.arrowUp4 = ArrowUp((self.menuRect.center[0] - self.menuRect.width/2 + TEXT_HEIGHT, text4_y), TEXT_HEIGHT, red)

        self.arrowDown1 = ArrowDown((self.menuRect.center[0] + self.menuRect.width/2 - TEXT_HEIGHT, text1_y), TEXT_HEIGHT, red)
        self.arrowDown2 = ArrowDown((self.menuRect.center[0] + self.menuRect.width/2 - TEXT_HEIGHT, text2_y), TEXT_HEIGHT, red)
        self.arrowDown3 = ArrowDown((self.menuRect.center[0] + self.menuRect.width/2 - TEXT_HEIGHT, text3_y), TEXT_HEIGHT, red)
        self.arrowDown4 = ArrowDown((self.menuRect.center[0] + self.menuRect.width/2 - TEXT_HEIGHT, text4_y), TEXT_HEIGHT, red)

    def text_objects(self, text, font):
        textSurface = font.render(text, True, white)
        return textSurface, textSurface.get_rect()

    def printText(self,text,position):
        largeText = pygame.font.Font('freesansbold.ttf',TEXT_HEIGHT)
        TextSurf, TextRect = self.text_objects(text, largeText)
        TextRect.center = position
        self.screen.blit(TextSurf, TextRect)

    def drawRect(self, rect, color):
        pygame.draw.rect(self.screen, color, rect, 0)

    def drawTriangleUp(self, center, size, color):
        top = [center[0], center[1] - size / 2]
        left = [center[0] - size/2, center[1] + size/2]
        right = [center[0] + size/2, center[1] + size/2]
        pygame.draw.polygon(self.screen, color, [top, left, right], 0)

    def print_menu(self, Q_len, score1, score2):
        self.drawRect(self.menuRect, black)

        self.printText("Epsilon: " + str(EPSILON), (self.menuRect.center[0], self.arrowUp1.center[1]))
        self.printText("Alpha: " + str(ALPHA), (self.menuRect.center[0], self.arrowUp2.center[1]))
        self.printText("Beta: " + str(BETA), (self.menuRect.center[0], self.arrowUp3.center[1]))
        self.printText("Bar size", (self.menuRect.center[0], self.arrowUp4.center[1]))

        self.printText("Player1: " + str(score1), (self.menuRect.center[0], self.text5_y))
        self.printText("Player2: " + str(score2), (self.menuRect.center[0], self.text6_y))
        self.printText("Len(Q): " + str(Q_len), (self.menuRect.center[0], self.text7_y))

        self.arrowUp1.draw(self.screen)
        self.arrowUp2.draw(self.screen)
        self.arrowUp3.draw(self.screen)
        self.arrowUp4.draw(self.screen)
        self.arrowDown1.draw(self.screen)
        self.arrowDown2.draw(self.screen)
        self.arrowDown3.draw(self.screen)
        self.arrowDown4.draw(self.screen)

    def startLearningGame(self, Q, test, test_no, adv_action_func=None):
        global EPSILON, ALPHA, BETA, SCORE, BAR_SIZE
        time_start = time.time()

        if test:
            state = get_initial_state(self.ball, self.enemyBar)
        else:
            state_bar1 = get_initial_state(self.ball, self.enemyBar)
            state_bar2 = get_initial_state(self.ball, self.playerBar)
        

        while self.game_state:
            # timeout, DRAW
            if (time.time()-time_start > TIMEOUT):
                SCORE["enemy"] += 1
                SCORE["player"] += 1
                return Q

            # limit the fps
            self.clock.tick(64)

            # draw background
            self.screen.fill((100,100,100))

            self.print_menu(len(Q), SCORE["enemy"], SCORE["player"])

            if test:
                actions = get_legal_actions(state)
                action = epsilon_greedy(Q, state, actions)

                                            # apply action and get the next state and the reward
                next_state, reward = apply_action(state, action, self.enemyBar)  # next_state = s'

                # get the best next action a' for next state s'
                next_best_action = best_action(Q, next_state, get_legal_actions(next_state))
                
                # q[s,a] = q[s,a] + alfa * (r + beta * maxQ(s',a') - q[s,a])
                Q[(state, action)] = Q.get((state, action), 0) + ALPHA * (reward + BETA * Q.get((next_state, next_best_action), 0) - Q.get((state, action),0))
                # advance state
                state = next_state
            else:
                # choose the best action
                action_bar1 = best_action(Q, state_bar1, get_legal_actions(state_bar1))
                state_bar1, reward = apply_action(state_bar1, action_bar1, self.enemyBar)

                action_bar2 = adv_action_func(Q, state_bar2, get_legal_actions(state_bar2))
                state_bar2, reward = apply_action(state_bar2, action_bar2, self.playerBar)


            # event handlers: keyboard, mouse input
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.arrowUp1.checkCollision(pos):
                        EPSILON += 0.01
                    if self.arrowDown1.checkCollision(pos) and EPSILON > 0.01:
                        EPSILON -= 0.01
                    if self.arrowUp2.checkCollision(pos):
                        ALPHA += 0.01
                    if self.arrowDown2.checkCollision(pos) and ALPHA > 0.01:
                        ALPHA -= 0.01
                    if self.arrowUp3.checkCollision(pos):
                        BETA += 0.01
                    if self.arrowDown3.checkCollision(pos) and BETA > 0.01:
                        BETA -= 0.01
                    if self.arrowUp4.checkCollision(pos):
                        BAR_SIZE[1] += 10
                        self.enemyBar.setHeight(BAR_SIZE[1])
                        self.playerBar.setHeight(BAR_SIZE[1])
                    if self.arrowDown4.checkCollision(pos) and BAR_SIZE[1] > 85:
                        BAR_SIZE[1] -= 10
                        self.enemyBar.setHeight(BAR_SIZE[1])
                        self.playerBar.setHeight(BAR_SIZE[1])

                if event.type == QUIT:
                    self.game_state = not RUNNING

                if event.type == pygame.KEYDOWN:
                    # player BAR
                    if event.key == pygame.K_UP:
                        self.playerBar.move = "UP"
                    elif event.key == pygame.K_DOWN:
                        self.playerBar.move = "DOWN"
                    elif event.key == pygame.K_s:
                        return Q
                elif event.type == KEYUP:
                    if event.key == K_UP or event.key == K_DOWN:
                        self.playerBar.move = "STOP"

            ballMove = self.ball.move(self.enemyBar, self.playerBar, test)
            if ballMove == 1:
                SCORE["enemy"] += 1
                return Q
            elif ballMove == 2:
                SCORE["player"] += 1
                return Q

            if test:
                state = (state[0], self.ball.directionY, self.ball.y)
            else:
                state_bar1 = (state_bar1[0], self.ball.directionY, self.ball.y)
                state_bar2 = (state_bar2[0], self.ball.directionY, self.ball.y)

            # draw elements on screen
            self.ball.draw(self.screen)
            self.enemyBar.draw(self.screen)
            if not test:
                self.playerBar.draw(self.screen)

            # switch screen
            pygame.display.flip()

        # close game
        pygame.quit()

class ArrowUp(object):
    def __init__(self, center, size, color):
        top = [center[0], center[1] - size / 2]
        left = [center[0] - size/2, center[1] + size/2]
        right = [center[0] + size/2, center[1] + size/2]
        self.points = [top, left, right]
        self.center = center
        self.size = size
        self.color = color

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.points, 0)

    def checkCollision(self, mouse):
        return mouse[0] > self.points[1][0] and mouse[0] < self.points[2][0] and mouse[1] > self.points[0][1] and mouse[1] < self.points[1][1]

class ArrowDown(object):
    def __init__(self, center, size, color):
        bottom = [center[0], center[1] + size / 2]
        left = [center[0] - size/2, center[1] - size/2]
        right = [center[0] + size/2, center[1] - size/2]
        self.points = [bottom, left, right]
        self.center = center
        self.size = size
        self.color = color

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.points, 0)

    def checkCollision(self, mouse):
        return mouse[0] > self.points[1][0] and mouse[0] < self.points[2][0] and mouse[1] > self.points[1][1] and mouse[1] < self.points[0][1]

class Ball(object):
    def __init__(self, screensize, speed, position, size, direction, color):
        self.x = position[0]
        self.y = position[1]
        self.size = size

        self.screensize = screensize
        self.speed = speed

        self.directionX = direction[0]
        self.directionY = direction[1]

        self.rect = pygame.Rect(self.x-self.size,self.y-self.size,self.size*2, self.size*2)

        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.size, 0)

    def move(self, bar1, bar2, test):
        if self.x + self.directionX * self.speed + self.size >= self.screensize[0]:
            if test:
                self.directionX = -1
            else:
                return 1 #1 a castigat
        if self.x + self.directionX * self.speed - self.size <= 0:
            return 2 #2 a castigat

        # collision with Bars
        if self.rect.right + self.directionX * self.speed >= bar2.rect.left and self.rect.top < bar2.rect.bottom and self.rect.bottom > bar2.rect.top:
            self.directionX = -1
        if self.rect.left + self.directionX * self.speed <= bar1.rect.right and self.rect.top < bar1.rect.bottom and self.rect.bottom > bar1.rect.top:            
            self.directionX = 1

        if self.y + self.directionY * self.speed + self.size >= self.screensize[1]:
            self.directionY = -1
        if self.y + self.directionY * self.speed - self.size <= 0:
            self.directionY = 1

        # move ball
        self.x += self.directionX * self.speed
        self.y += self.directionY * self.speed

        # recenter ball
        self.rect.center = (self.x, self.y)
        return 0

class Bar(object):
    def __init__(self, screensize, speed, width, height, position, color):
        self.screensize = screensize
        self.x = position * (screensize[0] - width) + int(width/2)
        self.y = int(screensize[1] / 2)

        self.height = height
        self.width = width
        self.speed = speed

        self.rect = pygame.Rect(self.x-int(self.width/2), self.y-int(self.height/2), self.width, self.height)
        self.color = color
        self.move = "STOP"

    def moveRight(self):
        if self.x + self.width / 2 + self.speed < self.screensize[0]:
            self.x += self.speed
            self.rect.center = (self.x, self.y)

    def moveLeft(self):
        if self.x - self.width / 2 - self.speed > 0:
            self.x -= self.speed
            self.rect.center = (self.x, self.y)

    def draw(self, screen):
        if self.move == "UP":
            self.moveUp()
        elif self.move == "DOWN":
            self.moveDown()
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def moveUp(self):
        if self.y - self.height / 2 - self.speed > 0:
            self.y -= self.speed
            self.rect.center = (self.x, self.y)

    def moveDown(self):
        if self.y + self.height / 2 + self.speed < self.screensize[1]:
            self.y += self.speed
            self.rect.center = (self.x, self.y)

    def setHeight(self, BAR_SIZE):
        self.height = BAR_SIZE
        self.rect = pygame.Rect(self.x-int(self.width/2), self.y-int(self.height/2), self.width, self.height)


def random_choice(Q, state, legal_actions):
    return random.choice(legal_actions)

def epsilon_greedy(Q, state, legal_actions):
    # Epsilon greedy
    probab = random.random()

    # unexplored actions
    actions_not_explored = [action for action in legal_actions if (state, action) not in Q]

    # apply an unexplored action
    if len(actions_not_explored) > 0:
        return random.choice(actions_not_explored)
    else:
        # random
        if probab < EPSILON:
            return random.choice(legal_actions)
        # best action
        else:
            return best_action(Q, state, legal_actions)

def best_action(Q, state, legal_actions):
    # Best action: action with maximum score out of th legal actions
    best_action_ = random.choice(legal_actions)
    best_score = -sys.maxint
    # sarch in actions
    for action in legal_actions:
        # check if the current action has a better score
        crt_score = Q.get((state, action),0)
        if (state, action) in Q and crt_score >= best_score:            
            best_score = crt_score
            best_action_ = action
    return best_action_

# Return the initial state of the game
def get_initial_state(ball, bar):
    return (bar.y, ball.directionY, ball.y)

# Return the available actions in a given state
def get_legal_actions(state):
    return copy(ACTIONS)

# Apply the action on the bar
def apply_action(state, action, bar):
    next_state = copy(state)
    reward = 0
    if action == ACTIONS[0]:  # up
        next_state = (state[0]-bar.speed, state[1], state[2])
        bar.moveUp()
        if state[1] == -1:
            reward = 1
        elif state[1] == 1:
            reward = -1
    elif action == ACTIONS[1]: # down
        next_state = (state[0]+bar.speed, state[1], state[2])
        bar.moveDown()
        if state[1] == -1:
            reward = -1
        elif state[1] == 1:
            reward = 1

    return next_state, reward

# generate a random game with given size and speed
def random_game(screensize, speed):
    ball_position = (random.randint(screensize[0]*0.1,screensize[0]*0.9), random.randint(screensize[1]*0.1,screensize[1]*0.9)) #(300,300)
    ball_direct = (random.choice([-1,1]), random.choice([-1,1])) #(1,1)
    ball_size = int(min(screensize[0], screensize[1])*0.02)
    color1 = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    color2 = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    color3 = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    #      Game(screensize, speed, ball_position, ball_size, ball_direct, bar_size, colors):
    return Game(screensize, speed, ball_position, ball_size, ball_direct, BAR_SIZE, {"ball": color1, "enemyBar": color2, "playerBar": color3})

def test_game(Q, no_tests, speed, screensize, testing, random_choice_function, message):
    for i in range(0, no_tests):
        game = random_game(screensize, speed)
        Q = game.startLearningGame(Q, testing, i, random_choice_function)
        print("===== " + message + " =====  Game: " + str(i+1) + "   " + str(len(Q)) + "  score: " + str(SCORE) + " =====")
    return Q

if __name__ == "__main__":
    global BAR_SIZE

    Q = {}
    screensize = (800,600)
    BAR_SIZE = [screensize[0]*0.03,screensize[1]*0.25]

    # Learning to play: creating Q
    time_start = time.time()
    Q = test_game(Q, 200, 3, screensize, True, None, "LEARNING")
    print("learned in: " + str(time.time()-time_start));
    
    # testing against random, greedy and epsilon-greedy enemies
    test_game(Q, 100, 3, screensize, False, random_choice, "RANDOM")
    test_game(Q, 100, 3, screensize, False, best_action, "GREEDY")
    test_game(Q, 100, 3, screensize, False, epsilon_greedy, "epsGREEDY")
