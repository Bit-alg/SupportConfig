from dataset import load_dataset
from dataset import process_dataset_ver2
from extract_templates_ver_2 import extract_templates
import math
import pandas as pd
from sklearn.decomposition import NMF

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

def create_input_matrix_ver2(config_templates):
    print("2パターン目の入力する行列を作成する")

#コンフィグのグルーピングをする.
def template_grouping(config_templates, frame_num, n_comp):
    #inputを入手
    X = create_input_matrix_ver1(config_templates, frame_num)
    columns = X.columns.values

    # X ~= WHに分解するNMFモデルを入手
    model = NMF(n_components = n_comp, init='random', random_state = 0)
    W = model.fit_transform(X)

    # Hは特徴数*テンプレートからなる行列
    H = model.components_
    H = pd.DataFrame(H)
    H.columns = columns
    

    return H


#テストモジュール
load_text = load_dataset()
config_statement = process_dataset_ver2(load_text)

config_template = extract_templates(config_statement)
X = create_input_matrix_ver1(config_template, 8)
print(X.columns.values)
X.to_csv('input.csv')

H = template_grouping(config_template, 8, 5)

print(H)
