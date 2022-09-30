import os
import time




def main():
    k_width = 1920 / 4096
    k_height = 1080 / 2160
    for file_name in os.listdir('./yolo_points2/'):
        with open(f'./yolo_points2/{file_name}') as file:
            res = []
            for line in file:
                lst = ''
                for word in line.split()[:1]:
                    lst += word
                j = 0
                for word in line.split()[1:]:
                    if j % 2 == 0:
                        lst += ' ' + str(float(word) * k_width)
                    else:
                        lst += ' ' + str(float(word) * k_height)
                    j += 1
                lst += '\n'
                res.append(lst)
            with open(f'./yolo_points2/{file_name}', 'w') as filehandle:
                for listitem in res:
                    filehandle.write(listitem)
       
if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
