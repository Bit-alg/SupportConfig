import math
import pandas as pd
from sklearn.decomposition import NMF
from tensorly.decomposition import tucker
import numpy as np

# タッカー分解を利用するためのネットワークコンフィグを変換する際に使用するテンプレートリスト
template_list = []

# NMFの入力形式に合わせたネットワークコンフィグの変換をする.
def NMF_input_matrix(config_templates, frame_num):
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

    pdFrame = pdFrame.where(pdFrame == 0, 1)
           
    return pdFrame


# テンプレートのリストの取得をする.
def get_template_list(config_templates):
    # テンプレートリストの初期化
    template_list = []

    # テンプレートの数をカウントする
    for config_template in config_templates:
        for word in config_template:
            if word not in template_list:
                template_list.append(word)

    return template_list
        

# Tucker分解の入力形式に合わせたネットワークコンフィグの変換をする.
def tucker_input_matrix(config_templates, frame_num):

    # ネットワークコンフィグの全テンプレートが保存されたリストの取得
    template_list = get_template_list(config_templates)

    # 3次元の入力行列の初期化
    input_tensor = np.empty((0,frame_num,len(template_list)))
    
    # 各テンプレートに対するカウントの初期化
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

# ネットワークコンフィグが属するブロックの候補を決定する (NMF)
def template_grouping_NMF(config_templates, frame, n_comp):

    # 分割するフレーム数
    frame_num = frame

    # 
    X = NMF_input_matrix(config_templates, frame_num)

    columns = X.columns.values

    # X ~= WHに分解するNMFモデルを入手
    model = NMF(n_components = n_comp, init='random', random_state = 1)
    W = model.fit_transform(X)

    # Hは特徴数*テンプレートからなる行列
    H = model.components_
    H = pd.DataFrame(H)
    H.columns = columns

    return H

# ネットワークコンフィグが属するブロックの候補を決定する (タッカー分解)
def template_grouping_Tucker(config_templates, frame, n_comp, alpha, beta, ganma):

    input_tucker = tucker_input_matrix(config_templates, frame)

    model = tucker(tensor = input_tucker, rank = [alpha, beta, ganma], random_state = 1)

    array = model[1][2].tolist()

    # テンプレートのリストの取得
    template_list = get_template_list(config_templates)

    # arrayをpandasに変換する
    result = pd.DataFrame(array)

    # 各行を対応するテンプレートのインデックス情報を付与する.
    result.index = template_list

    return result


