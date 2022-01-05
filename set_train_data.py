from dataset import load_dataset
from dataset import process_dataset
from extract_templates import extract_templates
import pandas as pd
import numpy as np
from config_templates_grouping import template_grouping_NMF
from config_templates_grouping import template_grouping_Tucker
import warnings

warnings.simplefilter('ignore')


# Trainデータの形に整えたcsvを取得
def setTrainDataFrame(config_templates, output_matrix, method):

    train_dataFrame = []
    output_matrix_temp = []

    if method == "NMF":
        output_matrix_temp = (output_matrix.T).copy()
    elif method == "Tucker":
        output_matrix_temp = output_matrix.copy()
    
    for config_template in config_templates:

        train_dataFrame.append(output_matrix_temp.loc[config_template,:])


    return train_dataFrame

def get_candidate_template_block_number(train_dataFrame, delta):

    temp_train_dataFrame = []

    for dataFrame in train_dataFrame:
        dataFrame = dataFrame.where(dataFrame > 0, 0)

        each_columns_max = dataFrame.max(axis = 1)

        for i in range(len(dataFrame.columns)):
            for j in range(len(dataFrame)):
                if dataFrame[i][j] >= each_columns_max[j]*delta:
                    dataFrame[i][j] = 1
                else:
                    dataFrame[i][j] = 0
        temp_train_dataFrame.append(dataFrame)

    return temp_train_dataFrame

def get_key(val, my_dict):
    for key, value in my_dict.items():
        if val == value:
            return key

    return -1

def get_index_max_sequence(l):

    start_temp = 0
    final = False
    index_and_length = {}

    if l[0] == 1:
        start_temp = -1

    for i in range(len(l)):
        if l[i+1] == 1 and l[i] == 0:
            start_temp = i
            
            if final:
                index_and_length[i+1] = 1

        elif l[i+1] == 0 and l[i] == 1:
            index_and_length[start_temp + 1] = (i+1) - start_temp - 1

        if final:
            break

        if i == len(l) - 3:
            final = True

    if l[-1] == 1:
        index_and_length[start_temp + 1] = (len(l)) - start_temp - 1


    length = max(index_and_length.values())
    start_index = get_key(length, index_and_length)
        

    return start_index, length

def get_template_block(train_dataFrame):

    template_block = []

    for dataFrame in train_dataFrame:

        template_list = list(dataFrame.T)
        temp_block = []

        for i in range(len(dataFrame.columns)):
            temp = []
            temp_list = list(dataFrame[i])

            start_index, length = get_index_max_sequence(temp_list)

            for j in range(start_index, start_index + length):
                temp.append(template_list[j])
            
            temp_block.append(temp)

        template_block.append(temp_block)

    return template_block


def set_train_data(method = "Tucker"):
    load_text = load_dataset('Dataset/Train')
    config_statement = process_dataset(load_text)

    config_template = extract_templates(config_statement)

    train_dataFrame = []

    if method == "NMF":
        output_matrix = template_grouping_NMF(config_template, 10, 5)
        train_dataFrame = setTrainDataFrame(config_template,output_matrix,"NMF")
        
    elif method == "Tucker":
        output_matrix = template_grouping_Tucker(config_template, 3, 5, 5, 5, 5)
        train_dataFrame = setTrainDataFrame(config_template,output_matrix,"Tucker")

    train_dataFrame = get_candidate_template_block_number(train_dataFrame, 0.4)

    template_block = get_template_block(train_dataFrame)

    return template_block

    

    
    

#---main-----
print(set_train_data())







