#!/usr/bin/python

# newclass.py

import wx, wx.html
import os
import codecs
import pyfits
import time
import re
import sys

#Import the modules needed to create the log
from mmtlogger_PDFtools import ReadScanned
from mmtlogger_PDFtools import CreatePDF
import mmtlogger_fitsutil as FITSUTIL


ID_CREATELOG = wx.NewId()
ID_CHANGEDIR = wx.NewId()
ID_SCANFILES = wx.NewId()
ID_AUTOMATE = wx.NewId()
ID_SAVECOMMENTS = wx.NewId()
ID_FILELIST = wx.NewId()
ID_ABOUT = wx.NewId()
ID_NUKE = wx.NewId()
ID_EXIT = wx.NewId()
ID_OBJECTLIST = wx.NewId()
ID_EXPTIMELIST = wx.NewId()
ID_GRATINGLIST = wx.NewId()
ID_UTLIST = wx.NewId()

wildcard = "All files (*.*)|*.*"

aboutText = """<p>Sorry, there is no information about this program. It is running on version %(wxpy)s of <b> 
wxPython </b> and %(python)s of <b>Python</b>.  See <a href="http://wiki.wxpython.org"> wxPython Wiki</a></p>"""



#For Aligning in corner of screen
def alignToTopRight(win):
    dw, dh = wx.DisplaySize()
    w, h = win.GetSize()
    x = dw-w
    y = 50
    win.SetPosition((x,y))


class NightParams(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Night Parameters", size=(250, 270), 
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL)
        panel = wx.Panel(self)

        self.observer = parent.observer
        self.instrument = parent.instrument
        self.date = parent.date
        self.program = parent.program
        self.exclude_prefix = parent.exclude_prefix

        wx.StaticText(self, -1, 'Observer:', (10, 20))
        wx.StaticText(self, -1, 'Instrument:', (10, 60))
        wx.StaticText(self, -1, 'Program:', (10, 100))
        wx.StaticText(self, -1, 'Date:', (10, 140))
           
        self.observer_box = wx.TextCtrl(self, -1, parent.observer,  (110, 15), (120, -1))
        self.instrument_box = wx.TextCtrl(self, -1, parent.instrument,  (110, 55), (120, -1))
        self.program_box = wx.TextCtrl(self, -1, parent.program,  (110, 95), (120, -1))
        self.date_box = wx.TextCtrl(self, -1, parent.date, (110, 135), (120, -1))

        okbutton = wx.Button(self, -1,  "OK", (10, 200))
        closebutton = wx.Button(self, -1, "Close", (120, 200))

        okbutton.Bind(wx.EVT_BUTTON, self.OnOK)
        closebutton.Bind(wx.EVT_BUTTON, self.OnClose)
  
        self.parent = parent

        self.Centre()


    def OnOK(self, e):

        self.observer = self.observer_box.GetValue()
        self.instrument = self.instrument_box.GetValue()
        self.program = self.program_box.GetValue()
        self.date = self.date_box.GetValue()

        fileout = open(self.parent.currentDirectory+'/.mmtlogger/nightparams.dat', 'w')
        fileout.write(self.observer+'\n')
        fileout.write(self.instrument+'\n')
        fileout.write(self.program+'\n')
        fileout.write(self.date+'\n')
        fileout.write(self.exclude_prefix+'\n')
        fileout.close()

        self.parent.observer = self.observer
        self.parent.instrument = self.instrument
        self.parent.program = self.program
        self.parent.date = self.date
        self.Close()


    def OnClose(self, e):
        self.Close()







class LoggerGUI(wx.Frame):
    
    def __init__(self, parent, title):    
        super(LoggerGUI, self).__init__(parent, title=title, 
                                        size=(720, 520), style=wx.SYSTEM_MENU|
										wx.CAPTION|wx.CLOSE_BOX)
        alignToTopRight(self)

        self.InitUI()
        self.Show()     
       
    def InitUI(self):
        panel = wx.Panel(self)
        self.newfile_string = "#*$&#)@(*#" 
        self.currentDirectory = os.environ['HOME']
        self.observer = ''
        self.instrument = ''
        self.date = ''
        self.program = ''
        self.exclude_prefix = ''


        FITSUTIL.ReadParams(self)
        #Start creating the grouped sizers and prey this works!
        vsizer_global = wx.BoxSizer(wx.VERTICAL)
        
        #Top row of buttons
        hsizer_toprow = wx.BoxSizer(wx.HORIZONTAL)
        
        #Current Logging Status
        self.status_txt = wx.StaticText(panel, label="Logger Offline")
        self.status_txt.SetForegroundColour((255,0,0))
        font = wx.Font(24, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.status_txt.SetFont(font)
        hsizer_toprow.Add(self.status_txt, 2, flag=wx.LEFT|wx.RIGHT|wx.TOP,
            border=10)
        
        #Setup the working directory
        
        self.WD_button = wx.Button(panel, -1, label=self.currentDirectory, 
            size=(250, 30))
        self.WD_button.Bind(wx.EVT_BUTTON, self.ChangeDir)
        hsizer_toprow.Add(self.WD_button, 1, flag=wx.LEFT|wx.RIGHT|wx.TOP,
            border=10)
        #Add all the sizers to the global sizer
        vsizer_global.Add(hsizer_toprow, 0.5, wx.EXPAND)        
        panel.SetSizer(vsizer_global)


        #Add The List boxes?
        self.filelist = []
        self.selectedfile = ''
        self.selectedfile_index = -1
        self.filebox = wx.ListCtrl(panel, ID_FILELIST, size=(700, 200), 
            style=wx.LC_REPORT)
        self.filebox.InsertColumn(0, "File", width=150)
        self.filebox.InsertColumn(1, "Object", width=200)
        self.filebox.InsertColumn(2, "Time", width=70)
        self.filebox.InsertColumn(3, "ExpTime", width=80)
        self.filebox.InsertColumn(4, "Grating", width=100)

        self.filebox.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, id=ID_FILELIST)
        vsizer_global.Add(self.filebox, border=10, flag=wx.LEFT|wx.TOP|
            wx.BOTTOM|wx.RIGHT)

        #Setup the comments section : 
        vsizer_global.Add(wx.StaticText(panel, label='Comments:'), 0.5)
        self.cbox = wx.TextCtrl(panel, size=(700, 50), style=wx.TE_MULTILINE)
        vsizer_global.Add(self.cbox, 1, flag=wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.TOP, 
            border=10)
        self.cbox.Disable()


        hsizer_bottom_row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.param = wx.Button(panel, -1, label="Night Parameters")
        self.param.Bind(wx.EVT_BUTTON, self.SetRunParam)
        hsizer_bottom_row1.Add(self.param, 1, border=10, 
            flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND)

        exclude_but = wx.Button(panel, -1, label='Exclude Prefix')
        exclude_but.Bind(wx.EVT_BUTTON, self.ExcludeList)
        hsizer_bottom_row1.Add(exclude_but, 1, border=10, 
            flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND)

        group_but = wx.Button(panel, -1, label='Group Selected')
        group_but.Bind(wx.EVT_BUTTON, self.GroupFiles)
        group_but.Disable()
        hsizer_bottom_row1.Add(group_but, 1, border=10, 
            flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND)


        vsizer_global.Add(hsizer_bottom_row1, 0.5, wx.EXPAND)
        panel.SetSizer(vsizer_global)

        hsizer_bottom_row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.poll_button = wx.Button(panel, label='Start Logging')
        self.poll_button.Bind(wx.EVT_BUTTON, self.OnToggle)
        hsizer_bottom_row2.Add(self.poll_button, 1, border=10, 
            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM)

        log_button = wx.Button(panel, label='Open Log')
        log_button.Bind(wx.EVT_BUTTON, self.OnOpenLog)
        hsizer_bottom_row2.Add(log_button,  1, border=10, 
            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM)

        quit_button = wx.Button(panel, label='Quit')
        quit_button.Bind(wx.EVT_BUTTON, self.OnQuit)
        hsizer_bottom_row2.Add(quit_button, 1, border=10, 
            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM)

        vsizer_global.Add(hsizer_bottom_row2, 0.5, wx.EXPAND)
        panel.SetSizer(vsizer_global)

        filemenu = wx.Menu()
        nitem = filemenu.Append(ID_NUKE, 'Nuke', 'Nuke the current log')
        qitem = filemenu.Append(ID_EXIT, 'Exit', 'Terminate the program')

        menubar = wx.MenuBar()
        menubar.Append(filemenu, '&File')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnQuit, qitem)
        self.Bind(wx.EVT_MENU, self.NukeLog, nitem)



        self.OnScan(self)

    #Setup some events
    def NotWorking(self, e):
       print 'This button does nothing'
       e.Skip()
       
    def SetRunParam(self, e):
        dlg = NightParams(self)
        dlg.Show()

    def GroupFiles(self,e):
        print "no worky"

    def ExcludeList(self, e):
        dialog = wx.TextEntryDialog(None, """Enter the prefixes you want to ignore \nin your log separated by commas.
            \nFor example:               focus,test """,
            "Text Entry", self.exclude_prefix, style=wx.OK|wx.CANCEL|wx.CENTER)
        if dialog.ShowModal() == wx.ID_OK :
            self.exclude_prefix = dialog.GetValue()
            fileout = open(self.currentDirectory+'/.mmtlogger/nightparams.dat', 'w')
            fileout.write(self.observer+'\n')
            fileout.write(self.instrument+'\n')
            fileout.write(self.program+'\n')
            fileout.write(self.date+'\n')
            fileout.write(self.exclude_prefix+'\n')
            fileout.close()
            self.OnScan(self)


    def OnToggle(self, event):
        btnLabel = self.poll_button.GetLabel()
        if btnLabel == 'Start Logging':
            print "Starting Automated logging."
            self.timer.Start(10000)
            self.poll_button.SetLabel("Stop Logging")
            font = wx.Font(24, wx.NORMAL, wx.BOLD, wx.NORMAL)
            self.status_txt.SetForegroundColour((0, 139, 0))
            self.status_txt.SetFont(font)
            self.status_txt.SetLabel("Logger Running")
            self.status_txt.Update()

        else:
            print "Logging Stopped"
            self.timer.Stop()
            self.poll_button.SetLabel("Start Logging")
            self.status_txt.SetForegroundColour((255,0,0))
            font = wx.Font(24, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
            self.status_txt.SetFont(font)
            self.status_txt.SetLabel("Logger Offline")
            self.status_txt.Update()

    def update(self, event):
        print "\n updated: ", 
        print time.ctime()
        self.OnScan(self)
    
    #The procedure that adds the comments to the log
    def AddComment(self, e):
        
        comment = self.cbox.GetValue()
        print(comment)
        #Format the output
        output = self.newfile_string + ' ' + self.selectedfile + ' ' + comment

        ReadScanned(self)
        
        #Now, is the current file already in there?
        counter = 0
        wasfound = 0
        for file in self.cfiles :
            if file == self.selectedfile :
                self.oldcomments[counter] = comment + '\n'
                wasfound = 1
            counter += 1
             
        commentfile = self.currentDirectory + '/.mmtlogger/commentlist.dat'
        
        #if was found is still 0, we need to just append (I could care less about order at this point)
        if wasfound == 0:
            cout = open(commentfile, 'a')
            
            output= output + '\n'
            cout.write(output)
            cout.close()
        else : 
            cout = open(commentfile, 'w')
            counter = 0
            for file in self.cfiles :    
                output = self.newfile_string + ' ' + file + ' ' + self.oldcomments[counter] + '\n'
            
                cout.write(output)
                counter += 1
            cout.close()
        
        self.OnCreate(self)
                
    
    def NukeLog(self, e):
        ret = wx.MessageBox("Nuking the log will remove everything you have entered and the full" + 
                            "list of files in the log (but not the fits files themselves). Are you sure?", 
                            'Question', wx.YES_NO | wx.CENTER | wx.NO_DEFAULT, self)
        if ret == wx.YES:
            #Check that the log exists
            ldir = os.path.dirname(self.currentDirectory +'/.mmtlogger/')
            if os.path.exists(ldir):
                os.remove(self.currentDirectory +'/.mmtlogger/filelist.dat')
                os.remove(self.currentDirectory + '/.mmtlogger/commentlist.dat')
                os.remove(self.currentDirectory + '/.mmtlogger/nightparams.dat')
                self.OnScan(self)
    
    def OnSelect(self, event):
        
        if self.selectedfile != '' :
            self.AddComment(self)
        self.cbox.Clear()
        
        index =  event.m_itemIndex        
        self.selectedfile = self.filelist[self.sortindex[index]]
        self.selectedfile_index = index
        self.cbox.Disable()
        
        ReadScanned(self)
        self.cbox.Enable()
        #is the slected file there
        counter = 0 
        wasfound = 0
        for file in self.cfiles : 
            if file == self.selectedfile : 
                self.cbox.SetValue(self.oldcomments[counter][:-1])
            counter += 1
                

    #Define the module that changes the working directory
    def ChangeDir(self, event):
        """ 
        Create and show the Open File Dialog. Hopefully this works!
        """
        dlg = wx.DirDialog(
            self, "Choose a directory:", 
            style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        dlg.SetPath(self.currentDirectory)
        if dlg.ShowModal() == wx.ID_OK:
            self.currentDirectory = dlg.GetPath()
            self.filebox.DeleteAllItems()
            self.WD_button.SetLabel(self.currentDirectory)
            self.WD_button.Update()

            #Now, check for a working directory in the new chosen directory.
            ldir = os.path.dirname(self.currentDirectory+'/.mmtlogger/')
            if not os.path.exists(ldir):
                os.makedirs(ldir)
        FITSUTIL.ReadParams(self)
        self.OnScan(self)
        dlg.Destroy()

    def OnScan(self,event):
        """
        Create the process that will scan the directory for fits files and compare them 
        against a current list of fits files that will live in $CWD/.mmtlogger/filelist 
        along with various information about them. For now, make the list and add basic 
        information to it.

        The second part will repopulate the ListBox with the information from that filelist
        """
        header_keys = ['EXPTIME', 'AIRMASS', 'DATE-OBS', 'RA','DEC',
                       'INSFILTE', 'ORDER', 'CENWAVE', 'IMAGETYP', 'UT', 'DISPERSE', 'APERTURE',
                       'POSANG', 'OBJECT']
        self.header_keys = header_keys
        #Get a full list of files in this directory
        files = []
        flist = os.listdir(self.currentDirectory)
        #May want to increase this later
        must_endwith = ['.fits','.fit','.fits.gz','.fit.gz']
        for ifile in flist:
            goodflag = 0
            for end in must_endwith:
                if ifile[-1*len(end):] == end:
                    if FITSUTIL.isgoodfile(self, ifile) == 1:
                        files.append(ifile)
        
        
        #Does the output/saved variable file exist? If not, then add a header
        filelist_path = self.currentDirectory+'/.mmtlogger/filelist.dat'
        if os.path.isfile(filelist_path) == 0:
            ldir = os.path.dirname(self.currentDirectory+'/.mmtlogger/')
            if not os.path.exists(ldir):
                os.makedirs(ldir)
            fileoutput = open(filelist_path, "w")
            for key in header_keys:   
                fileoutput.write("# " + key+'\n')        
            fileoutput.close()
        else :
            fileoutput = open(filelist_path, 'r')
            counter = 0
            for line in fileoutput:
                if counter == 0 and line[0] != '#' :
                    print "remaking the header"
                    fileinput = open(filelist_path, 'w')
                    for key in header_keys:
                        fileinput.write('# ' + key + '\n')
                    fileinput.close()
                counter += 1
            fileoutput.close()
            

        #Check the currently archived images to what we have already scanned. We won't 
        #waste CPU cycles scanning them again
        files_in = open(filelist_path, 'r')
        scanned_files = []
        for line in files_in : 
            if line[0] != '#':
                words = line.split()
                scanned_files.append(words[0])
        
        new_files = []
        newcounter = 0
        for ifile in files:
            if (ifile in scanned_files) == 0:
                new_files.append(ifile)
                newcounter =+ 1
             
        if newcounter > 0 :
            fileoutput = open(filelist_path, "a")
            #Grab the header info
            for ifile in new_files:
                hdulist = pyfits.open(self.currentDirectory + '/' + ifile)   
                hdulist.verify('fix')
                checkflag = 0
                outstring = ifile + ' ' 
                for key in header_keys:
                    if key == 'APERTURE':
                        if hdulist[0].header[key] == 'DirectImaging' :
                            outstring += "Direct "
                        else :
                            outstring += str(hdulist[0].header[key]) + ' ' 
                    elif key != 'OBJECT':
                        outstring += str(hdulist[0].header[key]) + ' '
                    else:
                        outstring += '***' + str(hdulist[0].header[key]) + '***\n' 
                fileoutput.write(outstring)
            fileoutput.close()

        ReadScanned(self)
        trunkfiles = []
        for ifile in self.file_list:
            syl = ifile.split('.')
            scounter = 0
            for sub in syl:
                if scounter == 0 :
                    word = sub
                elif sub != ".fits" :
                    word = word + '.' + sub
                scounter += 1 

            trunkfiles.append(word)


        output = []
        font = wx.Font(24, wx.FONTFAMILY_TELETYPE, wx.BOLD, wx.FONTSTYLE_NORMAL)

        self.filelist = trunkfiles
        index = 0
        self.filebox.DeleteAllItems()

        #Do a quick sort of the times in the files
        tupples = []
        for ii in range(0, len(self.filelist)):
            tupples.append((self.filelist[ii], self.mjd_list[ii], ii))
        sortedlist = sorted(tupples, key=lambda mjd: mjd[1])
        self.sortindex = []
        for item in sortedlist:
            self.sortindex.append(long(item[2]))

        for jj in range(0, len(trunkfiles)):
            ii = self.sortindex[jj]
            
            dont_print = 0
            if self.exclude_prefix != '':
                nstring = self.exclude_prefix.__len__()
                if self.filelist[ii][0:nstring] == self.exclude_prefix:
                    dont_print = 1

            if dont_print == 0:

                self.filebox.InsertStringItem(index, self.filelist[ii])
                self.filebox.SetStringItem(index, 1,  self.object_list[ii])
                self.filebox.SetStringItem(index, 2,  self.UT_list[ii])
                self.filebox.SetStringItem(index, 3, self.exptime_list[ii])
                self.filebox.SetStringItem(index, 4, self.grating_list[ii])
                index += 1

        FITSUTIL.ReadParams(self)
        self.OnCreate(self)

        if self.selectedfile_index != -1 :
            self.filebox.Select(self.selectedfile_index)
            self.filebox.Focus(self.selectedfile_index)
            self.cbox.SetInsertionPointEnd()

    #Create the module that creates the pdf log
    def OnCreate(self, e):
       CreatePDF(self)

    def OnQuit(self, e):
        self.Close()

    def OnOpenLog(self, e):

        if self.selectedfile != '' :
            self.AddComment(self)
        CreatePDF(self)
        output_filename = self.currentDirectory + '/MMT_logsheet.pdf'
        if os.path.isfile(output_filename) == 0 :
            print "Log file not found yet, try again after you have scanned"
        else :
            os.system('open ' + output_filename)
                
if __name__ == '__main__':
    
    app = wx.App()
    LoggerGUI(None, title="MMT Logger")
    app.MainLoop()
