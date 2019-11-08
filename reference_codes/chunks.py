#!/usr/bin/python3

chunk_size = 1024*1024
no_of_files = 1
chunks_name = "image_chunks_"

with open("image1.jpg", "rb") as fp1 :
    read_data = fp1.read(chunk_size)
    while read_data :
        with open(f"{chunks_name}{str(no_of_files)}.jpg", "wb") as fp2 :
            fp2.write(read_data)
        read_data = fp1.read(chunk_size)
        no_of_files = no_of_files + 1
