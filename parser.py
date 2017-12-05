import struct
import codecs
import json

with open('iden.json', 'r') as file:
    TAG_FRAME_IDENTIFIERS = json.load(file)

class MP3Format:
    def parse(self, filename):
        with open(filename, 'rb') as file:
            if file.read(3).decode() == 'ID3':
                self.tag_header = TagHeader(file.read(7))
                size = self.tag_header.size_of_tag
                while size != 0:
                    self.tag_frame_header = TagFrameHeader(file.read(10))
                    size -= 10+self.tag_frame_header.size
                    self.tag_frames = {}
                    self.tag_frames[TAG_FRAME_IDENTIFIERS[self.tag_frame_header.identifier]]=(TagFrame(file.read(self.tag_frame_header.size)))


class TagHeader():
    def __init__(self, meta):
        self.version = struct.unpack('!BB',meta[0:2])[0]
        self.flags = meta[2]
        self.size_of_tag = struct.unpack("!I", meta[3:7])[0]


class TagFrame():
    def __init__(self, meta):
        print(meta)
        meta = meta[1:]
        bom = codecs.BOM_UTF16_LE
        if meta.startswith(bom):
            self.info = meta.decode('utf-16le')
        else:
            self.info = meta.decode()

    def decode_text_info(self):
        pass
    def __str__(self):
        return self.info


class TagFrameHeader():
    def __init__(self, meta):
        print(meta)
        self.identifier = meta[0:4].decode()
        self.size = struct.unpack('!I', meta[4:8])[0]
        self.flags = meta[8:10]



if __name__ == "__main__":
    mp3 = MP3Format()
    mp3.parse("C:\\Users\\1\Downloads\Дайте танк (!)\\2016 - Глаза боятся\\04 Эхо.mp3")
    print(i for i in mp3.tag_frames.values())