"""
Basic circuit solver
Mark Fernandez
msfernan
Section I
"""
#Basic circuit solver
from Tkinter import *
import copy
import tkSimpleDialog
import tkMessageBox

#Control######
def voltageSourcePressed(canvas):
    canvas.data.pieceSelected="VoltageSource"
    redrawAll(canvas)
    msg="""Enter the input voltage in Volts(V)
You only get to place 1 voltage source on the grid-the value of which
can be modified by clicking this button again"""
    val=tkSimpleDialog.askstring('Input Voltage:',msg)
    if(val!=None):
        try:
           val=float(val)
           canvas.data.inputVoltage=val
        except:
             canvas.data.errMsg="Input voltage must be integer or decimal"
             error(canvas)

def groundPressed(canvas):
    canvas.data.pieceSelected="Ground"        

def wirePressed(canvas):
    canvas.data.pieceSelected="Wire"

def resistorPressed(canvas):
    canvas.data.pieceSelected="Resistor"
    
def solvePressed(canvas):
    canvas.data.pieceSelected="Solve"
    getNodes(canvas)
    if(isLegalCircuit(canvas)):
       collapseAndSolve(canvas)
       canvas.data.current=canvas.data.inputVoltage/canvas.data.rnet

def deletePressed(canvas):
    canvas.data.pieceSelected="Delete"

def resetPressed(canvas):
    canvas.data.pieceSelected="Reset"
    if(tkMessageBox.askyesno('Reset',
                          'Are you sure you want to reset?')):
       init(canvas)
       
def nodeViewPressed(canvas):
    canvas.data.pieceSelected="NodeView"
    canvas.data.inDebugMode=not(canvas.data.inDebugMode)
    getNodes(canvas)
    redrawAll(canvas)

def keyPressed(canvas,event):
    if(event.keysym=='d'):
        canvas.data.inDebugMode=not(canvas.data.inDebugMode)
        getNodes(canvas)
        redrawAll(canvas)

def mousePressed(canvas,event):
    pressButton(canvas,event.x,event.y)#This checks if a button was pressed
    if(canvas.data.isItemSelected==False):
        canvas.data.selection=getLegalSelection(canvas,event.x,event.y)
        if(canvas.data.selection!=(-1,-1)):
            canvas.data.isItemSelected=True
            doSingleSelectionOperations(canvas)
            #Single Selection Operations include
            #adding/deleting a Voltage Source/Ground         
    else:#an item had been previously selected.
        canvas.data.nextSelection=getLegalSelection(canvas,event.x,event.y)
        if(canvas.data.selection==canvas.data.nextSelection):
            resetSelectionNextSelection(canvas)#selecting the same pt twice
        elif(not(canvas.data.nextSelection==(-1,-1) or
           canvas.data.selection==(-1,-1))):
            (x0,y0)=canvas.data.selection
            (x1,y1)=canvas.data.nextSelection
            if(x0==x1 or y0==y1):
               doDoubleSelectionOperations(canvas)
               #These include adding/deleting wires and resistors
            else:#The x0==x1 or y0==y1 condition is False here
                canvas.data.errMsg="Pieces cannot be placed diagonally"
                error(canvas)
                canvas.data.nextSelection=(-1,-1)
    redrawAll(canvas)

def doSingleSelectionOperations(canvas):
    #These include adding/deleting from a Voltage Source/Ground
    if(canvas.data.pieceSelected=="Ground" and
               canvas.data.isGround==False):
                appendToGroundList(canvas)
                canvas.data.isGround=True
                resetSelectionNextSelection(canvas)
    elif(canvas.data.pieceSelected=="VoltageSource" and
                 canvas.data.isVoltageSource==False
                 and canvas.data.inputVoltage!=None):
                 appendToVoltageSourceList(canvas)
                 canvas.data.isVoltageSource=True
                 redrawAll(canvas)
                 resetSelectionNextSelection(canvas)
    elif(canvas.data.pieceSelected=="Delete"):
                 deleteVoltageSourceGround(canvas)

def doDoubleSelectionOperations(canvas):
    #These include adding/deleting wires/resistors
    if(canvas.data.pieceSelected=="Resistor"):
                   msg='Enter the value for the resitor in ohms'
                   val=(tkSimpleDialog.askstring('Resistor',msg))
                   try:
                       if(val!=None):
                         val=float(val)
                         if(val!=0.0):
                            appendToResistorList(canvas,val)
                         else:
                             canvas.data.errMsg="Value cant be 0 ohm"
                             error(canvas)
                   except:
                       canvas.data.errMsg="Values must be integers or decimals"
                       error(canvas)
                       resetSelectionNextSelection(canvas)
    elif(canvas.data.pieceSelected=="Wire"):
                   appendToWireList(canvas)
    elif(canvas.data.pieceSelected=="Delete"):
                    deleteSelectionIfPossible(canvas)                  
    resetSelectionNextSelection(canvas)
    
def pressButton(canvas,x0,y0):
    multFactor=0
    divFactor=2
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    maxmult=70
    if(left<x0<right):
        while(multFactor<=maxmult):
            top=canvas.data.margin+multFactor*canvas.data.border
            bottom=top+40
            if(top<=y0<=bottom and multFactor==0):
               voltageSourcePressed(canvas)
               canvas.data.rnet=None#This is so that rnet is not drawn
               #not needed
               break
            elif(top<=y0<=bottom and multFactor==10):
               groundPressed(canvas)
               canvas.data.rnet=None
               canvas.data.current=None
               break
            elif(top<=y0<=bottom and multFactor==20):
                wirePressed(canvas)
                canvas.data.rnet=None
                canvas.data.current=None
                break
            elif(top<=y0<=bottom and multFactor==30):
                resistorPressed(canvas)
                canvas.data.rnet=None
                canvas.data.current=None
                break
            elif(top<=y0<=bottom and multFactor==40):
                deletePressed(canvas)
                canvas.data.rnet=None
                canvas.data.current=None
                break
            elif(top<=y0<=bottom and multFactor==50):
                solvePressed(canvas)
                break
            elif(top<=y0<=bottom and multFactor==60):
                resetPressed(canvas)
                break
            elif(top<=y0<=bottom and multFactor==70):
                 nodeViewPressed(canvas)
                 break
            multFactor+=10

    
#View#########
def redrawAll(canvas):
    canvas.delete(ALL)
    drawCanvas(canvas)
    if(canvas.data.inDebugMode):
       drawDebugBoard(canvas)
    drawGrid(canvas)
    drawVoltageSourceButton(canvas)
    drawGroundButton(canvas)
    drawWireButton(canvas)
    drawResistorButton(canvas)
    drawDeleteButton(canvas)
    drawSolveButton(canvas)
    drawResetButton(canvas)
    drawNodeViewButton(canvas)
    drawWires(canvas)
    if(canvas.data.isVoltageSource):
        drawWires(canvas)
        drawVoltageSource(canvas)
    drawResistors(canvas)
    drawGround(canvas)
    drawSelectedOval(canvas)
    drawOutputScreen(canvas)
    
def drawOutputScreen(canvas):
    adjust=10
    left=canvas.data.width-canvas.data.margin+adjust
    right=canvas.data.width-adjust
    top=canvas.data.margin
    bottom=canvas.data.height-canvas.data.margin
    canvas.create_rectangle(left,top,right,bottom,
                            width=canvas.data.lineWidth)
    left+=10
    top+=10
    colour="black"
    f="Times 18"
    if(canvas.data.inputVoltage!=None and
       canvas.data.isVoltageSource==True):
       canvas.create_text(left, top, 
                       text="V: %0.3fV"%(canvas.data.inputVoltage),
                       fill=colour,anchor=W,
                       font=f)
    top+=20
    for i in xrange(len(canvas.data.resistorList)):
        (row0,col0,row1,col1,val)=canvas.data.resistorList[i]
        canvas.create_text(left, top, text="R%d: %0.2fOhm"%(i,val),
                            fill=colour,anchor=W,
                           font=f)
        top+=20
    if(canvas.data.rnet!=None):
       canvas.create_text(left, top, text="Rnet: %0.2fOhm"%(canvas.data.rnet),
                            fill=colour,anchor=W,
                           font=f )
    top+=20
    if(canvas.data.current!=None):
       canvas.create_text(left, top,
                       text="Inet: %0.2fA"%(canvas.data.current),
                       fill=colour,anchor=W,
                       font=f)
        
def drawGround(canvas):
    if(canvas.data.groundList!=[]):
       (row,col)=canvas.data.groundList[0]
       (x0,y0,igX1,igY1)=getGridCellBounds(canvas,row,col)
       r=10
       ovalColour="green"
       lineColour="green"
       canvas.create_line(x0,y0,x0,y0+canvas.data.cellSize/2,
       fill=lineColour,width=canvas.data.lineWidth/2)
       canvas.create_line(x0-r/4,y0+1.9*r,x0+r/4,y0+1.9*r,fill=lineColour)
       canvas.create_line(x0-r/2,y0+1.7*r,x0+r/2,y0+1.7*r,fill=lineColour)
       canvas.create_line(x0-r,y0+1.5*r,x0+r,y0+1.5*r,fill=lineColour)
       canvas.create_oval(x0-r/2,y0-r/2,x0+r/2,y0+r/2,fill=ovalColour)
       #Magic numbers needed to draw the ground accurately.
       #They draw 3 lines of decreasing lengths
       
        
def drawVoltageSource(canvas):
    if(canvas.data.voltageSourceList!=[]):
       (row,col)=canvas.data.voltageSourceList[0]
       (x0,y0,igX1,igY1)=getGridCellBounds(canvas,row,col)
       r=10
       ovalColour="red"
       lineColour="green"
       canvas.create_line(x0,y0,x0,y0+canvas.data.cellSize/2,
                          fill=lineColour,width=canvas.data.lineWidth/2)
       canvas.create_line(x0-r/4,y0+1.9*r,x0+r/4,y0+1.9*r,fill=lineColour)
       canvas.create_line(x0-r/2,y0+1.7*r,x0+r/2,y0+1.7*r,fill=lineColour)
       canvas.create_line(x0-r,y0+1.5*r,x0+r,y0+1.5*r,fill=lineColour)
       canvas.create_oval(x0-r,y0-r,x0+r,y0+r,fill=ovalColour)
       #Magic numbers needed to draw the ground accurately.
       #They draw 3 lines of decreasing lengths

def drawWires(canvas):
    (x0,y0)=canvas.data.selection
    r=canvas.data.lineWidth
    ovalColour=canvas.data.selectionColour
    canvas.create_oval(x0-r,y0-r,x0+r,y0+r,fill=ovalColour)
    cellSize=canvas.data.cellSize
    colour="black"
    for w in canvas.data.wireList:
        (startRow,startCol,endRow,endCol)=w
        (startX,startY,ignoreX,ignoreY)=getGridCellBounds(canvas,\
                                                    startRow,startCol)
        (endX,endY,ignoreX,ignoreY)=getGridCellBounds(canvas,\
                                                      endRow,endCol)
        if(startRow==endRow):
           canvas.create_line(startX,startY,endX,startY,fill=colour,\
                               width=canvas.data.lineWidth)
           drawOval(canvas,startX,startY,colour)
           drawOval(canvas,endX,startY,colour)
        elif(startCol==endCol):
            canvas.create_line(startX,startY,startX,endY,fill=colour,\
                           width=canvas.data.lineWidth)
            drawOval(canvas,startX,startY,colour)
            drawOval(canvas,startX,endY,colour)

def drawResistors(canvas):
    cellSize=canvas.data.cellSize
    colour="white"
    for i in xrange(len(canvas.data.resistorList)):
        (startRow,startCol,endRow,endCol,ignoreVal)=canvas.data.resistorList[i]
        (startX,startY,endX,endY)=getGridCellBounds(canvas,\
                                                    startRow,startCol)
        adj=canvas.data.cellSize/4
        rcolour="black"
        if(startRow==endRow):
            drawRowEqualResistors(canvas,startX,startY,endX,endY,adj,
                                  colour,rcolour,i)

        elif(startCol==endCol):
            drawColEqualResistors(canvas,startX,startY,endX,endY,adj,
                                  colour,rcolour,i)
            

def drawRowEqualResistors(canvas,startX,startY,endX,endY,adj,
                          colour,rcolour,i):
    canvas.create_line(startX,startY,endX,startY,fill=colour,\
                               width=canvas.data.lineWidth)
    canvas.create_line(startX,startY,startX+adj,startY-adj,
                              fill=rcolour)
    canvas.create_line(startX+adj,startY-adj,startX+2*adj,
                          startY,fill=rcolour)
    canvas.create_line(startX+2*adj,startY,startX+3*adj,startY-adj,
                           fill=rcolour)
    canvas.create_line(startX+3*adj,startY-adj,startX+4*adj,startY,
                           fill=rcolour)
    drawOval(canvas,startX,startY,colour)
    drawOval(canvas,endX,startY,colour)
    canvas.create_text(startX+2*adj,startY-1.5*adj,text="R%d"%(i))

def drawColEqualResistors(canvas,startX,startY,endX,endY,adj,
                          colour,rcolour,i):
    canvas.create_line(startX,startY,startX,endY,fill=colour,\
                           width=canvas.data.lineWidth)
    canvas.create_line(startX,startY,startX+adj,startY+adj)
    canvas.create_line(startX+adj,startY+adj,startX,startY+2*adj)
    canvas.create_line(startX,startY+2*adj,startX+adj,startY+3*adj)
    canvas.create_line(startX+adj,startY+3*adj,startX,startY+4*adj)                       
    drawOval(canvas,startX,startY,colour)
    drawOval(canvas,startX,endY,colour)
    canvas.create_text(startX+1.5*adj,startY+2*adj,text="R%d"%(i))
    
                          
def drawOval(canvas,x0,y0,ovalColour):
    r=canvas.data.lineWidth
    canvas.create_oval(x0-r,y0-r,x0+r,y0+r,fill=ovalColour)
        
def drawSelectedOval(canvas):
    (x0,y0)=canvas.data.selection
    r=canvas.data.lineWidth
    ovalColour=canvas.data.selectionColour
    canvas.create_oval(x0-r,y0-r,x0+r,y0+r,fill=ovalColour)

def drawCanvas(canvas):
    margin=canvas.data.margin
    width=canvas.data.width
    height=canvas.data.height
    border=canvas.data.border
    colour=canvas.data.colour
    canvas.create_rectangle(margin, margin, width-margin, height-margin,
                         fill=colour,width=border)
    
def drawDebugBoard(canvas):
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            drawDebugCell(canvas,row,col)

def drawDebugCell(canvas,row,col):
    (x0,y0,x1,y1)=getDebugCellBounds(canvas,row,col)
    canvas.create_rectangle(x0,y0,x1,y1)
    fontName="Helvatica"
    fontSize=12
    fontFormat="bold"
    cellSize=canvas.data.cellSize
    divFactor=4
    board=canvas.data.board
    canvas.create_text(x0+cellSize/divFactor,y0+cellSize/divFactor,
                               text=str(board[row][col]),
                               font=(fontName, fontSize,
                                     fontFormat))
def drawGrid(canvas):
    for row in xrange(canvas.data.rows-1):#not all rows and cols needed
        for col in xrange(canvas.data.cols-1):
            drawGridCell(canvas,row,col)

def drawGridCell(canvas,row,col):
    outlineColour="blue"
    w=canvas.data.lineWidth
    (x0,y0,x1,y1)=getGridCellBounds(canvas,row,col)
    canvas.create_rectangle(x0,y0,x1,y1,outline=outlineColour,width=w)

def drawVoltageSourceButton(canvas):
    divFactor=2
    top=canvas.data.margin
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    if(canvas.data.pieceSelected=="VoltageSource"
       and canvas.data.isVoltageSource==False):
        rectColour="green"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Voltage"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize
                                 ),fill=colour)

def drawGroundButton(canvas):
    divFactor=2
    multFactor=10
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    if(canvas.data.pieceSelected=="Ground"):
        rectColour="green"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Ground"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize
                                 ),fill=colour)

def drawWireButton(canvas):
    divFactor=2
    multFactor=20
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    if(canvas.data.pieceSelected=="Wire"):
        rectColour="green"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Wire"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize
                                 ),fill=colour)

def drawResistorButton(canvas):
    divFactor=2
    multFactor=30
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    if(canvas.data.pieceSelected=="Resistor"):
        rectColour="green"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Resistor"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize),fill=colour)
    
def drawDeleteButton(canvas):
    divFactor=2
    multFactor=40
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    if(canvas.data.pieceSelected=="Delete"):
        rectColour="green"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Delete"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize
                                 ),fill=colour)

def drawSolveButton(canvas):
    divFactor=2
    multFactor=50
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Solve"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize),fill=colour)

def drawResetButton(canvas):
    divFactor=2
    multFactor=60
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    canvas.create_rectangle(left,top,right,bottom,fill=rectColour)
    colour="black"
    message="Reset"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize
                                 ),fill=colour)

def drawNodeViewButton(canvas):
    divFactor=2
    multFactor=70
    top=canvas.data.margin+multFactor*canvas.data.border
    bottom=top+40
    left=canvas.data.margin/(2*divFactor)
    right=left+40*2
    rectColour="cyan"
    adj=5
    canvas.create_rectangle(left-adj,top,right+adj,bottom,fill=rectColour)
    colour="black"
    message="NodeView"
    fontName="Helvetica"
    fontSize=40/(divFactor)
    cx=(left+right)/2
    cy=(top+bottom)/2
    canvas.create_text(cx,cy, text=message,
                           font=(fontName, fontSize
                                 ),fill=colour)
#Model########
def error(canvas):
     tkMessageBox.showerror("Error",canvas.data.errMsg)
     canvas.data.errMsg=None    

def deleteVoltageSourceGround(canvas):
    (x0,y0)=canvas.data.selection
    (row,col)=translateIntoRowCol(canvas,x0,y0)
    if((row,col) in canvas.data.voltageSourceList):
        canvas.data.voltageSourceList=[]
        canvas.data.isVoltageSource=False
        resetSelectionNextSelection(canvas)
    elif((row,col) in canvas.data.groundList):
        canvas.data.groundList=[]
        canvas.data.isGround=False
        resetSelectionNextSelection(canvas)
   
def deleteSelectionIfPossible(canvas):
    (x0,y0)=canvas.data.selection
    (x1,y1)=canvas.data.nextSelection
    (row0,col0)=translateIntoRowCol(canvas,x0,y0)
    (row1,col1)=translateIntoRowCol(canvas,x1,y1)
    flag=0
    if(row1<row0):
        (row0,row1)=(row1,row0)
    elif(col1<col0):
        (col0,col1)=(col1,col0)
    for r in canvas.data.resistorList:
        (srow,scol,erow,ecol,igVal)=r
        if((srow,scol,erow,ecol)==(row0,col0,row1,col1)):
            canvas.data.resistorList.remove(copy.copy(r))
            flag=1
            break
    for w in canvas.data.wireList:
        (srow,scol,erow,ecol)=w
        if((srow,scol,erow,ecol)==(row0,col0,row1,col1)):
            canvas.data.wireList.remove(copy.copy(w))
            flag=1
            break
    if(flag==0):
       canvas.data.errMsg="The element you wish to delete does not exist"
       error(canvas)

def isLegalCircuit(canvas):
    #check if ground node and voltage node have been defined
    if(canvas.data.voltageSourceList==[] or canvas.data.groundList==[]):
       canvas.data.errMsg="Voltage and ground must be defined"
       error(canvas)
       return False
    #check if at least one resistor is defined.
    if(canvas.data.resistorList==[]):
        canvas.data.errMsg="No resistors defined"
        error(canvas)
        return False
    #check if ground and voltageNode are the same node.
    (vsrow,vscol)=canvas.data.voltageSourceList[0]
    (grow,gcol)=canvas.data.groundList[0]
    if(canvas.data.board[vsrow][vscol]==canvas.data.board[grow][gcol]):
        canvas.data.errMsg="Zero resistance between voltage and ground"
        error(canvas)
        return False
    #check if the start and end node of any resistor are the same
    err=""
    for  i in xrange(len(canvas.data.resistorList)):
        (srow,scol,erow,ecol,igval)=canvas.data.resistorList[i]
        if(canvas.data.board[srow][scol]==canvas.data.board[erow][ecol]):
            err+="R%d "%(i+1)
    if(err!=""):
        canvas.data.errMsg=err+"with the same start and end Node"
        error(canvas)
        return False
    #Collapses away all resistors except for the resistor being tested
    #It then checks if either the ground and voltage node of
    #the resistor become the same or the two ends of the resistor are
    #the ground and voltage node.
    if(allResistorsConnected(canvas)==False):
        return False
    return True

def allResistorsConnected(canvas):#Working explained in isLegalCircuit
    canvas.data.tempResistorList=copy.copy(canvas.data.resistorList)
    canvas.data.tempWireList=copy.copy(canvas.data.wireList)
    temp=copy.copy(canvas.data.resistorList)
    (vrow,vcol)=canvas.data.voltageSourceList[0]
    (grow,gcol)=canvas.data.groundList[0]
    for w in temp:
        (srow,scol,erow,ecol,igval)=w
        canvas.data.wireList.append((srow,scol,erow,ecol))
    errMsg=""
    for r in temp:
        canvas.data.resistorList=[]
        canvas.data.resistorList.append(r)
        (srow,scol,erow,ecol,igVal)=r
        canvas.data.wireList.remove((srow,scol,erow,ecol))
        getNodes(canvas)
        rsnode=canvas.data.board[srow][scol]
        renode=canvas.data.board[erow][ecol]
        vsnode=canvas.data.board[vrow][vcol]
        gnode=canvas.data.board[grow][gcol]
        if(not((rsnode,renode)==(vsnode,gnode) or
            (rsnode,renode)==(gnode,vsngetNodesode))):
            errMsg+="R%d "%(temp.index(r)+1)
        canvas.data.wireList.append((srow,scol,erow,ecol))
    canvas.data.resistorList=copy.copy(canvas.data.tempResistorList)
    canvas.data.wireList=copy.copy(canvas.data.tempWireList)
    getNodes(canvas)
    if(errMsg!=""):
        canvas.data.errMsg=errMsg+" not connected to ground/voltage source"
        error(canvas)
        return False
    return True
    
def collapseAndSolve(canvas):
    canvas.data.initialResistorList=copy.copy(canvas.data.resistorList)
    canvas.data.initialWireList=copy.copy(canvas.data.wireList)
    flag=0
    (igVal1,igVal2)=(-1,-1)
    #The algorithm works by comparing each resistor with the next and
    #collapsing both in series and parallel if such is possible
    while(len(canvas.data.resistorList)>1):
        for i in xrange(len(canvas.data.resistorList)):
            if(flag==1):
                flag=0
                break
            for j in xrange(len(canvas.data.resistorList)):
                r1=copy.copy(canvas.data.resistorList[i])
                r2=copy.copy(canvas.data.resistorList[j])
                if(r1!=r2 and not((i==igVal1 and j==igVal2)) and
                   not((i==igVal2 and j==igVal1))):
                    (srowR1,scolR1,erowR1,ecolR1,val1)=r1
                    (srowR2,scolR2,erowR2,ecolR2,val2)=r2
                    if(inSeries(canvas,r1,r2)):
                        canvas.data.resistorList.remove(r2)
                        val=val2+val1#rnet
                        r1=(srowR1,scolR1,erowR1,ecolR1,val)
                        canvas.data.resistorList[i]=r1
                        canvas.data.wireList.append((srowR2,scolR2,erowR2,
                                                     ecolR2))
                        getNodes(canvas)
                        flag=1
                        (igVal1,igVal2)=(-1,-1)
                        break                   
                    elif(inParallel(canvas,r1,r2)):
                        canvas.data.resistorList.remove(r2)
                        val=(val2*val1*1.0)/(val2+val1)#rnet
                        r1=(srowR1,scolR1,erowR1,ecolR1,val)
                        canvas.data.resistorList[i]=r1
                        flag=1
                        (igVal1,igVal2)=(-1,-1)
                        break
                    if(canvas.data.breakFlag==1):#The two resistors are neither
                        #in parallel or series
                        canvas.data.breakFlag=0
                        (igVal1,igVal2)=(i,j)
                        j+=1
                        #store the i and j values u just compared and ignore
                        #them, u dont need to carry out the comparison again
                        #after that, once the circuit collapses the ignore
                        #values are reset.
    finalResistor=canvas.data.resistorList[len(canvas.data.resistorList)-1]
    finalResistance=finalResistor[len(finalResistor)-1]
    canvas.data.rnet=finalResistance
    canvas.data.resistorList=canvas.data.initialResistorList
    canvas.data.wireList=canvas.data.initialWireList


def inSeries(canvas,r1,r2):
    #Two resistors are in series if they
    #1.share a single common Node,
    #2.there are no resistors connected to that common Node
    #3.are not connected in parallel via the other Node(checkWithTempNodes
    #validates this)
    (srowR1,scolR1,erowR1,ecolR1,val1)=r1
    (srowR2,scolR2,erowR2,ecolR2,val2)=r2
    board=canvas.data.board
    tempList=[]
    tempList.append(board[srowR1][scolR1])
    tempList.append(board[erowR1][ecolR1])
    tempList.append(board[srowR2][scolR2])
    tempList.append(board[erowR2][ecolR2])
    tempSet=set()
    tempSet.add(board[srowR1][scolR1])
    tempSet.add(board[erowR1][ecolR1])
    tempSet.add(board[srowR2][scolR2])
    tempSet.add(board[erowR2][ecolR2])
    if((len(tempList)-len(tempSet))==1):
        if(othersWithSameNode(canvas,tempList,r1,r2)==False):
           if(checkWithTempNodes(canvas,r1,r2)==True):              
              return True
    else:
        return False

def othersWithSameNode(canvas,tempList,r1,r2):
    node=0
    #count counts the resistors at the common Nodes from tempList
    board=canvas.data.board
    for i in tempList:
        count=0
        for j in tempList:
            if(i==j):
                count+=1
        if(count==2):
            node=i
            break           
    for r in canvas.data.resistorList:
        (srow,scol,erow,ecol,igval)=r
        if(r!=r1 and r!=r2):
            if(board[srow][scol]==node or
               board[erow][ecol]==node):
                return True
    return False               
           

def checkWithTempNodes(canvas,r1,r2):
    #temp nodes converts everything excpt the 2 resistors passed
    #into wires so as to check if the 2 resistors passed
    #are connected via the Node they do not share(through another wire etc.)
    canvas.data.tempResistorList=copy.copy(canvas.data.resistorList)
    canvas.data.tempWireList=copy.copy(canvas.data.wireList)
    temp=copy.copy(canvas.data.resistorList)
    for element in temp:
        (srow,scol,erow,ecol,igVal)=element
        if(element!=r1):
            if(element!=r2):
               canvas.data.wireList.append((srow,scol,erow,ecol))
    canvas.data.resistorList=[]
    canvas.data.resistorList.append(r1)
    canvas.data.resistorList.append(r2)
    getNodes(canvas)
    if(checkVoltageGroundSame(canvas)):
        #For a case when there are 2 resistors, if the voltage and
        #ground become the same, then r1 and r2 r in series
        canvas.data.resistorList=copy.copy(canvas.data.tempResistorList)
        canvas.data.wireList=copy.copy(canvas.data.tempWireList)
        getNodes(canvas)
        return True
    elif(inParallel(canvas,r1,r2)):#Else, if r1 connects to r2 in parallel,
                                   #they are neither in series/parallel
        canvas.data.resistorList=copy.copy(canvas.data.tempResistorList)
        canvas.data.wireList=copy.copy(canvas.data.tempWireList)
        getNodes(canvas)
        canvas.data.breakFlag=1
        return False
    else:#If the Voltage and ground do not result in the same value
         #but, r1 and r2 also do not end up in parallel, then they are in
         #series
        canvas.data.resistorList=copy.copy(canvas.data.tempResistorList)
        canvas.data.wireList=copy.copy(canvas.data.tempWireList)
        getNodes(canvas)
        return True

def checkVoltageGroundSame(canvas):
    #This tells me if after collapsing away all the
    #resistors, if the voltage and ground sources become the same
    (grow,gcol)=canvas.data.groundList[0]
    (vrow,vcol)=canvas.data.voltageSourceList[0]
    if(canvas.data.board[vrow][vcol]==canvas.data.board[grow][gcol]):
        return True #This means they are in series
    else:
        return False
    

def inParallel(canvas,r1,r2):
    #Checks if two resistors have only one Node in common
    (srowR1,scolR1,erowR1,ecolR1,val1)=r1
    (srowR2,scolR2,erowR2,ecolR2,val2)=r2
    board=canvas.data.board
    tempList=[]
    tempList.append(board[srowR1][scolR1])
    tempList.append(board[erowR1][ecolR1])
    tempList.append(board[srowR2][scolR2])
    tempList.append(board[erowR2][ecolR2])
    tempSet=set()
    tempSet.add(board[srowR1][scolR1])
    tempSet.add(board[erowR1][ecolR1])
    tempSet.add(board[srowR2][scolR2])
    tempSet.add(board[erowR2][ecolR2])
    if((len(tempList)-len(tempSet))==2):
        return True
    else:
        return False
    

def checkOnWire(canvas,row0,col0,row1,col1):
    #Checks if a particular set of data points in on a
    #wire. For example if a wire spans from col3 to col6
    #col3-col4,col3-col5,col4-col5,col4-col6 etc. are on the wire
    for w in canvas.data.wireList:
        (wireRow0,wireCol0,wireRow1,wireCol1)=w
        if(row0==row1 and row0==wireRow0 and wireRow0==wireRow1):
            if(wireCol0<=col0<=wireCol1 and wireCol0<=col1<=wireCol1):
                      (wireRow0,wireCol0,wireRow1,wireCol1)
                      (row0,col0,row1,col1)
                      return True 
        elif(col0==col1 and col0==wireCol0 and wireCol0==wireCol1):
            if(wireRow0<=row0<=wireRow1 and wireRow0<=row1<=wireRow1):
                      (wireRow0,wireCol0,wireRow1,wireCol1)
                      (row0,col0,row1,col1)
                      return True
    return False
            
    
def getNodes(canvas):#Calls a recursive flood-fill to get the Nodes
    canvas.data.board=copy.copy(make2DList(canvas.data.rows,canvas.data.cols))
    canvas.data.wirePoints=[]
    canvas.data.resistorPoints=[]
    getPointsWithWires(canvas)
    getPointsWithResistors(canvas)
    node=0
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            if(canvas.data.board[row][col]==0 and
               (((row,col) in canvas.data.wirePoints) or ((row,col) in \
                canvas.data.resistorPoints))):
                node+=1
            fillNodes(canvas,row,col,node)
                            

def fillNodes(canvas,row,col,node):
    #This recursive function sets all points on a wire to the
    #same Node. It floodfills across cells if they are connected
    #via a wire.
    if((row>=0) and (row<canvas.data.rows) and (col>=0) and
       (col<canvas.data.cols) and (canvas.data.board[row][col]==0)):
        if((row,col) in canvas.data.resistorPoints or (row,col) in
           canvas.data.wirePoints):
           canvas.data.board[row][col]=node
           if(checkOnWire(canvas,row-1,col,row,col)==True):
                 fillNodes(canvas,row-1,col,node)
           if(checkOnWire(canvas,row,col,row+1,col)==True):
                 fillNodes(canvas,row+1,col,node)
           if(checkOnWire(canvas,row,col-1,row,col)==True):
                 fillNodes(canvas,row,col-1,node)
           if(checkOnWire(canvas,row,col,row,col+1)==True):
                 fillNodes(canvas,row,col+1,node)
           
    
def getPointsWithWires(canvas):
    #This gets all the point on the grid that have a
    #wire
    for w in canvas.data.wireList:
        (row0,col0,row1,col1)=w
        tempRow0=row0
        while(tempRow0<=row1):
            if((tempRow0,col0)not in canvas.data.wirePoints):
               canvas.data.wirePoints.append((tempRow0,col0))
            tempRow0+=1
        tempCol0=col0
        while(tempCol0<=col1):
            if((row0,tempCol0) not in canvas.data.wirePoints):
              canvas.data.wirePoints.append((row0,tempCol0))
            tempCol0+=1
    
def getPointsWithResistors(canvas):
    #This gets all all the points that have a resistor
    for r in canvas.data.resistorList:
        (row0,col0,row1,col1,igVal)=r
        if((row0,col0) not in canvas.data.resistorPoints):
            canvas.data.resistorPoints.append((row0,col0))
        if((row1,col1) not in canvas.data.resistorPoints):
            canvas.data.resistorPoints.append((row1,col1))
    
def translateIntoRowCol(canvas,x0,y0):
    row=(y0-canvas.data.margin-canvas.data.cellSize/2)/(canvas.data.cellSize)
    col=(x0-canvas.data.margin-canvas.data.cellSize/2)/(canvas.data.cellSize)
    return (int(row),int(col))

def appendToResistorList(canvas,val):
    temp=0#a temp variable we will use for swapping
    (x0,y0)=canvas.data.selection
    (x1,y1)=canvas.data.nextSelection
    (startRow,startCol)=translateIntoRowCol(canvas,x0,y0)
    (endRow,endCol)=translateIntoRowCol(canvas,x1,y1)
    if(abs(endRow-startRow)>1 or abs(endCol-startCol)>1):
        resetSelectionNextSelection
        canvas.data.errMsg= "Resistors can be drawn over a single cell only"
        error(canvas)
    else:
       if(startRow>endRow):
          (startRow,endRow)=(endRow,startRow)
       if(startCol>endCol):
           (startCol,endCol)=(endCol,startCol)
       if(not(duplicatesResistor(canvas,startRow,startCol,endRow,endCol))):
          canvas.data.resistorList.append((startRow,startCol,endRow,
                                           endCol,val))
       else:
           canvas.data.errMsg="You cant draw over existing element"
           error(canvas)
    resetSelectionNextSelection(canvas)


def duplicatesResistor(canvas,startRow,startCol,endRow,endCol):
    #This checks if an element already exists in the resistor list
    for element in canvas.data.resistorList:
        (srow,scol,erow,ecol,igVal)=element
        if((srow,scol,erow,ecol)==(startRow,startCol,endRow,endCol)):
            return True
    if(checkOnWire(canvas,startRow,startCol,endRow,endCol)):
        return True
    return False

        
def appendToWireList(canvas):
    temp=0#a temp variable we will use for swapping
    (x0,y0)=canvas.data.selection
    (x1,y1)=canvas.data.nextSelection
    (startRow,startCol)=translateIntoRowCol(canvas,x0,y0)
    (endRow,endCol)=translateIntoRowCol(canvas,x1,y1)
    if(startRow>endRow):
       (startRow,endRow)=(endRow,startRow)
    if(startCol>endCol):
        (startCol,endCol)=(endCol,startCol)
    if(not(duplicatesWire(canvas,startRow,startCol,endRow,endCol))):
       canvas.data.wireList.append((startRow,startCol,endRow,endCol))
    else:
        canvas.data.errMsg="You cant draw over existing element"
        error(canvas)
    resetSelectionNextSelection(canvas)

def duplicatesWire(canvas,startRow,startCol,endRow,endCol):
    #Check for duplicates on wire
    (tempRow,tempCol)=(startRow,startCol)
    getPointsWithWires(canvas)
    if(startRow==endRow):#Checks if any point on the wire is in the
                        #list of points containing wires
        while(tempCol<=endCol-1):
            if(checkOnWire(canvas,startRow,tempCol,endRow,tempCol+1)):
               return True
            tempCol+=1           
    elif(startCol==endCol):#Checks for the same
        while(tempRow<=endRow-1):
            if(checkOnWire(canvas,tempRow,startCol,tempRow+1,endCol)):
                return True
            tempRow+=1
    #appends the new wire to the wire list and checks if any point on the
    #wire overlaps with the resistor.Later removes wire
    canvas.data.wireList.append((startRow,startCol,endRow,endCol))
    for element in canvas.data.resistorList:
        (srow,scol,erow,ecol,igVal)=element
        if(checkOnWire(canvas,srow,scol,erow,ecol)):
            canvas.data.wireList.remove((startRow,startCol,endRow,endCol))
            return True
    canvas.data.wireList.remove((startRow,startCol,endRow,endCol))
    return False

def appendToGroundList(canvas):
    (x0,y0)=canvas.data.selection
    (row,col)=translateIntoRowCol(canvas,x0,y0)
    canvas.data.groundList.append((row,col))
       
def appendToVoltageSourceList(canvas):
    if(canvas.data.voltageSourceList==[]):
       (x0,y0)=canvas.data.selection
       (row,col)=translateIntoRowCol(canvas,x0,y0)
       canvas.data.voltageSourceList.append((row,col))
       (srow,scol)=(row-1,col)
       (erow,ecol)=(row,col+1)
       if(not(duplicatesWire(canvas,srow,scol,row,col)) and
          0<=srow<canvas.data.rows):
              canvas.data.wireList.append((srow,scol,row,col))
       elif(not(duplicatesWire(canvas,row,col,erow,ecol)) and
                 0<=ecol<canvas.data.cols):
              canvas.data.wireList.append((row,col,erow,ecol))
       elif(not(duplicatesWire(canvas,row,ecol-2,erow,col))
            and 0<=ecol-2<canvas.data.cols):
            canvas.data.wireList.append((row,ecol-2,erow,col))
               

def resetSelectionNextSelection(canvas):
    canvas.data.isItemSelected=False
    canvas.data.selection=(-1,-1)
    canvas.data.nextSelection=(-1,-1)
    
def getLegalSelection(canvas,x,y):
    r=canvas.data.lineWidth
    for row in xrange(canvas.data.rows):
        for col in xrange(canvas.data.cols):
            (x0,y0,x1,y1)=getGridCellBounds(canvas,row,col)
            if((x0-r<=x<=x0+r) and (y0-r<=y<=y0+r)):
                return (x0,y0)
    return (-1,-1)
    
def getGridCellBounds(canvas,row,col):
    adjust=canvas.data.margin+canvas.data.cellSize/2
    x0=adjust+col*canvas.data.cellSize
    x1=x0+canvas.data.cellSize
    y0=adjust+row*canvas.data.cellSize
    y1=y0+canvas.data.cellSize
    return (x0,y0,x1,y1)

def getDebugCellBounds(canvas,row,col):
    x0=canvas.data.margin+col*canvas.data.cellSize
    y0=canvas.data.margin+row*canvas.data.cellSize
    x1=x0+canvas.data.cellSize
    y1=y0+canvas.data.cellSize
    return (x0,y0,x1,y1)

def make2DList(rows,cols):
    return [[0]*cols for row in xrange(rows)]
    
def init(canvas):
    canvas.data.pieceSelected="Voltage Source"
    canvas.data.inDebugMode=False
    canvas.data.lineWidth=5
    canvas.data.cellSize=(canvas.data.width-2*canvas.data.margin)\
                          /canvas.data.cols
    canvas.data.isItemSelected=False
    canvas.data.selection=(-1,-1)
    canvas.data.nextSelection=(-1,-1)
    canvas.data.lineColour="blue"
    canvas.data.selectionColour="red"
    canvas.data.pieceSelected="Voltage Source"
    canvas.data.board=copy.copy(make2DList(canvas.data.rows,canvas.data.cols))
    canvas.data.breakFlag=0
    #initialize Lists
    initLists(canvas)
    canvas.data.isItemSelected=False
    canvas.data.selection=(-1,-1)
    canvas.data.nextSelection=(-1,-1)
    canvas.data.isVoltageSource=False
    canvas.data.isGround=False
    canvas.data.errMsg=None
    canvas.data.motionRowCol=(-1,-1)
    canvas.data.inputVoltage=None
    canvas.data.rnet=None
    canvas.data.current=None
    redrawAll(canvas)

def initLists(canvas):
    canvas.data.resistorList=[]
    canvas.data.tempResistorList=[]
    canvas.data.tempWireList=[]
    canvas.data.voltageSourceList=[]
    canvas.data.currentSourceList=[]
    canvas.data.groundList=[]
    canvas.data.wireList=[]
    canvas.data.wirePoints=[]
    canvas.data.resistorPoints=[]
    canvas.data.initialResistorList=[]
    canvas.data.initialWireList=[]

def run():
    root=Tk()
    rows=10
    cols=rows
    margin=150
    width=700
    height=width
    border=5
    colour="white"
    canvas=Canvas(root,width=width,height=height)
    canvas.pack()
    class Struct:pass
    canvas.data=Struct()
    canvas.data.margin=margin
    canvas.data.width=width
    canvas.data.height=height
    canvas.data.colour=colour
    canvas.data.border=border
    canvas.data.rows=rows
    canvas.data.cols=cols
    root.bind("<Key>",
              lambda event:keyPressed(canvas,event))
    root.bind("<Button-1>", lambda event:mousePressed(canvas,event))
    #canvas.bind("<Motion>", lambda event:mouseMotion(canvas,event))
    init(canvas)
    root.mainloop()

run()

