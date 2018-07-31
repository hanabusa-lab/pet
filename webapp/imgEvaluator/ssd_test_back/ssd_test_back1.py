#インポート
import cv2
import keras
from keras.applications.imagenet_utils import preprocess_input
from keras.backend.tensorflow_backend import set_session
from keras.models import Model
from keras.preprocessing import image
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imread
import tensorflow as tf

from ssd import SSD300
from ssd_utils import BBoxUtility


##########各種設定済ませる##########
plt.rcParams['figure.figsize'] = (8, 8) #グラフサイズ(インチ
#http://d.hatena.ne.jp/nishiohirokazu/20111121/1321849806
plt.rcParams['image.interpolation'] = 'nearest' # 補完アルゴル設定
np.set_printoptions(suppress=True) #出力の圧縮=Trues
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.45 #プロセス辺りのGPU占有率
set_session(tf.Session(config=config))
##########各種設定済ませる##########


##########認識するクラス一覧#########
voc_classes = ['Aeroplane', 'Bicycle', 'Bird', 'Boat', 'Bottle',
               'Bus', 'Car', 'Cat', 'Chair', 'Cow', 'Diningtable',
               'Dog', 'Horse','Motorbike', 'Person', 'Pottedplant',
               'Sheep', 'Sofa', 'Train', 'Tvmonitor']
NUM_CLASSES = len(voc_classes) + 1
##########認識するクラス一覧#########


#########認識関連の設定・読み込み#####
input_shape=(300, 300, 3) #入力画像サイズ
model = SSD300(input_shape, num_classes=NUM_CLASSES) #モデル確保
model.load_weights('weights_SSD300.hdf5', by_name=True) #モデル読み込み
bbox_util = BBoxUtility(NUM_CLASSES) #バウンディングボックスクラス？
inputs = []
images = []
#########認識関連の設定・読み込み#####

########多数画像処理の名残##########
"""
img_path = './pics/fish-bike.jpg'
img = image.load_img(img_path, target_size=(300, 300))
img = image.img_to_array(img)
images.append(imread(img_path))
inputs.append(img.copy())
img_path = './pics/cat.jpg'
img = image.load_img(img_path, target_size=(300, 300))
img = image.img_to_array(img)
images.append(imread(img_path))
inputs.append(img.copy())
img_path = './pics/boys.jpg'
img = image.load_img(img_path, target_size=(300, 300))
img = image.img_to_array(img)
images.append(imread(img_path))
inputs.append(img.copy())
img_path = './pics/car_cat.jpg'
img = image.load_img(img_path, target_size=(300, 300))
img = image.img_to_array(img)
images.append(imread(img_path))
inputs.append(img.copy())
img_path = './pics/car_cat2.jpg'
img = image.load_img(img_path, target_size=(300, 300))
img = image.img_to_array(img)
images.append(imread(img_path))
inputs.append(img.copy())
"""
########多数画像処理の名残##########

########画像読み込み###############
img_path = './pics/hoshi.jpg'
img = image.load_img(img_path, target_size=(300, 300)) #画像読み込み
img = image.img_to_array(img) #キャスト
images.append(imread(img_path))
inputs.append(img.copy())
########画像読み込み###############

inputs = preprocess_input(np.array(inputs)) #前処理
preds = model.predict(inputs, batch_size=1, verbose=1) #認識
results = bbox_util.detection_out(preds) #結果クラス？生成

#time...謎処理。。。
#a = model.predict(inputs, batch_size=1)
#b = bbox_util.detection_out(preds)

#入力画像ごとループ
for i, img in enumerate(images):
    # 結果クラスを分割
    det_label = results[i][:, 0]
    det_conf = results[i][:, 1]
    det_xmin = results[i][:, 2]
    det_ymin = results[i][:, 3]
    det_xmax = results[i][:, 4]
    det_ymax = results[i][:, 5]

    #信頼度0.6以上を取得
    top_indices = [i for i, conf in enumerate(det_conf) if conf >= 0.6]

    top_conf = det_conf[top_indices]
    top_label_indices = det_label[top_indices].tolist()
    top_xmin = det_xmin[top_indices]
    top_ymin = det_ymin[top_indices]
    top_xmax = det_xmax[top_indices]
    top_ymax = det_ymax[top_indices]

    colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()

    plt.imshow(img / 255.) #画像描画
    currentAxis = plt.gca()

    #描画(認識結果ごとループ)
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
        currentAxis.add_patch(plt.Rectangle(*coords, fill=False, edgecolor=color, linewidth=2))
        currentAxis.text(xmin, ymin, display_txt, bbox={'facecolor':color, 'alpha':0.5})
    
    #保存
    plt.savefig('figure.png') 
    plt.show()

import gc; gc.collect() #メモリ解放
#https://qiita.com/haminiku/items/fc9878d59e19bd5d04fc
