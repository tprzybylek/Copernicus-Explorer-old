bbXYs = [[13.8932, 50.9964], [14.1898, 50.9964], [14.1898, 50.8977], [13.8932,50.8977], [13.713160,50.927328], [13.943002,50.927328], [13.943020,50.822501], [13.713167,50.822498]]

originXY = [12.0767, 52.0816]

xPixelSize = 0.000121607
yPixelSize = -0.000121607

xPixelCount = 34510.0
yPixelCount = 15697.0

def getColRow(XY):
    x = XY[0]
    y = XY[1]

    col = int((x - originXY[0])/xPixelSize)
    row = int((y - originXY[1])/yPixelSize)

    print '[%s, %s] [%s, %s]' % (x, y, col, row)

for i in bbXYs:
    getColRow(i)

