from dataset import load_dataset
from dataset import process_dataset
import math
import numpy as np
import matplotlib.pyplot as plt

#テキストファイルをもとに読み込んだコンフィグ
load_text = []

#コメントなど余分な要素を取り除いたコンフィグ
config_statement = []

#条件付き確率を求める際に頻度を数えるために使う(dict型)
pos_len = {}
word_pos_len = {}

#コンフィグのテンプレート
config_template = []

#単語の頻度を求める
def count(config_statement):
    #config_statementを空白ごとに分割してループを回して数を数える
    for row in config_statement:
        for str_list in row:
            
            length = len(str_list)
            position = 0
            
            for s in str_list:
                position = position + 1
                wpl_key = s + str(position) + str(length)
                pl_key = str(position) + str(length)

                if wpl_key in word_pos_len:
                    word_pos_len[wpl_key] = word_pos_len.get(wpl_key) + 1
                else:
                    word_pos_len[wpl_key] = 1

                if pl_key in pos_len:
                    pos_len[pl_key] = pos_len.get(pl_key) + 1
                else:
                    pos_len[pl_key] = 1
    
#各config文のスコアを算出する
def score(str_list):
    length = len(str_list)
    position = 0
    config_score = []

    for s in str_list:
        position = position + 1
        score = calc_score(s, position, length)
        config_score.append(score)

    return config_score

def calc_score(word, position, length):
    wpl = float(word_pos_len.get(word + str(position) + str(length)))
    pl = float(pos_len.get(str(position) + str(length)))
    return wpl/pl

# スコアのクラスタリングをする
# 閾値γを用意してクラスタ間の距離がγ(>=0)であるようにクラスタを分ける
def dbscan(config_score, ganma):
    cluster_labels = []
    label = 0
    n = 0
    summantion = 0
    flag = False

    for score in config_score:

        summantion = summantion + score
        n = n + 1

        # クラスタ間の閾値がγ以上の場合次の単語を新しいクラスター群として定める
        if(flag):
            label = label + 1
            flag = False
        
        #一つもクラスターがない時
        if not cluster_labels:
            cluster_labels.append(label)
            continue

        if abs(summantion/n - score) >= ganma:
            flag = True
            summantion = 0
            n = 0

        cluster_labels.append(label)
    
    return cluster_labels

def ratio_statement(config_score, cluster_label, beta):
    part_config = []
    index = math.floor(len(config_score)*beta)
    label = cluster_label[index]
    i = 0 

    #該当するクラスターラベルまでの単語をリストに格納する(ここからやる)
    for score in config_score:
        if cluster_label[i] <= label:
            part_config.append(score)
        i = i + 1

    return part_config

def extract_templates(config_statement, beta, ganma):
    #単語の頻度をカウントする
    count(config_statement)

    for row in config_statement:
        config = []
        for str_list in row:
            #configスコアとクラスターラベルの初期化をする.
            config_score = []
            cluster_labels = []
            
            #各config文のスコア化をする
            config_score = score(str_list)
            
            #コンフィグスコアの重複をなくす
            i = len(config_score)
            j = 0
            for s in config_score:
                config_score[j] = float(str(s)+str(i))
                i = i - 1
                j = j + 1

            #並べ替えた後の添字を入手する
            np_config_score = np.array(config_score)
            index = np.argsort(np_config_score)
            index = index[::-1]

            #スコアを降順にソートする
            config_score.sort(reverse=True)

            #クラスターのラベルを取得する
            cluster_labels = dbscan(config_score, ganma)

            #コンフィグスコア配列のβ%の取得
            temp = ratio_statement(config_score, cluster_labels, beta)

            #β%分のコンフィグを入手
            k = 0
            word = ""
            for c in temp:
                word = word  +" "+ str_list[index[k]] 
                k = k + 1

            #コンフィグを配列に保存
            config.append(word)

        #各テキストファイルのコンフィグを配列に追加
        config_template.append(config)
        
    return config_template

def plot_evaluation(config_statement):
    #テンプレートに失敗した単語数
    data_y = []
    #パラメータΓの範囲
    data_x = []
    temp = []

    for i in range(2,6,1):
        beta = i * 0.1

        for j in range(5,0,-1):
            count = 0
            ganma = pow(10, -i)
            data_x.append(ganma)
            config_templates = extract_templates(config_statement, beta, ganma)

            for config_template in config_templates:
                for word_list in config_template:
                    for word in word_list:
                        if word.isdigit():
                            count = count + 1
            temp.append(count)
        data_y.append(temp)

    plt.plot(data_x, data_y[2], color = 'red')
    plt.plot(data_x, data_y[3], color = 'blue')

    plt.show()

                    
            
load_text = load_dataset()
config_statement = process_dataset(load_text)
#plot_evaluation(config_statement)

config_template = extract_templates(config_statement, 0.4, 0.0015)
print(config_template)


