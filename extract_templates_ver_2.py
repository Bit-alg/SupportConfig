from dataset import load_dataset
from dataset import process_dataset_ver2
import re

#テキストファイルを基に読み込んだコンフィグ
load_text = []

#コメントなど余分な要素を取り除いたコンフィグ
config_statement = []

#コンフィグのテンプレート
config_template = []

#コンフィグのテンプレートを抽出する
#具体的はパラメータなどを種類毎に共通の文字列に置き換える
#そのことで一意なメッセージが出現しやすくなる
def extract_templates(config_statements):
    config_template = []
    config_templates= []
    for config_statement in config_statements:
        config_template  = []
        for config_word in config_statement:

             #数字のみの単語は共通して<Int>と表記する
            config_word = config_word.split()

            #正規表現では表現が難しい文字列をここでまとめて共通の表現でまとめている
            i = 0
            for word in config_word:
                if word.isdigit():
                    config_word[i] = '*'
                if word == 'route-map':
                    config_word[i+1] = '*'
                if word == 'hostname':
                    config_word[i+1] = '*'
                if word == 'name':
                    config_word[i+1] = '*'
                if word == 'neighbor':
                    config_word[i+1] = '*'
                if word == 'peer-group':
                    if i != len(config_word) -1:
                        config_word[i+1] = '*'
                if word == 'Interface' or  word == 'interface':
                    config_word[i+1] = '*'
                if word == 'pid':
                    config_word[i+1] = '*'
                if word == 'sn':
                    config_word[i+1] = '*'
                i = i + 1
            config_word = ' '.join(config_word)
            
            #IPアドレスに該当する文字列は共通して<IP>と表記する
            config_word = re.sub(r'\d+.\d+.\d+.\d+', '*', config_word)

            #プリフィックスに該当する文字列は共通して/<Prefix>と表記する
            config_word = re.sub(r'/\d+', '/*', config_word)

            #bgpのset communityの変数は共通して<Num>:<Num>と表記する
            config_word = re.sub(r'\d+:\d+', '*',config_word)
            
            config_template.append(config_word)
        config_templates.append(config_template)


            

    return config_templates



