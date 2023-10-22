import cv2
import mediapipe as mp
import time


class HandDetector:
    def __init__(
        self
        # mode=False,
        # num_hands=2,
        # min_hand_detection_confidence=0.5,
        # min_tracking_confidence=0.5,
    ) -> None:

        # self.mode = mode
        # self.num_hands = num_hands
        # self.min_hand_confidence = min_hand_detection_confidence
        # self.min_tracking_confidence = min_tracking_confidence

        
        self.fingers_head_marks = [4, 8 , 12, 16, 20]

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils

        self.hand_detected = False

    def detect_hands(self, img, show_connections=True):
        self.hand_detected = False
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:  # If detecting hand
            self.hand_detected = True
            for hand_lms in self.results.multi_hand_landmarks:
                if show_connections:
                    self.mp_drawing.draw_landmarks(
                        img, hand_lms, self.mp_hands.HAND_CONNECTIONS
                    )

        return img

    def landmarks_coordinate(self, img, hand_num=0, show_pointer=True) -> list:
        self.lmList = []
        img_heigh, img_width, imgc = img.shape

        if self.results.multi_hand_landmarks:
            hand_lms = self.results.multi_hand_landmarks[hand_num]
            for id, lm in enumerate(hand_lms.landmark):
                if id == 4:
                    mark_point_x, mark_point_y = int(lm.x * img_width), int(
                        lm.y * img_heigh
                    )
                    if show_pointer:
                        cv2.circle(
                            img,
                            (mark_point_x, mark_point_y),
                            10,
                            (255, 0, 0),
                            cv2.FILLED,
                        )
                self.lmList.append([id, int(lm.x * img_width), int(lm.y * img_heigh)])

        return self.lmList
    
    def witch_hand(self): # 1 for right| 0 for left
        if self.hand_detected:
            hand_lm0_x = self.lmList[self.fingers_head_marks[0]][1]
            hand_lm1_x  = self.lmList[self.fingers_head_marks[1]][1]

            if hand_lm0_x < hand_lm1_x :
                # Left hand
                return 0
            else:
                # Right_hand
                return 1

    def fingersState(self): # Open 1 | close 0
        fingers_state = []
        if self.hand_detected:
            if self.witch_hand():
                if self.lmList[self.fingers_head_marks[0]][1] > self.lmList[self.fingers_head_marks[0]-1][1]:
                    fingers_state.append(1)
                else :
                    fingers_state.append(0)
            else:
                if self.lmList[self.fingers_head_marks[0]][1] < self.lmList[self.fingers_head_marks[0]-1][1]:
                    fingers_state.append(1)
                else :
                    fingers_state.append(0)

            for head_mark_id in range(1, 5):
                if self.lmList[self.fingers_head_marks[head_mark_id]][2] < self.lmList[self.fingers_head_marks[head_mark_id] - 2][2]:
                    fingers_state.append(1)
                else:
                    fingers_state.append(0)
        return fingers_state

        


def main():
    capture = cv2.VideoCapture(0)
    detector = HandDetector()
    cur_time = 0
    prev_time = 0
    while True:
        cur_time = time.time()
        fps = 1 / (cur_time - prev_time)
        prev_time = cur_time

        success, img = capture.read()
        img = cv2.flip(img, 1)
        img = detector.detect_hands(img)
        
        #print(detector.landmarks_coordinate(img)[8], detector.landmarks_coordinate(img)[6])
        detector.landmarks_coordinate(img)

        # if detector.hand_detected:
        #     print(detector.fingersState())

        cv2.putText(
            img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0), 3
        )
        # Displaying Image
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
