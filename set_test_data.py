from dataset import load_dataset
from dataset import process_dataset
from extract_templates import extract_templates

def set_test_data():
    load_text = load_dataset('Dataset/Test')
    config_statement = process_dataset(load_text)

    config_template = extract_templates(config_statement)

    return config_template

print(set_test_data())
