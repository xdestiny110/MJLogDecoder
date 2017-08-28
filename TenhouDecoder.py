# -*- coding:utf-8 -*-  

import xml.etree.ElementTree as etree
import argparse
import glob

VERSION = "0.0.1"

#   数据格式定义
#   场风*1 本场*1 立直棒*1 宝牌指示1*4 各家点数1*4 是否立直1*4
#   (13+21)*4的各家牌况(未知则用-1表示)
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

    def decode(self):
        features = []
        for child in self.events:
            if child.tag == "INIT":
                data = child.attrib["data"].split(",")
                self.name = data[0]
                self.combo = data[1]
                self.riichi = data[2]
                self.dora[0] = data[5]
                ten = child.attrib["ten"].split(",")
                for i in range(0, len(ten)):
                    self.ten[i] = int(ten[i])
                self.hai = [[-1 for i in range(13)], [-1 for i in range(13)], [-1 for i in range(13)], [-1 for i in range(13)]]
                hai0 = child.attrib["hai0"].split(",")
                for i in range(0, len(hai0)):
                    self.hai[0][i] = int(hai0[i])

            if child.tag.startswith("E"):
                self.hai[1].append(int(child.tag[1:]))
            if child.tag.startswith("F"):
                self.hai[2].append(int(child.tag[1:]))
            if child.tag.startswith("G"):
                self.hai[3].append(int(child.tag[1:]))

            if child.tag.startswith("N"):
                who = int(child.attrib["who"])
                #鸣牌待完成...好复杂

            if child.tag == "DORA":
                self.dora.append(int(child.attrib["hai"]))

            if child.tag == "REACH":
                if self.whoRiichi[int(child.attrib["who"])] != 1:
                    self.whoRiichi[int(child.attrib["who"])] = 1

            if child.tag == "AGARI" or child.tag == "RYUUKYOKU":
                if(len(self.dora) < 4):
                    self.dora += [-1 for i in range(4-len(self.dora))]
                for i in range(len(self.hai)):
                    if(len(self.hai[i]) < 34):
                        self.hai[i] += [-1 for i in range(4-len(self.hai[i]))]
                feature = [self.name, self.combo, self.riichi] + self.dora + self.ten + self.whoRiichi
                feature += [i for i in self.hai]

        return features

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