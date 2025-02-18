import pygame
from pygame.locals import *
import matlab.engine
import time
import socket
import threading
import queue
import sys
import os

sys.path.append('matlabroot/extern/engines/python/build/lib/')
eng=matlab.engine.start_matlab()
eng.addpath('C:/Users/mech-user/jisyupro/BrainWaveGame/data/matlab')

class Client:  

    def __init__(self,q):
        self.q = q

    def c2s(self, ip, port, msg):  
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_address = (ip, port)
        s.sendto(msg.encode('utf-8'), serv_address)

class Server():
    def __init__(self,q):
        self.q = q
        self.host = "localhost"
        self.port = 8080
        self.bufsize = 1024

        self.sock =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.thread = threading.Thread(target=self.c2s, daemon=True)
        self.thread.start()

    def c2s(self):
        while True:
            msg, cli_addr = self.sock.recvfrom(self.bufsize)
            msg = msg.decode('utf-8')
            self.q.put(msg)

pygame.init() 
(w, h) = (1200, 800)
screen = pygame.display.set_mode((w, h),FULLSCREEN)

comm_queue = queue.Queue()
server = Server(comm_queue)
client = Client(comm_queue)
target_ip = "localhost"
target_port = 8080

Brain_img = pygame.image.load(os.path.join('data/images', 'brain.png')).convert_alpha() 
Brain_img = pygame.transform.scale(Brain_img,(300,250))
Brain_Wave_img = pygame.image.load(os.path.join('data/images', 'brain_wave.png')).convert_alpha() 
Brain_Wave_img = pygame.transform.scale(Brain_Wave_img,(400,400))
Noukin_img = pygame.image.load(os.path.join('data/images', 'noukin.png')).convert_alpha() 
Noukin_img = pygame.transform.scale(Noukin_img,(300,250))
pygame.display.set_icon(Brain_img)

game_name = '脳波ゲーム'
pygame.display.set_caption(game_name)
FONT = 'data/fonts/Arial'
# FONT = 'data/fonts/HinaMincho-Regular.ttf'
BLACK = (0,0,0)
WHITE = (255,255,255)
TURQUOISE = (0,206,175)
BLEU_CLAIR = (0,229,195)

initial = True
game = False
debug = False

def Std():
    # screen.fill((252,249,239))
    screen.fill((252,237,248))
    pygame.time.wait(30)

def Quit():
    pygame.quit()
    sys.exit()

def QuitStd():
    for event in pygame.event.get(): 
        if event.type == QUIT:
            Quit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                Quit()
            if event.key == K_q:
                Quit()

def Text(text,font,size,color,center_x,center_y):
    Font = pygame.font.Font(font, size)
    Surf = Font.render(text, True, color)
    Rect = Surf.get_rect()
    Rect.center = (center_x,center_y)
    screen.blit(Surf,Rect)

def DrawButton(msg,size,color,x,y,w,h,action = None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen,(100,100,100),Rect(x,y,w,h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(screen,(200,200,200),Rect(x,y,w,h))

    Text(msg,FONT,size,color,(x+(w/2)),(y+(h/2)))


def GameStart():
    global initial
    global game
    initial = False
    game = True

def Initial():
    global debug
    debug = False
    comm_queue.queue.clear()
    while initial:
        Std()
        # screen.blit(Brain_img,(w/2 - 150,h/3 - 150))
        screen.blit(Brain_Wave_img,(w/2 - 200,h/3 - 250))
        Text(game_name,FONT,100,BLACK,w/2,h/2)
        DrawButton("Start",20,BLACK,w/4,h/4*3,100,50,GameStart)
        DrawButton("Quit",20,BLACK,w - w/4,h/4*3,100,50,Quit)

        if(debug):
            Text('Debug mode',FONT,20,BLACK,w/2,h/4)

        pygame.display.update() 

        for event in pygame.event.get(): 
            if event.type == QUIT:
                Quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    Quit()
                if event.key == K_d:
                    debug ^= 1


def CountDown():
    start_time = time.time()
    WaitingTime = 3
    if debug:
        WaitingTime = 1
    while True:
        Std()
        current_time = time.time()
        elapsed_time = int(current_time - start_time)
        if WaitingTime - elapsed_time > 0:
            Text(str(WaitingTime - elapsed_time),FONT,100,BLACK,w/2,h/2)
        else:
            Text('Go!',FONT,100,BLACK,w/2,h/2)
            if elapsed_time == WaitingTime + 1:
                break

        pygame.display.update() 
        QuitStd()

def GetFromMatlab(player_id,alpha_queue):
    alpha = 0
    if player_id == 0:
         alpha = eng.alpha1s()
         client.c2s(target_ip,target_port,str(alpha))
         pass
    else:
        if not comm_queue.empty():
            alpha = float(comm_queue.get())

    alpha_queue.put(alpha)

def AccumulatePower():

    start_time = time.time()
    time_limit = 20
    if debug:
        time_limit = 1
    time_bar_leftedge = w/10
    time_bar_rightedge = w/10*9
    time_bar_height = h / 10
    time_bar_width = w/10*8

    alpha_power = [0.0] * 2
    if debug:
        alpha_power[0] += 1

    alpha_power_width = w/10*2

    alpha_queue = [queue.Queue()] * 2 

    pos_x = [0] * 2
    pos_y = [0] * 2
    pos_x[0] = w/4
    pos_x[1] = w - w/4
    pos_y[0] = h/8*7
    pos_y[1] = h/8*7

    amp_rate = 10 ** 7
    prev_sec = 0

    while True:
        Std()


        current_time = time.time()
        elapsed_time = current_time - start_time
        elapsed_sec = int(elapsed_time)
        ratio = elapsed_time / time_limit

        if ratio > 1:
            break

        Text('Time',FONT,40,BLACK,w/20,h/20)
        Text('α波をためろ!',FONT,70,BLACK,w/2,h/10*3)

        screen.blit(Noukin_img,(w/2 - 150,h/2))

        pygame.draw.rect(screen,(0,255,0),Rect(time_bar_leftedge,time_bar_height,time_bar_width,time_bar_height))
        pygame.draw.rect(screen,(0,0,0),Rect(time_bar_leftedge + time_bar_width * (1 - ratio),time_bar_height,time_bar_width * ratio + 1,time_bar_height))
        
        for i in range(2):
            if elapsed_sec != prev_sec:
                matlab_thread = threading.Thread(target = GetFromMatlab,args = (i,alpha_queue[i]),daemon = True)
                matlab_thread.start()
            if not alpha_queue[i].empty():
                alpha_power[i] += alpha_queue[i].get() * amp_rate

            pygame.draw.rect(screen,(255 * (1 - i),0,255 * i),Rect(pos_x[i] - alpha_power_width / 2,pos_y[i] - alpha_power[i] * 0.5 - 10,alpha_power_width,alpha_power[i] * 0.5))
        
            Text(str(i + 1) + 'P\'s alpha power',FONT,20,(255 *(1 - i),0,255 * i),pos_x[i],pos_y[i])

        prev_sec = elapsed_sec
        pygame.display.update() 
        QuitStd()

    return alpha_power

def DisplayResult(alpha_power):
    global initial
    global game
    start_time = time.time()
    while True:
        Std()

        Text('結果発表!',FONT,100,BLACK,w/2,h/5)

        current_time = time.time()
        elapsed_time = current_time - start_time

        for i in range(2):

            current_color = (255 * (1 - i),0,255 * i)
            if elapsed_time >= 2 + 3 * i:
                Text(str(i + 1) + 'P\'s alpha power ...',FONT,50,current_color,w/4,h/3 * (1 + i))

            if elapsed_time >= 3.5 + 3 * i:
                Text(str(alpha_power[i]) + '!!',FONT,50,current_color,w/4 + w/2,h/3 * (1 + i))


        if elapsed_time >= 7.5:
            if alpha_power[0] > alpha_power[1]:
                # Text('1P Win!! 君こそ脳波マスターだ!!!',FONT,60,BLEU_CLAIR,w/2,h/7*6)
                Text('Win!! おめでとう!君こそ脳波マスターだ!!!',FONT,60,BLEU_CLAIR,w/2,h/7*6)
            elif alpha_power[0] < alpha_power[1]:
                Text('Lose...!!',FONT,60,BLEU_CLAIR,w/2,h/7*6)
            else:
                Text('Draw!!',FONT,60,BLEU_CLAIR,w/2,h/7*6)

        pygame.display.update() 
        for event in pygame.event.get(): 
            if event.type == QUIT:
                Quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    Quit()
                if event.key == K_x:
                    initial = True
                    game = False

        if initial:
            break


def MainGame():
    CountDown()
    alpha_power = AccumulatePower()
    DisplayResult(alpha_power)

def main():
    while(True):
        Std()

        while initial:
            Initial()

        while game:
            MainGame()

        pygame.display.update() 
        QuitStd()

if __name__ == "__main__":
    main()
