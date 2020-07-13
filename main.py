import cv2
import os
import rule


def toBinaryImage(img):
    """
    function write to covert from RGB to Binary Image
    :param path: path to image
    :return: a binary image
    """
    #scale image
    ratio = 55 / img.shape[1]
    width = int(img.shape[1] * ratio)
    height = int(img.shape[0] * ratio)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    # to gray and reduce noise
    img_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_grayscale = cv2.GaussianBlur(img_grayscale, (1, 1), 0)
    # to binary img
    ret3, img_binary = cv2.threshold(img_grayscale, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # show binary img
    '''
    cv2.imshow("img", img_binary)
    cv2.waitKey()
    cv2.destroyAllWindows()
    '''
    # to 0 1
    img_binary[img_binary > 0] = 1
    return img_binary


def findBorder(img):
    """
    function write to find the bouding of number
    :param img: a binary image, which have a number
    :return: (left, right, top, bottom) are bouding of number
    """
    numRow = len(img)
    numColumn = len(img[0])
    left = -1
    for i in range(numColumn):
        for j in range(numRow):
            if img[j][i] == 0:
                left = i
                break
        if left != -1:
            break
    right = -1
    for i in range(numColumn-1, -1, -1):
        for j in range(numRow):
            if img[j][i] == 0:
                right = i
                break
        if right != -1:
            break
    top = -1
    for i in range(numRow):
        for j in range(numColumn):
            if img[i][j] == 0:
                top = i
                break
        if top != -1:
            break
    bottom = -1
    for i in range(numRow - 1, -1, -1):
        for j in range(numColumn):
            if img[i][j] == 0:
                bottom = i
                break
        if bottom != -1:
            break
    return left, right, top , bottom


def scanImg(left, right, top, bottom, img):
    """
    function is wrote to appply my algorithm
    """
    centerX = (left + right) // 2
    leftCenterX = (centerX - left) // 2 + left
    rightCenterX = (right - centerX) // 2 + centerX
    countCX = 0
    countL = 0
    countR = 0
    positionX = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1], [1, -1, -1]]
    for i in range(top, bottom + 1, 1):
        if img[i][rightCenterX] == 0 and (i == len(img) - 1 or img[i + 1][rightCenterX] == 1):
            if countR < 4:
                positionX[countR][2] = i
            countR += 1
        if img[i][centerX] == 0 and (i == len(img) - 1 or img[i + 1][centerX] == 1):
            if countCX < 4:
                positionX[countCX][1] = i
            countCX += 1
        if img[i][leftCenterX] == 0 and (i == len(img) - 1 or img[i + 1][leftCenterX] == 1):
            if countL < 4:
                positionX[countL][0] = i
            countL += 1

    centerY = (top + bottom) // 2
    bottomCenterY = (bottom - centerY) // 2 + centerY
    topCenterY = (centerY - top) // 2 + top
    countCY = 0
    countT = 0
    countB = 0
    positionY = [[-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1]]
    for i in range(left, right + 1, 1):
        if img[topCenterY][i] == 0 and (i == len(img[0]) - 1 or img[topCenterY][i + 1] == 1):
            if countT < 4:
                positionY[0][countT] = i
            countT += 1
        if img[centerY][i] == 0 and (i == len(img[0]) - 1 or img[centerY][i + 1] == 1):
            if countCY < 4:
                positionY[1][countCY] = i
            countCY += 1
        if img[bottomCenterY][i] == 0 and (i == len(img[0]) - 1 or img[bottomCenterY][i + 1] == 1):
            if countB < 4:
                positionY[2][countB] = i
            countB += 1
    return (countL, countCX, countR), (countT, countCY, countB), positionX, positionY


def predictAgain(predictAns, scanData, left, right, top, bottom):
    """
    if there are a lot of answer were predict, reduce them
    """
    # some rule to increase confidence
    if scanData[1][2] == 1:
        if scanData[3][2][0] > (right - left) // 2 + left:
            try:
                predictAns.remove(2)
            except ValueError:
                pass
        else:
            try:
                predictAns.remove(9)
            except ValueError:
                pass
    if scanData[1][1] == 1:
        if scanData[3][1][0] < right - 5:
            try:
                predictAns.remove(4)
            except ValueError:
                pass
        else:
            try:
                predictAns.remove(1)
            except ValueError:
                pass
    if scanData[1][0] == 1:
        if scanData[3][0][0] < (right - left) // 2 + left:
            try:
                predictAns.remove(3)
            except ValueError:
                pass
        else:
            try:
                predictAns.remove(5)
            except ValueError:
                pass


if __name__ == "__main__":
    listImg = os.listdir("testcase")
    for path in listImg:
        originImg = cv2.imread("testcase/" + path)
        img = toBinaryImage(originImg)
        left, right, top, bottom = findBorder(img)
        scanData = scanImg(left, right, top, bottom, img)
        print("Procesing--- : ", path)
        #print(scanData)
        predictAns = []
        for index, item in enumerate(rule.DATA):
            if scanData[0] in item[0] and scanData[1] in item[1]:
                predictAns.append(index)
        if len(predictAns) > 1:
            predictAgain(predictAns, scanData, left, right, top, bottom)
            #cv2.imwrite("Answer/" + str(ans) + "/" + path, originImg)
        if len(predictAns) == 0:
            print("Fail to predict")
        else:
            print("Predict: ", predictAns)


