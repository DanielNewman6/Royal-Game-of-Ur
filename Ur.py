from tkinter import *
from PIL import Image, ImageTk
from math import floor
import random
import winsound
from tkinter.font import Font
from datetime import datetime, time
from time import sleep
from num2word import word as n2w
from word2number import w2n

#TODO: winning logic, new game stuff

global turn
turn = 'black'

def number(word): return w2n.word_to_num(word)

def word(number):
    if number!=0: return n2w(number)
    else: return 'Zero'

def squareToPiece(x1,y1): return [x1-(pieceSide/2),y1-(pieceSide/2),x1+(pieceSide/2),y1+(pieceSide/2)]

def other(turn):
    if turn == 'white': return 'black'
    elif turn == 'black': return 'white'

def originalCoords(widget, thing):
    for tag in widget.gettags(thing):
        try:
            if type(eval(tag)) == list:
                return eval(tag)
        except:
            pass

def removeTag(widget, thing, tag):
    newtags = widget.gettags(thing)
    newtags = list(newtags)
    newtags.remove(tag)
    newtags = tuple(newtags)
    widget.itemconfig(thing, tags=newtags)

def addTag(widget, thing, tag):
    newtags = widget.gettags(thing) + (tag,)
    widget.itemconfig(thing, tags=newtags)

def numberOf(widget, thing):
    for tag in widget.gettags(thing):
        try:
            if number(tag)!=None:
                return number(tag)
            elif number(tag)=='':
                return 0
        except:
            pass

def accessTo(widget, space):
    for tag in widget.gettags(space):
        try:
            if type(eval(tag)) == tuple:
                return eval(tag)[0] == turn
        except:
            pass
    return True

def valid(widget, space):
    return (numberOf(widget, space) - numberOf(widget, widget.find_withtag('dragged')[0]) == outcome) and accessTo(widget, space)

def checkForWinner(widget):
    if len(set(widget.find_withtag('Fifteen')) & set(widget.find_withtag('white')))==8:
        rollButton.config(state=DISABLED)
        board.create_text(windowWidth*0.4, windowHeight/2, text='White wins', fill='red', font=Font(family='Times New Roman', size=50), tags=('temp'))
        board.update_idletasks()
    if len(set(widget.find_withtag('Fifteen')) & set(widget.find_withtag('black')))==8:
        rollButton.config(state=DISABLED)
        board.create_text(windowWidth*0.4, windowHeight/2, text='Black wins', fill='red', font=Font(family='Times New Roman', size=50), tags=('temp'))
        board.update_idletasks()
        
        
def onDragStart(event):
    global turn
    if rollButton['state']=='disabled':
        widget = event.widget
        for thing in widget.find_overlapping((event.x)-2,(event.y)-2,(event.x)+2,(event.y)+2):
            tags = widget.gettags(thing)
            if 'space' in tags and turn in tags:
                space = thing
        for thing in widget.find_overlapping((event.x)-2,(event.y)-2,(event.x)+2,(event.y)+2):
            tags = widget.gettags(thing)
            if 'piece' in tags and turn in tags:
                addTag(widget, thing, str(widget.coords(thing)))
                addTag(widget, thing, 'dragged')
                try:
                    r=numberOf(widget,thing)
                except:
                    try:
                        addTag(widget, thing, word(numberOf(widget, space)))
                    except:
                        pass
                try:
                    removeTag(widget, space, turn)
                except:
                    pass
                break
    else:
        rollButton.flash()
        
def onDragMotion(event):
    widget = event.widget
    for thing in widget.find_withtag('dragged'):
        widget.coords(thing, event.x-(pieceSide/2), event.y-(pieceSide/2), event.x+(pieceSide/2), event.y+(pieceSide/2))

def onDragEnd(event):
    global turn
    global winner
    widget = event.widget
    try:
        draggedThing = widget.find_withtag('dragged')[0]
    except:
        return
    relevantThings = widget.find_overlapping(event.x-(pieceSide/8), event.y-(pieceSide/8), event.x+(pieceSide/8), event.y+(pieceSide/8))
    for thing in relevantThings:
        tags = widget.gettags(thing)
        if 'space' in tags and turn not in tags and ('rosette' not in tags or 'black' not in tags) and ('rosette' not in tags or 'white' not in tags) and valid(widget, thing) and 'Fifteen' not in tags:
            spaceCoords = widget.coords(thing)
            widget.coords(draggedThing, *squareToPiece(*spaceCoords))
            addTag(widget, thing, turn)
            for thing2 in [i for i in relevantThings if i!=thing]:
                tags2=widget.gettags(thing2)
                if 'dragged' not in tags2 and 'piece' in tags2:
                    if turn=='black':
                        widget.coords(thing2, *whiteStart)
                        removeTag(widget, thing, 'white')
                    else:
                        widget.coords(thing2, *blackStart)
                        removeTag(widget, thing, 'black')
                    removeTag(widget, thing2, word(numberOf(widget, thing2)))
                    addTag(widget, thing2, 'Zero')
            if widget.coords(draggedThing)!=originalCoords(widget, draggedThing):
                turn=other(turn)
            removeTag(widget, draggedThing, 'dragged')
            removeTag(widget, draggedThing, str(originalCoords(widget, draggedThing)))
            try:
                removeTag(widget, draggedThing, word(numberOf(widget, draggedThing)))
            except:
                removeTag(widget, draggedThing, 'Zero')
            addTag(widget, draggedThing, word(numberOf(widget, thing)))
            rollButton.config(state='normal')
            return
        elif 'space' in tags and 'Fifteen' in tags and valid(widget, thing):
            addTag(widget, thing, turn)
            spaceCoords = widget.coords(thing)
            if widget.coords(draggedThing)!=originalCoords(widget, draggedThing):
                turn=other(turn)
            widget.coords(draggedThing, *squareToPiece((spaceCoords[0]+spaceCoords[2])/2, (spaceCoords[1]+spaceCoords[3])/2))
            removeTag(widget, draggedThing, 'dragged')
            removeTag(widget, draggedThing, str(originalCoords(widget, draggedThing)))
            removeTag(widget, draggedThing, word(numberOf(widget, draggedThing)))
            removeTag(widget, draggedThing, 'piece')
            addTag(widget, draggedThing, 'Fifteen')
            rollButton.config(state='normal')
            checkForWinner(widget)
            return
    widget.coords(draggedThing, *originalCoords(widget, draggedThing))
    onSpace = widget.find_overlapping(*originalCoords(widget, draggedThing))
    onSpace = [i for i in onSpace if 'space' in widget.gettags(i)]
    removeTag(widget, draggedThing, 'dragged')
    removeTag(widget, draggedThing, str(originalCoords(widget, draggedThing)))
    for space in onSpace:
        addTag(widget, space, turn)
        

def makeDraggable(widget):
    widget.bind("<Button-1>", onDragStart)
    widget.bind("<B1-Motion>", onDragMotion)
    widget.bind("<ButtonRelease-1>", onDragEnd)

def diceRoll(label):
    global outcome
    global turn
    outcome = 0
    for i in range(0,4):
        outcome += floor(2*random.random())
    winsound.PlaySound('Dice Sound.wav', winsound.SND_FILENAME)
    label.config(text=str(outcome))
    if outcome == 0:
        turn = other(turn)
        return False
    for i in board.find_withtag('piece'):
        tags=board.gettags(i)
        if turn in tags:
            prospects = numberOf(board, i)+outcome
            if prospects<16 and len(((set(board.find_withtag(word(prospects))) & set(board.find_withtag('space'))) - ((set(board.find_withtag(turn)) - set(board.find_withtag('Fifteen'))) | set(board.find_withtag('("'+other(turn)+'",)')) | (set(board.find_withtag('rosette')) & set(board.find_withtag(other(turn)))))))>0:
                return None
    board.create_text(windowWidth*0.4, windowHeight/2, text='No legal move', fill='red', font=Font(family='Times New Roman', size=50), tags=('temp'))
    board.update_idletasks()
    sleep(1.5)
    board.delete('temp')
    turn = other(turn)
    return False

#sets up window
root = Tk()

myFont = Font(family="Times New Roman", size=20)

root.title('Royal Game of Ur')
root.state('zoomed')
root.configure(background = 'MediumOrchid4')
root.update()

windowHeight = root.winfo_height()
windowWidth = root.winfo_width()
pieceSide = floor(windowHeight/10)
squareSide = floor(pieceSide*1.5)

#loads images
brownSpace1 = Image.open('brown tile 1.jpg')
brownSpace1 = brownSpace1.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace1 = ImageTk.PhotoImage(brownSpace1)
brownSpace2 = Image.open('brown tile 2.jpg')
brownSpace2 = brownSpace2.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace2 = ImageTk.PhotoImage(brownSpace2)
brownSpace3 = Image.open('brown tile 3.jpg')
brownSpace3 = brownSpace3.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace3 = ImageTk.PhotoImage(brownSpace3)
brownSpace4 = Image.open('brown tile 4.jpg')
brownSpace4 = brownSpace4.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace4 = ImageTk.PhotoImage(brownSpace4)
brownSpace5 = Image.open('brown tile 5.jpg')
brownSpace5 = brownSpace5.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace5 = ImageTk.PhotoImage(brownSpace5)
brownSpace6 = Image.open('brown tile 6.jpg')
brownSpace6 = brownSpace6.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace6 = ImageTk.PhotoImage(brownSpace6)
brownSpace7 = Image.open('brown tile 7.jpg')
brownSpace7 = brownSpace7.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace7 = ImageTk.PhotoImage(brownSpace7)
brownSpace8 = Image.open('brown tile 8.jpg')
brownSpace8 = brownSpace8.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace8 = ImageTk.PhotoImage(brownSpace8)
brownSpace9 = Image.open('brown tile 9.jpg')
brownSpace9 = brownSpace9.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace9 = ImageTk.PhotoImage(brownSpace9)
brownSpace10 = Image.open('brown tile 10.jpg')
brownSpace10 = brownSpace10.resize((squareSide, squareSide), Image.ANTIALIAS)
brownSpace10 = ImageTk.PhotoImage(brownSpace10)
orangeSpace1 = Image.open('orange tile 1.jpg')
orangeSpace1 = orangeSpace1.resize((squareSide, squareSide), Image.ANTIALIAS)
orangeSpace1 = ImageTk.PhotoImage(orangeSpace1)
orangeSpace2 = Image.open('orange tile 2.jpg')
orangeSpace2 = orangeSpace2.resize((squareSide, squareSide), Image.ANTIALIAS)
orangeSpace2 = ImageTk.PhotoImage(orangeSpace2)
orangeSpace3 = Image.open('orange tile 3.jpg')
orangeSpace3 = orangeSpace3.resize((squareSide, squareSide), Image.ANTIALIAS)
orangeSpace3 = ImageTk.PhotoImage(orangeSpace3)
orangeSpace4 = Image.open('orange tile 4.jpg')
orangeSpace4 = orangeSpace4.resize((squareSide, squareSide), Image.ANTIALIAS)
orangeSpace4 = ImageTk.PhotoImage(orangeSpace4)
orangeSpace5 = Image.open('orange tile 5.jpg')
orangeSpace5 = orangeSpace5.resize((squareSide, squareSide), Image.ANTIALIAS)
orangeSpace5 = ImageTk.PhotoImage(orangeSpace5)
orangeRosette = Image.open('rosette 1.jpg')
orangeRosette = orangeRosette.resize((squareSide, squareSide), Image.ANTIALIAS)
orangeRosette = ImageTk.PhotoImage(orangeRosette)
blueRosette1 = Image.open('rosette 2.jpg')
blueRosette1 = blueRosette1.resize((squareSide, squareSide), Image.ANTIALIAS)
blueRosette1 = ImageTk.PhotoImage(blueRosette1)
blueRosette2 = Image.open('rosette 3.jpg')
blueRosette2 = blueRosette2.resize((squareSide, squareSide), Image.ANTIALIAS)
blueRosette2 = ImageTk.PhotoImage(blueRosette2)
blueRosette3 = Image.open('rosette 4.jpg')
blueRosette3 = blueRosette3.resize((squareSide, squareSide), Image.ANTIALIAS)
blueRosette3 = ImageTk.PhotoImage(blueRosette3)
blueRosette4 = Image.open('rosette 5.jpg')
blueRosette4 = blueRosette4.resize((squareSide, squareSide), Image.ANTIALIAS)
blueRosette4 = ImageTk.PhotoImage(blueRosette4)


#sets up board space
board= Canvas(root, bg='chartreuse3', relief=SUNKEN, height=windowHeight, width=floor(0.8*windowWidth))
sideGap=(0.8*windowWidth-(16/15)*windowHeight)/2
topGap=0.35*windowHeight
board.pack(side=LEFT)

#create spaces
board.create_image(sideGap, topGap, image=blueRosette1, tags=('space', 'rosette', 'Four', '("black",)'))
board.create_image(sideGap+squareSide, topGap, image=brownSpace1, tags=('space', 'Three','("black",)' ))
board.create_image(sideGap+2*squareSide, topGap, image=orangeSpace1, tags=('space', 'Two', '("black",)'))
board.create_image(sideGap+3*squareSide, topGap, image=brownSpace2, tags=('space', 'One', '("black",)'))
board.create_image(sideGap+6*squareSide, topGap, image=blueRosette2, tags=('space', 'rosette', 'Fourteen','("black",)' ))
board.create_image(sideGap+7*squareSide, topGap, image=brownSpace3, tags=('space', 'Thirteen','("black",)' ))
board.create_image(sideGap, topGap+squareSide, image=brownSpace4, tags=('space', 'Five'))
board.create_image(sideGap+squareSide, topGap+squareSide, image=orangeSpace2, tags=('space', 'Six'))
board.create_image(sideGap+2*squareSide, topGap+squareSide, image=brownSpace5, tags=('space', 'Seven'))
board.create_image(sideGap+3*squareSide, topGap+squareSide, image=orangeRosette, tags=('space', 'rosette', 'Eight'))
board.create_image(sideGap+4*squareSide, topGap+squareSide, image=brownSpace6, tags=('space', 'Nine'))
board.create_image(sideGap+5*squareSide, topGap+squareSide, image=orangeSpace3, tags=('space', 'Ten'))
board.create_image(sideGap+6*squareSide, topGap+squareSide, image=brownSpace7, tags=('space', 'Eleven'))
board.create_image(sideGap+7*squareSide, topGap+squareSide, image=orangeSpace4, tags=('space', 'Twelve'))
board.create_image(sideGap, topGap+2*squareSide, image=blueRosette3, tags=('space', 'rosette', 'Four', '("white",)'))
board.create_image(sideGap+squareSide, topGap+2*squareSide, image=brownSpace8, tags=('space', 'Three', '("white",)'))
board.create_image(sideGap+2*squareSide, topGap+2*squareSide, image=orangeSpace5, tags=('space', 'Two', '("white",)'))
board.create_image(sideGap+3*squareSide, topGap+2*squareSide, image=brownSpace9, tags=('space', 'One', '("white",)'))
board.create_image(sideGap+6*squareSide, topGap+2*squareSide, image=blueRosette4, tags=('space', 'rosette', 'Fourteen', '("white",)'))
board.create_image(sideGap+7*squareSide, topGap+2*squareSide, image=brownSpace10, tags=('space', 'Thirteen', '("white",)'))

board.create_rectangle(sideGap+4.5*squareSide, topGap-0.5*squareSide, sideGap+5.5*squareSide, topGap+0.5*squareSide, fill='chartreuse3', tags=('space', 'Fifteen', '("black",)'))
board.create_rectangle(sideGap+4.5*squareSide, topGap+1.5*squareSide, sideGap+5.5*squareSide, topGap+2.5*squareSide, fill='chartreuse3', tags=('space', 'Fifteen', '("white",)'))

blackStart=[sideGap+3.5*squareSide+(squareSide-pieceSide)/2,topGap-0.35*squareSide,sideGap+4.5*squareSide-(squareSide-pieceSide)/2, topGap+pieceSide-0.35*squareSide]
whiteStart=[sideGap+3.5*squareSide+(squareSide-pieceSide)/2, windowHeight-topGap-0.35*squareSide, sideGap+4.5*squareSide-(squareSide-pieceSide)/2, windowHeight-topGap-0.35*squareSide+pieceSide]

for i in range(0, 7):
    board.create_oval(*blackStart, fill = 'black', tags = ('piece', 'black', 'Zero'))
for i in range(0, 7):
    board.create_oval(*whiteStart, fill = 'white', tags = ('piece', 'white', 'Zero'))
board.tag_raise('piece')

makeDraggable(board)

#adds dice roll stuff
roll = Label(root, bg='white', relief=SUNKEN, font=myFont, height=floor(windowHeight/200), width=floor(0.15*0.05*windowWidth))
roll.pack()

def rollDice():
    if diceRoll(roll)==None: rollButton.config(state=DISABLED)

rollButton = Button(root, bg='white', relief=SUNKEN, font=myFont, height=floor(windowHeight/400), width=floor(0.15*0.05*windowWidth), command=rollDice, text='Roll the Dice')
rollButton.pack()

def setupNewGame():
    global turn
    board.delete('piece')
    board.delete('temp')
    board.delete('Fifteen')
    board.create_rectangle(sideGap+4.5*squareSide, topGap-0.5*squareSide, sideGap+5.5*squareSide, topGap+0.5*squareSide, fill='chartreuse3', tags=('space', 'Fifteen', '("black",)'))
    board.create_rectangle(sideGap+4.5*squareSide, topGap+1.5*squareSide, sideGap+5.5*squareSide, topGap+2.5*squareSide, fill='chartreuse3', tags=('space', 'Fifteen', '("white",)'))
    for i in range(0, 7):
        board.create_oval(*blackStart, fill = 'black', tags = ('piece', 'black', 'Zero'))
    for i in range(0, 7):
        board.create_oval(*whiteStart, fill = 'white', tags = ('piece', 'white', 'Zero'))
    board.tag_raise('piece')
    rollButton.config(state=NORMAL)
    roll.config(text='')
    turn='black'
    for i in set(board.find_withtag('space')) & set(board.find_withtag('white')):
        removeTag(board, i, 'white')
    for i in set(board.find_withtag('space')) & set(board.find_withtag('black')):
        removeTag(board, i, 'black')

#adds new game button
newGameButton = Button(root, bg='white', relief=SUNKEN, font=myFont, height=floor(windowHeight/400), width=floor(0.15*0.05*windowWidth), command=setupNewGame, text='New Game')
newGameButton.pack()

root.mainloop()
