import re
import pandas as pd

def load_data(file_name):
    data = []
    with open(file_name, 'r') as file:
        data = file.read().split("#\n")

    if not data:
        print("File {} was unable to be read.".format(file_name))
    return data

def get_parameter_def(param_header):
    params_dict = {}
    params = param_header.split("\n")
    params_pattern = re.compile("# +(\w+) +- +(.+)")

    first_try = params
    for first_t in first_try:
        a = params_pattern.search(first_t)

        if a: 
            #print(first_t, a.group(1), a.group(2))
            params_dict[a.group(1)] = a.group(2)

    return params_dict

 
    


if __name__ == "__main__":
    file_name = "LA_Water_Quality_Data.txt"

    data = load_data(file_name)

    #  0:                               #  8: coll_ent_cd
    #  1: File created...               #  9: medium_cd
    #  2: U.S. Geological Survey        # 10: tu_id
    #  3: The data you have...          # 11: body_part_id
    #  4: To view additional...         # 12: remark_cd
    #  5: Param_id      - parameter     # 13: Data for the following sites...
    #  6: sample_start_time_datum_cd    # 14: WARNING: some preadsheet...
    #  7: tm_datum_rlbty_cd             # 15: Data!
    params_dict = get_parameter_def(data[5])
    
    
