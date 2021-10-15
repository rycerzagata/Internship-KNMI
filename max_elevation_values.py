import time

import numpy as np
import gdal
import math
import pandas as pd
import matplotlib.pyplot as plt
from numba import jit, njit, prange
from pvlib import solarposition


def rotate(origin: (float, float), point: (float, float), angle: float):
    """

    :param origin: A tuple with the X and Y position of the image origin.
    :param point: A tuple with X and Y position of a point that is supposed to be rotated.
    :param angle: The rotation angle, given in degrees.
    :return The coordinates of a point rotated clockwise by a given angle around a given origin.
    """
    angle = math.radians(-angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def linear(x0: int, z0: int, x1: int, z1: int, x: float):
    """
    Perform linear interpolation for x, y between (x0,y0) and (x1,y1)
    """
    return z0 + (z1 - z0) / (x1 - x0) * (x - x0)


def interpolate(height_map: np.array, point: (float, float)) -> float:
    """

    :param point: A tuple with the X and Y position of a point.
    :param height_map: 2D Numpy array of floating point values representing height readings
    :return: Bi-linear interpolation from height_map at a given point
    """
    # if condition returns False, AssertionError is raised
    # row, column = y, x

    x, y = point
    assert height_map.shape[0] - 1 > x >= 0  # , f"x:{x} out of bounds: (0, {height_map.shape[0] - 1})"
    assert height_map.shape[1] - 1 > y >= 0  # , f"y:{y} out of bounds: (0, {height_map.shape[1] - 1})"

    # Interpolate values
    x1 = math.floor(x)
    y1 = math.floor(y)
    x2 = math.ceil(x)
    y2 = math.ceil(y)

    z00 = height_map[y1, x1]
    z10 = height_map[y2, x1]
    z01 = height_map[y1, x2]
    z11 = height_map[y2, x2]

    if x2 == x1 and y2 == y1:
        interpolated_value = z00
    elif x2 == x1 and y1 < y2:
        interpolated_value = linear(y1, z00, y2, z11, y)
    elif y2 == y1 and x1 < x2:
        interpolated_value = linear(x1, z00, x2, z11, x)
    else:
        w11 = (x2 - x) * (y2 - y) / (x2 - x1) * (y2 - y1)
        w12 = (x2 - x) * (y - y1) / (x2 - x1) * (y2 - y1)
        w21 = (x - x1) * (y2 - y) / (x2 - x1) * (y2 - y1)
        w22 = (x - x1) * (y - y1) / (x2 - x1) * (y2 - y1)
        interpolated_value = w11 * z00 + w12 * z01 + w21 * z10 + w22 * z11

    return interpolated_value


def convert_to_alpha(origin: (float, float), point: (float, float), res: (float, float),
                     elevation_value: float) -> float:
    """

    :param origin: Coordinates of the origin.
    :param point: A tuple with the X and Y position of a point.
    :param res: A tuple with the X and Y spatial resolution of the height map in meters.
    :param elevation_value: Interpolated surface elevation value in the point in meters.
    :return: Look angle?.
    """
    ox, oy = origin
    x, y = point
    resx, resy = res
    dx, dy = (x - ox) * resx, (y - oy) * resy
    distance_from_origin = math.sqrt(dx * dx + dy * dy)

    alpha_radians = np.arctan(elevation_value / distance_from_origin)
    alpha = math.degrees(alpha_radians)

    return alpha


def get_points_from_rotation(origin: (float, float), angle: float, num_of_samples: int, height: int) -> np.array:
    """

    :param origin: Coordinates of the origin.
    :param angle: Angle in degrees.
    :param num_of_samples: Number of samples to be taken from the path.
    :param height: The height of the image (from the bottom to the top).
    :return: Coordinates of the points where a sample is taken.
    """
    step = (height - 2.1) // 2 / num_of_samples
    ox, oy = origin
    list_of_points = np.zeros((num_of_samples, 2))
    for i in range(num_of_samples):
        base_point = ox, oy + step * (i + 1)
        rotated_point = rotate(origin, base_point, angle)
        list_of_points[i, 0] = rotated_point[0]
        list_of_points[i, 1] = rotated_point[1]

    return list_of_points


@njit(parallel=True)
def scan_environment(height_map: np.array,
                     origin: (float, float),
                     res: (float, float),
                     num_of_samples: int,
                     num_of_rotations: int) -> np.array:
    """

    :param num_of_samples: Number of samples taken on a line from origin to the edge of height_map
    :param height_map: 2D Numpy array of floating point values representing height readings
    :param origin: Point which serves as an anchor for the rotation
    :param res: A tuple with the X and Y spatial resolution of the height map in meters
    :return: 360 x sampling step array where each row represent a full sampling done on each rotation
    """

    samples = np.zeros((num_of_rotations, num_of_samples), dtype='float')
    for rotation in prange(num_of_rotations):
        sample_index = 0
        angle = rotation / num_of_rotations * 360
        # Update deltas according to current rotation
        all_points = get_points_from_rotation(origin=origin,
                                              angle=angle,
                                              num_of_samples=num_of_samples,
                                              height=height_map.shape[1])
        for point in all_points:
            elevation_value = interpolate(height_map=height_map, point=point)
            samples[rotation, sample_index] = convert_to_alpha(origin=origin,
                                                               point=point,
                                                               res=res,
                                                               elevation_value=elevation_value)
            sample_index += 1
    return samples


def load_data(path: str) -> np.array:
    """
    Import a cropped DSM as a numpy array
    :return:
    """
    ds = gdal.Open(path)
    return np.array(ds.GetRasterBand(1).ReadAsArray())


def plot_heights_and_sun(height_values: np.array,
                         lat: float,
                         lon: float,
                         number_rotations: int,
                         timezone: str = 'Europe/Amsterdam') -> None:
    """

    :param height_values:
    :param lat:
    :param lon:
    :param number_rotations: 
    :param timezone:
    :return:
    """
    times = pd.date_range('2019-01-01 00:00:00', '2020-01-01', closed='left', freq='MS', tz=timezone)
    solpos = solarposition.get_solarposition(times, lat, lon)

    # remove nighttime
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]

    # plot the shade using the function fill_between
    max_angles = np.max(height_values, axis=1)
    x_array = np.linspace(0, 360, number_rotations)

    fig, ax = plt.subplots()

    for hour in np.unique(solpos.index.hour):
        # choose label position by the largest elevation for each hour
        subset = solpos.loc[solpos.index.hour == hour, :]
        height = subset.apparent_elevation
        pos = solpos.loc[height.idxmax(), :]
        ax.text(pos['azimuth'], pos['apparent_elevation'], str(hour))

    for date in pd.to_datetime(['2019-01-21', '2019-02-21', '2019-03-21',
                                '2019-04-21', '2019-05-21', '2019-06-21', '2019-12-21']):
        times = pd.date_range(date, date + pd.Timedelta('24h'), freq='5min', tz=timezone)
        solpos = solarposition.get_solarposition(times, lat, lon)
        solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
        label = date.strftime('%Y-%m-%d')
        ax.plot(solpos.azimuth, solpos.apparent_elevation, label=label)

    ax.figure.legend(loc='upper right')
    ax.set_xlabel('Solar Azimuth (degrees)')
    ax.set_ylabel('Solar Elevation (degrees)')
    ax.fill_between(x_array, max_angles, 0)

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    print('Compiling helper functions to C...')
    interpolate = jit()(interpolate)
    linear = jit()(linear)
    get_points_from_rotation = jit()(get_points_from_rotation)
    convert_to_alpha = jit()(convert_to_alpha)
    rotate = jit()(rotate)
    print('Done')

    lat, lon = 52.434883, 6.262284  # Heino AWS
    height_map = np.zeros((60, 60))
    height_map[10][10] = 200
    number_samples = 5000
    number_rotations = 10000

    print('Scanning environment...')
    start_time = time.time()

    test_samples = scan_environment(height_map=height_map,
                                    origin=(30, 30),
                                    res=(1, 1),
                                    num_of_samples=number_samples,
                                    num_of_rotations=number_rotations)
    print(f'Scanning took {time.time() - start_time :.6f} seconds')

    plot_heights_and_sun(height_values=test_samples,
                         lat=lat,
                         lon=lon,
                         number_rotations=number_rotations)
