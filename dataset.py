from glob import glob

# 指定したディレクトリ内のテキストを読みこむ
def load_dataset(path):
    config_statement = []
    
    for file in glob(path + '/*.txt'):
        print(file)
        with open(file, 'r') as f:
            datalist = f.readlines()
            config_statement.append(datalist)

    return config_statement

def process_dataset(config_statement):
     # 前処理が完了した状態のステートメント
    str_list = []
    processed_config = []
    new_str_list = []
    new_processed_config =[]
    
    #\n, !, version, などを空文字に変換する
    for row in config_statement:
        str_list  = []
        for str in row:
            str = str.replace('!','').replace('\n','').replace('end','').strip()
            if(str.find('version')>=0):
                str = str.replace(str,'')
            str_list.append(str)
        processed_config.append(str_list)

    ## 空文字をリストから消し去る(以下に記述する)
    for str in processed_config:
        while(True):
            try:
                index = str.index('')
                del str[index]
            except ValueError:
                break

            
    return processed_config

