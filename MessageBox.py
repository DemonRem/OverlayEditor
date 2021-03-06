from os.path import join
from sys import platform
import wx

from version import appname, appversion

class myCreateStdDialogButtonSizer(wx.BoxSizer):
    # Dialog.CreateStdDialogButtonSizer for pre 2.6
    def __init__(self, parent, style):
        assert not (style & ~(wx.OK|wx.CANCEL))
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        ok=style&wx.OK
        no=style&wx.CANCEL

        # adjust order of buttons per Windows or Mac conventions
        if platform!='darwin':
            if ok: buttonok=wx.Button(parent, wx.ID_OK)
            if no: buttonno=wx.Button(parent, wx.ID_CANCEL)
            self.Add([0,0], 1)		# push following buttons to right
            if ok: self.Add(buttonok, 0, wx.ALL)
            if ok and no: self.Add([6,0], 0)	# cosmetic
            if no: self.Add(buttonno, 0, wx.ALL)
        else:
            if no: buttonno=wx.Button(parent, wx.ID_CANCEL)
            if ok: buttonok=wx.Button(parent, wx.ID_OK)
            self.Add([0,0], 1)		# push following buttons to right
            if no: self.Add(buttonno, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            if ok and no: self.Add([16,0], 0)	# cosmetic
            if ok: self.Add(buttonok, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            self.Add([0,0], 1)	# centre
        if ok: buttonok.SetDefault()

# Custom MessageBox/MessageDialog to replace crappy wxMac default icons
def myMessageBox(message, caption, style=wx.OK, parent=None):

    def WrapText(textctl, width):
        # StaticText.Wrap is not in 2.5.3
        words=textctl.GetLabel().split(' ')
        message=''
        startofline=0
        for word in words:
            if '\n' in word:
                firstword=word[:word.index('\n')]
            else:
                firstword=word
            (x,y)=textctl.GetTextExtent(message[startofline:]+firstword)
            if x>width:
                if startofline!=len(message):
                    message+='\n'
                    startofline=len(message)
                else:
                    #width=x	# Grow dialog to fit long word
                    pass
            message+=word+' '
            if '\n' in word:
                startofline=len(message)-len(word)+len(firstword)
        textctl.SetLabel(message)

    def OnButton(event):
        id=event.GetId()
        if id==wx.ID_OK:
            event.GetEventObject().GetGrandParent().EndModal(wx.OK)
        elif id in [wx.YES, wx.ID_SAVE, wx.ID_REPLACE]:
            event.GetEventObject().GetGrandParent().EndModal(wx.YES)
        elif id==wx.ID_NO:
            event.GetEventObject().GetGrandParent().EndModal(wx.NO)
        else:
            event.GetEventObject().GetGrandParent().EndModal(wx.CANCEL)

    # Spacings from http://developer.apple.com/documentation/UserExperience/Conceptual/OSXHIGuidelines/XHIGLayout/chapter_19_section_2.html

    if platform!='darwin':
        return wx.MessageBox(caption+'\n\n'+message, appname, style, parent)
        
    assert (style&~wx.ICON_MASK in [wx.OK,wx.CANCEL,wx.YES_NO,wx.CANCEL|wx.YES_NO])
    txtwidth=320

    dlg=wx.Dialog(parent, style=wx.CAPTION)
    panel0 = wx.Panel(dlg)

    bitmap=wx.StaticBitmap(panel0, -1,
                           wx.Bitmap(join('Resources','%s.png' % appname),
                                     wx.BITMAP_TYPE_PNG))

    cap=wx.StaticText(panel0, -1, caption)
    font=cap.GetFont()
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    cap.SetFont(font)
    WrapText(cap, txtwidth)
    
    text=wx.StaticText(panel0, -1, message)
    text.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
    WrapText(text, txtwidth)

    # Mac doesn't display icons so change the confirm button depending on context
    if style&wx.YES_NO == wx.YES_NO and style&wx.ICON_MASK == wx.ICON_EXCLAMATION:
        button=wx.Button(panel0, wx.ID_SAVE)
    elif style&wx.YES_NO == wx.YES_NO and style&wx.ICON_MASK == wx.ICON_QUESTION:
        button=wx.Button(panel0, wx.ID_REPLACE)
    elif style&wx.YES_NO:
        button=wx.Button(panel0, wx.ID_YES)
    else:
        button=wx.Button(panel0, wx.ID_OK)
    button.SetDefault()
    
    grid=wx.GridBagSizer()	# 7 rows, 8 cols
    grid.SetEmptyCellSize((0,0))
    
    grid.Add([24,15], (0,0))
    grid.Add([16,15], (0,2))
    grid.Add([txtwidth,15],(0,3), (1,4))	# Minimum size
    
    grid.Add(bitmap,  (1,1), (4,1), flag=wx.ALIGN_TOP|wx.ALIGN_LEFT)
    grid.Add(cap,     (1,3), (1,4), flag=wx.ALIGN_TOP|wx.ALIGN_LEFT)

    #grid.Add([0,8],  (2,3))
    grid.Add(text,    (3,3), (1,4), flag=wx.ALIGN_TOP|wx.ALIGN_LEFT)
    grid.Add([24,15], (4,0))
    if (style&wx.YES_NO):
        grid.Add(wx.Button(panel0, wx.ID_NO), (5,3), flag=wx.ALIGN_LEFT)
    if (style&wx.YES_NO) and (style&wx.CANCEL):
        grid.Add(wx.Button(panel0, wx.ID_CANCEL), (5,5), flag=wx.ALIGN_RIGHT|wx.RIGHT, border=14)
    grid.Add(button, (5,6), flag=wx.ALIGN_RIGHT)
    grid.Add([20,20], (6,7))
    
    panel0.SetSizerAndFit(grid)

    dlg.SetClientSize(panel0.GetMinSize())
    if True: # wx.VERSION>=(2,8,11):	# crashes on wxMac 2.8 (and earlier?) when display asleep, but hopefully that won't happen with this app
        dlg.CenterOnParent()	# see http://trac.wxwidgets.org/ticket/11557
    wx.EVT_BUTTON(dlg, wx.ID_OK, OnButton)
    wx.EVT_BUTTON(dlg, wx.ID_YES, OnButton)
    wx.EVT_BUTTON(dlg, wx.ID_SAVE, OnButton)    
    wx.EVT_BUTTON(dlg, wx.ID_REPLACE, OnButton)
    wx.EVT_BUTTON(dlg, wx.ID_NO, OnButton)
    wx.EVT_BUTTON(dlg, wx.ID_CANCEL, OnButton)
    retval=dlg.ShowModal()
    dlg.Destroy()

    return retval

def AboutBox(parent=None):
    dlg=wx.Dialog(parent, style=wx.CLOSE_BOX)
    panel0 = wx.Panel(dlg)

    bitmap=wx.StaticBitmap(panel0, -1,
                           wx.Bitmap(join('Resources','%s.png' % appname),
                                     wx.BITMAP_TYPE_PNG))

    name=wx.StaticText(panel0, -1, appname)
    name.SetWindowVariant(wx.WINDOW_VARIANT_LARGE)
    font=name.GetFont()
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    name.SetFont(font)
    
    ver=wx.StaticText(panel0, -1, "Version %4.2f" % appversion)
    ver.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

    blurb=wx.StaticText(panel0, -1, "Copyright 2007-2014 Jonathan Harris")
    blurb.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

    box=wx.BoxSizer(wx.VERTICAL)
    
    box.Add([0,10])
    box.Add(bitmap, flag=wx.ALIGN_CENTER)
    box.Add([0,12])
    box.Add(name,   flag=wx.ALIGN_CENTER)
    box.Add([0,10])
    box.Add(ver,    flag=wx.ALIGN_CENTER)
    box.Add([0,8])
    box.Add(blurb,  flag=wx.ALIGN_CENTER)

    panel0.SetSizerAndFit(box)
    dlg.SetClientSize([284,178])
    dlg.CenterOnParent()
    dlg.ShowModal()
    dlg.Destroy()
