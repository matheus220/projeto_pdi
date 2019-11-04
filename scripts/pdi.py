import os
import cv2
import imutils
import numpy as np
from datetime import datetime


def mixture_gaussian():
    norm_params = np.array([[-20, 1.5],
                            [0, 0.8],
                            [20, 1.5]])
    # Weight of each component, in this case all of them are 1/3
    weights = [1.0/10.0, 8.0/10.0, 1.0/10.0]
    # A stream of indices from which to choose the component
    mixture_id = np.random.choice(len(weights), size=1, replace=True, p=weights)[0]
    # y is the mixture sample
    return np.random.normal(*(norm_params[mixture_id]))


def overlay_images(background, image, pos_x, pos_y):
    bg_w, bg_h, _ = background.shape
    im_w, im_h, a = image.shape

    x_min, x_max = max(pos_y, 0), min(pos_y + im_w, bg_w)
    y_min, y_max = max(pos_x, 0), min(pos_x + im_h, bg_h)

    if x_max < 0 or x_min >= bg_w or y_max < 0 or y_min >= bg_h:
        return None

    x_im_min, x_im_max = x_min-pos_y, im_w-(pos_y+im_w-x_max)
    y_im_min, y_im_max = y_min-pos_x, im_h-(pos_x+im_h-y_max)

    if a == 4:
        alpha_im = image[x_im_min:x_im_max, y_im_min:y_im_max, 3] / 255.0
        alpha_bg = (1.0 - alpha_im)

        for c in range(0, 3):
            background[x_min:x_max, y_min:y_max, c] = alpha_im*image[x_im_min:x_im_max, y_im_min:y_im_max, c] \
                                                      + alpha_bg*background[x_min:x_max, y_min:y_max, c]
    else:
        background[x_min:x_max, y_min:y_max] = image[x_im_min:x_im_max, y_im_min:y_im_max]

# All times are in seconds
# All distances are in centimeters.

width = 1280
height = 720
conveyor_width = 100  # cm
pixels_per_centimeter = round(width / conveyor_width)
conveyor_height = round(height / pixels_per_centimeter)  # cm
object_width = 8  # cm
object_height = 5.77  # cm
object_width_px = round(object_width * pixels_per_centimeter)  # px
object_height_px = round(object_height * pixels_per_centimeter)  # px
conveyor_speed = 10  # cm/s
conveyor_speed_px = conveyor_speed * pixels_per_centimeter  # px/s
objects_per_column = 4
h_distance_between_columns = (object_width + 3) * pixels_per_centimeter  # px
v_distance_between_lines = int(np.ceil((height + object_height_px) / (objects_per_column + 1)))  # px
line_positions = range(v_distance_between_lines - object_height_px, height, v_distance_between_lines)
column_positions = range(-(int(np.ceil(width / h_distance_between_columns)) + 3) * h_distance_between_columns,
                         -h_distance_between_columns + 1, h_distance_between_columns)
FPS = 30
video_duration = 10  # s
pixels_shift_per_frame = conveyor_speed_px / FPS
half_object_width_px = round(object_width_px / 2)  # px
half_object_height_px = round(object_height_px / 2)  # px

noise_object_position = 0.8  # x: evenly distributed random value in the range [-x cm, x cm]
noise_position = noise_object_position * pixels_per_centimeter
object_characteristics = np.zeros(
    (len(column_positions), len(line_positions), 5))  # pos_noise_x, pos_noise_y, size_noise_x, size_noise_y, rotation
column_matching = [x for x in range(len(column_positions))]

noise_object_size = 0.5  # x: evenly distributed random value in the range [-x cm, x cm]
noise_size = noise_object_size * pixels_per_centimeter

fourcc = cv2.VideoWriter_fourcc(*'MP42')
os.makedirs("../results", exist_ok=True)
video = cv2.VideoWriter('../results/video_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.avi', fourcc, float(FPS), (width, height))

bg_pattern = cv2.imread('../images/background/bg2.jpg')
toast = cv2.imread('../images/toast/toast1.png', cv2.IMREAD_UNCHANGED)
toast_resized = cv2.resize(toast, (object_width_px, object_height_px), interpolation=cv2.INTER_AREA)

def add_objects(background):
    for i, x in enumerate(column_positions):
        for j, y in enumerate(line_positions):
            i = column_matching[i]
            if all(object_characteristics[i, j, :] == np.zeros(5)):
                object_characteristics[i, j, 0] = round(np.random.uniform(-noise_position, noise_position, 1)[0])
                object_characteristics[i, j, 1] = round(np.random.uniform(-noise_position, noise_position, 1)[0])
                object_characteristics[i, j, 2] = round(np.random.uniform(-noise_size, noise_size, 1)[0])
                object_characteristics[i, j, 3] = round(np.random.uniform(-noise_size, noise_size, 1)[0])
                object_characteristics[i, j, 4] = mixture_gaussian()

            x += int(object_characteristics[i, j, 0])
            y += int(object_characteristics[i, j, 1])
            rotated = imutils.rotate_bound(toast_resized, object_characteristics[i, j, 4])

            overlay_images(background, rotated, x, y)


def add_background(background, x_pos):
    w, h, _ = background.shape
    bgp_w, bgp_h, _ = bg_pattern.shape

    for i in range(x_pos-bgp_h, h, bgp_h):
        for j in range(0, w, bgp_w):
            overlay_images(frame, bg_pattern, i, j)


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


pixels_accumulator = 0.0
background_shift = 0
print()
for f in range(FPS * video_duration):
    progress = round(f / (FPS * video_duration) * 100)
    print_progress_bar(f, FPS * video_duration - 1, prefix='Progress:', suffix='Complete', length=50)

    pixels_accumulator += pixels_shift_per_frame
    iteration_shift = round(pixels_accumulator)
    if iteration_shift >= 1:
        pixels_accumulator -= iteration_shift
        column_positions = list(map(lambda x: x + iteration_shift, column_positions))
        if column_positions[-1] >= int(np.ceil(width / h_distance_between_columns) + 1) * h_distance_between_columns:
            difference = column_positions[-1] - int(
                np.ceil(width / h_distance_between_columns) + 1) * h_distance_between_columns + 1
            column_positions.pop()
            column_matching.insert(0, column_matching.pop())
            object_characteristics[column_matching[0], :, :] = np.zeros((len(line_positions), 5))
            # np.delete(object_characteristics, -1, 0)
            column_positions.insert(0, -2 * h_distance_between_columns - 2 + difference)
            # np.insert(object_characteristics, 0, np.zeros((len(line_positions), 5)), axis=0)

    frame = np.zeros([height, width, 3], dtype=np.uint8)
    frame.fill(255)

    background_shift = (background_shift+iteration_shift)%bg_pattern.shape[1]
    add_background(frame, background_shift)
    add_objects(frame)

    video.write(frame)

video.release()
