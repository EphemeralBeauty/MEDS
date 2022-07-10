import cv2
import mediapipe
import time
import pyautogui

screenWidth, screenHeight = pyautogui.size()
pyautogui.FAILSAFE = False

def initialization():
    video = cv2.VideoCapture(0) #It should be a good practicte to implement some video selector for the end user
    handsdetector = mediapipe.solutions.hands
    handsdetection = handsdetector.Hands(static_image_mode=False,max_num_hands=4,min_detection_confidence=0.4, min_tracking_confidence=0.5)
    drawing = mediapipe.solutions.drawing_utils #Yay!
    return video, handsdetector, handsdetection, drawing

def move(x, y, image_height, image_width):
    currentMouseX, currentMouseY = pyautogui.position()
    x = (x*screenWidth)/image_width
    y = (y*screenHeight)/image_height
    print(x, y)
    pyautogui.moveTo(x, y)

def checkdistance(r, m, l):
    firstdist = abs(r[0] - m[0]) + abs(r[1] - m[1])
    secondist = abs(m[0] - l[0]) + abs(m[1] - l[1])
    if firstdist <= secondist:
        return True
    else:
        return False

def mainhands():
    video, handsdetector, handsdetection, drawing = initialization()
    ctime, ptime = 0, 0
    success, img = video.read()
    image_height, image_width, _ = img.shape
    while True:
        success, img = video.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = handsdetection.process(imgRGB)
        print(results)
        print("End of test.\n\n")
        if results.multi_hand_landmarks:
            for positions in results.multi_hand_landmarks:
                r = [positions.landmark[handsdetector.HandLandmark.INDEX_FINGER_TIP].x * image_width, positions.landmark[handsdetector.HandLandmark.INDEX_FINGER_TIP].y * image_height]
                m = [positions.landmark[handsdetector.HandLandmark.MIDDLE_FINGER_TIP].x * image_width, positions.landmark[handsdetector.HandLandmark.MIDDLE_FINGER_TIP].y * image_height]
                l = [positions.landmark[handsdetector.HandLandmark.RING_FINGER_TIP].x * image_width, positions.landmark[handsdetector.HandLandmark.RING_FINGER_TIP].y * image_height]
                r[0], r[1] = int(r[0]), int(r[1])
                m[0], m[1] = int(m[0]), int(m[1])
                l[0], l[1] = int(l[0]), int(l[1])
                cv2.circle(img, (r[0], r[1]), 3, (255,0,255), cv2.FILLED)
                move(r[0], r[1], image_height, image_width)
                if checkdistance(r, m, l) == True:
                    pyautogui.click()
        cv2.imshow("Image", img)
        cv2.waitKey(1)

mainhands()
