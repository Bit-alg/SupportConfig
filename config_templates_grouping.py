from dataset import load_dataset
from dataset import process_dataset_ver2
from extract_templates_ver_2 import extract_templates
import math
import pandas as pd
from itertools import islice
from sklearn.decomposition import NMF
import matplotlib.pyplot as plt
from tensorly.decomposition import tucker
import numpy as np

#テキストファイルを基に読み込んだコンフィグ
load_text = []

#コメントなど余分な要素を取り除いたコンフィグ
config_statement = []

#コンフィグのテンプレート
config_template = []

#各コンフィグファイルごとに適当なフレーム数に分割して考える(pattern 1)
def create_input_matrix_ver1(config_templates, frame_num):
    pdFramelist = []
    #各indexごとに各フレームのテンプレートとその頻度のdictionaryを格納する
    temp = []
    #分割するフレーム数
    frame = frame_num
    #フレーム数のdictionaryを用意する
    for i in range(0,frame+1):
        temp.append({})
        
    for config_template in config_templates:
        #カウント
        count = 1
        #1フレームごとの行数
        num_per_frame = math.floor(len(config_template)/frame_num)

        #tempのindex
        i = 0
        for word in config_template:
            #フレームが切り替わる時の処理
            if count == num_per_frame:
                i = i + 1
                count = 1
                if i == frame+1:
                    break
                
            count = count + 1

            #フレーム内にテンプレートが含まれている場合ビットを立たせる.
            temp[i][word] = 1
            
    #dictionaryからPandasFrameを作成(ここからやる)
    for i in range(0, frame+1):
        pdFramelist.append(pd.DataFrame([temp[i]],index=[i]))

    #各フレームのpandasを連結させる
    pdFrame = pdFramelist[0]
    for i in range(1, frame + 1):
        pdFrame = pd.concat([pdFrame, pdFramelist[i]], join='outer', sort=True)

    # Nanを0に置き換える
    pdFrame = pdFrame.fillna(0)
        
    return pdFrame


def get_template_list(config_templates):
    template_list = []
    count = 0
    for config_template in config_templates:
        for word in config_template:
            if word not in template_list:
                template_list.append(word)
                count = count + 1

    print(count)
    return template_list
        

# Tucker分解で用いる
def tucker_input_matrix(config_templates, frame_num):

    #ネットワークコンフィグの全テンプレートが保存されたリストの取得
    template_list = get_template_list(config_templates)

    #入力
    input_tensor = np.empty((0,frame_num,len(template_list)))

    
    count_template = [0]*len(template_list)

    
                
    #分割するフレーム数
    frame = frame_num
    flag = True
    for config_template in config_templates:
        #各テンプレートの頻度をカウント数を格納するnumpy
        temp = np.empty((0,len(template_list)), int)
        #カウント
        count = 1
        #1フレームごとの行数
        num_per_frame = math.floor(len(config_template)/frame)
        #最後のフレームかどうかを判別するフラグ
        flag_remin = True
        #コンフィグの行数をカウント
        word_count = 0
        #フレーム数のカウント
        flag_count = 0

        #各ネットワークコンフィグを行数ごとにループ
        for word in config_template:

            word_count = word_count  + 1

            #フレーム内に含まれるテンプレートのビットを立てる.
            count_template[template_list.index(word)] = 1
            
            #フレームが切り替わる時の処理
            if count == num_per_frame and flag_remin:
                count_template_num = np.array(count_template)
                temp = np.append(temp, [count_template_num], axis = 0)
                
                #該当するテンプレートの個数のカウントの初期化をする
                count_template  = [0]*len(template_list)
                
                count = 1
                flag_count = flag_count + 1

                #最後のフレームの一つ前のフレームで実行される
                if flag_count == frame-1:
                    flag_remin = False
                continue

            if word_count == len(config_template):
                count_template_num = np.array(count_template)
                temp = np.append(temp, [count_template_num], axis = 0)
    
            count = count + 1

        # 各ネットワークコンフィグのテンプレートの頻度をinput_tensorに追加する.
        input_tensor = np.append(input_tensor,[temp], axis = 0)

    return input_tensor
    

#コンフィグのグルーピングをする.
def template_grouping(config_templates, n_comp, version ):

    #分割するフレーム数
    frame_num = 15
    X = create_input_matrix_ver1(config_templates, frame_num)

    columns = X.columns.values

    # X ~= WHに分解するNMFモデルを入手
    model = NMF(n_components = n_comp, init='random', random_state = 1)
    W = model.fit_transform(X)

    # Hは特徴数*テンプレートからなる行列
    H = model.components_
    H = pd.DataFrame(H)
    H.columns = columns
    
    return H

#----------------------テストモジュール(データセットの取り込みとテンプレートの抽出)-----
load_text = load_dataset()
config_statement = process_dataset_ver2(load_text)

config_template = extract_templates(config_statement)

count = 0

for i in config_template:
    for word in i:
        count = count + 1


print(count)


#----------------------テストモジュール(NMFとTucker分解の実行)----------------------

# Tucker分解の入力テンソルの取得
input_tucker = tucker_input_matrix(config_template, 5)

# input_tuckerをTucker分解に適応する
# パラメータは経験則に基づいて決めた.(後にパラメータのチューニングは考える)
model = tucker(tensor = input_tucker, rank = [5,5,5],random_state = 1)

# テンプレート次元方向の行列の取得
pdDataFrame = model[1][2].tolist()

# テンプレートのリストの取得
template_list = get_template_list(config_template)

# arrayをpandasに変換する
result = pd.DataFrame(pdDataFrame)

# 各行を対応するテンプレートのインデックス情報を付与する.
result.index = template_list

#特定のテンプレートだけ抽出したpandas
result = result.loc[["interface *","ip address * *","router ospf *","router-id *","network * * area *","redistribute connected subnets", "router bgp *","bgp router-id *", "bgp log-neighbor-changes", "neighbor * peer-group", "neighbor * remote-as *", "neighbor * update-source Loopback0", "route-map * permit *", "match ip address *", "set metric *"],:]

#Tucker分解の結果のcsvファイルの出力
result.to_csv("Tucker_result_K=5_M=5_Frame_10122319.csv")

# NMFにおけるテンプレート次元方向の行列の取得
H = template_grouping(config_template, 5,1)

#特定のテンプレートだけ抽出したpandas
H = H.loc[:,["interface *","ip address * *","router ospf *","router-id *","network * * area *","redistribute connected subnets", "router bgp *","bgp router-id *", "bgp log-neighbor-changes", "neighbor * peer-group", "neighbor * remote-as *", "neighbor * update-source Loopback0", "route-map * permit *", "match ip address *", "set metric *"]]

#NMFの結果のcsvファイルの出力
H.to_csv('output_ver1_K=5_M=5_ver2.csv')

