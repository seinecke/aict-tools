import numpy as np
import logging


log = logging.getLogger(__name__)


def euclidean_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def convert_to_float32(df):
    ''' Convert a pandas dataframe to float32, replacing overflows with maxvalues '''

    df = df.astype('float32')
    df.replace(np.inf, np.finfo('float32').max, inplace=True)
    df.replace(-np.inf, np.finfo('float32').min, inplace=True)

    return df


def check_valid_rows(df):
    ''' Check for nans in df, warn if there are any, returns a mask with non-nan rows'''
    valid = np.logical_not(df.isnull().any(axis=1))

    if len(df.loc[valid]) < len(df):
        invalid_columns = df.isnull().any(axis=0)
        log.warning(
            'Data contains not-predictable events.\n'
            'There are nan-values in columns: {}'.format(
                df.columns[invalid_columns]
            )
        )

    return valid


def calc_true_disp(source_x, source_y, cog_x, cog_y, delta):
    true_disp = euclidean_distance(
        source_x, source_y,
        cog_x, cog_y
    )

    true_delta = np.arctan2(
        cog_y - source_y,
        cog_x - source_x,
    )
    true_sign = np.sign(np.abs(delta - true_delta) - np.pi / 2)

    return true_disp, true_sign


from astropy import units as u
from astropy.coordinates import SkyCoord, AltAz
from ctapipe.coordinates import CameraFrame, EngineeringCameraFrame

def horizontal_to_camera(az, alt, az_pointing, alt_pointing, focal_length):
    hf = AltAz()

    pointing = SkyCoord(
                alt=alt_pointing.values*u.rad,
                az=az_pointing.values*u.rad,
                frame=hf,
            )

    # cf = CameraFrame(
    #         focal_length=focal_length.values*u.m,
    #         telescope_pointing=pointing,
    #         )

    cf = EngineeringCameraFrame(
        n_mirrors=2,
        #location=LOCATION,
        #obstime=obstime,
        focal_length=focal_length.values*u.m,
        telescope_pointing=pointing,
    )

    xy_coord = SkyCoord(az=az.values*u.rad, alt=alt.values*u.rad, frame=hf)
    xy_coord = xy_coord.transform_to(cf)

    return xy_coord.x.to(u.m).value, xy_coord.y.to(u.m).value


def camera_to_horizontal(x, y, az_pointing, alt_pointing, focal_length):
    hf = AltAz()

    pointing = SkyCoord(
                alt=alt_pointing.values*u.rad,
                az=az_pointing.values*u.rad,
                frame=hf,
            )

    # cf = CameraFrame(
    #         focal_length=focal_length.values*u.m,
    #         telescope_pointing=pointing,
    #         )

    cf = EngineeringCameraFrame(
        n_mirrors=2,
        #location=LOCATION,
        #obstime=obstime,
        focal_length=focal_length.values*u.m,
        telescope_pointing=pointing,
    )

    altaz_coord = SkyCoord(x=x.values*u.m, y=y.values*u.m, frame=cf)
    altaz_coord = altaz_coord.transform_to(hf)

    return altaz_coord.alt.to(u.rad).value, altaz_coord.az.to(u.rad).value

