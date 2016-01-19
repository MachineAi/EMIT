__author__ = 'Mario'

import wx
import wx.aui
import wx.xrc

import environment
from coordinator import engineManager
from gui.controller.EMITCtrl import LogicEMIT


class EMITApp(wx.App):
    def OnInit(self):

        # load environment variables
        environment.getEnvironmentVars()

        # Don't delete this line, instantiating the Borg Engine main thread here
        engine = engineManager.Engine()

        # We are terminating dependency logging errors, We may want this in the future but it
        # tends to add clutter to our console.
        wx.Log.SetLogLevel(0)

        self.logicEmit = LogicEMIT(None)
        return True

if __name__ == '__main__':

    app = EMITApp()
    app.MainLoop()
    # pid = os.getpid()
    # os.system("kill -9 " + str(pid))

