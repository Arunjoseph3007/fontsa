from renderer import Renderer
from fparser import FontParser

fp = FontParser("assets/Roboto-Regular.ttf")

rend = Renderer(fp)
rend.mainloop()
