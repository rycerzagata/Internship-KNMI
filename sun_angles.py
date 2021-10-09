from pvlib import solarposition
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tz = 'Europe/Amsterdam'
lat, lon = 52.139586, 4.436399  # Voorschoten AWS

times = pd.date_range('2019-01-01 00:00:00', '2020-01-01', closed='left', freq='SM', tz=tz)
solpos = solarposition.get_solarposition(times, lat, lon)

# remove nighttime
solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]

fig, ax = plt.subplots()

for hour in np.unique(solpos.index.hour):
    # choose label position by the largest elevation for each hour
    subset = solpos.loc[solpos.index.hour == hour, :]
    height = subset.apparent_elevation
    pos = solpos.loc[height.idxmax(), :]
    ax.text(pos['azimuth'], pos['apparent_elevation'], str(hour))

for date in pd.to_datetime(['2019-03-21', '2019-06-21', '2019-12-21']):
    times = pd.date_range(date, date+pd.Timedelta('24h'), freq='5min', tz=tz)
    solpos = solarposition.get_solarposition(times, lat, lon)
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
    label = date.strftime('%Y-%m-%d')
    ax.plot(solpos.azimuth, solpos.apparent_elevation, label=label)

ax.figure.legend(loc='upper left')
ax.set_xlabel('Solar Azimuth (degrees)')
ax.set_ylabel('Solar Elevation (degrees)')

plt.show()

# plot the shade using the function fill_between
import matplotlib.pyplot as plt
degrees = np.zeros((1, 360), dtype='float')
max_angles = np.max(test_samples, axis=1)
x_array = np.array(range(1,361))

fig, ax = plt.subplots(figsize=(10,5))
ax.fill_between(x_array, max_angles, degrees[0])
ax.set_title('fill between zeros and max angles')
ax.set_xlabel('x')
fig.tight_layout()
plt.show()
