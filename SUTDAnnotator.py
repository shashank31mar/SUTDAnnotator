#!/usr/bin/env python
# coding=utf-8

##===================================================================##
#   Annotation tools
#   Written by Jie Yang at SUTD
#   Jan. 6, 2016
# 
##===================================================================##

from Tkinter import *
from ttk import *#Frame, Button, Label, Style, Scrollbar
import tkFileDialog
import tkFont
import re
from collections import deque



class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        self.fileName = ""
        self.history = deque(maxlen=10)
        self.currentContent = deque(maxlen=1)
        self.pressCommand = {'t':"TITLE", 'o':"ORG", 'd':"DATE",'a':"ACTION", 'e':"EDU",
         'g':"GEND",'c':"CONT", 'p':"PRO", 'r':"RACE",'l':"LOC", 'n':"NAME", 'm':"MISC"}
        self.allKey = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.controlCommand = {'q':"unTag", 'ctrl+z':'undo'}
        self.labelEntryList = []
        self.shortcutLabelList = []
        # default GUI display parameter
        self.textRow = 18
        self.textColumn = 5

        self.initUI()
        
        
    def initUI(self):
      
        self.parent.title("SUTDNLP Annotation Tool")
        self.pack(fill=BOTH, expand=True)
        
        for idx in range(0,self.textColumn):
            self.columnconfigure(idx, weight =2)
        # self.columnconfigure(0, weight=2)
        self.columnconfigure(self.textColumn+2, weight=1)
        self.columnconfigure(self.textColumn+4, weight=1)
        for idx in range(0,16):
            self.rowconfigure(idx, weight =1)
        # self.rowconfigure(5, weight=1)
        # self.rowconfigure(5, pad=7)
        
        self.lbl = Label(self, text="File: no file is opened")
        self.lbl.grid(sticky=W, pady=4, padx=5)

        fnt = tkFont.Font(family="Helvetica",size=self.textRow,weight="bold",underline=0)
        self.text = Text(self, font=fnt,selectbackground='red')
        self.text.grid(row=1, column=0, columnspan=self.textColumn, rowspan=self.textRow, padx=12, sticky=E+W+S+N)

        
        self.sb = Scrollbar(self)
        self.sb.grid(row = 1, column = self.textColumn, rowspan = self.textRow, padx=0, sticky = E+W+S+N)
        self.text['yscrollcommand'] = self.sb.set 
        self.sb['command'] = self.text.yview 
        # self.sb.pack()

        abtn = Button(self, text="Open", command=self.onOpen)
        abtn.grid(row=1, column=self.textColumn +1)

        ubtn = Button(self, text="Update map", command=self.renewPressCommand)
        ubtn.grid(row=2, column=self.textColumn +1, pady=4)

        exportbtn = Button(self, text="Export", command=self.generateSequenceFile)
        exportbtn.grid(row=3, column=self.textColumn +1, pady=4)

        cbtn = Button(self, text="Quit", command=self.quit)
        cbtn.grid(row=4, column=self.textColumn +1, pady=4)

        self.cursorName = Label(self, text="Cursor: ", foreground="red", font=("Helvetica", 14, "bold"))
        self.cursorName.grid(row=5, column=self.textColumn +1, pady=4)
        self.cursorIndex = Label(self, text="", foreground="red", font=("Helvetica", 14, "bold"))
        self.cursorIndex.grid(row=6, column=self.textColumn +1, pady=4)
        
        # obtn = Button(self, text="OK")
        # obtn.grid(row=5, column=3) 

        lbl_entry = Label(self, text="Command:")
        lbl_entry.grid(row = self.textRow +1,  sticky = E+W+S+N, pady=4,padx=4)
        self.entry = Entry(self)
        self.entry.grid(row = self.textRow +1, columnspan=self.textColumn + 1, rowspan = 1, sticky = E+W+S+N, pady=4, padx=80)
        self.entry.bind('<Return>', self.returnEnter)

        
        # for press_key in self.pressCommand.keys():
        for idx in range(0, len(self.allKey)):
            press_key = self.allKey[idx:idx+1]
            self.text.bind(press_key, lambda event, arg=press_key:self.textReturnEnter(event,arg))
            simplePressKey = "<KeyRelease-" + press_key + ">"
            self.text.bind(simplePressKey, self.deleteTextInput)
            controlPlusKey = "<Control-Key-" + press_key + ">"
            self.text.bind(controlPlusKey, self.keepCurrent)
            altPlusKey = "<Command-Key-" + press_key + ">"
            self.text.bind(altPlusKey, self.keepCurrent)
            
        # self.text.bind('<Return>', self.pushToHistoryEvent)
        # self.text.bind('<KeyRelease-Return>', self.backToHistory)

        self.text.bind('<Control-Key-z>', self.backToHistory)


        self.setMapShow()


        # control_text = "Control key: \n"
        # for press_key in self.controlCommand.keys():
        #     control_text += press_key + "-> " + self.controlCommand[press_key] + '\n'
        # control_table = Label(self, text=control_text, foreground="red", font=("Helvetica", 13))
        # control_table.grid(row=4, column=self.textColumn +1)

        self.enter = Button(self, text="Enter", command=self.returnButton)
        self.enter.grid(row=self.textRow +1, column=self.textColumn +1) 
 

    def onOpen(self):
        ftypes = [('all files', '.*'), ('text files', '.txt'), ('ann files', '.ann')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        # file_opt = options =  {}
        # options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        # dlg = tkFileDialog.askopenfilename(**options)
        fl = dlg.show()
        if fl != '':
            self.text.delete("1.0",END)
            text = self.readFile(fl)
            self.text.insert(END, text)
            self.setNameLabel("File: " + fl)
            self.setDisplay()
            # self.initAnnotate()
            self.text.mark_set(INSERT, "1.0")
            self.setCursorLabel(self.text.index(INSERT))

    def readFile(self, filename):
        f = open(filename, "r")
        text = f.read()
        self.fileName = filename
        return text

    def setFont(self, value):
        _family="Helvetica"
        _size = value
        _weight="bold"
        _underline=0
        fnt = tkFont.Font(family= _family,size= _size,weight= _weight,underline= _underline)
        Text(self, font=fnt)
    
    def setNameLabel(self, new_file):
        self.lbl.config(text=new_file)

    def setCursorLabel(self, new_file):
        self.cursorIndex.config(text=new_file)

    # def initAnnotate():
    #     text = self.text.get('1.0','end-1c')
        

    def returnButton(self):
        self.pushToHistory()
        # self.returnEnter(event)
        content = self.entry.get()
        self.clearCommand()
        self.executeEntryCommand(content)
        return content


    def returnEnter(self,event):
        self.pushToHistory()
        content = self.entry.get()
        self.clearCommand()
        self.executeEntryCommand(content)
        return content

    def textReturnEnter(self,event, press_key):
        self.pushToHistory()
        # print "event: ", press_key
        # content = self.text.get()
        self.clearCommand()
        self.executeCursorCommand(press_key.lower())
        # self.deleteTextInput()
        return press_key

    def backToHistory(self,event):
        if len(self.history) > 0:
            historyCondition = self.history.pop()
            # print "history condition: ", historyCondition
            historyContent = historyCondition[0]
            # print "history content: ", historyContent
            cursorIndex = historyCondition[1]
            # print "get history cursor: ", cursorIndex
            self.writeFile(self.fileName, historyContent, cursorIndex)
        else:
            print "History is empty!"
        self.text.insert(INSERT, 'p')   # add a word as pad for key release delete

    def keepCurrent(self, event):
        self.text.insert(INSERT, 'p')


    def clearCommand(self):
        self.entry.delete(0, 'end')


    def getText(self):
        textContent = self.text.get("1.0","end-1c")
        textContent = textContent.encode('utf-8')
        return textContent

    def executeCursorCommand(self,command):
        content = self.getText()
        firstSelection_index = self.text.index(SEL_FIRST)
        cursor_index = self.text.index(SEL_LAST)
        aboveHalf_content = self.text.get('1.0',firstSelection_index).encode('utf-8')
        followHalf_content = self.text.get(firstSelection_index, "end-1c").encode('utf-8')
        try:
            selected_string = self.text.selection_get().encode('utf-8')
            if ((command == "q")&(selected_string[0] == '[')&(selected_string[-1] == ']')&(selected_string.find('#')>0)&(selected_string.find('*')>0)):
                print "q yes"
                if True:    
                    new_string_list = selected_string.strip('[]').rsplit('#',1)
                    new_string = ''
                    # for idx in range(0, len(new_string_list)-1):
                    #     new_string += new_string_list[idx]
                    new_string = new_string_list[0]
                    followHalf_content = followHalf_content.replace(selected_string, new_string,1)
                    content = aboveHalf_content + followHalf_content
                    # newcursor_index = "%s - %sc" % (cursor_index, str(len(selected_string)-len(new_string)))
                    print "q length: ", len(new_string_list[1]), new_string_list[1], cursor_index

                    newcursor_index = "%s - %sc" % (cursor_index, str(len(new_string_list[1])+3))
                    print "new index: ", newcursor_index
                    self.writeFile(self.fileName, content, newcursor_index)
            else:
                if len(selected_string) > 0:
                    # print "insert index: ", self.text.index(INSERT) 
                    followHalf_content, newcursor_index = self.replaceString(followHalf_content, selected_string, command, cursor_index)
                    content = aboveHalf_content + followHalf_content
                self.writeFile(self.fileName, content, newcursor_index)
        except ValueError:
            print "Have not selected content!"


    def executeEntryCommand(self,command):
        if len(command) == 0:
            currentCursor = self.text.index(INSERT)
            newCurrentCursor = str(int(currentCursor.split('.')[0])+1) + ".0"
            self.text.mark_set(INSERT, newCurrentCursor)
            self.setCursorLabel(newCurrentCursor)
        else:
            command_list = decompositCommand(command)
            for idx in range(0, len(command_list)):
                command = command_list[idx]
                if len(command) == 2:
                    select_num = int(command[0])
                    command = command[1]
                    content = self.getText()
                    cursor_index = self.text.index(INSERT)
                    newcursor_index = cursor_index.split('.')[0]+"."+str(int(cursor_index.split('.')[1])+select_num)
                    # print "new cursor position: ", select_num, " with ", newcursor_index, "with ", newcursor_index
                    selected_string = self.text.get(cursor_index, newcursor_index).encode('utf-8')
                        
                    aboveHalf_content = self.text.get('1.0',cursor_index).encode('utf-8')
                    followHalf_content = self.text.get(cursor_index, "end-1c").encode('utf-8')
                        
                    if command in self.pressCommand:
                        if len(selected_string) > 0:
                            # print "insert index: ", self.text.index(INSERT) 
                            followHalf_content, newcursor_index = self.replaceString(followHalf_content, selected_string, command, newcursor_index)
                            content = aboveHalf_content + followHalf_content
                    self.writeFile(self.fileName, content, newcursor_index)
            

    def deleteTextInput(self,event):
        get_insert = self.text.index(INSERT)
        insert_list = get_insert.split('.')
        last_insert = insert_list[0] + "." + str(int(insert_list[1])-1)
        get_input = self.text.get(last_insert, get_insert).encode('utf-8')
        # print "get_input: ", get_input
        aboveHalf_content = self.text.get('1.0',last_insert).encode('utf-8')
        followHalf_content = self.text.get(last_insert, "end-1c").encode('utf-8')
        if len(get_input) > 0: 
            followHalf_content = followHalf_content.replace(get_input, '', 1)
            content = aboveHalf_content + followHalf_content
        self.writeFile(self.fileName, content, last_insert)



    def replaceString(self, content, string, replaceType, cursor_index):
        if replaceType in self.pressCommand:
            new_string = "[" + string + '#' + self.pressCommand[replaceType] + "*]" 
            cursor_indexList = cursor_index.split('.') 
            newcursor_index = "%s + %sc" % (cursor_index, str(len(self.pressCommand[replaceType])+4))
            # newcursor_index = cursor_indexList[0] + "." + str(int(cursor_indexList[1])+ len(new_string))
        else:
            print "Invaild command!"  
            print "cursor index: ", self.text.index(INSERT)  
            return content, cursor_index
        # print "new string: ", new_string
        # print "find: ", content.find(string)
        content = content.replace(string, new_string,1)
        # print "content: ", content
        return content, newcursor_index


    def writeFile(self, fileName, content, newcursor_index):
        if len(fileName) > 0:
            if ".ann" in fileName:
                new_name = fileName
                ann_file = open(new_name, 'w')
                ann_file.write(content)
                ann_file.close()
            else:
                new_name = fileName+'.ann'
                ann_file = open(new_name, 'w')
                ann_file.write(content)
                ann_file.close()   
            # print "Writed to new file: ", new_name 
            self.autoLoadNewFile(new_name, newcursor_index)
            # self.generateSequenceFile()
        else:
            print "Don't write to empty file!"        


    def autoLoadNewFile(self, fileName, newcursor_index):
        if len(fileName) > 0:
            self.text.delete("1.0",END)
            text = self.readFile(fileName)
            self.text.insert("end-1c", text)
            self.setNameLabel("File: " + fileName)
            self.text.mark_set(INSERT, newcursor_index)
            self.text.see(newcursor_index)
            self.setCursorLabel(newcursor_index)
            self.setLineDisplay()
            


    def setLineDisplay(self):
        self.text.config(insertbackground='red', insertwidth=4)

        countVar = StringVar()
        currentCursor = self.text.index(INSERT)
        lineStart = currentCursor.split('.')[0] + '.0'
        lineEnd = currentCursor.split('.')[0] + '.end'
        self.text.mark_set("matchStart", lineStart)
        self.text.mark_set("matchEnd", lineStart) 
        self.text.mark_set("searchLimit", lineEnd)
        while True:
            self.text.tag_configure("catagory", background="green")
            self.text.tag_configure("edge", background="blue")
            pos = self.text.search(r'\[.*?\#.*?\*\]', "matchEnd" , "searchLimit",  count=countVar, regexp=True)
            if pos =="":
                break
            self.text.mark_set("matchStart", pos)
            self.text.mark_set("matchEnd", "%s+%sc" % (pos, countVar.get()))
            
            first_pos = pos
            second_pos = "%s+%sc" % (pos, str(1))
            lastsecond_pos = "%s+%sc" % (pos, str(int(countVar.get())-1))
            last_pos = "%s + %sc" %(pos, countVar.get())

            self.text.tag_add("catagory", second_pos, lastsecond_pos)
            self.text.tag_add("edge", first_pos, second_pos)
            self.text.tag_add("edge", lastsecond_pos, last_pos)    



    def setDisplay(self):
        self.text.config(insertbackground='red', insertwidth=4)

        self.text.mark_set("matchStart", "1.0")
        self.text.mark_set("matchEnd", "1.0") 
        self.text.mark_set("searchLimit", 'end-1c')

        
        countVar = StringVar()
        # for annotate_type in self.pressCommand.values():
        while True:
            self.text.tag_configure("catagory", background="green")
            self.text.tag_configure("edge", background="blue")
            pos = self.text.search(r'\[.*?\#.*?\*\]', "matchEnd" , "searchLimit",  count=countVar, regexp=True)
            if pos =="":
                break
            self.text.mark_set("matchStart", pos)
            self.text.mark_set("matchEnd", "%s+%sc" % (pos, countVar.get()))
            
            first_pos = pos
            second_pos = "%s+%sc" % (pos, str(1))
            lastsecond_pos = "%s+%sc" % (pos, str(int(countVar.get())-1))
            last_pos = "%s + %sc" %(pos, countVar.get())

            self.text.tag_add("catagory", second_pos, lastsecond_pos)
            self.text.tag_add("edge", first_pos, second_pos)
            self.text.tag_add("edge", lastsecond_pos, last_pos)
            
    
    def pushToHistory(self):
        currentList = []
        content = self.getText()
        cursorPosition = self.text.index(INSERT)
        # print "push to history cursor: ", cursorPosition
        currentList.append(content)
        currentList.append(cursorPosition)
        self.history.append(currentList)

    def pushToHistoryEvent(self,event):
        currentList = []
        content = self.getText()
        cursorPosition = self.text.index(INSERT)
        # print "push to history cursor: ", cursorPosition
        currentList.append(content)
        currentList.append(cursorPosition)
        self.history.append(currentList)


    def renewPressCommand(self):
        seq = 0
        new_dict = {}
        listLength = len(self.labelEntryList)
        delete_num = 0
        for key in sorted(self.pressCommand):
            label = self.labelEntryList[seq].get()
            if len(label) > 0:
                new_dict[key] = label
            else: 
                delete_num += 1
            seq += 1
        self.pressCommand = new_dict
        for idx in range(1, delete_num+1):
            self.labelEntryList[listLength-idx].delete(0,END)
            self.shortcutLabelList[listLength-idx].config(text="NON== ") 

        self.setMapShow()


    def setMapShow(self):
        hight = len(self.pressCommand)
        width = 2
        row = 0
        mapLabel = Label(self, text ="Shortcuts map Labels", foreground="blue", font=("Helvetica", 14, "bold"))
        mapLabel.grid(row=0, column = self.textColumn +2,columnspan=2, rowspan = 1, padx = 10)
        self.labelEntryList = []
        self.shortcutLabelList = []
        for key in sorted(self.pressCommand):
            row += 1
            # print "key: ", key, "  command: ", self.pressCommand[key]
            symbolLabel = Label(self, text =key + " == ", foreground="blue", font=("Helvetica", 14, "bold"))
            symbolLabel.grid(row=row, column = self.textColumn +2,columnspan=1, rowspan = 1, padx = 3)
            self.shortcutLabelList.append(symbolLabel)

            labelEntry = Entry(self, foreground="blue", font=("Helvetica", 14, "bold"))
            labelEntry.insert(0, self.pressCommand[key])
            labelEntry.grid(row=row, column = self.textColumn +3, columnspan=1, rowspan = 1)
            self.labelEntryList.append(labelEntry)
            # print "row: ", row

    def getCursorIndex(self):
        return self.text.index(INSERT)


    # def export2seqformat(self,event):
    #     self.generateSequenceFile()


    def generateSequenceFile(self):
        if ".ann" not in self.fileName: 
            return -1
        fileLines = open(self.fileName, 'rU').readlines()
        new_filename = self.fileName.split('.ann')[0]+ '.anns'
        seqFile = open(new_filename, 'w')
        for line in fileLines:
            if len(line) <= 2:
                seqFile.write('\n')
                continue
            else:
                wordTagPairs = getWordTagPairs(line)
                for wordTag in wordTagPairs:
                    seqFile.write(wordTag)
        seqFile.close()
        print "Exported file into sequence style in file: ",new_filename


def getWordTagPairs(tagedSentence):
    newSent = tagedSentence.strip('\n').decode('utf-8')
    filterList = re.findall('\[.*?\#.*?\*\]', newSent)
    newSentLength = len(newSent)
    pairList = []
    chunk_list = []
    start_pos = 0
    end_pos = 0
    if len(filterList) == 0:
        singleChunkList = []
        singleChunkList.append(newSent)
        singleChunkList.append(0)
        singleChunkList.append(len(newSent))
        singleChunkList.append(False)
        chunk_list.append(singleChunkList)
        # print singleChunkList
        singleChunkList = []
    else:
        for pattern in filterList:
            singleChunkList = []
            start_pos = end_pos + newSent[end_pos:].find(pattern)
            end_pos = start_pos + len(pattern)
            singleChunkList.append(pattern)
            singleChunkList.append(start_pos)
            singleChunkList.append(end_pos)
            singleChunkList.append(True)
            chunk_list.append(singleChunkList)
            singleChunkList = []
    full_list = []
    for idx in range(0, len(chunk_list)):
        if idx == 0:
            if chunk_list[idx][1] > 0:
                full_list.append([newSent[0:chunk_list[idx][1]], 0, chunk_list[idx][1], False])
                full_list.append(chunk_list[idx])
            else:
                full_list.append(chunk_list[idx])
        else:
            if chunk_list[idx][1] == chunk_list[idx-1][2]:
                full_list.append(chunk_list[idx])
            elif chunk_list[idx][1] < chunk_list[idx-1][2]:
                print "ERROR: found pattern has overlap!", chunk_list[idx][1], ' with ', chunk_list[idx-1][2]
            else:
                full_list.append([newSent[chunk_list[idx-1][2]:chunk_list[idx][1]], chunk_list[idx-1][2], chunk_list[idx][1], False])
                full_list.append(chunk_list[idx])

        if idx == len(chunk_list) - 1 :
            if chunk_list[idx][2] > newSentLength:
                print "ERROR: found pattern position larger than sentence length!"
            elif chunk_list[idx][2] < newSentLength:
                full_list.append([newSent[chunk_list[idx][2]:newSentLength], chunk_list[idx][2], newSentLength, False])
            else:
                continue
                
    for each_list in full_list:
        if each_list[3]:
            contLabelList = each_list[0].strip('[]').rsplit('#', 1)
            if len(contLabelList) != 2:
                print "Error: sentence format error!"
            label = contLabelList[1].strip('*')
            contentLength = len(contLabelList[0])
            for idx in range(0, contentLength):
                if label != 'MISC':
                    if idx == 0:
                        pair = contLabelList[0][idx]+ ' ' + 'B-' + label + '\n'
                        pairList.append(pair.encode('utf-8'))
                    else:
                        pair = contLabelList[0][idx]+ ' ' + 'I-' + label + '\n'
                        pairList.append(pair.encode('utf-8'))
                else:
                    pair = contLabelList[0][idx] + ' ' + 'O' + '\n'
                    pairList.append(pair.encode('utf-8'))
        else:
            for idx in range(0, len(each_list[0])):
                pair = each_list[0][idx]+ ' ' + 'O\n'
                pairList.append(pair.encode('utf-8'))
    # for i in pairList:
    #     print i
    return pairList


def decompositCommand(command_string):
    command_list = []
    each_command = []
    num_select = ''
    for idx in range(0, len(command_string)):
        if command_string[idx].isdigit():
            num_select += command_string[idx]
        else:
            each_command.append(num_select)
            each_command.append(command_string[idx])
            command_list.append(each_command)
            each_command = []
            num_select =''
    # print command_list
    return command_list



def main():
    root = Tk()
    root.geometry("1000x700+200+200")
    app = Example(root)
    app.setFont(17)
    root.mainloop()  


if __name__ == '__main__':
    main()
    # sent = "[洪理芳#NAME*][先生#GEND*][历任#ACTION*][皖南电机厂#ORG*][厂长#TITLE*][、#MISC*][党委书记#TITLE*][；#MISC*][宣城行署机电局#ORG*][副局长#TITLE*][、#MISC*][党组书记#TITLE*][；#MISC*][皖南机动车辆厂#ORG*][厂长#TITLE*][、#MISC*][党委书记#TITLE*][；#MISC*][安徽飞彩（集团）有限公司#ORG*][董事长#TITLE*][、#MISC*][总经理#TITLE*][；#MISC*][安徽飞彩车辆股份有限公司#ORG*][董事长#TITLE*][、#MISC*][总经理#TITLE*][。#MISC*][现任#ACTION*][安徽飞彩车辆股份有限公司#ORG*][董事长#TITLE*][。#MISC*]"
    # newSent = sent.decode('utf-8')
    # filterList = re.findall('\[.*?\#.*?\*\]', newSent)
    # newSentLength = len(newSent)
    # pairList = []
    # print "length: ", len(sent), len(newSent)
    # chunk_list = []
    # start_pos = 0
    # end_pos = 0
    # for pattern in filterList:

    #     singleChunkList = []
    #     # pattern = pattern.decode('utf-8')
    #     print "pattern: ",  " length: ", len(pattern)
    #     start_pos = end_pos + newSent[end_pos:].find(pattern)
    #     end_pos = start_pos + len(pattern)
    #     print "pos: ", start_pos, ' ', end_pos, pattern.encode('utf-8')
    #     singleChunkList.append(pattern)
    #     singleChunkList.append(start_pos)
    #     singleChunkList.append(end_pos)
    #     singleChunkList.append(True)
    #     chunk_list.append(singleChunkList)
    #     singleChunkList = []
    # full_list = []
    # for idx in range(0, len(chunk_list)):
    #     if idx == 0:
    #         if chunk_list[idx][1] > 0:
    #             full_list.append([newSent[0:chunk_list[idx][1]], 0, chunk_list[idx][1], False])
    #             full_list.append(chunk_list[idx])
    #         else:
    #             full_list.append(chunk_list[idx])
    #     else:
    #         if chunk_list[idx][1] == chunk_list[idx-1][2]:
    #             full_list.append(chunk_list[idx])
    #         elif chunk_list[idx][1] < chunk_list[idx-1][2]:
    #             print "ERROR: found pattern has overlap!", chunk_list[idx][1], ' with ',chunk_list[idx-1][2]
    #         else:
    #             full_list.append([newSent[chunk_list[idx-1][2]:chunk_list[idx][1]], chunk_list[idx-1][2], chunk_list[idx][1], False])
    #             full_list.append(chunk_list[idx])

    #     if idx == len(chunk_list) - 1 :
    #         if chunk_list[idx][2] > newSentLength:
    #             print "ERROR: found pattern position larger than sentence length!"
    #         elif chunk_list[idx][2] < newSentLength:
    #             full_list.append([newSent[chunk_list[idx][2]:newSentLength], chunk_list[idx][2], newSentLength, False])
    #         else:
    #             continue
                
    # for each_list in full_list:
    #     if each_list[3]:
    #         contLabelList = each_list[0].strip('[]').rsplit('#', 1)
    #         if len(contLabelList) != 2:
    #             print "Error: sentence format error!"
    #         label = contLabelList[1].strip('*')
    #         contentLength = len(contLabelList[0])
    #         for idx in range(0, contentLength):
    #             if label != 'MISC':
    #                 if idx == 0:
    #                     pairList.append(contLabelList[0][idx] + ' ' + 'B-' + label + '\n')
    #                 else:
    #                     pairList.append(contLabelList[0][idx] + ' ' + 'I-' + label + '\n')
    #             else:
    #                 pairList.append(contLabelList[0][idx] + ' ' + 'O' + '\n')
    #     else:
    #         for idx in range(0, len(each_list[0])):
    #             pairList.append(each_list[0][idx] + ' ' + 'O\n')
    # for i in pairList:
    #     print i.encode('utf-8')




