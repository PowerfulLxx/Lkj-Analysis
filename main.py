# 使用pandas对于数据进行处理
import pandas as pd
from utils.config import Config

conf = Config()
for i in conf.args:
    print(i,":",conf.args[i])


if __name__ == '__main__':
    lkjDf = pd.read_csv(conf.csv_path)
    print(lkjDf.head())