chunk_size = 10*1024
i=1
file_name=[]
with open("ten61.txt","rb") as fp:
    while i:
        read_data = fp.read(chunk_size)
        if not read_data:
            break # done
        with open(f"temp{i}.txt","wb") as f:
            file_name.append(f"temp{i}.txt")
            f.write(read_data)
        i=i+1


with open('merged_file.txt', 'wb') as outfile:
    for fname in file_name:
        with open(fname,"rb") as infile:
            outfile.write(infile.read())
