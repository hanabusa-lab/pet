#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 17:27:42 2018

@author: yoshiki
"""

import imgevaluator
import featuredetector
import os
import json
import collections as cl
import warnings
warnings.filterwarnings('ignore')  # warning非表示


class ImgProcessor():
    """
    画像がワンちゃん主役の良画像か判定するクラス
    """
    def __init__(self):
        # 特徴抽出クラス
        self.featureDetector = featuredetector.FeatureDetector()
        # 評価クラス
        self.imgEvaluator = imgevaluator.ImgEvaluator()

    def proc(self, src, fname):
        """
        画像がワンちゃん主役の良画像か判定
        """
        # 入力画像パスセット
        img_paths = []
        img_paths.append(src)

        # 認識
        self.featureDetector.objct_recognition(img_paths)
        # 特徴抽出
        self.featureDetector.detect()
        # ROI算出
        self.featureDetector.calcRois()

        # 結果をjsonに書き出す
        self.__out(fname)

    def __out(self, fname):
        """
        判定結果をjsonに出力する
        """
        if os.path.exists(fname):
            os.remove(fname)  # 前回作ったファイルを削除

        ys = cl.OrderedDict()
        data = cl.OrderedDict()
        self.imgEvaluator.setFeatures(self.featureDetector.features)  # 特徴量をセット
        data["score"] = self.imgEvaluator.evaluate()[0][1]  # 良画像の確率を出力
        if self.featureDetector.rois!=[[]]:
            # ワンちゃん検出されている場合
            data["x"] = self.featureDetector.rois[0][0]
            data["y"] = self.featureDetector.rois[0][1]
            data["width"] = self.featureDetector.rois[0][2]
            data["height"] = self.featureDetector.rois[0][3]
        else:
            # ワンちゃん検出されていない場合
            data["x"] = -1
            data["y"] = -1
            data["width"] = -1
            data["height"] = -1
            
        ys["picture info"] = data
        fw = open(fname, 'w')
        json.dump(ys, fw, indent=4)


if __name__ == '__main__':
    """
    入力画像について、ワンちゃんが主役でいい感じか評価し出力する。
    入力：画像のファイルパス、出力：評価結果json
    """
    imgProcessor = ImgProcessor()
    # imgProcessor.proc("./data/sample/000006.png", "./data/sample/000006.json")
    imgProcessor.proc("./data/sample/2.jpg", "./data/sample/2.json")