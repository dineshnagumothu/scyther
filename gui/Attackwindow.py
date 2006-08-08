#!/usr/bin/python

#---------------------------------------------------------------------------

""" Import externals """
import wx
import time
# Python Imaging library?
usePIL = True
try:
    import Image
except ImportError:
    usePIL = False 

#---------------------------------------------------------------------------

""" Import scyther-gui components """
import Icon

#---------------------------------------------------------------------------

class AttackDisplay(wx.ScrolledWindow):
    def __init__(self, daddy, parent, attack):

        self.win = daddy
        self.attack = attack

        wx.ScrolledWindow.__init__(self,parent,id=-1)
	self.SetBackgroundColour('White')

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Image = wx.StaticBitmap(self, -1, wx.EmptyBitmap(1,1))
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.Image,1,wx.ALIGN_CENTER)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.box,1,wx.ALIGN_CENTER)
        self.SetSizer(self.hbox)

        self.original = None

        filename = attack.file
        if attack.filetype == "png":
            self.original = wx.Image(filename,wx.BITMAP_TYPE_PNG)
        elif attack.filetype == "ps":
            # depends on PIL lib
            self.original = Image.open(filename)
        else:
            print "Unknown file type %s." % (self.filetype)

        # TODO self.Bind(wxSizeEvent
        self.Fit()

    def OnSize(self,event):
        self.update()
        event.Skip()

    def update(self):

        self.SetScrollbars(0,0,0,0,0,0)
        (sw,sh) = self.GetClientSizeTuple()
        (W,H) = (sw,sh)

        def makefit(W,H):
            if self.win.fit:
                # determine scaling factors for fitting
                wfactor = float(sw) / W
                hfactor = float(sh) / H

                # select smallest factor (so it will fit)
                if hfactor < wfactor:
                    factor = hfactor
                else:
                    factor = wfactor
    
                # apply scaling factor
                W = W * factor
                H = H * factor
            return (int(W),int(H))

        if self.attack.filetype == "png":
            bmp = self.original
            if not bmp.Ok():
                bmp = wx.EmptyBitmap((1,1))
            else:
                (W,H) = (bmp.GetWidth(), bmp.GetHeight())
                if self.win.fit:
                    (W,H) = makefit(W,H)
                    bmp = self.original.Scale(W,H)
            self.Image.SetBitmap(wx.BitmapFromImage(bmp))

        elif self.attack.filetype == "ps":
            pil = self.original.copy()
            (W,H) = pil.size
            (W,H) = makefit(W,H)
            # we really only want antialias when it's smaller
            pil.thumbnail((W,H),Image.ANTIALIAS)

            image = wx.EmptyImage(pil.size[0],pil.size[1])
            image.SetData(pil.convert('RGB').tostring())
            self.Image.SetBitmap(image.ConvertToBitmap())
        else:
            print "Unknown file type %s." % (self.attack.filetype)


        #self.box.SetItemMinSize(self.Image.GetContainingSizer())
        self.box.Layout()

        # wx.StaticBitmap(self, -1, bmp, (0, 0), (bmp.GetWidth(), bmp.GetHeight()))
        step = 20
        xn = int(W / step) + 1
        yn = int(H / step) + 1
        self.SetScrollbars(step,step,xn,yn,0,0)

        self.Refresh()

#---------------------------------------------------------------------------

class AttackWindow(wx.Frame):
    def __init__(self,cl):
        global usePIL

        super(AttackWindow, self).__init__(None, size=(400,800))
	self.SetBackgroundColour('Default')
        self.claim = cl

        # TODO maybe fitting defaults should come from Preferences.
        # Now, it is default yes if it looks nice (i.e. we are using
        # PIL)
        if usePIL:
            self.fit = True
        else:
            self.fit = False

        self.CreateInteriorWindowComponents()

        Icon.ScytherIcon(self)
        self.SetTitle()

    def SetTitle(self):

        tstr = self.claim.stateName(len(self.claim.attacks))
        tstr += " for claim %s" % self.claim.id
        super(AttackWindow, self).SetTitle(tstr)

    def CreateInteriorWindowComponents(self):
        ''' Create "interior" window components. In this case it is the
        attack picture. '''

        # Make zoom buttons
        sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        bt = wx.Button(self,wx.ID_ZOOM_100)
        buttons.Add(bt,0)
        self.Bind(wx.EVT_BUTTON, self.OnZoom100, bt)
        bt = wx.Button(self,wx.ID_ZOOM_FIT)
        buttons.Add(bt,0)
        self.Bind(wx.EVT_BUTTON, self.OnZoomFit, bt)
        sizer.Add(buttons, 0, wx.ALIGN_LEFT)
        
        # Add attacks (possible with tabs)
        self.displays=[]
        attacks = self.claim.attacks
        n = len(attacks)
        if n <= 1:
            # Just a single window
            dp = AttackDisplay(self, self, attacks[0])
            self.displays.append(dp)
        else:
            # Multiple tabs
            dp = wx.Notebook(self,-1)
            for i in range(0,n):
                disp = AttackDisplay(self,dp,attacks[i])
                classname = "%s %i" % (self.claim.stateName(),(i+1))
                dp.AddPage(disp, classname)
                self.displays.append(disp)

        sizer.Add(dp, 1, wx.EXPAND,1)

        self.SetSizer(sizer)

    def update(self):
        for t in self.displays:
            t.update()

    def OnFit(self,event):

        if self.fit:
            self.fit = False
        else:
            self.fit = True
        self.update()

    def OnRealSize(self):

        self.fit = False
        self.update()

    def OnSize(self):
        self.Refresh()

    def OnZoom100(self,evt):
        self.Refresh()
        self.fit = False
        self.update()

    def OnZoomFit(self,evt):
        self.Refresh()
        self.fit = True
        self.update()


