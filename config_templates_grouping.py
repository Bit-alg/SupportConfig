from dataset import load_dataset
from dataset import process_dataset_ver2
from extract_templates_ver_2 import extract_templates
import math
import pandas as pd
from itertools import islice
from sklearn.decomposition import NMF
import matplotlib.pyplot as plt

#テキストファイルを基に読み込んだコンフィグ
load_text = []

#コメントなど余分な要素を取り除いたコンフィグ
config_statement = []

#コンフィグのテンプレート
config_template = []

def dict_chunks(data, size):

    it = iter(data)

    for i in range(0, len(data), size):

        yield {k:data[k] for k in islice(it, size)}


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

            #dictionaryのkeyに同じテンプレートが存在する場合
            if word in temp[i]:
                temp[i][word] = temp[i][word] + 1
                continue

            #dictionaryのkeyに存在しないテンプレートの場合
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

#テンプレートの頻度を基準にした行列の取得
def create_input_matrix_ver2(config_templates):
    count = {}

    for config_template in config_templates:
        for template in config_template:
            if template in count:
                count[template] = count[template] + 1
                continue

            count[template] = 1

    pdFrame = pd.DataFrame([count])

    return pdFrame

#Document * Templateからなる行列の作成
def create_input_matrix_ver3(config_templates):
    temp = []
    pdFramelist = []

    for i in range(0, len(config_templates)):
        temp.append({})

    i = 0

    for config_template in config_templates:
        for template in config_template:
            if template in temp:
                temp[i][template] = temp[i][template] + 1
                continue

            temp[i][template] = 1
        i = i + 1

     #dictionaryからPandasFrameを作成
    for i in range(0, len(temp)):
        pdFramelist.append(pd.DataFrame([temp[i]],index=[i]))

    #各フレームのpandasを連結させる
    pdFrame = pdFramelist[0]
    for i in range(1,  len(pdFramelist)):
        pdFrame = pd.concat([pdFrame, pdFramelist[i]], join='outer', sort=True)

    # Nanを0に置き換える
    pdFrame = pdFrame.fillna(0)
        
    return pdFrame

def create_input_matrix_ver4(config_templates, frame_num, freq_num):
    
    pdFramelist = []
    #各indexごとに各フレームのテンプレートとその頻度のdictionaryを格納する
    temp = []
    #分割するフレーム数
    frame = frame_num
    freq = freq_num
    #フレーム数のdictionaryを用意する
    for i in range(0,frame+1):
        temp.append({})
        
    for config_template in config_templates:
        #カウント
        count = 1
        #1フレームごとの行数
        num_per_frame = math.floor(len(config_template)/frame)

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

            #dictionaryのkeyに同じテンプレートが存在する場合
            if word in temp[i]:
                temp[i][word] = temp[i][word] + 1
                continue

            #dictionaryのkeyに存在しないテンプレートの場合
            temp[i][word] = 1

    


    count = 0
    
    #各フレーム毎に頻度を基にいくつかのパーツに分ける
    for per_frame_template in temp:

        sorted_frame_template = sorted(per_frame_template.items(), key = lambda x:x[1], reverse = True)

        sorted_dict = dict(sorted_frame_template)

        chunks = dict_chunks(sorted_dict, freq)

        #dictionaryからPandasFrameを作成(ここからやる)
        for c in chunks:
            pdFramelist.append(pd.DataFrame(c,index=[count]))
            count = count + 1

        #各フレームのpandasを連結させる
    pdFrame = pdFramelist[0]
    for i in range(1,  len(pdFramelist)):
        pdFrame = pd.concat([pdFrame, pdFramelist[i]], join='outer', sort=True)

    # Nanを0に置き換える
    pdFrame = pdFrame.fillna(0)
        
    return pdFrame
        
        
    

#コンフィグのグルーピングをする.
def template_grouping(config_templates, n_comp, version ):
    #inputを入手

    if version == 1:
        frame_num = 10
        X = create_input_matrix_ver1(config_templates, frame_num)

    elif version == 2:
        X = create_input_matrix_ver2(config_templates)

    elif version == 3:
        X = create_input_matrix_ver3(config_templates)

    elif version == 4:
        frame_num = 10
        freq_num = 3
        X = create_input_matrix_ver4(config_templates, frame_num, freq_num)

    columns = X.columns.values

    X.to_csv('input_ver2.csv')

    # X ~= WHに分解するNMFモデルを入手
    model = NMF(n_components = n_comp, init='random', random_state = 0)
    W = model.fit_transform(X)

    # Hは特徴数*テンプレートからなる行列
    H = model.components_
    H = pd.DataFrame(H)
    H.columns = columns
    

    return H

def evaluate_result(H):
    H.plot(subplots = True)

    plt.show()


#テストモジュール
load_text = load_dataset()
config_statement = process_dataset_ver2(load_text)

config_template = extract_templates(config_statement)


H = template_grouping(config_template, 15,2)
H.to_csv('output_ver4.csv')
evaluate_result(H)

