import os
import cv2
import imutils
import numpy as np
import scripts.utils as utils
from datetime import datetime


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
conveyor_speed = 7  # cm/s
conveyor_speed_px = conveyor_speed * pixels_per_centimeter  # px/s
objects_per_column = 6
h_distance_between_columns = (object_width + 4) * pixels_per_centimeter  # px
v_distance_between_lines = int(np.ceil((height + object_height_px) / (objects_per_column + 1)))  # px
line_positions = range(v_distance_between_lines - object_height_px, height, v_distance_between_lines)
column_positions = range(-(int(np.ceil(width / h_distance_between_columns)) + 3) * h_distance_between_columns,
                         -h_distance_between_columns + 1, h_distance_between_columns)
FPS = 30
video_duration = 30  # s
pixels_shift_per_frame = conveyor_speed_px / FPS
half_object_width_px = round(object_width_px / 2)  # px
half_object_height_px = round(object_height_px / 2)  # px

noise_object_position = 0.5  # x: evenly distributed random value in the range [-x cm, x cm]
noise_position = noise_object_position * pixels_per_centimeter
object_characteristics = np.zeros(
    (1, len(line_positions), 5))  # pos_noise_x, pos_noise_y, size_noise_x, size_noise_y, rotation
column_matching = [x for x in range(len(column_positions))]

noise_object_size = 0.5  # x: evenly distributed random value in the range [-x cm, x cm]
noise_size = noise_object_size * pixels_per_centimeter
norm_params = np.array([[-20, 6], [0, 4], [20, 6]])
norm_weights = [1.0/18.0, 16.0/18.0, 1.0/18.0]

fourcc = cv2.VideoWriter_fourcc(*'MP42')
os.makedirs("../results", exist_ok=True)
video = cv2.VideoWriter('../results/video_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.avi', fourcc, float(FPS), (width, height))

bg_pattern = cv2.imread('../images/background/bg2.jpg')
toast = cv2.imread('../images/toast/toast1.png', cv2.IMREAD_UNCHANGED)
toast_resized = cv2.resize(toast, (object_width_px, object_height_px), interpolation=cv2.INTER_AREA)


def add_objects(background, object, x_pos, bg_limit):
    h, w = background.shape[0], min(bg_limit, background.shape[1])
    obj_h, obj_w = object.shape[0], h_distance_between_columns

    for i, x in enumerate(range(x_pos - obj_w, w, obj_w)):
        for j, y in enumerate(line_positions):
            if all(object_characteristics[i, j, :] == np.zeros(5)):
                object_characteristics[i, j, 0] = round(np.random.uniform(-noise_position, noise_position, 1)[0])
                object_characteristics[i, j, 1] = round(np.random.uniform(-noise_position, noise_position, 1)[0])
                object_characteristics[i, j, 2] = round(np.random.uniform(-noise_size, noise_size, 1)[0])
                object_characteristics[i, j, 3] = round(np.random.uniform(-noise_size, noise_size, 1)[0])
                object_characteristics[i, j, 4] = utils.mixture_gaussian(norm_params, norm_weights)

            obj_rotated = imutils.rotate_bound(object, object_characteristics[i, j, 4])
            dx = round((obj_rotated.shape[1] - object.shape[1]) / 2.0)
            dy = round((obj_rotated.shape[0] - object.shape[0]) / 2.0)

            x = x - dx + int(object_characteristics[i, j, 0])
            y = y - dy + int(object_characteristics[i, j, 1])

            utils.overlay_images(background, obj_rotated, x, y)


def add_background(background, x_pos):
    w, h, _ = background.shape
    bgp_w, bgp_h, _ = bg_pattern.shape

    for i in range(x_pos-bgp_h, h, bgp_h):
        for j in range(0, w, bgp_w):
            utils.overlay_images(frame, bg_pattern, i, j)


pixels_count = 0
pixels_accumulator = 0.0
background_shift = 0
objects_shift = 0
for f in range(FPS * video_duration):
    utils.print_progress_bar(f, FPS * video_duration - 1, prefix='Progress:', suffix='Complete', length=50)

    pixels_accumulator += pixels_shift_per_frame
    iteration_shift = int(np.ceil(pixels_accumulator))
    pixels_accumulator -= iteration_shift
    pixels_count += iteration_shift

    if objects_shift + iteration_shift >= h_distance_between_columns:
        if pixels_count >= width + h_distance_between_columns:
            object_characteristics = np.delete(object_characteristics, -1, 0)
        object_characteristics = np.insert(object_characteristics, 0, 0, axis=0)

    frame = np.zeros([height, width, 3], dtype=np.uint8)
    frame.fill(255)

    background_shift = (background_shift+iteration_shift)%bg_pattern.shape[1]
    add_background(frame, background_shift)

    objects_shift = (objects_shift + iteration_shift) % h_distance_between_columns
    add_objects(frame, toast_resized, objects_shift, pixels_count)

    video.write(frame)

video.release()
