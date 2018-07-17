# -*- coding: UTF-8 -*-
import csv
import os
import shutil
import pytesseract
from PIL import Image
from docx import Document


class MyFolder:
    def __init__(self, folder_name):
        self.name = folder_name

    def __str__(self):
        return self.__name__

    def create(self):
        if not os.path.exists(self.name):
            os.makedirs(self.name)

    def move(self):
        pass

    def copy(self):
        pass

    def get_file_list(self):
        return os.listdir(self.name)

    def get_basename(self):
        return os.path.basename(self.name)

    def delete(self):
        pass

class MyFile:
    def __init__(self, file_name):
        self.name = file_name

    def __str__(self):
        return '{self.__class__.__name__} {self.name}'.format(self=self)


    def create(self):
        with open(self.name, 'w') as f:
            f.close()
    
    def delete(self):
        os.remove(self.name)
        
    def move(self, dst):
        shutil.move(self.name, dst)
        
    def copy(self, dst):
        shutil.copy(self.name, dst)
        
    def read(self):
        pass
        
    def write(self, content):
        pass

    def append(self):
        pass

    def get_size(self):
        return os.path.getsize(self.name)

    def get_filename(self):
        return os.path.basename(self.name)

    def get_dirname(self):
        return os.path.dirname(self.name)

    def exists(self):
        return os.path.exists(self.name)

class MyTextFile(MyFile):
    def __init__(self, file_name):
        super().__init__(file_name)

    def read(self):
        try:
            with open(self.name, 'r') as f:
                self.content = f.read()
                return self.content
        except Exception as e:
            print(e)

    def write(self, content):
        try:
            with open(self.name, "w") as f:
                f.write(content)
        except Exception as e:
            print(e)

class MyCsvFile(MyFile):
    def __init__(self, file_name):
        super().__init__(file_name)

    def read_dict(self):
        with open(self.name, encoding='utf-8_sig') as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                data_dict = dict.fromkeys(reader.fieldnames)
            except:
                return None
            for key in data_dict:
                data_dict[key] = []
            for row in reader:
                for key in data_dict:
                    data_dict[key].append(row[key])
        self.content = data_dict
        return self.content

    def write(self, content):
        with open(self.name, 'w', newline='', encoding='utf-8_sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(content.keys())
            writer.writerows(zip(*content.values()))

    def write_dict(self, fields, content):
        with open(self.name, 'w', newline='', encoding='utf-8_sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for row in content:
                writer.writerow(row)

class MyDocFile(MyFile):
    def __init__(self, file_name):
        super().__init__(file_name)

    def read(self):
        try:
            document = Document(self.name)
            l = [paragraph.text for paragraph in document.paragraphs]
            self.content = ''.join(str(e) for e in l)
            #print(self.content)
            return self.content
        except Exception as e:
            print(e)
            print("Document %s is invalid" % self.name)


class MyImageFile(MyFile):
    def __init__(self, file_name):
        super().__init__(file_name)


    def write(self, content):
        with open(self.name, 'wb') as f:
            f.write(content)

    def _process_img(self, img, threshold=180):
        '''对图片进行二值化 255 是白色 0是黑色'''
        # 灰度转换
        img = img.convert('L')
        # 二值化
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                pixels[x, y] = 255 if pixels[x, y] > threshold else 0
        return img

    def _smooth(self, picture):
        '''平滑降噪
            二值化的图片传入 去除像噪小点
        '''
        pixels = picture.load()
        (width, height) = picture.size

        xx = [1, 0, -1, 0]
        yy = [0, 1, 0, -1]

        for i in range(width):
            for j in range(height):
                if pixels[i, j] != 255:
                    count = 0
                    for k in range(4):
                        try:
                            if pixels[i + xx[k], j + yy[k]] == 255:
                                count += 1
                        except IndexError:  # 忽略访问越界的情况
                            pass
                    if count > 3:
                        pixels[i, j] = 255
        return picture

    def read(self, lang='eng'):
        with open(self.name, 'rb') as f:
            img = self._smooth(self._process_img(Image.open(f)))
        print(pytesseract.image_to_string(img, lang))
        return pytesseract.image_to_string(img, lang)