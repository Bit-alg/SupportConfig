from set_train_data import set_train_data
from set_test_data import set_test_data

# リスト化されたトレインデータを比較しやすいように文字列として扱う
def train_data_to_str(train_data):
    str_train_data = []

    for conf_file in train_data:
        for block in conf_file:
            s = ""
            for config in block:
                s = s + config + "\n"
            str_train_data.append(s)

    return str_train_data

# リスト化されたテストデータを比較しやすいように文字列として扱う
def test_data_to_str(test_data):
    str_test_data = []

    for t in test_data:
        s = ""
        for config in t:
            s = s + config + "\n"

        str_test_data.append(s)


    return str_test_data

# 抽出したコンフィグブロックがどの程度テストデータと一致しているかを計算する
def calc_acc():
    train_data = set_train_data()
    test_data = set_test_data()

    str_train_data = train_data_to_str(train_data)
    str_test_data = test_data_to_str(test_data)

    # コンフィグブロックが何個一致したかをカウントする.
    count = 0

    for tr in str_train_data:
        for te in str_test_data:
            if tr in te:
                count = count + 1
                break

    print("精度: " + str(float(float(count)/float(len(str_train_data)))))

#-----main----
calc_acc()
        
