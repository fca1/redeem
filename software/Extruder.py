"""
Extruder file for Replicape.

Author: Elias Bakken
email: elias(dot)bakken(at)gmail(dot)com
Website: http://www.thing-printer.com
License: GNU GPL v3: http://www.gnu.org/copyleft/gpl.html

 Redeem is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Redeem is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Redeem.  If not, see <http://www.gnu.org/licenses/>.
"""

from threading import Thread
import time
import logging

class Heater(object):
    """
    A heater element that must keep temperature,
    either an extruder, a HBP or could even be a heated chamber
    """
    def __init__(self, thermistor, mosfet, name, onoff_control):
        """ Init """
        self.thermistor = thermistor
        self.mosfet = mosfet
        self.name = name                   # Name, used for debugging
        self.current_temp = 0.0
        self.target_temp = 0.0             # Target temperature (Ts). Start off. 
        self.last_error = 0.0              # Previous error term, used in calculating the derivative
        self.error_integral = 0.0          # Accumulated integral since the temperature came within the boudry
        self.error_integral_limit = 100.0  # Integral temperature boundary
        self.P = 1.0                      # Proportional 
        self.I = 0.0                      # Integral 
        self.D = 0.0                      # Derivative
        self.onoff_control = onoff_control  # If we use PID or ON/OFF control
        self.ok_range = 4.0

        self.current_time = time.time()
        self.prev_time = time.time()

    def set_target_temperature(self, temp):
        """ Set the desired temperature of the extruder """
        self.target_temp = float(temp)

    def get_temperature(self):
        """ get the temperature of the thermistor"""
        return self.current_temp

    def is_target_temperature_reached(self):
        """ Returns true if the target temperature is reached """
        if self.target_temp == 0:
            return True
        err = abs(self.current_temp - self.target_temp)
        return err < self.ok_range

    def disable(self):
        """ Stops the heater and the PID controller """
        self.enabled = False
        # Wait for PID to stop
        while self.disabled == False:
            time.sleep(0.2)
            # The PID loop has finished
        self.mosfet.set_power(0.0)
        self.mosfet.close()

    def enable(self):
        """ Start the PID controller """
        self.enabled = True
        self.disabled = False
        self.t = Thread(target=self.keep_temperature)
        self.t.daemon = True
        self.t.start()

    def keep_temperature(self):
        """ PID Thread that keeps the temperature stable """
        while self.enabled:
            self.current_temp = self.thermistor.getTemperature()
            error = self.target_temp-self.current_temp

            if self.onoff_control:
                if error > 1.0:
                    power = 1.0
                else:
                    power = 0.0
            else:
                if abs(error) > 30:  # Avoid windup
                    if error > 0:
                        power = 1.0
                    else:
                        power = 0.0

                    self.error_integral = 0
                    self.last_error = error
                else:
                    derivative = self._getErrorDerivative(error)
                    integral = self._getErrorIntegral(error)
                    power = self.P*(error + self.D*derivative + self.I*integral)  # The formula for the PID				
                    power = max(min(power, 1.0), 0.0)                             # Normalize to 0,1

            # If the Thermistor is disconnected or running away or something
            if self.current_temp <= 5 or self.current_temp > 250:
                power = 0
            self.mosfet.set_power(power)
            if self.current_time-self.prev_time > 2:
                logging.warning("Heater time update large: " +
                                self.name + " temp: " +
                                str(self.current_temp) + " time delta: " +
                                str(self.current_time-self.prev_time))
            self.prev_time = self.current_time
            self.current_time = time.time()
            time.sleep(1)
        self.disabled = True

    def _getErrorDerivative(self, current_error):
        """ Get the derivative of the error term """
        derivative = current_error-self.last_error		# Calculate the diff
        self.last_error = current_error					      # Update the last error 
        return derivative

    def _getErrorIntegral(self, error):
        """ Calculate and return the error integral """
        self.error_integral += error
        return self.error_integral


class Extruder(Heater):
    """ Subclass for Heater, this is an extruder """
    def __init__(self, smd, thermistor, mosfet, name, onoff_control):
        Heater.__init__(self, thermistor, mosfet, name, onoff_control)
        self.smd = smd
        self.enable()


class HBP(Heater):
    """ Subclass for heater, this is a Heated build platform """
    def __init__(self, thermistor, mosfet, onoff_control):
        Heater.__init__(self, thermistor, mosfet, "HBP", onoff_control)
        self.enable()
