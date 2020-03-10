def string_to_2d_int_array(string, end):
    temp = []
    result = []
    for word in string.split(','):
        word = word.replace('[', '')
        word = word.replace(']', '')
        word = word.replace('(', '')
        word = word.replace(')', '')
        if word != '':
            temp.append(int(word))
    for i in range(0,len(temp),end):
        result.append((temp[i:i+end]))
    return result

def string_to_2d_float_array(string, end):
    temp = []
    result = []
    for word in string.split(','):
        word = word.replace('[', '')
        word = word.replace(']', '')
        word = word.replace('(', '')
        word = word.replace(')', '')
        temp.append(float(word))
    for i in range(0,len(temp),end):
        result.append((temp[i:i+end]))
    return result

def v_strip_2d_array(array, column):
    """ Removes a specific column from an temp """
    result = []
    for y in range(len(array)):
        result.append(array[y][:column])
    return result  

def string_to_int_array(string):
    result = []
    for word in string.split(','):
        word = word.replace('(', '')
        word = word.replace(')', '')
        word = word.replace('[', '')
        word = word.replace(']', '')
        result.append(int(word))
    return result

def div_non_zero(numerator, denominator):
    if denominator != 0:
        return numerator / denominator
    else:
        return 0

def map(value, left_min, left_max, right_min, right_max):
    left = float(left_max) - float(left_min)
    right = right_max - right_min
    value_scaled = div_non_zero(float(value - left_min), float(left)) # Convert left range into a 0-1 range
    mapped_value =  right_min + (value_scaled * right) # Convert 0-1 range into right range
    if mapped_value > right_max:
        mapped_value = right_max
    elif mapped_value < right_min:
        mapped_value = right_min
    return mapped_value

def convert_to_int_array(array):
    result = []
    for element in array:
        result.append(int(element))
    return result