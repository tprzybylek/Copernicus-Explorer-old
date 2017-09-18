import os, sys
import requests
import zipfile, shutil

order = '{"token":"w98jxvpd","orderedTime":1505726940806,"completedTime":"0","extent":{"minX":18.463622946292162,"maxX":18.834411520510912,"minY":54.22144910734839,"maxY":54.53180058573668},"cart":[{"ID":"d31b76a6-7894-42ed-9bf1-871f73fba2eb","title":"S1B_IW_GRDH_1SDV_20170101T045911_20170101T045940_003650_006425_45AB","Satellite":"S1B"},{"ID":"22cf4553-6051-42ca-805a-e1775aee49d9","title":"S1B_IW_GRDH_1SDV_20170111T162702_20170111T162732_003803_006895_B25A","Satellite":"S1B"}],"email":"example@example.com","status":"0"}'

def getProduct (order):

    print order

def main(order):
    getProduct(order)

if __name__ == "__main__":
    main(sys.argv[1])