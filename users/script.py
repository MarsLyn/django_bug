from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os


class ImageCode():

    def __init__(self) -> None:
        self.width = 120
        self.height = 30
        self.char_length = 5
        self.font_file = 'msyh.ttc'
        self.font_size = 28
        self.code = []
        self.image = None
        self.draw = None
        self.font = None

    def new_image(self):
        self.image = Image.new(mode='RGB', size=(self.width, self.height), color=(255, 255, 255))

    def new_draw(self):
        self.draw = ImageDraw.Draw(self.image, mode='RGB')

    def new_font(self):
        try:
            self.font = ImageFont.truetype(self.font_file, self.font_size)
        except Exception as e:
            return

    def rndChar(self):
        return chr(random.randint(65, 90))

    def rndColor(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def write_font(self):

        x = self.image.width // self.char_length
        box = self.draw.textbbox([0,0], self.rndChar(), font=self.font)
        y = (self.image.height - (box[3] - box[1])) // 2

        for i in range(self.char_length):
            char = self.rndChar()
            self.code.append(char)
            
            
            # print(box)
            # print(y)
            
            self.draw.text((i*x, -y), char, font=self.font, fill=self.rndColor())

    def write_point(self):
        for i in range(40):
            self.draw.point([random.randint(0, self.width), random.randint(0, self.height)], fill=self.rndColor())

    def write_round(self):
        for i in range(40):
            self.draw.point([random.randint(0, self.width), random.randint(0, self.height)], fill=self.rndColor())
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.draw.arc((x, y, x + 4, y + 4), 0, 90, fill=self.rndColor())

    def write_line(self):
        for i in range(5):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)

            self.draw.line((x1, y1, x2, y2), fill=self.rndColor())

    def get_image(self):
        self.new_image()
        self.new_draw()
        self.new_font()
        if self.font:
            self.write_font()
            self.write_point()
            self.write_round()
            self.write_line()
            self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            return self.image
        else:
            self.close()
            raise AttributeError('没有找到当前的字体')
    
    def get_code(self):
        return ''.join(self.code)
    
    def close(self):
        self.image.close()
        return
    
if __name__ == '__main__':
    
    i1 = ImageCode()
    i1.get_image()
    code = i1.get_code()
    print(code)
    i1.image.show()