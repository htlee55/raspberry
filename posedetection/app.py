from flask import Flask, request
import pygame
import os
import sys
import datetime
import threading
import numpy as np
import cv2
from picamera2 import Picamera2, Preview
import time
from posedetection import PoseDetection
from libcamera import controls

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GREEN = (100,200, 100)
WHITE = (255, 255, 255)
BLUE = (20, 60, 120)
RED = (250, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

FPS = 60

app = Flask(__name__)

# Mutual Exclusion
Semaphore = threading.Semaphore(1)

hit_time = datetime.datetime.now()

# HTTP POST data and save it
@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    global hit_time
    if request.method == 'POST':
        imagestr = request.files['image']  #f는 파일 객체
        #convert string data to numpy array
        npimg = np.frombuffer(imagestr.read(),np.uint8)
        #convert numpy array to image
        img = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
        img2 = cv2.resize(img,(960,1080))
        Semaphore.acquire()
        cv2.imwrite(resource_path('assets/image1.jpg'),img2)
        print("Add image to queue.")
        Semaphore.release()
        #Image processing here!
        #Save hitting time, display it
        hit_time = datetime.datetime.now()   
        #hitting sound
        #hit_sound = pygame.mixer.Sound(resource_path('assets/gwanjung2.wav'))
        #hit_sound.play()
        return 'File upload complete'
    
class Console():
    def __init__(self):
        self.start = False
#        self.image_intro = pygame.image.load(resource_path('assets/Intro.jpg'))
        self.font120 = pygame.font.SysFont('FixedSys',140,False,False)
        self.font80 = pygame.font.SysFont('FixedSys',80,False,False)
        self.font50 = pygame.font.SysFont('FixedSys',50,False,False)
#        self.sound_intro = pygame.mixer.Sound(resource_path('assets/Intro.wav'))
#        self.intro_on = True
        #initialize picamera2
        self.picam2 = Picamera2()
        self.picam2.start_preview(Preview.NULL)
        capture_config = self.picam2.create_still_configuration(main={"size":(SCREEN_WIDTH//2,SCREEN_HEIGHT//2),"format":"BGR888"})
        self.picam2.configure(capture_config)
        controls = {
            "AeMeteringMode": 0,
            "ExposureValue":1.9,
            "AwbEnable":True,
        }
        self.picam2.start()
        self.picam2.set_controls(controls)
        self.detection = PoseDetection()
        time.sleep(1)          
    #이벤트 처리
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
#            elif event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_UP:
#                    PoseDetection.is_triggered = True
#                elif event.key == pygame.K_DOWN:
#                    PoseDetection.is_replaying = False
#                elif event.key == pygame.K_LEFT:
#                    PoseDetection.is_replaying = False
#                elif event.key == pygame.K_RIGHT:
#                    PoseDetection.is_replaying = False
#        return False
    
    # Draw text
    def draw_text(self,screen,text,font,x,y,main_color):
        text_obj = font.render(text,True,main_color)
        text_rect = text_obj.get_rect()
        text_rect.midleft = x,y
        screen.blit(text_obj,text_rect)
        
    # display console frame
    def display_frame(self,screen):
        global hit_time, target_id, target_lum
        screen.fill(GREEN)
        # target image
        Semaphore.acquire()
        image = pygame.image.load(resource_path('assets/image1.jpg'))
        Semaphore.release()
        screen.blit(image,[0,0])
        # display current time
        now = datetime.datetime.now()
        s = "%04d-%02d-%02d %02d:%02d:%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        draw_x = SCREEN_WIDTH//4
        draw_y = int(SCREEN_HEIGHT - 100)
        self.draw_text(screen,s,self.font50,draw_x,draw_y,BLUE)
        # display hitting time
        s = "%04d-%02d-%02d %02d:%02d:%02d" % (hit_time.year, hit_time.month, hit_time.day, hit_time.hour, hit_time.minute, hit_time.second)
        draw_x = 100
        draw_y = int(SCREEN_HEIGHT - 100)
        self.draw_text(screen,s,self.font50,draw_x,draw_y,RED)
       
    # Display camera frame
    def display_camera(self,screen):
        image = None
        image = self.picam2.capture_array("main")
        if image is not None:
            # mediapipe를 이용한 동작 인식
            landmarks_image = self.detection.process_frame(image)
            #image_rot = np.rot90(landmarks_image,1)
            image_rot = np.rot90(image,1)
            im_surface = pygame.pixelcopy.make_surface(image_rot)
            screen.blit(im_surface,(int(SCREEN_WIDTH/2),0))
            #screen.blit(im_surface,(640,0))

# relative address to absolute address
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("/home/user/workspace/posedetection")
    return os.path.join(base_path, relative_path)
  
def thread_pygame():
    pygame.init()
    pygame.display.set_caption("Server")
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    console = Console()
#    start_ticks = pygame.time.get_ticks()

    done = False
    print('pygame start!\n')
    
    while not done:
        console.display_frame(screen)
        console.display_camera(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

thread_1 = threading.Thread(target=thread_pygame)
thread_1.start()

if __name__ == '__main__':
    app.run(host='192.168.137.182', port=5000, debug=False)
    #app.run(host='220.81.195.192', port=8000, debug=False)
