# -*- coding:utf-8 -*-  

import xml.etree.ElementTree as etree
import argparse
import glob

VERSION = "0.0.1"

#   数据格式定义
#   场风*1 本场*1 立直棒*1 宝牌指示1*4 各家点数1*4 是否立直1*4
#   13+16的自家牌况(未知则用-1表示)
#   变化的牌(可以是别人打出的牌，也可以是自己摸的牌)
#   可以做的决策：吃、碰、杠、和、打

class GameInfo(object):
    def __init__(self, _events):
        self.events = _events
        self.name = 0
        self.combo = 0
        self.riichi = 0
        self.dora = [0]
        self.ten = [0,0,0,0]
        self.whoRiichi = [0,0,0,0]
        self.hai = [[-1 for i in range(13)], [-1 for i in range(13)], [-1 for i in range(13)], [-1 for i in range(13)]]
        self.ignoreTag = ["GO", "UN", "TAIKYOKU", "BYE", "RYUUKYOKU", "AGARI", "N"]

    def decode(self):
        features = []
        drawTile = -1
        for child in self.events:

            if child.tag in self.ignoreTag:
                continue

            if child.tag == "INIT":
                seed = child.attrib["seed"].split(",")
                self.name = seed[0]
                self.combo = seed[1]
                self.riichi = seed[2]
                self.dora[0] = [seed[5],0,0,0]
                self.ten = [int(i) for i in child.attrib["ten"].split(",") ]
                self.hai = [[int(i) for i in child.attrib["hai0"].split(",")], [-1 for i in range(13)], [-1 for i in range(13)], [-1 for i in range(13)]]
                self.hai[0].sort()
                continue

            if child.tag.startswith("T"):
                drawTile = int(child.tag[1:])
                continue
            if child.tag.startswith("D"):
                dropTile = int(child.tag[1:])
                self.hai[0][self.hai[0].index(dropTile)] = drawTile
                self.hai[0].append(dropTile)
                t = self.hai[0][:13]
                t.sort()
                self.hai[0][:13] = t
                continue
            if child.tag.startswith("E"):
                self.hai[1].append(int(child.tag[1:]))
                continue
            if child.tag.startswith("F"):
                self.hai[2].append(int(child.tag[1:]))
                continue
            if child.tag.startswith("G"):
                self.hai[3].append(int(child.tag[1:]))
                continue

            # if child.tag.startswith("N"):
            #     who = int(child.attrib["who"])
            #     self.decodeMeld(int(child.attrib["m"]))
            #     continue

            if child.tag == "DORA":
                self.dora.append(int(child.attrib["hai"]))
                continue

            if child.tag == "REACH":
                if self.whoRiichi[int(child.attrib["who"])] != 1:
                    self.whoRiichi[int(child.attrib["who"])] = 1
                continue

        return features

    def generateFeature(self, waitTile):
        if(len(self.dora) < 4):
            dora = self.dora + [-1 for i in range(4-len(self.dora))]
            hai = self.hai
            for i in range(len(hai)):
                if(len(hai[i]) < 34):
                    hai[i] += [-1 for i in range(4-len(hai[i]))]
            feature = [self.name, self.combo, self.riichi] + dora + self.ten + self.whoRiichi
            feature += [i for i in hai] + waitTile
            return feature

    # def decodeMeld(self, meld):
    #     if meld & 0x4:
    #         t0, t1, t2 = (meld >> 3) & 0x3, (meld >> 5) & 0x3, (meld >> 7) & 0x3

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tenhou MJLog decoder. Ver %s. By Xdestiny."%(VERSION))
    parser.add_argument("-f", "--folder", help="Log folder")
    parser.add_argument("-r", "--regex", default = "*.mjlog", help="Regex")
    args = parser.parse_args()

    print("Log folder = %s"%(args.folder))
    print("regex = %s"%(args.regex))

    files = glob.glob(args.folder + "/" + args.regex)
    for f in files:
        events = etree.parse(open(f)).getroot()
        gameInfo = GameInfo(events)
        gameInfo.decode()