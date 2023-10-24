import cv2
#import mediapipe
import numpy as np
import time
import os
import math
from hand_tracking_module import HandDetector


# Initialisations
BOARD_NAME = "boards_folder/virtual_bord"
BOARD_NUM = 0
cap  = cv2.VideoCapture(0)
windw_heigh = 640
windw_width = 480

prev_time = 0
cur_time = 0

image_file_path = "virtual_painter_header"
header_image_heigh = 70
img_canevas = np.zeros((windw_width, windw_heigh , 3), np.uint8)

detector = HandDetector()

# Configuration
cap.set(3, windw_heigh)
cap.set(4, windw_width)

# Importing header images
folder_content = os.listdir(image_file_path)
images_list = []
for image in folder_content:
    images_list.append(cv2.imread("{}/{}".format(image_file_path, image)))

#print(folder_content)
header_image = images_list[0]
drawing_color = (255,0,0)
drawing_point_size = 15
active_title_list = ["Blue Brush", "Ereaser", "Green Brush", "Pink Brush"]
active_title = active_title_list[0]
drawing_prev_point_x, drawing_prev_point_y = 0,0


# Settings

# Limite size
min_hand = 18
max_hand = 160

# Volume
min_drawing_size = 5
max_drawing_size = 50


while cap.isOpened():
    PICTURE_TAKEN = False

    cv2.waitKey(10)
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img[0:header_image_heigh, 0:windw_width] = header_image

    cur_time = time.time()
    fps = 1/(cur_time-prev_time)
    prev_time = cur_time

    detector.detect_hands(img)
    lm_2dim_position = detector.landmarks_coordinate(img)
    fingers_state = detector.fingersState()
    # print(fingers_state)

    if detector.hand_detected:
        drawing_finger_x, drawing_finger_y = lm_2dim_position[8][1:]

        #setting mode
        if fingers_state[4]:
            cv2.putText(img, "SETTING MODE", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 136, 255), 2)
            setting_finger_x, setting_finger_y = lm_2dim_position[20][1:]
            thumb_x, thumb_y = lm_2dim_position[4][1:]
            
            cv2.circle(img, (setting_finger_x, setting_finger_y), drawing_point_size, (0, 136, 255), cv2.FILLED)
            cv2.circle(img, (drawing_finger_x, drawing_finger_y), 15, (0, 136, 255), cv2.FILLED)
            cv2.circle(img, (thumb_x, thumb_y), 15, (0, 136, 255), cv2.FILLED)
            cv2.line(img, (thumb_x, thumb_y), (drawing_finger_x, drawing_finger_y), (255, 0, 0), 8)

            cv2.circle(img, (int((thumb_x+drawing_finger_x)/2), int((thumb_y+drawing_finger_y)/2)), 7, (255, 0, 0), cv2.FILLED)

            control_lenth = math.hypot(thumb_x - drawing_finger_x, thumb_y - drawing_finger_y)
            drawing_point_size = np.interp(control_lenth, [min_hand, max_hand], [min_drawing_size, max_drawing_size])
            drawing_point_size = int(drawing_point_size)
        # Picture taking
        if all(fingers_state[:3]) and not fingers_state[4]:
            cv2.putText(img, "SAVING BOARD", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

            cv2.circle(img, (lm_2dim_position[4][1], lm_2dim_position[4][2] ), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (lm_2dim_position[8][1], lm_2dim_position[8][2] ), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (lm_2dim_position[12][1], lm_2dim_position[12][2] ), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (lm_2dim_position[16][1], lm_2dim_position[16][2] ), 15, (255, 0, 255), cv2.FILLED)

            cv2.imwrite(BOARD_NAME+str(BOARD_NUM)+".png", img_canevas)
            PICTURE_TAKEN = True
            
        # Drawing mode
        elif fingers_state[1] and not fingers_state[2] and not fingers_state[4]:
            if PICTURE_TAKEN:
                BOARD_NUM+=1
            if drawing_finger_y > 76 :
                cv2.circle(img, (drawing_finger_x, drawing_finger_y), drawing_point_size, drawing_color, cv2.FILLED)
                if drawing_prev_point_x==0 and drawing_prev_point_y==0:
                    drawing_prev_point_x, drawing_prev_point_y = drawing_finger_x, drawing_finger_y

                cv2.line(img_canevas, (drawing_finger_x, drawing_finger_y), (drawing_prev_point_x, drawing_prev_point_y), drawing_color, drawing_point_size)
                drawing_prev_point_x, drawing_prev_point_y = drawing_finger_x, drawing_finger_y
        
        
        if fingers_state[1] and fingers_state[2] and not fingers_state[4]: # Selection mode
            # 0px : 74 px | 75- 175| 176-276 | 277-377 | 378-478
            cv2.putText(img, "SELECTION MODE", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
            drawing_prev_point_x, drawing_prev_point_y = 0,0

            if drawing_finger_y < 75 :
                if drawing_finger_x > 0 and drawing_finger_x <= 74:
                    cv2.putText(img, "ABODJI Kondi Kaled", (50, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

                elif drawing_finger_x > 75 and drawing_finger_x <= 175:
                    drawing_color = (255,0,0)
                    header_image = images_list[0]
                    #drawing_point_size = 15
                    active_title = active_title_list[0]

                elif drawing_finger_x > 176 and drawing_finger_x <= 276:
                    drawing_color = (255,0,255)
                    header_image = images_list[-1]
                    #drawing_point_size = 15
                    active_title = active_title_list[-1]

                elif drawing_finger_x > 277 and drawing_finger_x <= 377:
                    drawing_color = (0,255,0)
                    header_image = images_list[2]
                    #drawing_point_size = 15
                    active_title = active_title_list[2]
                elif drawing_finger_x > 378 and drawing_finger_x <= 480:
                    drawing_color = (0,0,0)
                    header_image = images_list[1]
                    #drawing_point_size = 25
                    active_title = active_title_list[1]

            assist_finger_x, assist_finger_y = lm_2dim_position[12][1:]
            cv2.circle(img, (int((drawing_finger_x+assist_finger_x)/2), int((drawing_finger_y+assist_finger_y)/2)), 25, (255,128,0), cv2.FILLED)


    img_gray = cv2.cvtColor(img_canevas,cv2.COLOR_BGR2GRAY)
    _, img_binary = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
    img_binary = cv2.cvtColor(img_binary, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, img_binary)
    img = cv2.bitwise_or(img, img_canevas)
    
    cv2.putText(img, "FPS : {}".format(str(int(fps))), (480, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
    cv2.putText(img, active_title, (480, 65), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, drawing_color, 1)
    #cv2.imshow("Canevas", img_canevas)
    cv2.imshow("Image", img)

cv2.destroyAllWindows()