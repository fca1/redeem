"""
Printer class holding all printer components

Author: Mathieu Monney
email: zittix(at)xwaves(dot)net
Website: http://www.xwaves.net
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

from Path import Path


class Printer:
    """ A command received from pronterface or whatever """

    def __init__(self, steppers=None, heaters=None, end_stops=None, fans=None,
                 cold_ends=None, path_planner=None):
        if steppers is None:
            self.steppers = {}
        else:
            self.steppers = steppers

        if heaters is None:
            self.heaters = {}
        else:
            self.heaters = heaters

        if end_stops is None:
            self.end_stops = {}
        else:
            self.end_stops = end_stops

        if fans is None:
            self.fans = []
        else:
            self.fans = fans

        if cold_ends is None:
            self.cold_ends = []
        else:
            self.cold_ends = cold_ends

        self.heaters = heaters
        self.end_stops = end_stops
        self.fans = fans
        self.cold_ends = cold_ends
        self.path_planner = path_planner
        self.coolers = []

        self.comms = {}  # Communication channels

        self.factor = 1.0
        self.extrude_factor = 1.0
        self.movement = Path.ABSOLUTE
        self.feed_rate = 0.5
        self.acceleration = [0.5, 0.5, 0.5, 0.5,  0.5]
        self.maxJerkXY = 20
        self.maxJerkZ = 1
        self.maxJerkEH = 4
        self.current_tool = "E"

    def ensure_steppers_enabled(self):
        """
        This method is called for every move, so it should be fast/cached.
        """
        for name, stepper in self.steppers.iteritems():
            if stepper.in_use and not stepper.enabled:
                # Stepper should be enabled, but is not.
                stepper.set_enabled(True)  # Force update

    def reply(self, gcode):
        """ Send a reply through the proper channel """
        if gcode.get_answer() is not None:
            self.send_message(gcode.prot, gcode.get_answer())

    def send_message(self, prot, msg):
        """ Send a message back to host """
        self.comms[prot].send_message(msg)
