empty_dict = {}
with open("../template/template.txt") as f:
    lines = f.readlines()
    count = 0
    for line in lines:
        dictionary = {}
        if line[0] == "&":
            print("{}".format(str(count), line.strip()))
            count += 1 