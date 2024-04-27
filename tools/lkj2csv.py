import csv
from lkjutil.decoder import ex_lkj
import sys

lkj_path = sys.argv[1]
output_csv_path = sys.argv[2]
lkj_header, lkj_records = ex_lkj(lkj_path, is_html=False)

print('routing_id,train_name,train_checi,main_driver_id,sub_driver_id,passenger,pusher_engine,start_time,end_time,ic_copy_num')
print(lkj_header)
print(lkj_header.routing_id)

with open(output_csv_path, 'w', encoding='utf-8') as fout:
    csv_writer = csv.writer(fout)
    csv_writer.writerow(["时间", "事件", "交路id", "公里标", "距离", "信号", "信号机", "信号类型", "速度", "限速", "工况", "管压", "缸压", "转速/电流", "均缸1", "均缸2", "其他"])

    for lkj_record in lkj_records:
        items = [str(lkj_record.timestamp), lkj_record.event, lkj_record.routing_id, lkj_record.mileage,
                 lkj_record.distance,
                 lkj_record.signal_color, lkj_record.signal_id, lkj_record.signal_type,
                 lkj_record.speed, lkj_record.speed_limit, lkj_record.locomotive_status,
                 lkj_record.pipe_pressure, lkj_record.cylinder_pressure, lkj_record.rotate_speed,
                 lkj_record.equalizing_cylinder_1, lkj_record.equalizing_cylinder_2, lkj_record.others]
        csv_writer.writerow(items)

