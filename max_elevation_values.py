import os

os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'
os.chdir("C:/Users/HP/Documents/Internship/Data")

import numpy as np
import gdal

# Import a cropped DSM as a numpy array
fp = r"C:/Users/HP/Documents/Internship/Data/dsm_voorschoten_RD_clip.tif"
ds = gdal.Open(fp)
myarray = np.array(ds.GetRasterBand(1).ReadAsArray())
print(myarray.shape)


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degrees.
    """
    angle = -math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


import numpy as np
import math


def interpolate(height_map: np.arrray, x: float, y: float) -> float:
    """

    :param y:
    :param x:
    :param height_map: 2D Numpy array of floating point values representing height readings
    :return: Bi-linear interpolation from height_map at a given point
    """

    # TODO Test if it works, implement edge case checks and finish documentation

    # Take care of edge cases, i.e. when a point is outside or on the edge of height_map
    # ....
    # if condition returns False, AssertionError is raised:
    # assert x == "goodbye", "x should be 'hello'"

    # Interpolate values
    z00 = height_map[math.floor(x), math.floor(y)]
    z10 = height_map[math.ceil(x), math.floor(y)]
    z01 = height_map[math.floor(x), math.ceil(y)]
    z11 = height_map[math.ceil(x), math.ceil(y)]

    return z00 * (1 - x) * (1 - y) + z10 * x * (1 - y) + z01 * (1 - x) * y + z11 * x * y


def get_deltas_from_rotation(origin: (float, float), point: (float, float), angle: int) -> (float, float):
    # TODO Document and implement, now it returns mock values
    qx, qy = rotate(origin, point, angle)
    ox, oy = origin
    dx = qx - ox
    dy = qy - oy

    return dx, dy


def scan_environment(height_map: np.array, origin: (float, float), sampling_step: float) -> np.array:
    """

    :param sampling_step: Sampling advances by this amount on a line from origin to the edge of height_map
    :param height_map: 2D Numpy array of floating point values representing height readings
    :param origin: Point which serves as an anchor for the rotation
    :return: 360 x sampling step array where each row represent a full sampling done on each rotation
    """

    # TODO Test if it works

    samples = np.zeros((360, sampling_step), dtype='float')
    for rotation in range(360):
        x, y = origin
        sample_index = 0
        # Update deltas according to current rotation
        delta_x, delta_y = get_deltas_from_rotation(rotation)
        while 0 < x <= len(height_map) and 0 < y <= len(height_map[x]):
            x += delta_x
            y += delta_y
            samples[rotation, sample_index] = interpolate(height_map, x, y)
            sample_index += 1

    return samples
