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
            
            #IPアドレスに該当する文字列は共通して<IP>と表記する
            config_word = re.sub(r'\d+.\d+.\d+.\d+', '<IP address>', config_word)


            #インタフェースに該当する文字列は共通して<Interface>と表記する
            config_word = re.sub(r'([A-Z]|[a-z])+\d+/\d+', '<Interface>', config_word)
            #プリフィックスに該当する文字列は共通して/<Prefix>と表記する
            config_word = re.sub(r'/\d+', '/<Prefix>', config_word)

             #数字のみの単語は共通して<Int>と表記する
            config_word = config_word.split()

            #正規表現では表現が難しい文字列をここでまとめて共通の表現でまとめている
            i = 0
            for word in config_word:
                if word.isdigit():
                    config_word[i] = '<Num>'
                if word == 'route-map':
                    config_word[i+1] = '<Map-tag>'
                if word == 'hostname':
                    config_word[i+1] = '<Hostname>'
                if word == 'name':
                    config_word[i+1] = '<Name>'
                i = i + 1
            config_word = ' '.join(config_word)

            #as numberは共通して<IP address>と表記する
            config_word = re.sub(r'(as|As)\d+', '<IP address>', config_word)

            #bgpのset communityの変数は共通して<Num>:<Num>と表記する
            config_word = re.sub(r'\d+:\d+', '<Num>:<Num>',config_word)
            config_template.append(config_word)
        config_templates.append(config_template)
            

    return config_templates

