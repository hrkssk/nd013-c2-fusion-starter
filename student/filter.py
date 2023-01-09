# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Kalman filter class
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params

class Filter:
    '''Kalman filter class'''
    def __init__(self):
        self.dim_state = params.dim_state
        self.dt = params.dt # time increment
        self.q = params.q # process noise variable for Kalman filter Q

    def F(self):
        # system matrix
        return np.matrix([
                [1, 0, 0, self.dt, 0, 0],
                [0, 1, 0, 0, self.dt, 0],
                [0, 0, 1, 0, 0, self.dt],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1]
            ])

    def Q(self):
        # process noise covariance Q
        return np.matrix([
            [1/3*self.dt**3*self.q, 0, 0, 1/2*self.dt**2*self.q, 0, 0],
            [0, 1/3*self.dt**3*self.q, 0, 0, 1/2*self.dt**2*self.q, 0],
            [0, 0, 1/3*self.dt**3*self.q, 0, 0, 1/2*self.dt**2*self.q],
            [1/2*self.dt**2*self.q, 0, 0, self.dt*self.q, 0, 0],
            [0, 1/2*self.dt**2*self.q, 0, 0, self.dt*self.q, 0],
            [0, 0, 1/2*self.dt**2*self.q, 0, 0, self.dt*self.q]
        ])

    def predict(self, track):
        # predict state and estimation error covariance to next timestep
        F = self.F()
        track.set_x(F*track.x) # state prediction
        track.set_P(F*track.P*F.transpose() + self.Q()) # covariance prediction

    def update(self, track, meas):
        H = meas.sensor.get_H(track.x) # measurement matrix
        K = track.P*H.transpose()*np.linalg.inv(self.S(track, meas, H)) # Kalman gain
        track.set_x(track.x + K*self.gamma(track, meas)) # state update
        I = np.identity(self.dim_state)
        track.set_P((I - K*H) * track.P) # covariance update
        track.update_attributes(meas)

    def gamma(self, track, meas):
        return meas.z - meas.sensor.get_hx(track.x) # residual

    def S(self, track, meas, H):
        return H*track.P*H.transpose() + meas.R # covariance of residual