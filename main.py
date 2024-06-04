from renderer import Renderer
from font import Font

font = Font("assets/Montserrat-Regular.ttf")

# # print([x.components[1].glyphIndex for x in font.glyphs if x.isCompound])
# compGlyph = None
# for g in font.glyphs:
#     if g.isCompound:
#         compGlyph = g
#         break

# print([x.glyphIndex for x in compGlyph.components])
print(len(font.glyphs[2].components))

rend = Renderer(font)
rend.mainloop()
