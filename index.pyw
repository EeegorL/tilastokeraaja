from tkinter import Tk;
from ui.GUI import UI;

window = Tk();
window.iconbitmap("rsrc/ico.ico");
window.resizable(False, False);

window.minsize(550, 300);
window.title("Tilastokerääjä");

ui = UI(window);
ui.start(window);

window.mainloop();
