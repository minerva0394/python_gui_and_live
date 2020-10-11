from tkinter import *


def circle(canvas, x, y, r):
    id = canvas.create_oval(x - r, y - r, x + r, y + r,fill='red')
    return id


canvas_width = 190
canvas_height = 150

master = Tk()

w = Canvas(master)
w.pack()


circle(w,120,20,20)

mainloop()
