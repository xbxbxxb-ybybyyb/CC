import os

read_path = 'A://weiyc//data//EAST//'
write_path = 'A://weiyc//for_gzj//EASTMONEY//'

file_list = [os.path.join(read_path, i) for i in os.listdir(read_path)]

for file in file_list:
    print(file + '*'*50)
    for line in open(file,"r"):
        print(line)
        line = line[:-1]
        contents = line.split('|')
        date = contents[-1][:10]
        with open(write_path + date.replace('-',''), 'a+') as f:  # 设置文件对象
            f.writelines(contents[-1] + '|' + contents[0].split(',')[1] + '|' + contents[1] +'\n')
