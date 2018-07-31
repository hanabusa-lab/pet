#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold as SKF
import os
import sys
import shutil
import pickle
import warnings
warnings.filterwarnings('ignore')  # warning非表示


class ImgEvaluator():
    def __init__(self):
        self.features = []
        self.targets = []
        self.files = []

    def pca_plot(self):
        """
        特徴量をSVMし、グラフ表示
        参照コード https://blog.amedama.jp/entry/2017/04/02/130530
        """
        # 主成分分析する
        pca = PCA(n_components=2)
        pca.fit(self.features)

        # 分析結果を元に特徴量を主成分に変換する
        transformed = pca.fit_transform(self.features)

        # 主成分をプロットする
        for label in np.unique(self.targets):
            plt.scatter(transformed[self.targets == label, 0],
                        transformed[self.targets == label, 1])
        plt.title('principal component')
        plt.xlabel('pc1')
        plt.ylabel('pc2')

        # 主成分の寄与率を出力する
        print('各次元の寄与率: {0}'.format(pca.explained_variance_ratio_))
        print('累積寄与率: {0}'.format(sum(pca.explained_variance_ratio_)))

        # グラフを表示する
        plt.show()

    def read(self, datapaths):
        """
        データの読み込み
        """
        self.targets = pd.DataFrame(columns=[])
        self.features = pd.DataFrame(columns=[])
        self.files = pd.DataFrame(columns=[])
        for datapath in datapaths:
            # データを読み込む
            data_names = ('fname', 'sizef', 'scoref', 'xf', 'yf', 'is_good')
            dataset = pd.read_csv(datapath, header=None, names=data_names)

            # ワンちゃん写ってないデータを削除
            dataset = dataset[dataset.sizef > 0]

            # ラベルとデータを分離する
            tmp_targets = dataset.iloc[:, [5]]
            tmp_features = dataset.iloc[:, 1:5]
            tmp_files = dataset.iloc[:, [0]]

            # 000と001を結合する
            self.targets = pd.concat([self.targets, tmp_targets])
            self.features = pd.concat([self.features, tmp_features])
            self.files = pd.concat([self.files, tmp_files])

        # dataframe->numpy変換
        self.targets = self.targets.values
        self.features = self.features.values
        self.files = self.files.values

        # targetsのフォーマットを変換
        self.targets = self.targets.swapaxes(1, 0)[0]

    def SVM_KCross(self):
        """
        SVM, 10交差検証で精度と結果を出力
        参照　https://qiita.com/kazuki_hayakawa/items/18b7017da9a6f73eba77
             https://qiita.com/nittaryo1977/items/44553b9f555fe7932cca
             https://hayataka2049.hatenablog.jp/entry/2018/03/12/213524
             https://qiita.com/yhyhyhjp/items/c81f7cea72a44a7bfd3a
        """
        # 交差検証
        skf = SKF(n_splits=10, random_state=0, shuffle=True)
        trues = []
        preds = []
        test_files = []
        for train_index, test_index in skf.split(self.features, self.targets):
            # 正規化
            sc = StandardScaler()
            sc.fit(self.features[train_index])
            X_train_std = sc.transform(self.features[train_index])
            X_test_std = sc.transform(self.features[test_index])

            # モデル定義(デフォルトだとRBFカーネル)
            num_m = self.targets[train_index].size
            num_c = np.sum(self.targets[train_index] == 0)
            svm = SVC(random_state=None,  probability=True,
                      class_weight={0: 1, 1: num_c/num_m})

            # 学習
            svm.fit(X_train_std, self.targets[train_index])
            trues.append(self.targets[test_index])

            # 推論
            preds.append(svm.predict(X_test_std))
            test_files.append(np.hstack(self.files[test_index]))

        # 精度出力
        print(classification_report(np.hstack(trues), np.hstack(preds),
                                    target_names=["bad", "good"]))
        # 予測結果を出力
        self.__makeResultDir(np.hstack(test_files),
                             np.hstack(trues), np.hstack(preds))


    def __setResultDir(self):
        # 正解TP, 検出漏れFN, 誤検出FP, 正解TN
        if os.path.exists("./data/TP"):
            shutil.rmtree("./data/TP")
        if os.path.exists("./data/FN"):
            shutil.rmtree("./data/FN")
        if os.path.exists("./data/FP"):
            shutil.rmtree("./data/FP")
        if os.path.exists("./data/TN"):
            shutil.rmtree("./data/TN")
        os.mkdir("./data/TP")
        os.mkdir("./data/FN")
        os.mkdir("./data/FP")
        os.mkdir("./data/TN")        
        
    def __makeResultDir(self, test_files, trues, preds):
        # 予測結果を出力
        # ディレクトリ削除&生成
        self.__setResultDir()

        for test_file, true, pred in zip(test_files, trues, preds):
            # print(test_file, true, pred)

            basename = os.path.basename(test_file)
            if true == 1 and pred == 1:
                shutil.copyfile(test_file, "./data/TP/"+basename)
            if true == 1 and pred == 0:
                shutil.copyfile(test_file, "./data/FN/"+basename)
            if true == 0 and pred == 1:
                shutil.copyfile(test_file, "./data/FP/"+basename)
            if true == 0 and pred == 0:
                shutil.copyfile(test_file, "./data/TN/"+basename)

                
    def makeDictionary(self):
        """
        全特徴量を用いて辞書学習
        """

        # 正規化
        sc = StandardScaler()
        sc.fit(self.features)
        X_train_std = sc.transform(self.features)

        # SVMのモデル定義(デフォルトだとRBFカーネル)
        _class_weight = {0: 1, 1: np.sum(self.targets == 0)/self.targets.size}
        svm = SVC(random_state=None, probability=True,
                  class_weight=_class_weight)

        # 学習
        svm.fit(X_train_std, self.targets)

        # モデルを保存する
        sc_filename = "sc_dog.sav"
        svm_filename = 'dictionary_dog.sav'
        pickle.dump(sc, open(sc_filename, 'wb'))
        pickle.dump(svm, open(svm_filename, 'wb'))

        # 保存したモデルをロードする
        """
        sc_filename = "sc_dog.sav"
        svm_filename = 'dictionary_dog.sav'
        sc_model = pickle.load(open(sc_filename, 'rb'))
        svm_model = pickle.load(open(svm_filename, 'rb'))
        X_train_std2 = sc_model.transform(self.features)
        print(svm_model.score(X_train_std2, self.targets))
        """

    def setFeatures(self, features):
        """
        Featuresのセッター
        """
        self.features = features

    def evaluate(self):
        """
        保存したモデルで推論
        """
        # 保存したモデルをロードする
        sc_filename = "sc_dog.sav"
        svm_filename = 'dictionary_dog.sav'
        sc_model = pickle.load(open(sc_filename, 'rb'))
        svm_model = pickle.load(open(svm_filename, 'rb'))

        # 推論
        features_std = sc_model.transform(self.features)
        return svm_model.predict_proba(features_std)


if __name__ == '__main__':
    """
    評価部分のテスト実行及び解析プログラム
    引数0:特徴量プロット&10交差検証
    引数1:辞書学習&全評価
    """

    # 引数チェック
    args = sys.argv
    if len(args) < 1:
        sys.stderr.write("please input mode")
        sys.stderr.write("mode=0:feature plot and 10-k validation")
        sys.stderr.write("mode=1:learn dictionary and evaluate")
    else:
        mode = int(args[1])

    # データ読み込み
    imgEvaluator = ImgEvaluator()
    imgEvaluator.read(["./data/000_data.txt", "./data/001_data.txt"])

    if mode == 0:
        # 特徴量プロット&10交差検証
        imgEvaluator.pca_plot()
        imgEvaluator.SVM_KCross()
    elif mode == 1:
        # 辞書学習&全評価
        imgEvaluator.makeDictionary()
        print(np.c_[imgEvaluator.files, imgEvaluator.evaluate()])

    else:
        sys.stderr.write("please input mode")
        sys.stderr.write("mode=0:feature plot and 10-k validation")
        sys.stderr.write("mode=1:learn dictionary and evaluate")
