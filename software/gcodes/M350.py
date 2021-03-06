"""
GCode M350
Set microstepping mode

Author: Elias Bakken
email: elias.bakken(at)gmail(dot)com
Website: http://www.thing-printer.com
License: CC BY-SA: http://creativecommons.org/licenses/by-sa/2.0/
"""

from GCodeCommand import GCodeCommand
from Stepper import Stepper
import logging


class M350(GCodeCommand):

    def execute(self, g):
        self.printer.path_planner.wait_until_done()
        
        for i in range(g.num_tokens()):
            axis = g.token_letter(i)
            logging.debug("M350 on "+axis)
            stepper = self.printer.steppers[axis]
            stepper.set_microstepping(int(g.token_value(i)))
        Stepper.commit()
        self.printer.path_planner.make_acceleration_tables()
        logging.debug("acceleration tables recreated")

    def get_description(self):
        return "Set microstepping mode for the axes present with a token. " \
               "Microstepping will be 2^val. Steps pr. mm. is changed" \
               " accordingly."
