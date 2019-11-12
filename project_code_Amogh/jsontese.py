import json

data_info={'a.txt': { 'P': {'ch1': [1, 2, 3, 4], 'ch2': [5, 6, 7]},'S' : {'ch1': [1, 2, 3, 4], 'ch2': [5, 6, 7]}}, 'b.txt':{'P':{'ch1': [23, 34]},'S':{'ch1': [23, 34]}},'c.txt':{'P':{'ch4':[1,4,3,2],'ch7':[5,6,7,8,9],'ch3':[10,11,12,13]},'S':{'ch4':[1,4,3,2],'ch7':[5,6,7,8,9],'ch3':[10,11,12,13]}}}
chunk_info={'a.txt':[1,2,3,4,5,6,7],'b.txt':[1,2,3,4,5,6]}
size_info={'a.txt':123456,'b.txt':5672387}

with open('data.json', 'w') as outfile:
    json.dump(data_info, outfile)
with open('chunkinfo.txt', 'w') as outfile:
    json.dump(chunk_info, outfile)
with open('sizeinfo.txt', 'w') as outfile:
    json.dump(size_info, outfile)


json_file=open('data.json','r')
data1 = json.load(json_file)
for p in data1['a.txt']['P']:
    print('Chunk Name: ' + p)
    print(data1['a.txt']['P'][p])
    print('')
json_file.close()