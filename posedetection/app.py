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
import poseDetection
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
target_id = 'No Target'
target_lum = 0
alive_ticks = 0


# HTTP POST data and save it
@app.route('/', methods=['GET', 'POST'])
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
        hit_sound = pygame.mixer.Sound(resource_path('assets/gwanjung2.wav'))
        hit_sound.play()
        return 'File upload complete'
# HTTP POST, 'i am alive' message
@app.route('/iamalive', methods=['POST'])
def i_am_alive():
    global target_lum, target_id, alive_ticks
    upload_data = request.json
    if upload_data:
        Semaphore.acquire()
        target_id = upload_data.get("identity")
        target_lum = upload_data.get("lum")
        Semaphore.release()
        #convert string data to numpy array
        print(target_lum)
        print(target_id)
        #reset alive timer
        alive_ticks = pygame.time.get_ticks()
        return 'iamalive upload complete', 200
    else:
        return 'Bad request',400
    
class Console():
    def __init__(self):
        self.start = False
        #image = cv2.imread(resource_path('assets/Intro.jpg'))
        #image2 = cv2.resize(image,(3840,2160))
        #cv2.imwrite(image2,resource_path('assets/Intro.jpg'))
        self.image_intro = pygame.image.load(resource_path('assets/Intro.jpg'))
        self.font120 = pygame.font.SysFont('FixedSys',140,False,False)
        self.font80 = pygame.font.SysFont('FixedSys',80,False,False)
        self.font50 = pygame.font.SysFont('FixedSys',50,False,False)
        self.sound_intro = pygame.mixer.Sound(resource_path('assets/Intro.wav'))
        self.intro_on = True
        self.replay_video_capture = None
        #initialize picamera2
        self.picam2 = Picamera2()
        self.picam2.start_preview(Preview.NULL)
        capture_config = self.picam2.create_still_configuration(main={"size":(SCREEN_WIDTH//2,SCREEN_HEIGHT//2),"format":"BGR888"})
        self.picam2.configure(capture_config)
        controls = {
            "AeMeteringMode": 0,
            "ExposureValue":1.9,
            "AwbEnable":True,
    #        "AeExposureRegion":(0.25,0.25,0.5,0.5),
    #        "ExposureTime":6000,
    #        "AnalogueGain":1.0,
        }
        self.picam2.start()
        self.picam2.set_controls(controls)
    #    self.picam2.set_controls({"AeEnable":True,"AeExposureMode": controls.AeExposureModeEnum.Long}) #Normal,Short,Long
    #    self.picam2.set_controls({"AwbEnable":True,"AwbMode": controls.AwbModeEnum.Cloudy}) #
    #    self.picam2.set_controls({"ExposureTime":50000,"AnalogueGain":1.0})
        self.detection = poseDetection.Detection()
        time.sleep(1)          
    #이벤트 처리
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    poseDetection.is_triggered = True
                elif event.key == pygame.K_DOWN:
                    poseDetection.is_replaying = False
                elif event.key == pygame.K_LEFT:
                    poseDetection.is_replaying = False
                elif event.key == pygame.K_RIGHT:
                    poseDetection.is_replaying = False
        return False
    # Console logic
    def run_logic(self):
        global target_id, alive_ticks
        elapsed_time = (pygame.time.get_ticks() - alive_ticks) / 1000
        if(elapsed_time > 20):
            target_id = 'No Target'
    
    # Draw text
    def draw_text(self,screen,text,font,x,y,main_color):
        text_obj = font.render(text,True,main_color)
        text_rect = text_obj.get_rect()
        text_rect.midleft = x,y
        screen.blit(text_obj,text_rect)
        
    # display Intero image
    def display_intro(self,screen):
        screen.fill(GREEN)
        #image = cv2.resize(self.image_intro,(3840,2160))
        screen.blit(self.image_intro,[0,0])
        draw_x = int(SCREEN_WIDTH/3)
        draw_y = int(SCREEN_HEIGHT/2 - 100)
        self.draw_text(screen,"Bullseye Hit Monitoring System",self.font80,draw_x,draw_y,BLUE)    
        self.sound_intro.play()

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
        #Print target status
        s = "%s: lum(%03d)" % (target_id, target_lum)
        draw_x = 100
        draw_y = int(SCREEN_HEIGHT - 200)
        if target_id == 'No Target':
            self.draw_text(screen,s,self.font50,draw_x,draw_y,RED)
        else:
            self.draw_text(screen,s,self.font50,draw_x,draw_y,BLUE)
        #Print recording status
        draw_x = SCREEN_WIDTH // 2 - 300
        draw_y = 100
        if poseDetection.is_recording:
            self.draw_text(screen,"Recording!",self.font50,draw_x,draw_y,RED)
        elif poseDetection.is_replaying:
            self.draw_text(screen,"Replaying!",self.font50,draw_x,draw_y,YELLOW) 
        else:
            self.draw_text(screen,"Preview",self.font50,draw_x,draw_y,WHITE) 
        
    # Display camera frame
    def display_camera(self,screen):
        image = None
        image = self.picam2.capture_array("main")
        if image is not None:
            # mediapipe를 이용한 동작 인식
            landmarks_image = self.detection.pose_detection(image)
            #image_rot = np.rot90(landmarks_image,1)
            image_rot = np.rot90(image,1)
            im_surface = pygame.pixelcopy.make_surface(image_rot)
            screen.blit(im_surface,(int(SCREEN_WIDTH/2),0))
            #screen.blit(im_surface,(640,0))

    def trigger_replay(self):
        #global is_replaying, is_recording, replay_video_capture 
        if not poseDetection.is_replaying and not poseDetection.is_recording:
            video_files = [f for f in os.listdir(poseDetection.REPLAY_FOLDER) if f.endswith(".avi")]
            if video_files:
                latest_video = max(
                    video_files,
                    key=lambda f: os.path.getmtime(os.path.join(poseDetection.REPLAY_FOLDER,f)),
                )
                #filepath = os.path.join(poseDetection.REPLAY_FOLDER,latest_video)
                filepath = os.path.join(poseDetection.REPLAY_FOLDER,'replay_video.avi')
                self.replay_video_capture = cv2.VideoCapture(filepath)
                self.replay_video_capture.set(cv2.CAP_PROP_FPS,FPS*0.3)  #Set replay speed to 0.3 x
                poseDetection.is_replaying = True
                print(f"Replaying {latest_video}")
            else:
                print("No replaying videos found.")
 
    #Display the Recorded Frames
    def display_replay(self,screen):
        #global is_replaying, is_recording, replay_video_capture 
        if poseDetection.is_replaying and self.replay_video_capture.isOpened():
            ret,replay_frame = self.replay_video_capture.read()
            if ret:
                replay_frame = cv2.cvtColor(replay_frame,cv2.COLOR_BGR2RGB)
                replay_frame = cv2.rotate(replay_frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
                target_width = SCREEN_WIDTH // 2
                target_height = SCREEN_HEIGHT // 2
                #Resize
                aspect_ratio = replay_frame.shape[1] / replay_frame.shape[0]
                if aspect_ratio > target_width / target_height:
                    new_width = target_width
                    new_height = int(target_height/aspect_ratio)
                else:
                    new_height = target_height
                    new_width = int(target_height*aspect_ratio)
                #replay_frame = cv2.resize(replay_frame,(new_width,new_height))
                #Center position
                #x_offset = SCREEN_WIDTH // 2 + (target_width - new_width) // 2
                #y_offset = SCREEN_HEIGHT // 2 + (target_height - new_height) // 2
                x_offset = SCREEN_WIDTH // 2
                y_offset = 0
                #replay_video_rect = pygame.Rect(x_offset,y_offset,new_width,new_height)
                replay_video_rect = pygame.Rect(x_offset,y_offset,replay_frame.shape[1],replay_frame.shape[0])
                replay_surface = pygame.surfarray.make_surface(replay_frame)
                screen.blit(replay_surface,replay_video_rect)
            else:
                poseDetection.is_replaying = False
                self.replay_video_capture.release()
                print("Replaying finished!")
# relative address to absolute address
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("/home/user/Bullseye")
    return os.path.join(base_path, relative_path)
  
def thread_pygame():
    pygame.init()
    pygame.display.set_caption("Bullseye")
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    console = Console()
    start_ticks = pygame.time.get_ticks()

    done = False
    print('pygame start!\n')
    
    while not done:
        done = console.process_events()
        if console.intro_on:
            console.display_intro(screen)
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            if(elapsed_time > 5):
                console.intro_on = False
        else:
            console.run_logic()
            console.display_frame(screen)
            console.display_camera(screen)
            if poseDetection.is_triggered:
                console.trigger_replay()
                poseDetection.is_triggered = False
                poseDetection.is_replaying = True
            elif poseDetection.is_replaying:
                console.display_replay(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

thread_1 = threading.Thread(target=thread_pygame)
thread_1.start()

if __name__ == '__main__':
    app.run(host='192.168.0.130', port=8000, debug=False)
    #app.run(host='220.81.195.192', port=8000, debug=False)
