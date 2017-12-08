import struct
import codecs
import json
import argparse
from functools import reduce

HEADER_SIZE = 10
FRAME_SIZE = 4
with open('iden.json', 'r') as file:
    IDs = json.load(file)

PICTURE_TYPES = {
    0x00: "Other",
    0x01: "32x32 pixels 'file icon' (PNG only)",
    0x02: "Other file icon",
    0x03: "Cover (front)",
    0x04: "Cover (back)",
    0x05: "Leaflet page",
    0x06: "Media (e.g. lable side of CD)",
    0x07: "Lead artist/lead performer/soloist",
    0x08: "Artist/performer",
    0x09: "Conductor",
    0x0a: "Band/Orchestra",
    0x0b: "Composer",
    0x0C: "Lyricist/text writer",
    0x0D: "Recording Location",
    0x0E: "During recording",
    0x0F: "During performance",
    0x10: "Movie/video screen capture",
    0x11: "A bright coloured fish",
    0x12: "Illustration",
    0x13: "Band/artist logotype",
    0x14: "Publisher/Studio logotype",
}

def decode_text_info(meta):
    bom = codecs.BOM_UTF16_LE
    if meta.startswith(bom):
        return meta.decode('utf-16le')
    else:
        return meta.decode()

class MP3Format:
    def parse(self, filename):
        with open(filename, 'rb') as file:
            if file.read(3).decode() == 'ID3':
                self.tag_header = TagHeader(file.read(7))
                self.tag_frames = []
                size = self.tag_header.size
                while size > 0:
                    raw_frame_header = file.read(HEADER_SIZE)
                    size -= len(raw_frame_header)
                    if len(raw_frame_header) != HEADER_SIZE:
                        break
                    tag_frame = TagFrame()
                    tag_frame.frame_header.decode(raw_frame_header)
                    if tag_frame.frame_header.compression:
                        decompressedSize = struct.unpack("!L", file.read(4))[0]
                        size -= 4
                    if len(tag_frame.frame_header.identifier) != 4:
                        break
                    tag_frame.decode(file.read(tag_frame.frame_header.size))
                    self.tag_frames.append(tag_frame)
                    size -= tag_frame.frame_header.size

class TagHeader():
    def __init__(self, meta):
        self.version = struct.unpack('!BB',meta[0:2])[0]
        flags = meta[2]
        self.unsynchronisation = (flags & 128)
        self.extendedHeader = (flags & 64)
        self.experimentalIndicator = (flags & 32)
        self.size = self._calc_size(meta[3:7])
        print(self.size)

    def _calc_size(self, bytearr):
        print(bytearr)
        return ((bytearr[0] & 0xFF) << 21) | ((bytearr[1] & 0xFF) << 14 ) | ((bytearr[2] & 0xFF) << 7 ) | (bytearr[3] & 0xFF)


class TagFrame():
    def __init__(self):
        self.frame_header = TagFrameHeader()

    def decode(self, meta):
        meta=meta[:1]
        if self.frame_header.identifier[0]=='T':
            self.info = TextFrame(meta)
        elif self.frame_header.identifier == 'APIC':
            self.info = AttachedPicture(meta)
        else:
            self.info = 'not yet'

    def __str__(self):
        return self.info if self.info is str else self.info.__str__()


class TagFrameHeader():
    def decode(self, meta):
        print(meta)
        self.identifier = meta[0:4].decode()
        self.size = struct.unpack('!I', meta[4:8])[0]
        self.tag_alter_preservation = (meta[8] & 128)
        self.file_alter_preservation = (meta[8] & 64)
        self.readonly = (meta[8] & 32)
        self.compression = (meta[9] & 128)
        self.encryption = (meta[9] & 64)
        self.grouping_identity = (meta[9] & 32)

class AttachedPicture():
    def __init__(self, meta):
        index = 0
        result = b''
        while meta[index] != 0:
            result += b'meta[index]'
            index+=1
        self.mime_type = decode_text_info(result)
        self.picture_type = PICTURE_TYPES[meta[index]]
        result = b''
        while meta[index] != 0:
            result += b'meta[index]'
            index += 1
        self.description = decode_text_info(result)
        self.picture_data = meta[index]

    def __str__(self):
        return "mimeType : {}" \
               "pictureType : {} " \
               "description : {}" \
               "pictureData : <... {} bytes ...>".format(self.mime_type, self.picture_type, self.description, self.picture_data)

class TextFrame():
    def __init__(self, meta):
        self.string = decode_text_info(meta)

    def __str__(self):
        return self.string

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Parses mp3 tags data'''
    )
    parser.add_argument('file', help='full path to audio')
    args = parser.parse_args()

    if args.file is None:
        print("You forgot to enter params, for more info ask for help [-h]")
    else:
        mp3 = MP3Format()
        mp3.parse(args.file)
        [print(i) for i in mp3.tag_frames]

if __name__ == "__main__":
    mp3 = MP3Format()
    mp3.parse("C:\\Users\\1\Downloads\Tigers Jaw\June.mp3")
    [print(i) for i in mp3.tag_frames]