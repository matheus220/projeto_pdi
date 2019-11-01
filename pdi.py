import cv2
import sys
import numpy as np
import imutils
from cv2 import VideoWriter, VideoWriter_fourcc

def overlay_transparent(background_img, img_to_overlay_t, x, y):
    """
    @brief      Overlays a transparant PNG onto another image using CV2
    
    @param      background_img    The background image
    @param      img_to_overlay_t  The transparent image to overlay (has alpha channel)
    @param      x                 x location to place the top-left corner of our overlay
    @param      y                 y location to place the top-left corner of our overlay
    @param      overlay_size      The size to scale our overlay to (tuple), no scaling if None
    
    @return     Background image with overlay on top
    """

    # Extract the alpha mask of the RGBA image, convert to RGB 
    b,g,r,a = cv2.split(img_to_overlay_t)
    overlay_color = cv2.merge((b,g,r))
    
    # Apply some simple filtering to remove edge noise
    mask = cv2.medianBlur(a,5)

    h, w, _ = overlay_color.shape
    roi = background_img[y:y+h, x:x+w]

    # Black-out the area behind the logo in our original ROI
    img1_bg = cv2.bitwise_and(roi.copy(),roi.copy(), mask = cv2.bitwise_not(mask))
    
    # Mask out the logo from the logo image.
    img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask = mask)

    # Update the original image with our new ROI
    background_img[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)


# All times are in seconds
# All distances are in centimeters.

width = 1280
height = 720
conveyor_width = 100 # cm
pixels_per_centimeter = round(width/conveyor_width)
conveyor_height = round(height/pixels_per_centimeter) # cm
object_width = 8 # cm
object_height = 5.77 # cm
object_width_px = round(object_width*pixels_per_centimeter) # px
object_height_px = round(object_height*pixels_per_centimeter) # px
conveyor_speed = 10 # cm/s
conveyor_speed_px = conveyor_speed*pixels_per_centimeter # px/s
objects_per_column = 4
h_distance_between_columns = (object_width + 3)*pixels_per_centimeter # px
v_distance_between_lines = int(np.ceil((height+object_height_px)/(objects_per_column+1))) # px
line_positions = range(v_distance_between_lines-object_height_px, height, v_distance_between_lines)
column_positions = range(-(int(np.ceil(width/h_distance_between_columns))+3)*h_distance_between_columns, -h_distance_between_columns+1, h_distance_between_columns)
FPS = 30
video_duration = 20 # s
pixels_shift_per_frame = conveyor_speed_px/FPS
half_object_width_px = round(object_width_px/2) # px
half_object_height_px = round(object_height_px/2) # px

noise_object_position = 0.8 # x: evenly distributed random value in the range [-x cm, x cm]
noise_position = noise_object_position*pixels_per_centimeter
object_characteristics = np.zeros((len(column_positions), len(line_positions), 5)) # pos_noise_x, pos_noise_y, size_noise_x, size_noise_y, rotation
column_matching = [x for x in range(len(column_positions))]

noise_object_size = 0.5 # x: evenly distributed random value in the range [-x cm, x cm]
noise_size = noise_object_size*pixels_per_centimeter

fourcc = VideoWriter_fourcc(*'MP42')
video = VideoWriter('./pdi.avi', fourcc, float(FPS), (width, height))

toast = cv2.imread('toast.png', cv2.IMREAD_UNCHANGED)
toast_resized = cv2.resize(toast, (object_width_px, object_height_px), interpolation = cv2.INTER_AREA)

def add_object(frame, i, x, j, y):
    i = column_matching[i]
    if all(object_characteristics[i, j, :] == np.zeros(5)):
        object_characteristics[i, j, 0] = round(np.random.uniform(-noise_position, noise_position, 1)[0])
        object_characteristics[i, j, 1] = round(np.random.uniform(-noise_position, noise_position, 1)[0])
        object_characteristics[i, j, 2] = round(np.random.uniform(-noise_size, noise_size, 1)[0])
        object_characteristics[i, j, 3] = round(np.random.uniform(-noise_size, noise_size, 1)[0])
        object_characteristics[i, j, 4] = np.random.normal(0, 0.05, 1)[0]
    
    x += int(object_characteristics[i, j, 0])
    y += int(object_characteristics[i, j, 1])
    y1, y2 = y, y + toast_resized.shape[0]
    x1, x2 = x, x + toast_resized.shape[1]

    #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1, lineType=8, shift=0)
    if x2>=0 and x1<width:
        if x1<0: x1 = 0
        if x2>width: x2 = width-1
        alpha_s = toast_resized[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            if frame[y1:y2, x1:x2, c].shape != toast_resized[:, :, c].shape:
                if x1 == 0:
                    #print(y1, y2)
                    frame[y1:y2, x1:(x2+1), c] = (alpha_s[:, -(x2-x1+1):] * toast_resized[:, -(x2-x1+1):, c] + alpha_l[:, -(x2-x1+1):] * frame[y1:y2, x1:(x2+1), c])
                elif x2 == (width-1):
                    frame[y1:y2, x1:(x2+1), c] = (alpha_s[:, :(x2-x1+1)] * toast_resized[:, :(x2-x1+1), c] + alpha_l[:, :(x2-x1+1)] * frame[y1:y2, x1:(x2+1), c])
            else:
                frame[y1:y2, x1:x2, c] = (alpha_s * toast_resized[:, :, c] + alpha_l * frame[y1:y2, x1:x2, c])

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

pixels_accumulator = 0.0
print()
for f in range(FPS*video_duration):
    progress = round(f/(FPS*video_duration)*100)
    printProgressBar(f, FPS*video_duration-1, prefix = 'Progress:', suffix = 'Complete', length = 50)

    pixels_accumulator += pixels_shift_per_frame
    if round(pixels_accumulator)>=1:
        iteration_shift = round(pixels_accumulator)
        pixels_accumulator -= iteration_shift
        column_positions = list(map(lambda x: x + iteration_shift, column_positions))
        if column_positions[-1] >= int(np.ceil(width/h_distance_between_columns)+1)*h_distance_between_columns:
            difference = column_positions[-1] - int(np.ceil(width/h_distance_between_columns)+1)*h_distance_between_columns + 1
            column_positions.pop()
            column_matching.insert(0, column_matching.pop())
            object_characteristics[column_matching[0],:,:] = np.zeros((len(line_positions), 5))
            #np.delete(object_characteristics, -1, 0)
            column_positions.insert(0, -2*h_distance_between_columns-2+difference)
            #np.insert(object_characteristics, 0, np.zeros((len(line_positions), 5)), axis=0)

    frame = np.zeros([height, width, 3], dtype=np.uint8)
    frame.fill(255)

    for i, x in enumerate(column_positions):
        for j, y in enumerate(line_positions):
            add_object(frame, i, x, j, y)

    video.write(frame)

video.release()