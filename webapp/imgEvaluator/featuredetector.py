# インポート
import os
import cv2
from keras.applications.imagenet_utils import preprocess_input
from keras.backend.tensorflow_backend import set_session
from keras.preprocessing import image
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imread
import tensorflow as tf
import glob
from ssd import SSD300
from ssd_utils import BBoxUtility
import warnings
warnings.filterwarnings('ignore')  # warning非表示


class FeatureDetector:
    """
    ディープラーニングを用いた特徴抽出クラス
    """

    def __init__(self):
        self.img_paths = []        # 対象画像パス
        self.results = []        # 認識結果
        self.shapes = []        # 元画像の大きさ
        self.dogRates = []        # ワンちゃんの占める割合特徴
        self.aveScores = []        # 認識スコア特徴
        self.xPoses = []        # x方向中心度特徴
        self.yPoses = []        # y方向中心度特徴
        self.features = []        # 特徴量
        self.rois = []        # メインワンちゃんのROI

    def objct_recognition(self, img_paths):
        """
        ssdを用いた物体検出    
        """
        """各種設定"""
        self.img_paths = img_paths
        plt.rcParams['figure.figsize'] = (8, 8)  # グラフサイズ(インチ
        # http://d.hatena.ne.jp/nishiohirokazu/20111121/1321849806
        plt.rcParams['image.interpolation'] = 'nearest'  # 補完アルゴル設定
        np.set_printoptions(suppress=True)  # 出力の圧縮=Trues
        config = tf.ConfigProto()
        # プロセス辺りのGPU占有率
        config.gpu_options.per_process_gpu_memory_fraction = 0.45
        set_session(tf.Session(config=config))
        """各種設定"""

        """認識クラス一覧"""
        voc_classes = ['Aeroplane', 'Bicycle', 'Bird', 'Boat', 'Bottle',
                       'Bus', 'Car', 'Cat', 'Chair', 'Cow', 'Diningtable',
                       'Dog', 'Horse', 'Motorbike', 'Person', 'Pottedplant',
                       'Sheep', 'Sofa', 'Train', 'Tvmonitor']
        NUM_CLASSES = len(voc_classes) + 1
        """認識クラス一覧"""

        """認識関連の設定・読み込み"""
        input_shape = (300, 300, 3)  # 入力画像サイズ
        model = SSD300(input_shape, num_classes=NUM_CLASSES)  # モデル確保
        model.load_weights('weights_SSD300.hdf5', by_name=True)  # モデル読み込み
        bbox_util = BBoxUtility(NUM_CLASSES)  # バウンディングボックスクラス？
        """認識関連の設定・読み込み"""

        """画像読み込み"""
        inputs = []
        images = []
        for img_path in self.img_paths:
            img = image.load_img(img_path, target_size=(300, 300))  # 画像読み込み
            img = image.img_to_array(img)  # キャスト
            images.append(imread(img_path))
            inputs.append(img.copy())
        """画像読み込み"""

        inputs = preprocess_input(np.array(inputs))  # 前処理
        preds = model.predict(inputs, batch_size=1, verbose=1)  # 認識
        self.results = bbox_util.detection_out(preds)  # 結果クラス？生成

        # 入力画像ごとループ
        for i_, img in enumerate(images):
            # shapesの更新
            self.shapes.append([img.shape[1], img.shape[0]])

            # 結果クラスを分割
            if self.results[i_] == []:
                # 認識結果ない場合、以降の処理しない
                continue
            det_label = self.results[i_][:, 0]
            det_conf = self.results[i_][:, 1]
            det_xmin = self.results[i_][:, 2]
            det_ymin = self.results[i_][:, 3]
            det_xmax = self.results[i_][:, 4]
            det_ymax = self.results[i_][:, 5]

            # 信頼度0.6以上を取得
            top_indices = [i_ for i_, conf in enumerate(
                det_conf) if conf >= 0.6]

            top_conf = det_conf[top_indices]
            top_label_indices = det_label[top_indices].tolist()
            top_xmin = det_xmin[top_indices]
            top_ymin = det_ymin[top_indices]
            top_xmax = det_xmax[top_indices]
            top_ymax = det_ymax[top_indices]

            colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()

            plt.imshow(img / 255.)  # 画像描画
            currentAxis = plt.gca()

            # 描画(認識結果ごとループ)
            for i in range(top_conf.shape[0]):
                xmin = int(round(top_xmin[i] * img.shape[1]))
                ymin = int(round(top_ymin[i] * img.shape[0]))
                xmax = int(round(top_xmax[i] * img.shape[1]))
                ymax = int(round(top_ymax[i] * img.shape[0]))
                score = top_conf[i]
                label = int(top_label_indices[i])
                label_name = voc_classes[label - 1]
                display_txt = '{:0.2f}, {}'.format(score, label_name)
                coords = (xmin, ymin), xmax-xmin+1, ymax-ymin+1
                color = colors[label]
                currentAxis.add_patch(plt.Rectangle(
                    *coords, fill=False, edgecolor=color, linewidth=2))
                currentAxis.text(xmin, ymin, display_txt, bbox={
                                 'facecolor': color, 'alpha': 0.5})
                # print(xmin, ymin, xmax, ymax)

            # 保存
            # plt.savefig("./data/recognition_imgs/"+os.path.basename(img_paths[i_]))
            plt.close()

        import gc
        gc.collect()  # メモリ解放
        # https://qiita.com/haminiku/items/fc9878d59e19bd5d04fc

        # return results, shapes, [xmin, ymin, xmax-xmin, ymax-ymin]
        # return results, shapes

    def calcDogRate(self, result, shape):
        """
        単画像でワンちゃん占有率特徴を計算
        """
        brank_img = np.zeros((shape[1], shape[0], 1), np.uint8)  # 元画像と同サイズの0配列

        if result == []:
            # 何も認識していない場合
            return 0

        # 結果クラスを分割
        det_label = result[:, 0]
        det_conf = result[:, 1]
        det_xmin = result[:, 2]
        det_ymin = result[:, 3]
        det_xmax = result[:, 4]
        det_ymax = result[:, 5]

        # 信頼度0.6以上を取得
        top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]
        top_conf = det_conf[top_indices]  # 信頼度のリスト
        top_label_indices = det_label[top_indices].tolist()  # 認識ラベルのリスト
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]

        for i in range(len(top_conf)):
            label_indices = top_label_indices[i]
            if label_indices != 12:
                # dig label = 12
                # ワンちゃん以外は無視！
                continue

            else:
                # ワンちゃんなら黒画像を白塗り
                left_top = [int(top_xmin[i]*shape[0]),
                            int(top_ymin[i]*shape[1])]
                right_top = [int(top_xmax[i]*shape[0]),
                             int(top_ymin[i]*shape[1])]
                right_bottom = [int(top_xmax[i]*shape[0]),
                                int(top_ymax[i]*shape[1])]
                left_bottom = [int(top_xmin[i]*shape[0]),
                               int(top_ymax[i]*shape[1])]
                count = np.array(
                    [left_top, left_bottom, right_bottom, right_top])
                cv2.fillPoly(brank_img, pts=[count], color=255)

        # ワンちゃん占有率を返す
        return np.sum(brank_img)/255/(shape[0]*shape[1])

    def calcDogRateFeature(self):
        """
        複数画像でワンちゃん占有率を計算
        """
        self.dogRates = []
        for result, shape in zip(self.results, self.shapes):
            dogRate = self.calcDogRate(result, shape)
            self.dogRates.append(dogRate)

    def calcSSDScore(self, result):
        """
        単画像でワンちゃん平均認識スコアを計算
        """
        # ワンちゃん平均認識スコア
        aveScore = 0

        # 何も認識していない場合
        if result == []:
            return 0

        # 結果クラスを分割
        det_label = result[:, 0]
        det_conf = result[:, 1]

        # 信頼度0.6以上を取得
        top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]
        top_conf = det_conf[top_indices]  # 信頼度のリスト
        top_label_indices = det_label[top_indices].tolist()  # 認識ラベルのリスト

        counter = 0
        for i in range(len(top_conf)):
            label_indices = top_label_indices[i]
            if label_indices != 12:
                # dig label = 12
                # ワンちゃん以外は無視！
                continue

            else:
                aveScore = aveScore+top_conf[i]
                counter = counter+1

        # 平均スコアを返す
        if counter == 0:
            return 0
        else:
            return aveScore/counter

    def calcSSDScoreFeature(self):
        """
        複数画像でワンちゃん平均認識スコアを計算
        """
        self.aveScores = []
        for result in self.results:
            aveScore = self.calcSSDScore(result)
            self.aveScores.append(aveScore)

    def calcXPoseScore(self, result, shape):
        """
        単画像でワンちゃんx位置を計算
        """
        # 何も認識していない場合
        if result == []:
            return 0

        # 結果クラスを分割
        det_label = result[:, 0]
        det_conf = result[:, 1]
        det_xmin = result[:, 2]
        det_ymin = result[:, 3]
        det_xmax = result[:, 4]
        det_ymax = result[:, 5]

        # 信頼度0.6以上を取得
        top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]
        top_conf = det_conf[top_indices]  # 信頼度のリスト
        top_label_indices = det_label[top_indices].tolist()  # 認識ラベルのリスト
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]

        XPos = 0  # ワンちゃん X位置
        size = 0  # ワンちゃんサイズ（最大ワンちゃんのXを返す）
        for i in range(len(top_conf)):
            label_indices = top_label_indices[i]
            if label_indices != 12:
                # dig label = 12
                # ワンちゃん以外は無視！
                continue

            else:
                # ワンちゃんなら黒画像を白塗り
                tmp_size = (top_xmax[i]*shape[0] - top_xmin[i]*shape[0]) * \
                    (top_ymax[i]*shape[1] - top_ymin[i]*shape[1])
                if tmp_size > size:
                    size = tmp_size
                    XPos = (top_xmax[i] + top_xmin[i])/2
        return XPos

    def calcXPosFeature(self):
        """
        複数画像でワンちゃんx位置を計算
        """
        self.xPoses = []
        for result, shape in zip(self.results, self.shapes):
            xPos = self.calcXPoseScore(result, shape)
            self.xPoses.append(xPos)

    def calcYPoseScore(self, result, shape):
        """
        単画像でワンちゃんy位置を計算
        """
        # 何も認識していない場合
        if result == []:
            return 0

        # 結果クラスを分割
        det_label = result[:, 0]
        det_conf = result[:, 1]
        det_xmin = result[:, 2]
        det_ymin = result[:, 3]
        det_xmax = result[:, 4]
        det_ymax = result[:, 5]

        # 信頼度0.6以上を取得
        top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]
        top_conf = det_conf[top_indices]  # 信頼度のリスト
        top_label_indices = det_label[top_indices].tolist()  # 認識ラベルのリスト
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]

        YPos = 0  # ワンちゃん y位置
        size = 0  # ワンちゃんサイズ（最大ワンちゃんのXを返す）
        for i in range(len(top_conf)):
            label_indices = top_label_indices[i]
            if label_indices != 12:
                # dig label = 12
                # ワンちゃん以外は無視！
                continue

            else:
                # ワンちゃんなら黒画像を白塗り
                tmp_size = (top_xmax[i]*shape[0] - top_xmin[i]*shape[0]) * \
                    (top_ymax[i]*shape[1] - top_ymin[i]*shape[1])
                if tmp_size > size:
                    size = tmp_size
                    YPos = (top_ymax[i] + top_ymin[i])/2
        return YPos

    def calcYPosFeature(self):
        """
        複数画像でワンちゃんy位置を計算
        """
        self.yPoses = []
        for result, shape in zip(self.results, self.shapes):
            yPos = self.calcYPoseScore(result, shape)
            self.yPoses.append(yPos)

    def out(self, outname):
        """
        特徴量をテキストファイルに出力
        """
        if os.path.exists(outname):
            os.remove(outname)  # 前回作ったファイルを削除
        f = open(outname, 'w')
        for img_id in range(len(self.img_paths)):
            _str = img_paths[img_id]
            for f_id in range(len(self.features[0])):
                _str = _str+","+str(self.features[img_id][f_id])
            # 引数の文字列をファイルに書き込む
            # 末尾に評価値(0)を入れる
            f.write(_str+",0\n")
        f.close()

    def detect(self):
        # 特徴１：画像でワンちゃん占める割合
        self.calcDogRateFeature()
        # 特徴２：ワンちゃんの認識スコア
        self.calcSSDScoreFeature()
        # 特徴３：メインワンちゃんのx方向中心度
        self.calcXPosFeature()
        # 特徴４：メインワンちゃんのy方向中心度
        self.calcYPosFeature()

        # 特徴量をセット
        self.features = [self.dogRates,
                         self.aveScores, self.xPoses, self.yPoses]
        # 行列を入れ替えて、画像id, 特徴idとする
        self.features = list(map(list, zip(*self.features)))

    def calcRoi(self, result, shape):
        # 何も認識していない場合
        if result == []:
            return 0

        # 結果クラスを分割
        det_label = result[:, 0]
        det_conf = result[:, 1]
        det_xmin = result[:, 2]
        det_ymin = result[:, 3]
        det_xmax = result[:, 4]
        det_ymax = result[:, 5]

        # 信頼度0.6以上を取得
        top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]
        top_conf = det_conf[top_indices]  # 信頼度のリスト
        top_label_indices = det_label[top_indices].tolist()  # 認識ラベルのリスト
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]

        roi = []  # メインワンちゃん ROI
        size = 0  # ワンちゃんサイズ（最大ワンちゃんのXを返す）
        for i in range(len(top_conf)):
            label_indices = top_label_indices[i]
            if label_indices != 12:
                # dig label = 12
                # ワンちゃん以外は無視！
                continue

            else:
                # ワンちゃんなら黒画像を白塗り
                tmp_size = (top_xmax[i]*shape[0] - top_xmin[i]*shape[0]) * \
                    (top_ymax[i]*shape[1] - top_ymin[i]*shape[1])
                if tmp_size > size:
                    size = tmp_size
                    
                    roi = [int(top_xmin[i]*shape[0]), int(top_ymin[i]*shape[1]), int(
                        (top_xmax[i]-top_xmin[i])*shape[0]), int((top_ymax[i]-top_ymin[i])*shape[1])]
        return roi

    def calcRois(self):
        """
        複数画像でメインワンちゃんROIを計算
        """
        self.rois = []
        for result, shape in zip(self.results, self.shapes):
            roi = self.calcRoi(result, shape)
            self.rois.append(roi)


if __name__ == '__main__':
    """
    ディープラーニングを用いた特徴抽出のテスト実行
    """
    # 入力画像パス取得
    data_path = "./data/images_min"
    img_paths = glob.glob(data_path+"/*")

    # 特徴抽出クラス宣言
    featureDetector = FeatureDetector()

    # SSDによる認識
    featureDetector.objct_recognition(img_paths)
    # 特徴抽出
    featureDetector.detect()
    # ファイル出力
    featureDetector.out("./data/data.txt")
    # メインワンちゃんのROI取得
    featureDetector.calcRois()

    print("feature detected ./data/images_min=>./data/data.txt")
