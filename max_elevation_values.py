import numpy as np
import math
import gdal


def rotate(origin: (float, float), point: (float, float), angle: int):
    import math
    """
    
    :param origin: A tuple with the X and Y position of the image origin.
    :param point: A tuple with X and Y position of a point that is supposed to be rotated.
    :param angle: The rotation angle, given in degrees.
    :return The coordinates of a point rotated counterclockwise by a given angle around a given origin.
    """
    angle = -math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def interpolate(height_map: np.array, point: (float, float)) -> float:
    """
    :param point: A tuple with the X and Y position of a point.
    :param height_map: 2D Numpy array of floating point values representing height readings
    :return: Bi-linear interpolation from height_map at a given point
    """

    # TODO Test if it works, implement edge case checks and finish documentation

    # Take care of edge cases, i.e. when a point is outside or on the edge of height_map

    # if condition returns False, AssertionError is raised

    # row, column = y, x

    x, y = point
    assert height_map.shape[0] > x >= 0, "x out of bounds"
    assert height_map.shape[1] > y >= 0, "y out of bounds"

    # Interpolate values
    x1 = math.floor(x)
    y1 = math.floor(y)
    x2 = math.ceil(x)
    y2 = math.ceil(y)

    z00 = height_map[y1, x1]
    z10 = height_map[y2, x1]
    z01 = height_map[y1, x2]
    z11 = height_map[y2, x2]

    def linear(x0: float, z0: float, x1: float, z1: float, x: float):
        """Perform linear interpolation for x, y between (x0,y0) and (x1,y1) """
        return z0 + (z1 - z0)/(x1 - x0) * (x - x0)

    if x2 == x1 and y2 == y1:
        interpolated_value = z00
    elif x2 == x1 and y1 < y2:
        interpolated_value = linear(y1, z00, y2, z11, y)
    elif y2 == y1 and x1 < x2:
        interpolated_value = linear(x1, z00, x2, z11, x)
    else:
        w11 = (x2 - x)*(y2 - y)/(x2 - x1)*(y2 - y1)
        w12 = (x2 - x)*(y - y1)/(x2 - x1)*(y2 - y1)
        w21 = (x - x1)*(y2 - y)/(x2 - x1)*(y2 - y1)
        w22 = (x - x1)*(y - y1)/(x2 - x1)*(y2 - y1)
        interpolated_value = w11*z00 + w12*z01 + w21*z10 + w22*z11

    return interpolated_value


def get_points_from_rotation(origin: (float, float), angle: int, num_of_samples: int, height: int) -> np.array:
    # na podstawie kata obrotu w stopniach i ilości sampli zrob liste z pozycjami punktów
    """
    :param origin: Coordinates of the origin.
    :param angle: Angle in degrees.
    :param num_of_samples: Number of samples to be taken from the path.
    :param height: The height of the image (from the bottom to the top).
    :return: Coordinates of the points where a sample is taken.
    """
    step = height // 2 // num_of_samples
    ox, oy = origin
    list_of_points = np.zeros((num_of_samples, 2), dtype=tuple)
    for i in range(num_of_samples):
        base_point = ox, oy + step * i
        rotated_point = rotate(origin, base_point, angle)
        list_of_points[i, 0] = base_point
        list_of_points[i, 1] = rotated_point

    return list_of_points


def scan_environment(height_map: np.array, origin: (float, float), num_of_samples: int) -> np.array:
    """
    :param num_of_samples: Number of samples taken on a line from origin to the edge of height_map
    :param height_map: 2D Numpy array of floating point values representing height readings
    :param origin: Point which serves as an anchor for the rotation
    :return: 360 x sampling step array where each row represent a full sampling done on each rotation
    """

    # TODO Change sampling_step to num_step

    samples = np.zeros((360, num_of_samples), dtype='float')
    for rotation in range(360):
        sample_index = 0
        # Update deltas according to current rotation
        all_points = get_points_from_rotation(origin=origin,
                                              angle=rotation,
                                              num_of_samples=num_of_samples,
                                              height=height_map.shape[1])
        rotated_points = all_points[:, 1]
        for point in rotated_points:
            samples[rotation, sample_index] = interpolate(height_map, point)
            sample_index += 1
    return samples


def load_data() -> np.array:
    # os.environ['PROJ_LIB'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/proj'
    # os.environ['GDAL_DATA'] = 'C:/Users/HP/anaconda3/envs/knmi/Library/share/gdal'

    # Import a cropped DSM as a numpy array
    path = r"dsm_voorschoten_RD_clip.tif"
    ds = gdal.Open(path)
    return np.array(ds.GetRasterBand(1).ReadAsArray())


if __name__ == '__main__':
    height_map = load_data()
    test_samples = scan_environment(height_map=height_map, origin=(643, 652), num_of_samples=10)