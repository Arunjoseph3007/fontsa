from renderer import Renderer
from fparser import FontParser

fp = FontParser("assets/Roboto-Regular.ttf")
fp.parseFontDirectory()

rend = Renderer(fp)
rend.mainloop()
