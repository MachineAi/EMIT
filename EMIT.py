#!/usr/bin/env python2

__author__ = 'Mario'


import os

import wx
import wx.xrc
import wx.aui

import gui.log as log
from coordinator import main as cmd
from gui.mainGui import  MainGui
from gui.CanvasController import CanvasController
import logging
import threading

#sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__),'../../odm2/src')))


# ##########################################################################
# # Class MainFrame
# ##########################################################################

if __name__ == '__main__':

    # setup logger
    #logger = log.setup_custom_logger('root')

    # create and instance of the coordinator engine
    cmd = cmd.Coordinator()

    # connect to databases and set default
    currentdir = os.path.dirname(os.path.abspath(__file__))
    connections_txt = os.path.abspath(os.path.join(currentdir,'./data/connections'))

    # We are terminating dependency logging errors, We may want this in the future but it
    # tends to add clutter to our console.
    wx.Log.SetLogLevel(0)
    app = wx.App(False)

    frame = MainGui(None,cmd)
    frame.Show(True)

    #app.SetTopWindow(frame)
    CanvasController(cmd, frame.Canvas)

    cmd.connect_to_db([connections_txt])
    if not cmd.get_default_db():
        cmd.set_default_database()


    # from tests import non_blocking_gui
    # f2 = non_blocking_gui.Frame()
    # thread = threading.Thread(target=f2.run, args=())
    # thread.setDaemon(True)
    # thread.start()
    # f2.Show()

    # from console import consoleOutput
    # c = consoleOutput(frame)

    #thread = threading.Thread(target=c.run,args=())
    #thread.daemon = True
    #thread.start()

    # C = console(None)
    # C.Show(True)

    app.MainLoop()




