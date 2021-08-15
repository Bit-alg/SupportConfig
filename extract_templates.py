from dataset import load_dataset
from dataset import process_dataset
import math
import numpy as np

#コンフィグのステートメント
load_text = []
config_statement = []

#条件付き確率を求める際に頻度を数えるために使う(dict型)
pos_len = {}
word_pos_len = {}

config_template = []


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
    
#各config文のスコアを算出する(listを返す)
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

# betaとganmaはdbscanの閾値.
def dbscan(config_score, ganma):
    cluster_labels = []
    label = 0

    for score in config_score:
        if not cluster_labels:
            cluster_labels.append(label)
            temp_score = score
            continue

        if abs(score - temp_score) >= ganma:
            label = label + 1

        cluster_labels.append(label)
        temp_score = score
    
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

def extract_templates(config_statement):
    count(config_statement)
    flag = 0

    for row in config_statement:
        config = []
        for str_list in row:
            if flag == 1:
                break
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


            cluster_labels = dbscan(config_score, 0.015)

            temp = ratio_statement(config_score, cluster_labels, 0.4)

            k = 0
            word = ""
            #β%分のコンフィグを入手
            for c in temp:
                word = word  +" "+ str_list[index[k]] 
                k = k + 1
            
            config.append(word)

            #part_configをfor文で回して各スコアを単語に戻す.
        config_template.append(config)
    return config_template

def plot_evaluation(config_template):
    print("コンフィグのテンプレート化の評価をする")
            
load_text = load_dataset()
config_statement = process_dataset(load_text)

config_template = extract_templates(config_statement)
print(config_template)


