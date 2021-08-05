from dataset import load_dataset
from dataset import process_dataset
import math

#コンフィグのステートメント
load_text = []
config_statement = []

#条件付き確率を求める際に頻度を数えるために使う(dict型)
pos_len = {}
word_pos_len = {}

#スコアと単語を対応させる
word_to_score = {}

config_score = []
cluster_labels = []
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

        if score - temp_score >= ganma:
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
    temp = []

    for row in config_statement:
        for str_list in row:
            #configスコアとクラスターラベルの初期化をする.
            config_score = []
            cluster_labels = []
            
            #各config文のスコア化をする
            config_score = score(str_list)

            #スコアと単語を1対1で対応づけておく

            #スコアを降順にソートする
            config_score.sort(reverse=True)

            cluster_labels = dbscan(config_score, 10)

            temp.append(ratio_statement(config_score, cluster_labels, 0.4))

            #part_configをfor文で回して各スコアを単語に戻す.
        config_template.append(temp)
    
            
load_text = load_dataset()
config_statement = process_dataset(load_text)

extract_templates(config_statement)


