import pandas as pd

#Tucker Decompositionによって得られrたテンプレート次元方向の行列をpandasにして取得
infer = pd.read_csv('infer_data.csv', header = None)

#Headerの削除
infer = infer[1:]
config_name = infer.loc[:, 0]
infer = infer.drop(0,axis = 1)

#infer ... 各コンフィグが属する特徴数の数値(相関性を示す)
#config_name ... 各テンプレートの名前を表したpandas

#以下ではinferをいじりながらconfig block numberの推論を行う.

#inferの各要素が負の値ならば0とする
infer = infer.where(infer > 0, 0)

#各テンプレートのあたいの最大値を取得
each_columns_max = infer.max(axis=1)

delta = 0.4
for i in range(len(infer.columns)):
    for j in range(len(infer)):
        #各テンプレートの行に対する最大の特徴数をXとした時にX * δを上回っているとビット1
        if infer[i+1][j+1] >= each_columns_max[j+1]*delta:
            infer[i+1][j+1] = 1
        #それ以外はビット0とする
        else:
            infer[i+1][j+1] = 0

print(infer)
