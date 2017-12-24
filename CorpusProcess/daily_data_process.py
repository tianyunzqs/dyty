# -*- coding: utf-8 -*-

fout = open("E:/dyty_set_data/seg_word_crf.txt", "w+", encoding="utf-8")


def get_sample(text):
    te = text.split()
    words_list = list()
    for tt in te:
        w_p = tt.split("/", 1)
        if len(w_p) == 1:
            continue
        if w_p[0] == "" and "/" in w_p[1]:
            w_p[0] = "/"
            w_p[1] = w_p[1][1:]
        if "[" in w_p[0]:
            w_p[0] = w_p[0].replace("[", "")
        if "]" in w_p[1]:
            w_p[1] = w_p[1][:w_p[1].index("]")]

        words_list.append(w_p[0])
    return words_list


def get_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        hang = 0
        for line in lines:
            line = line.strip()
            hang += 1
            print(hang)
            words = get_sample(line)
            for word in words:
                if len(word) == 1:
                    fout.write(word + "\t" + "O" + "\n")
                else:
                    for i in range(len(word)):
                        if i == 0:
                            fout.write(word[i] + "\t" + "B" + "\n")
                        else:
                            fout.write(word[i] + "\t" + "I" + "\n")
            fout.write("\n")
                    
                    
if __name__ == '__main__':
    get_file("E:/dyty_set_data/people_daily2014.txt")
    # text = "[交通/n 安全/an]/nz"
    # ttt, name_list = get_sample(text)
    # print(ttt)
    # print(name_list)

