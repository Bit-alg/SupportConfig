from glob import glob

# 指定したディレクトリ内のテキストを読みこむ
def load_dataset():
    config_statement = []
    
    for file in glob('Dataset/*.txt'):
        print(file)
        with open(file, 'r') as f:
            datalist = f.readlines()
            config_statement.append(datalist)

    return config_statement

            
# 学習に不要な文字などを除外する
def process_dataset(config_statement):
    # 前処理が完了した状態のステートメント
    str_list = []
    processed_config = []
    new_str_list = []
    new_processed_config =[]
    
    #\n, !, version, 先頭にno(コンフィグの設定が有効化してないもの)などを空文字に変換する
    for row in config_statement:
        for str in row:
            str = str.replace('!','').replace('\n','').replace('end','').strip()
            if(str.find('version')>=0):
                str = str.replace(str,'')
            if(str.find('no')>=0):
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

    for row in processed_config:
        for str in row:
            str = str.split()
            new_str_list.append(str)
        new_processed_config.append(new_str_list)
            
    return new_processed_config

def process_dataset_ver2(config_statement):
     # 前処理が完了した状態のステートメント
    str_list = []
    processed_config = []
    new_str_list = []
    new_processed_config =[]
    
    #\n, !, version, 先頭にno(コンフィグの設定が有効化してないもの)などを空文字に変換する
    for row in config_statement:
        str_list  = []
        for str in row:
            str = str.replace('!','').replace('\n','').replace('end','').strip()
            if(str.find('version')>=0):
                str = str.replace(str,'')
            if(str.find('no')>=0):
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



