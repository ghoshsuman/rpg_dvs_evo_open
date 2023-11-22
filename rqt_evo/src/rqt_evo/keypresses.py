#!/usr/bin/env python
import keyboard
import os
import rospy
import numpy as np
from std_msgs.msg import String, Bool
import subprocess
import time


class KeyPressCommand():
    """
    EVO rqt widget actions
    """
    #_last_info_msg = Info()
    _publisher = None
    _subscriber = None
    _publisher_copilot = None

    def __init__(self, evo_namespace='evo'):


        if not evo_namespace:
            evo_namespace = 'evo'

        self._evo_namespace = evo_namespace
        self.register(evo_namespace)
        self.useEVO = False
        self.checkbox_map_expansion = True
        self.append_to_pc = True
        rospy.init_node('keypresser', anonymous=True)


    def register(self, evo_namespace):
        """
        Subscribes to ROS Info topic and registers callbacks
        """
        # self._subscriber = rospy.Subscriber(evo_namespace+'/info', Info, self.info_cb)

        # Initialize Publisher
        self._publisher = rospy.Publisher(
            evo_namespace+'/remote_key', String, queue_size=1)
        self._publisher_copilot = rospy.Publisher(
            evo_namespace+'/copilot_remote', Bool, queue_size=1)

    def unregister(self):
        """
        Unregisters publishers
        """
        if self._publisher is not None:
            self._publisher.unregister()
            self._publisher = None

        if self._publisher_copilot is not None:
            self._publisher_copilot.unregister()
            self._publisher_copilot = None

        if self._subscriber is not None:
            self._subscriber.unregister()
            self._subscriber = None


    def on_bootstrap_button_pressed(self):
        """
        Triggers bootstrap
        """
        print('BOOTSTRAPPING')
        self.send_command('bootstrap')

    def on_start_button_pressed(self):
        """
        Triggers reset button
        """
        print('START/RESET')
        self.send_command('reset')

    def on_update_button_pressed(self):
        """
        Triggers map update
        """
        print('UPDATE')
        self.send_command('update')

    def on_switch_button_pressed(self):
        """
        Turns on tracking thread
        """
        print('SWITCH TO TRACKING')
        self.send_command('switch')

    def on_map_expansion_changed(self):
        """
        Switches on and off the map expansion algorithm based on checkbox_map_expansion 
        """
        if self.checkbox_map_expansion:
            print('ENABLE MAP EXPANSION')
            self.send_command('enable_map_expansion')
        else:
            print('DISABLE EXPANSION')
            self.send_command('disable_map_expansion')
        self.checkbox_map_expansion = not self.checkbox_map_expansion

    def on_pointcloud_update_changed(self):
        self.send_command("global_pc_switch")
        self.append_to_pc = not self.append_to_pc
        print("APPEND TO POINTCLOUD: ", self.append_to_pc)

    def on_copilot_state_changed(self):
        """
        Switch from bootstrapping tracker to evo tracker
        """

        print('SWITCH COPILOT TO ' + ('EVO' if self.useEVO else 'INITIAL PILOT'))
        self._publisher_copilot.publish(Bool(self.useEVO))
        self.useEVO = not self.useEVO

    def send_command(self, cmd):
        """
        Utils to send remote command
        """
        if self._publisher is None:
            return
        self._publisher.publish(String(cmd))


if __name__=="__main__":
    keypresser = KeyPressCommand()
    is_enabled = True


    while True:
        if keyboard.is_pressed("x"):
            is_enabled = not is_enabled
            print("listening to the keyboard is ", is_enabled)
            time.sleep(1)

        if not is_enabled:
            continue
        if keyboard.is_pressed("t"):
            keypresser.on_start_button_pressed()
            time.sleep(0.2)
            keypresser.on_switch_button_pressed()
        if keyboard.is_pressed("m"):
            keypresser.on_map_expansion_changed()
            time.sleep(0.5)
        if keyboard.is_pressed("e"):
            keypresser.on_copilot_state_changed()
            time.sleep(0.5)
        if keyboard.is_pressed("u"):
            keypresser.on_update_button_pressed()
            time.sleep(0.5)
        if keyboard.is_pressed("k"):
            break
        if keyboard.is_pressed("r"):
            keypresser.send_command("reset_rovio")
            print("resetting ROVIO")
            time.sleep(0.5)
        if keyboard.is_pressed("p"):
            keypresser.on_pointcloud_update_changed()
            time.sleep(0.5)

        


