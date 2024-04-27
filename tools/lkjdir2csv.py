import csv
from lkjutil.decoder import ex_lkj
import sys
import os

lkj_dir = sys.argv[1]
#lkj_path = sys.argv[1]
input_output_pair = []
for root, dirs, files in os.walk(lkj_dir):
    for file in files:
        #input_path = os.path.join(root, file)
        #output_path = input_path + '.csvFile'
        if not file.endswith('.csvFile'):
            input_output_pair.append((root, file))
#output_csv_path = sys.argv[2]

for root, input_file in input_output_pair:

    lkj_header, lkj_records = ex_lkj(os.path.join(root, input_file), is_html=False)

    print(lkj_header)

    if lkj_header == None:
        print('error: ' + os.path.join(root, input_file))
        continue

    save_path = os.path.join(root, lkj_header.train_name + '_' + lkj_header.train_checi + '_' + input_file + '.csvFile')

    with open(save_path, 'w', encoding='utf-8') as fout:
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
