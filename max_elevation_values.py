import numpy as np
import gdal
import math
import pandas as pd
import matplotlib.pyplot as plt

from pvlib import solarposition


def rotate(origin: (float, float), point: (float, float), angle: int):
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
    # if condition returns False, AssertionError is raised
    # row, column = y, x

    x, y = point
    assert height_map.shape[0] - 1 > x >= 0, f"x:{x} out of bounds: (0, {height_map.shape[0] - 1})"
    assert height_map.shape[1] - 1 > y >= 0, f"y:{y} out of bounds: (0, {height_map.shape[1] - 1})"

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
        # Perform linear interpolation for x, y between (x0,y0) and (x1,y1)
        return z0 + (z1 - z0) / (x1 - x0) * (x - x0)

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


def convert_to_alpha(origin: (float, float), point: (float, float), res: (float, float), elevation_value: int) -> float:
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
    distance_from_origin = math.sqrt(dx ** 2 + dy ** 2)

    alpha_radians = math.atan(elevation_value / distance_from_origin)
    alpha = math.degrees(alpha_radians)

    return alpha


def get_points_from_rotation(origin: (float, float), angle: int, num_of_samples: int, height: int) -> np.array:
    """

    :param origin: Coordinates of the origin.
    :param angle: Angle in degrees.
    :param num_of_samples: Number of samples to be taken from the path.
    :param height: The height of the image (from the bottom to the top).
    :return: Coordinates of the points where a sample is taken.
    """
    step = (height - 2.1) // 2 / num_of_samples
    ox, oy = origin
    list_of_points = []
    for i in range(1, num_of_samples + 1):
        base_point = ox, oy + step * i
        rotated_point = rotate(origin, base_point, angle)
        list_of_points.append(rotated_point)

    return list_of_points


def scan_environment(height_map: np.array, origin: (float, float), res: (float, float),
                     num_of_samples: int) -> np.array:
    """

    :param num_of_samples: Number of samples taken on a line from origin to the edge of height_map
    :param height_map: 2D Numpy array of floating point values representing height readings
    :param origin: Point which serves as an anchor for the rotation
    :param res: A tuple with the X and Y spatial resolution of the height map in meters
    :return: 360 x sampling step array where each row represent a full sampling done on each rotation
    """

    samples = np.zeros((360, num_of_samples), dtype='float')
    for rotation in range(360):
        sample_index = 0
        # Update deltas according to current rotation
        all_points = get_points_from_rotation(origin=origin,
                                              angle=rotation,
                                              num_of_samples=num_of_samples,
                                              height=height_map.shape[1])
        for point in all_points:
            elevation_value = interpolate(height_map=height_map, point=point)
            samples[rotation, sample_index] = convert_to_alpha(origin=origin,
                                                               point=point,
                                                               res=res,
                                                               elevation_value=int(elevation_value))
            sample_index += 1
    return samples


def load_data(path: str) -> np.array:
    """
    Import a cropped DSM as a numpy array
    :return:
    """
    ds = gdal.Open(path)
    return np.array(ds.GetRasterBand(1).ReadAsArray())


def plot_heights_and_sun(height_values: np.array, lat: float, lon: float, timezone: str = 'Europe/Amsterdam') -> None:
    """

    :param height_values:
    :param lat:
    :param lon:
    :param timezone:
    :return:
    """
    times = pd.date_range('2019-01-01 00:00:00', '2020-01-01', closed='left', freq='MS', tz=timezone)
    solpos = solarposition.get_solarposition(times, lat, lon)

    # remove nighttime
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]

    # plot the shade using the function fill_between
    degrees = np.zeros((1, 360), dtype='float')
    max_angles = np.max(height_values, axis=1)
    x_array = np.array(range(1, 361))

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

    ax.figure.legend(loc='upper left')
    ax.set_xlabel('Solar Azimuth (degrees)')
    ax.set_ylabel('Solar Elevation (degrees)')
    ax.fill_between(x_array, max_angles, degrees[0])

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    lat, lon = 52.139586, 4.436399  # Voorschoten AWS
    height_map = load_data('./height_map.tif')
    test_samples = scan_environment(height_map=height_map, origin=(774, 774),
                                    res=(0.193884753946769, 0.193884753946785), num_of_samples=1000)
    plot_heights_and_sun(test_samples, lat, lon)
