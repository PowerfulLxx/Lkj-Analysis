# 使用pandas对于数据进行处理
import pandas as pd
from utils.config import Config
from utils import airBrakeTest

conf = Config()
for i in conf.args:
    print(i,":",conf.args[i])


if __name__ == '__main__':
    lkj_df = pd.read_csv(conf.csv_path)
    # 将列控监数据中 时间改为pandas时间
    # print(lkj_df.head())

    lkj_df['时间'] = pd.to_datetime(lkj_df['时间'])
    # print(lkj_df.head())
    # 开车对标 事件
    start_button_index = lkj_df[lkj_df['事件'] == '开车对标'].index.item()
    info_before_start = lkj_df.iloc[:start_button_index + 1]
    
    # 判断是否存在始发站制动机未试验
    if airBrakeTest.brakeTestAtDeparture(info_before_start):
        print('不存在始发站制动机未试验')
    else:
        # 将这个信息以及对应违规操作添加到LkjItem()
        print('存在始发站制动机未试验')

    print(info_before_start.tail())