"""
This is a housing of various tools that will help the main logger code be less bloated.
"""
import os 
from reportlab.pdfgen import canvas, pdfimages
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape, portrait
from reportlab.lib.units import inch, mm 
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import Image
import re
from jdate import julian_date

"""
This code allows the log to contain "Page x of y" and was 
originally copied from 
http://code.activestore.com/recipes/546511
"""
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._codes = []
    def showPage(self):
        self._codes.append({'code': self._code, 'stack': self._codeStack})
        self._startPage()
    def save(self):
        """add page info to each page (page x of y)"""
        # reset page counter 
        self._pageNumber = 0
        for code in self._codes:
            # recall saved page
            self._code = code['code']
            self._codeStack = code['stack']
            self.setFont("Times-Roman", 9)
            #self.drawRightString(200*mm, 20*mm,
            self.drawString(0.3*inch, 0.3*inch,
                            "Page %(this)i of %(total)i" % {
                    'this': self._pageNumber+1,
                    'total': len(self._codes),
                    }
                            )
            canvas.Canvas.showPage(self)
            self._doc.SaveToFile(self._filename, self)





#This little piece of code will read the existing files and match the comments to it. 
#This should take care of much of the bloat itself
def ReadScanned(self):
    
    
    self.header_keys = []
    self.file_list = []
    self.object_list = []
    self.UT_list = []
    self.filterlist_list = []
    self.grating_list = []
    self.slit_list = []
    self.cenwave_list = []
    self.pa_list = []
    self.exptime_list = []
    self.airmass_list = []
    self.comment_list = []
    self.date_list = []
    self.mjd_list = []

    filelist_path = self.currentDirectory + '/.mmtlogger/filelist.dat'
    commentlist_path = self.currentDirectory + '/.mmtlogger/commentlist.dat'
    files_in = open(filelist_path, 'r')
    for line in files_in:

        #Set default parameters to keep things from crashing
        storedate = '1900-01-01'
        storetime = '0:00:00'

        if line[0] == '#' :
            junk = line.split('# ')
            self.header_keys.append(junk[1][:(len(junk[1])-1)])
        else  :
            words = line.split()
            file_base = words[0]
            syl = file_base.split('.')
            scounter = 0
            for sub in syl:
                if scounter == 0:
                    word = sub
                elif scounter < len(syl) -1 :
                    word = word + '.' + syl[scounter]
                scounter += 1
            self.file_list.append(word)
            counter = 1
            for key in self.header_keys:
                if key == 'EXPTIME':
                    self.exptime_list.append(words[counter])
                if key == 'AIRMASS':
                    self.airmass_list.append(words[counter])
                if key == 'UT':
                    self.UT_list.append(words[counter])
                    storetime = words[counter]
                if key == 'INSFILTE':
                    self.filterlist_list.append(words[counter])
                if key == 'CENWAVE':
                    self.cenwave_list.append(words[counter])
                if key == 'DISPERSE':
                    self.grating_list.append(words[counter])
                if key == 'APERTURE':
                    self.slit_list.append(words[counter])
                if key == 'POSANG':
                    self.pa_list.append(words[counter])
                    self.comment_list.append('')
                if key == 'DATE-OBS':                 
                    storedate = words[counter]
                    self.date_list.append(words[counter])
                counter +=1
            words = line.split('***') 
            self.object_list.append(words[1])

            #Calculate the MJD
            mjd = storedate.split('-')
            hms = storetime.split(':')
            
            julian = 0.0
            if len(mjd) == 3 & len(hms) == 3 :
                julian = julian_date(mjd[0],mjd[1],mjd[2],hms[0], hms[1], hms[2])
            self.mjd_list.append(julian)
    #read the comments      
 

            
    self.cfiles = []   
    self.oldcomments = []
    if os.path.isfile(commentlist_path) != 0:
       cin = open(commentlist_path, 'r')
       linecounter = 0
       filecounter = -1

       clinestart = []
       clineend = []

       
       for line in cin :
        if line[:len(self.newfile_string)] == self.newfile_string :
            filecounter += 1
            junk = line.split(self.newfile_string)
            newfile = junk[1].split()
            self.cfiles.append(newfile[0])
            clinestart.append(linecounter)
            if len(self.cfiles) != 1: clineend.append(linecounter-1)
            pastecomment = junk[1][len(newfile[0])+2:-1]
         
            self.oldcomments.append(pastecomment.strip())

        else : self.oldcomments[filecounter] += line
        linecounter += 1
        clineend.append(linecounter-1)


        



def CreatePDF(self):
    styles = getSampleStyleSheet()
    header_text = "MMT Observatory Observing Log Sheet"
    output_filename = self.currentDirectory +'/MMT_logsheet.pdf'
    elements = []
    
    ReadScanned(self)
    if len(self.file_list) > 0 :
        
        counter = 0
        maxline = 20
        for ii in range(0, len(self.file_list)):
            if self.file_list[ii] in self.cfiles:
                for jj in range(0, len(self.cfiles)):
                    if self.file_list[ii] == self.cfiles[jj] :
                        if len(self.oldcomments[jj]) < maxline :
                            self.comment_list[ii] = self.oldcomments[jj].strip()
                        else : 
                          
                            line = self.oldcomments[jj]
                            orig_line = line
                            stopsearch = 0
                            comment = ''
                            goal_length = len(line)
                            while stopsearch == 0:
                                if len(line) < maxline : 
                                    comment += line
                                    stopsearch = 1
                                elif int(' ' in line[0:maxline]) == 0 : 
                                    newseg = line[0:maxline] + '\n'
                                    goal_length += 1
                                    comment += newseg
                                    line = line[maxline+1:]
                                    if line == '' : stopsearch = 1
                                else :
                                    kk = [m.start() for m in re.finditer(' ', line[0:maxline])]
                                    newseg = line[0:(kk[-1])] + '\n'
                                    goal_length += 1
                                    comment += newseg
                                    line = line[kk[-1]+1:]
                                    
                                if len(comment) == goal_length : stopsearch = 1
                            if comment[-1] == '\n' : 
                                comment=comment.strip()
                            
                            self.comment_list[ii] = comment.strip()

        
        headers = ['File', 'Object','UT', 'Filter', 'Grating', 'Slit', 'Cenwave', 'PA', 'Exposure \n Time','Airmass', 'Comments']
        logentry = [headers]
        counter = 0

        #This *should* sort files by MJD
        tupples = []
        for ii in range(0, len(self.filelist)):
            tupples.append( (self.filelist[ii], self.mjd_list[ii], ii))
        sorted_tupples = sorted(tupples, key=lambda mjd: mjd[1])
        sortindex = []
        for item in sorted_tupples:
            sortindex.append(item[2])

        for ifile in self.file_list:
            sscounter = sortindex[counter]
            dont_print = 0
            if self.exclude_prefix != '':
                nstring = self.exclude_prefix.__len__()
                if ifile[0:nstring] == self.exclude_prefix:
                    dont_print = 1

            if dont_print == 0:
                logentry.append([self.file_list[sscounter], self.object_list[sscounter], 
                             self.UT_list[sscounter], self.filterlist_list[sscounter],
                             self.grating_list[sscounter], self.slit_list[sscounter],
                             self.cenwave_list[sscounter],self.pa_list[sscounter], 
                             self.exptime_list[sscounter], self.airmass_list[sscounter],self.comment_list[sscounter]])
            counter += 1

        #Set the Column widths for the log
        file_width = 1.5 # width of "File" column
        object_width = 1.2 
        other_width = 0.7
        filter_width = 1.0

        #Derive width of Comments
        totalwidth = other_width*(len(headers)-2)+object_width+file_width + (filter_width - other_width)
        comment_width = (11-totalwidth)*inch
        rowwidth = [file_width*inch, object_width*inch]
        for ii in range(0, len(headers)-3):
            rowwidth.append(other_width*inch)
        counter = 0
        for ii in headers:
            if ii == 'Filter':
                rowwidth[counter] = filter_width * inch
            counter += 1


        rowwidth.append(comment_width)
        log_table=Table(logentry, rowwidth, style=[
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey), 
                    ('BOX',(0,0),(-1,-1),2,colors.black), 
                    ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), (0xF0F0F0, None)),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-2, -1), 'CENTER')]) 

        PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)
        topmargin = 0.5*inch
        bottommargin = 0.5*inch
        leftmargin = 1.0*inch
        rightmargin = 1.0*inch
        top_position = PAGE_HEIGHT - topmargin

        doc = SimpleDocTemplate(output_filename,pagesize=landscape(letter),leftMargin=leftmargin,
            rightMargin=rightmargin,topMargin=topmargin,bottomMargin=bottommargin)
        logo_boxsize=(0.8*inch,0.8*inch)
        code_location = '/mmtobs.backup.files/mmtobs_applications/mmtlogger/'
#        code_location = '/Users/rcool/mmtlogger/'
        logoimage = code_location + '/mmtlogo.png'
        logo = Image.open(logoimage)

        #These will be set by the code at some point
        observer_text = self.observer
        instrument_text = self.instrument
        date_text = self.date
        program_text = self.program

        font_choice = 'Times-Roman'

        def myFirstPage(canvas, doc): 
            canvas.saveState() 
            canvas.setFont(font_choice,24) 
            canvas.drawCentredString(PAGE_WIDTH/2.0, top_position-0.2*inch, header_text)
            canvas.setFont(font_choice, 14)
            canvas.drawString(0.7*inch+logo_boxsize[0], top_position-0.6*inch, 'Observer: ' + observer_text) 
            canvas.drawString(0.7*inch+logo_boxsize[0], top_position-0.8*inch, 'Instrument: ' + instrument_text)
            canvas.drawString(8.5*inch-(0.7*inch+logo_boxsize[0]), top_position-0.6*inch, 'Date: ' + date_text)
            canvas.drawString(8.5*inch-(0.7*inch+logo_boxsize[0]), top_position-0.8*inch, 'Program: ' + program_text)
            canvas.drawInlineImage(logoimage,0.3*inch,top_position - logo_boxsize[1],width=logo_boxsize[0],
                                   height=logo_boxsize[1],preserveAspectRatio=True,anchor='nw')
            canvas.restoreState() 

        def myLaterPages(canvas, doc): 
            canvas.saveState() 

        elements.append(Spacer(1,1.0*inch)) 
        elements.append(log_table)
        # Write the document to disk
        doc.build(elements, onFirstPage=myFirstPage, onLaterPages=myLaterPages, canvasmaker=NumberedCanvas)

        #Open the file
   #os.system('open ' + output_filename)


       
       
       
