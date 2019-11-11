wf = open("final.jpg", "wb")
for i in range(10):
    with open(f"chunk{i}.chunk", "rb") as f:
        wf.write(f.read())
wf.close()
