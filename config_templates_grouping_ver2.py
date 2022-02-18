import math
import pandas as pd
import numpy as np
from dataset import load_dataset
from dataset import process_dataset
from extract_templates import extract_templates
from tensorly.decomposition import non_negative_tucker
from sklearn.decomposition import NMF

#全てのコンフィグの中の最大行を取得する.
def maxline_config(config_templates):

    # 最大の行数をもつコンフィグのインデックスを格納している.
    max_index = -1
    # 各コンフィグの中で最大の行数を取得する.
    max_line = 0

    for i in range(len(config_templates)):
        #全てのコンフィグを調べていき, 最大のコンフィグを更新するたびネスト内の操作を行う.
        if len(config_templates[i]) > max_line:
            max_line = len(config_templates[i])
            max_index = i

    return max_line

# 最大の行数に合わせてコンフィグを補う
def padding(config_templates):
    max_line = maxline_config(config_templates)
    result_config = []

    blank_char = "blank"

    for config in config_templates:
        rest_line = max_line - len(config)
        if rest_line == 1:
            config = [blank_char] + config
        elif rest_line > 2:
            upper_line = math.ceil(rest_line/2)
            lower_line = math.floor(rest_line/2)

            for i in range(upper_line):
                config = [blank_char] + config
            for i in range(lower_line):
                config.append(blank_char)

        result_config.append(config)
        

    return result_config

def get_template_list(config_templates):
    # テンプレートリストの初期化
    template_list = []

    # テンプレートの数をカウントする
    for config_template in config_templates:
        for word in config_template:
            if word not in template_list:
                template_list.append(word)

    return template_list



# タッカー分解の入力形式に即した3次元行列を構築する.
def tucker_input_matrix(config_templates, frame_num):
    # コンフィグファイルの全テンプレートが格納されたリストの取得
    template_list = get_template_list(config_templates)

    config_templates = padding(config_templates)

    input_tensor = np.empty((0, maxline_config(config_templates),len(template_list)))

    count_template = [0]*len(template_list)

    line_per_frame = math.floor(maxline_config(config_templates)/frame_num)

    config_list_frame = ["blank"]*line_per_frame


    for config in config_templates:
        #フレーム内にコンフィグを格納する添字
        i = 0
        frame_count = np.empty((0,len(template_list)), int)
        for c in config:
            count_template = [0]*len(template_list)
            config_list_frame[i%line_per_frame] = c

            for c_temp in config_list_frame:
                if c_temp == "blank":
                    continue
                count_template[template_list.index(c_temp)] = 1
            count_template_num = np.array(count_template)
            frame_count = np.append(frame_count, [count_template_num], axis = 0)

            i = i + 1
        input_tensor = np.append(input_tensor, [frame_count], axis = 0)

    return input_tensor

# NTDの入力行列を圧縮して2次元の行列で表現する.
def NMF_input_matrix(config_templates, frame_num):
    input_tensor = tucker_input_matrix(config_templates, frame_num)

    NMF_input = input_tensor[0]

    for i in range(len(input_tensor)):
        if i == 0:
            continue
        NMF_input = NMF_input + input_tensor[i]
    
    df = pd.DataFrame(data = NMF_input, columns = get_template_list(config_templates))

    df.to_csv("NMF.csv")

    df.where(df>0, 0)

    return df

# ネットワークコンフィグが属するブロックの候補を決定する (タッカー分解)
def template_grouping_Tucker(config_templates, frame, n_comp):

    input_tucker = tucker_input_matrix(config_templates, frame)

    model =  non_negative_tucker(tensor = input_tucker, rank = n_comp, random_state = 1)

    array = model[1][2].tolist()

    # テンプレートのリストの取得
    template_list = get_template_list(config_templates)

    # arrayをpandasに変換する
    result = pd.DataFrame(array)

    # 各行を対応するテンプレートのインデックス情報を付与する.
    result.index = template_list

    return result

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

