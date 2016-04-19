from PIL import Image, ImageOps, ImageDraw

im = Image.open('temp.jpeg')
overmask_size = (im.size[0] * 3, im.size[1] * 3)
overmask = Image.new('L', overmask_size, 0)
draw = ImageDraw.Draw(overmask)
draw.ellipse((0, 0) + overmask_size, fill = 255)
overmask = overmask.resize(im.size, Image.ANTIALIAS)
im.putalpha(overmask)

im.save('output5.png')

composite_background = Image.new('RGBA', (1920, 1080), (0, 0, 0, 255))
centre = ((composite_background.size[0] / 2) - (im.size[0] / 2), (composite_background.size[1] / 2) - (im.size[1] / 2))
print centre
composite_background.paste(im, centre, im)
composite_background.save('output6.png')