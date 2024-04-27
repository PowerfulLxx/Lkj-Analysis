class LKJITEMS(object):
    def __init__(self, item_name, timestamp, details={}):
        self.item_name = item_name
        self.timestamp = timestamp
        self.details = details

    def __str__(self):
        items = [self.item_name, self.timestamp, self.details]
        return ','.join([str(n) for n in items])


SEQUENCE = ["绿灯", "绿黄", "黄灯", "黄2", "红黄", "双黄", "红灯", "白灯"]


def disconnection_pressure_unreserved(lkj_record, in_station_flag, pull_over_flag, shunt_flag,
                                      disconnection_pressure_unreserved_params, ans):
    if in_station_flag and pull_over_flag == 0 and shunt_flag:
        if lkj_record.pipe_pressure < disconnection_pressure_unreserved_params[0] and \
                disconnection_pressure_unreserved_params[2] == 0:
            disconnection_pressure_unreserved_params[0] = lkj_record.pipe_pressure
            disconnection_pressure_unreserved_params[1] = lkj_record.timestamp
        elif (lkj_record.timestamp - disconnection_pressure_unreserved_params[1]).total_seconds() > 10 and \
                disconnection_pressure_unreserved_params[2] == 0:
            ans.append(LKJITEMS("摘解未保压", lkj_record.timestamp))
            disconnection_pressure_unreserved_params[2] = 1
        if lkj_record.event == "进入调车":
            disconnection_pressure_unreserved_params[0] = lkj_record.pipe_pressure
            disconnection_pressure_unreserved_params[1] = lkj_record.timestamp
            disconnection_pressure_unreserved_params[2] = 0


def coupling_pull_over(lkj_record, departure_flag, last_2_stops, changing_condition, ans):
    if lkj_record.event == "开车对标":
        if abs(last_2_stops[0][0] - last_2_stops[1][0]) > 50 or abs(last_2_stops[0][0] - last_2_stops[1][0]) < 10:
            ans.append(
                LKJITEMS("连挂前无一度停车", lkj_record.timestamp, "两次停车距离为:{}".format(abs(last_2_stops[0][0] - last_2_stops[1][0]))))
        if last_2_stops[0][1] == 1:
            ans.append(LKJITEMS("连挂超速"))
        if changing_condition[0] == 1:
            ans.append(LKJITEMS("连挂后拉钩试验", lkj_record.timestamp, changing_condition[1]))
    if departure_flag == 0:
        if lkj_record.event == "停车":
            last_2_stops[0] = last_2_stops[1]
            last_2_stops[1] = [lkj_record.distance, 0]
            changing_condition[0] = 0
            changing_condition[1] = ""
        if lkj_record.speed:
            if lkj_record.speed > 5:
                last_2_stops[1][1] == 1
        if lkj_record.event == "机车工况变化":
            if changing_condition[0] == 0:
                changing_condition[0] = 1
                changing_condition[1] += lkj_record.locomotive_status
            elif changing_condition[0] == 1:
                changing_condition[1] += "->" + lkj_record.locomotive_status


def penetration_trial(lkj_record, penetr_params, delta_pull_over, ans):
    if delta_pull_over//60 >= 20:
        if penetr_params[1] == 0 and lkj_record.speed > 40:
            penetr_params[1] = 1
        if penetr_params[1] == 1:
            if penetr_params[2] > lkj_record.speed:
                penetr_params[3] += penetr_params[2] - lkj_record.speed
            elif penetr_params[2] < lkj_record.speed:
                penetr_params[3] = 0
            if penetr_params[4] > lkj_record.pipe_pressure:
                penetr_params[5] += penetr_params[4] - lkj_record.pipe_pressure
            elif penetr_params[4] < lkj_record.pipe_pressure:
                penetr_params[5] = 0
            penetr_params[2] = lkj_record.speed
            penetr_params[4] = lkj_record.pipe_pressure
            if penetr_params[3] >= 5 and penetr_params[5] >= 50:
                for i in range(len(penetr_params)):
                    penetr_params[i] = 0
            if lkj_record.event == "停车":
                ans.append(LKJITEMS("贯通试验违标", lkj_record.timestamp))


def zero_pressure(lkj_record, ans):
    if lkj_record.speed and lkj_record.pipe_pressure:
        if lkj_record.speed > 0 and lkj_record.pipe_pressure < 200:
            ans.append(LKJITEMS("管压为0", lkj_record.timestamp))


def before_departure_brake(lkj_record, before_departure_brake_params, departure_flag, ans):
    if lkj_record.event == "开车对标":
        if before_departure_brake_params[0] == 0:
            ans.append(LKJITEMS("始发站制动机未试验", lkj_record.timestamp))
    if departure_flag == 0:
        if before_departure_brake_params[0] == 0 and lkj_record.pipe_pressure:
            if before_departure_brake_params[2] < lkj_record.pipe_pressure and before_departure_brake_params[3] + lkj_record.pipe_pressure - before_departure_brake_params[2] > -100:
                before_departure_brake_params[3] = 0
                if before_departure_brake_params[1] and (lkj_record.timestamp - before_departure_brake_params[1]).total_seconds() >= 60:
                    before_departure_brake_params[0] = 1
                before_departure_brake_params[1] = lkj_record.timestamp
            else:
                before_departure_brake_params[3] += lkj_record.pipe_pressure - before_departure_brake_params[2]
            before_departure_brake_params[2] = lkj_record.pipe_pressure


def first_in_brake(lkj_record, first_in_params, departure_flag, in_station_flag, temp_limit_flag, ans):
    if departure_flag == 1:
        if in_station_flag == 1 and first_in_params[4] == 0:
            if first_in_params[3] == 0:
                ans.append(LKJITEMS("第一停车站前未试闸", lkj_record.timestamp))
            first_in_params[4] = 1
        if temp_limit_flag == 1 and first_in_params[4] == 0 and first_in_params[5] == 0:
            if first_in_params[3] == 0:
                ans.append(LKJITEMS("第一临时限速点前未试闸", lkj_record.timestamp))
            first_in_params[5] = 1
        if first_in_params[4] == 0 and first_in_params[5] == 0 and in_station_flag == 0 and temp_limit_flag == 0 and first_in_params[3] == 0 and lkj_record.pipe_pressure:
            if first_in_params[0] < lkj_record.pipe_pressure and first_in_params[1] == 0:
                {}
            else:
                first_in_params[1] += first_in_params[0] - lkj_record.pipe_pressure
                if first_in_params[1] <= -50:
                    first_in_params[2] = 1
                elif first_in_params[1] >= 0:
                    if first_in_params[2] == 1:
                        first_in_params[3] = 1
                    else:
                        first_in_params[1] = 0
            first_in_params[0] = lkj_record.pipe_pressure


def long_pull_over(lkj_record, long_pull_over_params, pull_over_flag, delta_pull_over, ans):
    if pull_over_flag[0] == 0:
        if long_pull_over_params[0] == 0 and lkj_record.pipe_pressure:
            if lkj_record.pipe_pressure - long_pull_over_params[1] + long_pull_over_params[2] >= 0:
                long_pull_over_params[1] = lkj_record.pipe_pressure
                long_pull_over_params[2] = 0
                long_pull_over_params[4] = lkj_record.timestamp
                if long_pull_over_params[3] == 1 and (lkj_record.timestamp - long_pull_over_params[4]).total_seconds() >= 60:
                    long_pull_over_params[0] = 1
                else:
                    long_pull_over_params[3] = 0
            else:
                long_pull_over_params[2] += lkj_record.pipe_pressure - long_pull_over_params[1]
                long_pull_over_params[1] = lkj_record.pipe_pressure
                if long_pull_over_params[2] <= -100:
                    long_pull_over_params[3] = 1
    if lkj_record.event == "开车":
        if long_pull_over_params[0] == 0 and delta_pull_over >= 1200:
            ans.append(LKJITEMS("停车超20分钟未简略试验", lkj_record.timestamp))
        for i in range(len(long_pull_over_params)):
            long_pull_over_params[i] = 0


def station_shunt(lkj_record, station_shunt_params, in_station_flag, pull_over_flag, shunt_flag, ans):
    if in_station_flag == 1 and pull_over_flag[0] == 0:
        if shunt_flag == 0:
            if station_shunt_params[0] == 0 and lkj_record.pipe_pressure:
                if lkj_record.pipe_pressure - station_shunt_params[1] + station_shunt_params[2] >= 0:
                    station_shunt_params[1] = lkj_record.pipe_pressure
                    station_shunt_params[2] = 0
                    station_shunt_params[4] = lkj_record.timestamp
                    if station_shunt_params[3] == 1 and (lkj_record.timestamp - station_shunt_params[4]).total_seconds() >= 60:
                        station_shunt_params[0] = 1
                    else:
                        station_shunt_params[3] = 0
                else:
                    station_shunt_params[2] += lkj_record.pipe_pressure - station_shunt_params[1]
                    station_shunt_params[1] = lkj_record.pipe_pressure
                    if station_shunt_params[2] <= -100:
                        station_shunt_params[3] = 1
        if lkj_record.event == "退出调车":
            if station_shunt_params[0] == 0:
                ans.append(LKJITEMS("中间站本务机调车结束未简略试验", lkj_record.timestamp))
            for i in range(len(station_shunt_params)):
                station_shunt_params[i] = 0


def insufficient_decompress(lkj_record, insufficient_decompress_params, ans):
    if lkj_record.pipe_pressure:
        if lkj_record.pipe_pressure >= 600:
            insufficient_decompress_params[0] = lkj_record.timestamp
        elif lkj_record.pipe_pressure < 600 and lkj_record.pipe_pressure > 550:
            if insufficient_decompress_params[0] and (lkj_record.timestamp - insufficient_decompress_params[0]).total_seconds() >= 5:
                ans.append(LKJITEMS("初减压不足", lkj_record.timestamp))
        else:
            insufficient_decompress_params[0] = 0
            insufficient_decompress_params[1] = 0


def total_decompress(lkj_record, standard_pressure, total_decompress_params, pull_over_flag, ans):
    if pull_over_flag[0] == 1 and lkj_record.pipe_pressure:
        if lkj_record.event == "开车":
            total_decompress_params[0] = lkj_record.pipe_pressure
        if lkj_record.pipe_pressure > total_decompress_params[0]:
            if total_decompress_params[0] < standard_pressure:
                total_decompress_params[1] += standard_pressure - total_decompress_params[0]
        total_decompress_params[0] = lkj_record.pipe_pressure
        if (standard_pressure == 600 and total_decompress_params[1] >= 170) or (standard_pressure == 500 and total_decompress_params[1] >= 140):
            ans.append(LKJITEMS("累计减压超过最大减压量", lkj_record.timestamp))
            total_decompress_params[1] = 0


def over_pressure(lkj_record, standard_pressure, pull_over_flag, ans):
    if pull_over_flag[0] == 1 and lkj_record.pipe_pressure:
        if lkj_record.pipe_pressure > (standard_pressure+50):
            ans.append(LKJITEMS("列车管压过量供给", lkj_record.timestamp))


def invalid_release_EB(lkj_record, invalid_release_EB_params, ans):
    if lkj_record.speed and lkj_record.pipe_pressure:
        if lkj_record.speed > 0 and lkj_record.pipe_pressure < 200:
            if invalid_release_EB_params[0] > lkj_record.pipe_pressure:
                invalid_release_EB_params[0] = lkj_record.pipe_pressure
            elif invalid_release_EB_params[0] < lkj_record.pipe_pressure:
                ans.append(LKJITEMS("紧急制动后违规缓解", lkj_record.timestamp))
                invalid_release_EB_params[0] = 200


def pressure_unreserved_pull_over(lkj_record, pull_over_pressure, pull_over_flag, ans):
    if lkj_record.event == "停车":
        pull_over_pressure[0] = lkj_record.pipe_pressure
        pull_over_pressure[1] = 0
    if (lkj_record.timestamp - pull_over_flag[1]).total_seconds() > 30 and pull_over_pressure[1] == 0:
        pull_over_pressure[1] = 1
        if lkj_record.pipe_pressure and lkj_record.pipe_pressure - pull_over_pressure[0] < 100:
            ans.append(LKJITEMS("停车后未保压", lkj_record.timestamp))


def single_vlave_brake(lkj_record, single_valve_brake_params, standard_pressure, ans):
    if lkj_record.speed:
        if lkj_record.speed > 2 and single_valve_brake_params[0] == 0:
            single_valve_brake_params[0] = 1
        elif lkj_record.speed == 0 and single_valve_brake_params[0]:
            single_valve_brake_params[0] = 0
            if lkj_record.pipe_pressure >= standard_pressure and lkj_record.cylinder_pressure >= 50:
                ans.append(LKJITEMS("单阀制动停车", lkj_record.timestamp))


def band_brake(lkj_record, band_brake_params, standard_pressure, ans):
    if lkj_record.speed and lkj_record.pipe_pressure and lkj_record.cylinder_pressure:
        if lkj_record.speed > 5 and lkj_record.pipe_pressure >= standard_pressure and lkj_record.cylinder_pressure >= 20 and band_brake_params[2] == 0:
            if band_brake_params[1] == 0:
                band_brake_params[0] = lkj_record.timestamp
                band_brake_params[1] = 1
            elif (lkj_record.timestamp - band_brake_params[0]).total_seconds() >= 120:
                ans.append(LKJITEMS("抱闸运行", lkj_record.timestamp))
                band_brake_params[2] = 1
        elif not(lkj_record.speed > 5 and lkj_record.pipe_pressure >= standard_pressure and lkj_record.cylinder_pressure >= 20) and band_brake_params[2] == 1:
            band_brake_params[2] = 0


def EB_invalid_release(lkj_record, EB_invalid_release_params, ans):
    if EB_invalid_release_params[3] and (lkj_record.timestamp - EB_invalid_release_params[0]).total_seconds() >= 10:
        if lkj_record.cylinder_pressure < 250:
            ans.append(LKJITEMS("紧急制动后小闸违规缓解", lkj_record.timestamp))
        for i in range(4):
            EB_invalid_release_params[i] = 0
    if EB_invalid_release_params[3] == 0 and lkj_record.pipe_pressure:
        EB_invalid_release_params[1] = lkj_record.pipe_pressure
        if lkj_record.pipe_pressure < EB_invalid_release_params[1]:
            if EB_invalid_release_params[4] == 0 and lkj_record.speed > 0:
                EB_invalid_release_params[2] = 1
                EB_invalid_release_params[4] = 1
            elif EB_invalid_release_params[4] and EB_invalid_release_params[2]:
                if EB_invalid_release_params[1] == 0:
                    EB_invalid_release_params[3] = 1
                    EB_invalid_release_params[0] = lkj_record.timestamp
        elif lkj_record.pipe_pressure > EB_invalid_release_params[1]:
            if EB_invalid_release_params[4]:
                EB_invalid_release_params[4] = 0
            if EB_invalid_release_params[2]:
                EB_invalid_release_params[2] = 0


def turn_off(lkj_record, pull_over_flag, turn_off_params, ans):
    if pull_over_flag[0] and lkj_record.event == "关机" and lkj_record.speed > 0:
        ans.append(LKJITEMS("途中关机", lkj_record.timestamp))
    elif pull_over_flag[0] == 0 and lkj_record.event == "关机":
        turn_off_params[0] = 1
        turn_off_params[1] = lkj_record.timestamp
    if turn_off_params[0] and lkj_record.event == "开机":
        if (lkj_record.timestamp - turn_off_params[1]).total_seconds() >= 1800:
            ans.append(LKJITEMS("途中关机", lkj_record.timestamp))


def passing_neural_section(lkj_record, passing_neural_section_params, ans):
    if lkj_record.event == "过分相":
        passing_neural_section_params[0] = 1
        passing_neural_section_params[1] = lkj_record.distance
        passing_neural_section_params[2] = lkj_record.locomotive_status
    elif passing_neural_section_params[0]:
        if lkj_record.event == "机车工况变化":
            passing_neural_section_params[2] = lkj_record.locomotive_status
        if abs(lkj_record.distance - passing_neural_section_params[1]) >= 30:
            if "非" in passing_neural_section_params[2]:
                ans.append(LKJITEMS("手柄非零位过分相", lkj_record.timestamp))
            passing_neural_section_params[0] = 0
            passing_neural_section_params[1] = 0
            passing_neural_section_params[2] = ""


def LKJ_behavior(lkj_record, LKJ_behavior_params, ans):
    if lkj_record.event == "防溜警报开始":
        LKJ_behavior_params[0] = 1
    elif lkj_record.event == "防溜警报结束":
        LKJ_behavior_params[0] = 0
    elif lkj_record.event == "警惕键":
        LKJ_behavior_params[1] = 1
    elif lkj_record.event == "警惕确认":
        LKJ_behavior_params[1] = 0
    elif lkj_record.event == "超模式限速开始":
        LKJ_behavior_params[2] = 1
    elif lkj_record.event == "超模式限速结束":
        LKJ_behavior_params[2] = 0
    elif lkj_record.event == "进入平调":
        LKJ_behavior_params[3] = 1
    elif lkj_record.event == "退出平调":
        LKJ_behavior_params[3] = 0
    elif lkj_record.event == "防撞土档开始":
        LKJ_behavior_params[4] = 1
    elif lkj_record.event == "防撞土档结束":
        LKJ_behavior_params[4] = 0
    elif lkj_record.event == "退出调车":
        LKJ_behavior_params[5] = 0
    elif lkj_record.event == "开车对标":
        LKJ_behavior_params[5] = 1
    if lkj_record.pipe_pressure and lkj_record.pipe_pressure < 200 and LKJ_behavior_params[7] == 0:
        if 1 not in LKJ_behavior_params:
            LKJ_behavior_params[6] = 1
        if LKJ_behavior_params[0]:
            ans.append(LKJITEMS("防溜紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[0] = 0
        if LKJ_behavior_params[1]:
            ans.append(LKJITEMS("警惕功能紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[1] = 0
        if LKJ_behavior_params[2]:
            ans.append(LKJITEMS("超模式限速紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[2] = 0
        if LKJ_behavior_params[3]:
            ans.append(LKJITEMS("平调紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[3] = 0
        if LKJ_behavior_params[4]:
            ans.append(LKJITEMS("放撞土档紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[4] = 0
        if LKJ_behavior_params[5]:
            ans.append(LKJITEMS("降级状态下紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[5] = 0
        if LKJ_behavior_params[6]:
            ans.append(LKJITEMS("其它紧急制动", lkj_record.timestamp))
            LKJ_behavior_params[6] = 0
        LKJ_behavior_params[7] = 1


def degrade(lkj_record, ans):
    if lkj_record.event == "降级运行":
        ans.append(LKJITEMS("降级", lkj_record.timestamp))


def position_adjust(lkj_record, ans):
    if lkj_record.event == "车位对中" and int(lkj_record.others[3:]) > 50:
        ans.append(LKJITEMS("车位对中", lkj_record.timestamp))
    elif lkj_record.event == "车位向后" and int(lkj_record.ohters[3:]) > 50:
        ans.append(LKJITEMS("车位向后", lkj_record.timestamp))
    elif lkj_record.event == "车位向前":
        ans.append(LKJITEMS("车位向前", lkj_record.timestamp))


def misconfirm(lkj_record, misconfirm_params, ans):
    if lkj_record.event == "绿/绿黄确认":
        misconfirm_params[0] = 1
    if misconfirm_params[0] and lkj_record.event == "过信号机":
        if lkj_record.signal_color == "红黄":
            misconfirm_params[1] = 1
            misconfirm_params[2] = lkj_record.timestamp
        elif lkj_record.signal_color == "白灯":
            misconfirm_params[1] = 2
        else:
            misconfirm_params[0] = 0
    if misconfirm_params[1] == 1:
        if (lkj_record.timestamp - misconfirm_params[2]).total_seconds() > 5:
            if misconfirm_params[3] == 0:
                ans.append(LKJITEMS("出站绿/绿黄灯误确认", lkj_record.timestamp))
            misconfirm_params[0] = 0
        elif lkj_record.event == "机车信号变化":
            misconfirm_params[3] = 1
    elif misconfirm_params[1] == 2:
        if lkj_record.event == "停车":
            ans.append(LKJITEMS("出站绿/绿黄灯误确认", lkj_record.timestamp))
            misconfirm_params[0] = 0
        if lkj_record.signal_color != "白灯":
            misconfirm_params[0] = 0


def invalid_direction_change(lkj_record, pull_over_flag, invalid_direction_change_params, ans):
    if lkj_record.event == "机车工况变化":
        if pull_over_flag[0] == 0:
            if "前" in lkj_record.locomotive_status:
                invalid_direction_change_params[0] = 1
            else:
                invalid_direction_change_params[0] = 2
        else:
            if "前" in lkj_record.locomotive_status:
                if invalid_direction_change_params[0] == 2:
                    ans.append(LKJITEMS("违规换向", lkj_record.timestamp))
                invalid_direction_change_params[0] = 1
            else:
                if invalid_direction_change_params[0] == 1:
                    ans.append(LKJITEMS("违规换向", lkj_record.timestamp))
                invalid_direction_change_params[0] = 2


def invalid_switch_handle(lkj_record, invalid_switch_handle_params, ans):
    if lkj_record.event == "机车工况变化":
        if "非" in lkj_record.locomotive_status:
            invalid_switch_handle_params[0] = 1
        else:
            if invalid_switch_handle_params[0] == 1 and lkj_record.rotate_speed > 600:
                ans.append(LKJITEMS("回手柄违规", lkj_record.timestamp))
            invalid_switch_handle_params[0] = 0


def double_pull_over(lkj_record, in_station_flag, double_pull_over_params, ans):
    if in_station_flag:
        if lkj_record.event == "停车":
            if double_pull_over_params[0] == 0:
                double_pull_over_params[0] = 1
            else:
                ans.append(LKJITEMS("列车站内停车违规", lkj_record.timestamp))
    if lkj_record.event == "出站":
        double_pull_over_params[0] = 0


def pull_over_switch(lkj_record, handle, pull_over_flag, ans):
    if pull_over_flag[0] and (lkj_record.timestamp - pull_over_flag[1]).total_seconds() > 10 and "非" in handle:
        ans.append(LKJITEMS("停车后未回手柄", lkj_record.timestamp))


def move_forward(lkj_record, pull_over_flag, move_forward_params, ans):
    if lkj_record.event == "停车":
        move_forward_params[0] = lkj_record.distance
    if (lkj_record.timestamp - pull_over_flag[1]).total_seconds() < 300:
        if lkj_record.distance and abs(lkj_record.distance - move_forward_params[0]) >= 15 and move_forward_params[1] == 0:
            move_forward_params[1] = 1
    else:
        if move_forward_params[1] == 0:
            ans.append(LKJITEMS("单机未前移", lkj_record.timestamp))
        move_forward_params[1] = 0


def signal_unchanged(lkj_record, signal_color, ans):
    if lkj_record.event == "开车":
        if signal_color[0] == "红灯":
            ans.append(LKJITEMS("未转换机车信号开车", lkj_record.timestamp))


def rotate_over_speed(lkj_record, rotate_speed_limit, ans):
    if lkj_record.rotate_speed and lkj_record.rotate_speed > rotate_speed_limit:
        ans.append(LKJITEMS("柴速超速", lkj_record.timestamp))


def rotate_zero_speed(lkj_record, ans):
    if lkj_record.rotate_speed == 0:
        ans.append(LKJITEMS("转速为0", lkj_record.timestamp))


def outside_pullover(lkj_record, departure_flag, in_station_flag, ans):
    if lkj_record.event == "停车" and departure_flag:
        if in_station_flag == 0:
            ans.append(LKJITEMS("区间停车", lkj_record.timestamp))
        else:
            ans.append(LKJITEMS("站内停车", lkj_record.timestamp))


def in_station_shunt(lkj_record, in_station_flag, pull_over_flag, ans):
    if in_station_flag and pull_over_flag[0] == 0:
        if lkj_record.event == "进入调车":
            ans.append(LKJITEMS("中间站调车", lkj_record.timestamp))


def calibration(lkj_record, ans):
    if lkj_record.event == "定标键":
        ans.append(LKJITEMS("定标", lkj_record.timestamp))


def low_pressure_driving(lkj_record, pull_over_flag, standard_pressure, ans):
    if pull_over_flag[0] and lkj_record.pipe_pressure:
        if lkj_record.speed > 5 and lkj_record.pipe_pressure < standard_pressure - 30:
            ans.append(LKJITEMS("充风不足开车", lkj_record.timestamp))


def pull_over_unbraked(lkj_record, pull_over_unbraked_params, pull_over_flag, ans):
    if pull_over_flag[0] == 0:
        if lkj_record.pipe_pressure and lkj_record.pipe_pressure < 50:
            if pull_over_unbraked_params[0] == 0:
                pull_over_unbraked_params[0] = lkj_record.timestamp
            elif (lkj_record.timestamp - pull_over_unbraked_params[0]).total_seconds() > 240:
                pull_over_unbraked_params[1] = 1
        elif lkj_record.pipe_pressure and lkj_record.pipe_pressure >= 50:
            if pull_over_unbraked_params[0] != 0:
                pull_over_unbraked_params[0] = 0
    if pull_over_flag[0] and pull_over_unbraked_params[1]:
        ans.append(LKJITEMS("停车后小闸未制动", lkj_record.timestamp))


def brake_trial(lkj_record, ans):
    if lkj_record.event == "常用制动试验":
        ans.append("常用试验", lkj_record.timestamp)
    elif lkj_record.event == "紧急制动试验":
        ans.append("紧急试验", lkj_record.timestamp)


def IW_least_pressure(lkj_record, exit_section_flag, standard_pressure, IW_least_pressure_params, ans):
    if exit_section_flag and lkj_record.pipe_pressure:
        if lkj_record.pipe_pressure <= standard_pressure - 40 and lkj_record.pipe_pressure >= standard_pressure - 80 and IW_least_pressure_params[0] == 0:
            IW_least_pressure_params[0] = lkj_record.timestamp
            IW_least_pressure_params[1] = lkj_record.pipe_pressure
        if IW_least_pressure_params[0] and not IW_least_pressure_params[2]:
            if (lkj_record.timestamp - IW_least_pressure_params[0]).total_seconds() >= 60:
                IW_least_pressure_params[2] = 1
            if lkj_record.pipe_pressure != IW_least_pressure_params[1]:
                IW_least_pressure_params[2] = -1
        if lkj_record.event == "LKJ结束":
            if IW_least_pressure_params[2] != 1:
                ans.append(LKJITEMS("库内无最小减压", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_least_pressure_params[2] != 1:
            ans.append(LKJITEMS("库内无最小减压", lkj_record.timestamp))
        IW_least_pressure_params[0] = 0
        IW_least_pressure_params[1] = 0
        IW_least_pressure_params[2] = 0


def IW_most_pressure(lkj_record, exit_section_flag, standard_pressure, IW_most_pressure_params, ans):
    if exit_section_flag and lkj_record.pipe_pressure:
        if standard_pressure == 600 and lkj_record.pipe_pressure >= 410 and lkj_record.pipe_pressure <= 450 and IW_most_pressure_params[0] == 0:
            IW_most_pressure_params[0] = 1
        elif standard_pressure == 500 and lkj_record.pipe_pressure >= 340 and lkj_record.pipe_pressure <= 380 and IW_most_pressure_params[0] == 0:
            IW_most_pressure_params[0] = 1
        if lkj_record.event == "LKJ结束":
            if IW_most_pressure_params[0] == 0:
                ans.append(LKJITEMS("库内无最大减压", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_most_pressure_params[0] == 0:
            ans.append(LKJITEMS("库内无最大减压", lkj_record.timestamp))
        IW_most_pressure_params[0] = 0


def IW_over_pressure(lkj_record, exit_section_flag, standard_pressure, IW_over_pressure_params, ans):
    if exit_section_flag and lkj_record.pipe_pressure:
        if lkj_record.pipe_pressure >= standard_pressure - 260 and lkj_record.pipe_pressure <= standard_pressure - 220 and IW_over_pressure_params[0] == 0:
            IW_over_pressure_params[0] = 1
        if lkj_record.event == "LKJ结束":
            if IW_over_pressure_params[0] == 0:
                ans.append(LKJITEMS("库内无过量减压", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_over_pressure_params[0] == 0:
            ans.append(LKJITEMS("库内无过量减压", lkj_record.timestamp))
        IW_over_pressure_params[0] = 0


def IW_emergency_brake(lkj_record, exit_section_flag, standard_pressure, IW_emergency_brake_params, ans):
    if exit_section_flag and lkj_record.pipe_pressure:
        if lkj_record.pipe_pressure >= standard_pressure:
            IW_emergency_brake_params[0] = lkj_record.timestamp
        elif lkj_record.pipe_pressure <= 20 and IW_emergency_brake_params[0] != 0:
            if (lkj_record.timestamp - IW_emergency_brake_params[0]).total_seconds() <= 5 and lkj_record.cylinder_pressure > 400:
                IW_emergency_brake_params[1] = 1
        if lkj_record.event == "LKJ结束":
            if IW_emergency_brake_params[1] == 0:
                ans.append(LKJITEMS("库内无紧急制动试验", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_emergency_brake_params[1] == 0:
            ans.append(LKJITEMS("库内无紧急制动试验", lkj_record.timestamp))
        IW_emergency_brake_params[0] = 0
        IW_emergency_brake_params[1] = 0


def IW_single_valve(lkj_record, exit_section_flag, standard_pressure, pull_over_flag, IW_single_valve_params, ans):
    if exit_section_flag and lkj_record.pipe_pressure:
        if pull_over_flag[0] == 0:
            if lkj_record.pipe_pressure >= standard_pressure:
                if lkj_record.cylinder_pressure == 0 and IW_single_valve_params[0] == 0:
                    IW_single_valve_params[0] = 1
                elif lkj_record.cylinder_pressure >= 280 and lkj_record.cylinder_pressure <= 320 and IW_single_valve_params[0]:
                    IW_single_valve_params[1] = 1
                if lkj_record.cylinder_pressure == 0 and IW_single_valve_params[1]:
                    IW_single_valve_params[2] = 1
        elif lkj_record.event == "开车" and IW_single_valve_params[2] == 0:
            IW_single_valve_params[0] = 0
            IW_single_valve_params[1] = 0
        if lkj_record.event == "LKJ结束":
            if IW_single_valve_params[2] == 0:
                ans.append(LKJITEMS("库内无单阀试验", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_single_valve_params[2] == 0:
            ans.append(LKJITEMS("库内无单阀试验", lkj_record.timestamp))
        IW_single_valve_params[0] = 0
        IW_single_valve_params[1] = 0
        IW_single_valve_params[2] = 0


def IW_over_charge(lkj_record, exit_section_flag, standard_pressure, IW_over_charge_params, ans):
    if exit_section_flag and lkj_record.pipe_pressure:
        if IW_over_charge_params[0] == 0:
            if lkj_record.pipe_pressure >= standard_pressure+30:
                IW_over_charge_params[0] = 1
        if lkj_record.event == "LKJ结束":
            if IW_over_charge_params[0] == 0:
                ans.append(LKJITEMS("库内无过充试验", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_over_charge_params[0] == 0:
            ans.append(LKJITEMS("库内无过充试验", lkj_record.timestamp))
        IW_over_charge_params[0] = 0


def IW_rotate_speed_adjust(lkj_record, exit_section_flag, pull_over_flag, IW_rotate_speed_params, ans):
    if exit_section_flag:
        if IW_rotate_speed_params[0] == 0:
            if pull_over_flag[0] == 0 and lkj_record.rotate_speed and lkj_record.cylinder_pressure:
                if lkj_record.rotate_speed > 600 and lkj_record.cylinder_pressure >= 280:
                    IW_rotate_speed_params[0] = 1
        if lkj_record.event == "LKJ结束":
            if IW_rotate_speed_params[0] == 0:
                ans.append(LKJITEMS("库内无柴油机调速试验", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_rotate_speed_params[0] == 0:
            ans.append(LKJITEMS("库内无柴油机调速试验", lkj_record.timestamp))
        IW_rotate_speed_params[0] = 0


def IW_locomotive_status(lkj_record, exit_section_flag, IW_locomotive_status_params, ans):
    if exit_section_flag:
        if IW_locomotive_status_params[0] == 0:
            if lkj_record.event == "机车工况变化":
                if lkj_record.locomotive_status == "非前牵" or lkj_record.locomotive_status == "非后牵":
                    IW_locomotive_status_params[0] = 1
        if lkj_record.event == "LKJ结束":
            if IW_locomotive_status_params[0] == 0:
                ans.append(LKJITEMS("库内无工况试验", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_locomotive_status_params[0] == 0:
            ans.append(LKJITEMS("库内无工况试验", lkj_record.timestamp))
        IW_locomotive_status_params[0] = 0


def IW_high_pressure(lkj_record, exit_section_flag, handle, pull_over_flag, IW_high_pressure_params, ans):
    if exit_section_flag:
        if lkj_record.event == "入段":
            IW_high_pressure_params[0] = handle
        if pull_over_flag[0] == 0:
            if lkj_record.event == "机车工况变化":
                if lkj_record.locomotive_status != IW_high_pressure_params[0]:
                    IW_high_pressure_params[1] = 1
                IW_high_pressure_params[0] = lkj_record.locomotive_status
        if lkj_record.event == "主断断开" or lkj_record.event == "主断闭合" or lkj_record.event == "自动过分相":
            IW_high_pressure_params[1] = 1
        if lkj_record.event == "LKJ结束":
            if IW_high_pressure_params[1] == 0:
                ans.append(LKJITEMS("库内无高压试验", lkj_record.timestamp))
    elif lkj_record.event == "出段":
        if IW_high_pressure_params[1] == 0:
            ans.append(LKJITEMS("库内无高压试验", lkj_record.timestamp))
        IW_high_pressure_params[0] = ""
        IW_high_pressure_params[1] = 0


def IW_speeding(lkj_record, exit_section_flag, IW_speeding_params, ans):
    if exit_section_flag and lkj_record.speed:
        if lkj_record.speed > IW_speeding_params[0] and IW_speeding_params[1] == 0:
            IW_speeding_params[1] = 1
        if lkj_record.event == "LKJ结束":
            if IW_speeding_params[1] == 0:
                ans.append(LKJITEMS("库内超速", lkj_record.timestamp))
            IW_speeding_params[1] = 0
    elif lkj_record.event == "出段":
        if IW_speeding_params[1] == 0:
            ans.append(LKJITEMS("库内超速", lkj_record.timestamp))
        IW_speeding_params[1] = 0


def IW_check_release(lkj_record, exit_section_flag, pull_over_flag, IW_check_release_params, ans):
    if exit_section_flag:
        if pull_over_flag[0] == 0:
            if IW_check_release_params[1] == 0:
                if lkj_record.cylinder_pressure and lkj_record.cylinder_pressure <= 30:
                    if IW_check_release_params[0] == 0:
                        IW_check_release_params[0] = lkj_record.timestamp
                    elif (lkj_record.timestamp - IW_check_release_params[0]).total_seconds() >= 30:
                        IW_check_release_params[1] = 1
        if lkj_record.event == "LKJ结束":
            if IW_check_release_params[1] == 0:
                ans.append(LKJITEMS("库内未检查缓解状态", lkj_record.timestamp))
            IW_check_release_params[0] = 0
            IW_check_release_params[1] = 0


def invalid_benchmark(lkj_record, invalid_benchmark_params, ans):
    if lkj_record.event == "过机校正":
        if int(lkj_record.others.split("，")[0][5:]) > 100:
            invalid_benchmark_params[2] = 1
    elif "车位" in lkj_record.event:
        invalid_benchmark_params[1] = 1
    elif lkj_record.event == "过信号机":
        invalid_benchmark_params[0] = invalid_benchmark_params[1]
        invalid_benchmark_params[1] = 0
    if invalid_benchmark_params[0] and invalid_benchmark_params[1]:
        invalid_benchmark_params[2] = 1
    if invalid_benchmark_params[2]:
        ans.append(LKJITEMS("未按规定对标", lkj_record.timestamp))
        invalid_benchmark_params[2] = 0


def set_off_untried(lkj_record, pull_over_flag, standard_pressure, set_off_untried_params, ans):
    if pull_over_flag[0]:
        if lkj_record.event == "开车":
            if set_off_untried_params[4] == 0 and set_off_untried_params[1]:
                ans.append(LKJITEMS("紧急制动后开车未试闸", lkj_record.timestamp))
            for i in range(len(set_off_untried_params)):
                set_off_untried_params[i] = 0
        elif lkj_record.pipe_pressure:
            if lkj_record.pipe_pressure >= standard_pressure:
                set_off_untried_params[0] = lkj_record.timestamp
            elif set_off_untried_params[0] and lkj_record.pipe_pressure <= 20:
                if lkj_record.cylinder_pressure > 400 and (lkj_record.timestamp - set_off_untried_params[0]) <= 5:
                    set_off_untried_params[1] = 1
    else:
        if lkj_record.event == "停车":
            if lkj_record.pipe_pressure == 0:
                set_off_untried_params[1] = 1
        elif lkj_record.pipe_pressure:
            if lkj_record.pipe_pressure >= standard_pressure:
                if set_off_untried_params[2] == 0:
                    set_off_untried_params[2] = 1
                elif set_off_untried_params[3]:
                    set_off_untried_params[4] = 1
            elif lkj_record.pipe_pressure <= standard_pressure - 50:
                if set_off_untried_params[2] and set_off_untried_params[3] == 0:
                    set_off_untried_params[3] = 1


def low_speed_release(lkj_record, pull_over_flag, low_speed_release_params, ans):
    if pull_over_flag[0] and lkj_record.speed and lkj_record.speed < 15:
       if lkj_record.pipe_pressure < 200:
           if low_speed_release_params[0] > lkj_record.pipe_pressure:
               low_speed_release_params[0] = lkj_record.pipe_pressure
           elif low_speed_release_params[0] < lkj_record.pipe_pressure:
               ans.append(LKJITEMS("货车低速缓解", lkj_record.timestamp))
               low_speed_release_params[0] = 200


def big_split(lkj_record, handle, big_split_params, ans):
    if lkj_record.pipe_pressure and lkj_record.cylinder_pressure:
        if handle != "非前制" and handle != "非后制" and big_split_params[0] > lkj_record.pipe_pressure and lkj_record.cylinder_pressure < 50:
            ans.append(LKJITEMS("货车大劈叉", lkj_record.timestamp))
        big_split_params[0] = lkj_record.pipe_pressure


def electrical_brake_stop(lkj_record, pull_over_flag, handle, equalizing_reservior, electrical_brake_stop_params, ans):
    if pull_over_flag[0] and lkj_record.speed:
        if lkj_record.speed < electrical_brake_stop_params[0]:
            if handle == "非前制" or handle == "非后制":
                electrical_brake_stop_params[1] = 1
            if equalizing_reservior[1] < 0:
                electrical_brake_stop_params[2] = 1
        elif lkj_record.speed > electrical_brake_stop_params[0]:
            electrical_brake_stop_params[1] = 0
            electrical_brake_stop_params[2] = 0
        electrical_brake_stop_params[0] = lkj_record.speed
    elif lkj_record.event == "停车":
        if electrical_brake_stop_params[1] == 1 and electrical_brake_stop_params[2] == 0:
            ans.append(LKJITEMS("电制停车", lkj_record.timestamp))
        electrical_brake_stop_params[1] = 0
        electrical_brake_stop_params[2] = 0


def invalid_cancel_EB(lkj_record, standard_pressure, handle, invalid_cancel_EB_params, ans):
    if lkj_record.pipe_pressure:
        if lkj_record.pipe_pressure < standard_pressure - 50:
            if (handle == "非前制" or handle == "非后制") and invalid_cancel_EB_params[1] == 0:
                invalid_cancel_EB_params[1] = 1
            if invalid_cancel_EB_params[1] and handle != "非前制" and handle != "非后制":
                if lkj_record.pipe_pressure > invalid_cancel_EB_params[0]:
                    invalid_cancel_EB_params[2] = 1
            invalid_cancel_EB_params[0] = lkj_record.pipe_pressure
        else:
            if invalid_cancel_EB_params[2]:
                ans.append(LKJITEMS("违规解除电制", lkj_record.timestamp))
                invalid_cancel_EB_params[2] = 0
            if invalid_cancel_EB_params[1]:
                invalid_cancel_EB_params[1] = 0


def EBWB_cowork(lkj_record, handle, EBWB_cowork_params, ans):
    if lkj_record.event == "机车工况变化":
        if handle == "非前制" or handle == "非后制":
            EBWB_cowork_params[0] = lkj_record.timestamp
    if EBWB_cowork_params[1] == 0 and EBWB_cowork_params[0]:
        if (lkj_record.timestamp - EBWB_cowork_params[0]).total_seconds() > 5 and lkj_record.cylinder_pressure > 150:
            ans.append(LKJITEMS("电制带闸", lkj_record.timestamp))
            EBWB_cowork_params[1] = 1


def unreleased_small_brake(lkj_record, handle, unreleased_small_brake_params, ans):
    if handle == "非前制" or handle == "非后制" and unreleased_small_brake_params[1] == 0:
        if unreleased_small_brake_params[0] == 0:
            if lkj_record.pipe_pressure < 200:
                unreleased_small_brake_params[0] = lkj_record.timestamp
        else:
            if (lkj_record.timestamp - unreleased_small_brake_params[0]).total_seconds() > 5 and lkj_record.cylinder_pressure > 50:
                unreleased_small_brake_params[1] = 1
                ans.append(LKJITEMS("小闸未缓解", lkj_record.timestamp))
    elif unreleased_small_brake_params[1]:
        unreleased_small_brake_params[1] = 0


def abnormal_pull_over(lkj_record, departure_flag, signal_color, in_station_flag, ans):
    if departure_flag:
        if in_station_flag == 0:
            if lkj_record.event == "停车" and signal_color[0] != "红黄灯":
                ans.append(LKJITEMS("区间非正常停车", lkj_record.timestamp))


def wheelset_sliding(lkj_record, wheelset_sliding_params, ans):
    if lkj_record.event == "轮对滑行":
        wheelset_sliding_params[0] = lkj_record.timestamp
    elif lkj_record.event == "滑行结束":
        if (lkj_record.timestamp - wheelset_sliding_params[0]).total_seconds() > 5:
            ans.append(LKJITEMS("轮对滑行", lkj_record.timestamp))


def wheelset_idling(lkj_record, pull_over_flag, wheelset_idling_params, ans):
    if pull_over_flag[0]:
        if lkj_record.speed and lkj_record.speed < 5:
            if lkj_record.event == "轮对空转":
                wheelset_idling_params[1] = lkj_record.timestamp
            elif lkj_record.event == "空转结束":
                if wheelset_idling_params[1] and (lkj_record.timestamp - wheelset_idling_params[1]).total_seconds() > 10:
                    ans.append(LKJITEMS("起车持续空转", lkj_record.timestamp))
                wheelset_idling_params[1] = 0
        elif lkj_record.event == "空转结束":
            wheelset_idling_params[1] = 0


def pullover_instation(lkj_record, departure_flag, in_station_flag, ans):
    if departure_flag:
        if in_station_flag:
            if lkj_record.event == "停车":
                ans.append(LKJITEMS("站内停车", lkj_record.timestamp))


def revealing_inputs(lkj_record, ans):
    if lkj_record.event == "揭示输入":
        ans.append(LKJITEMS("揭示输入", lkj_record.timestamp, lkj_record.others))


def speed_channel_switch(lkj_record, ans):
    if lkj_record.event == "速度通道切换":
        ans.append(LKJITEMS("速度通道人工切换", lkj_record.timestamp, lkj_record.others))


def signal_mutation(lkj_record, signal_color, ans):
    if lkj_record.event == "机车信号变化":
        if signal_color[0] != "" and lkj_record.signal_color[:2] != "其他" and signal_color[0][:2] != "其他" and abs(SEQUENCE.index(signal_color[0][:2]) - SEQUENCE.index(lkj_record.signal_color[:2])) > 1:
            ans.append(LKJITEMS("机车信号突变", lkj_record.timestamp))


def wrong_mode(lkj_record, wrong_mode_params, ans):
    if lkj_record.event == "总重":
        wrong_mode_params[0] = int(lkj_record.others)
    elif lkj_record.event == "辆数":
        wrong_mode_params[1] = int(lkj_record.others)
    elif lkj_record.event == "模式状态":
        if lkj_record.others == "通用模式":
            if wrong_mode_params[0] >= 5500 or wrong_mode_params[1] >= 60:
                ans.append(LKJITEMS("模式选择错误", lkj_record.timestamp))
        else:
            if wrong_mode_params[0] < 5500 or wrong_mode_params[1] < 60:
                ans.append(LKJITEMS("模式选择错误", lkj_record.timestamp))


def abnormal_signal(lkj_record, departure_flag, in_station_flag, standard_pressure, signal_color, abnormal_signal_params, ans):
    if departure_flag and in_station_flag == 0:
        if lkj_record.event == "机车信号变化":
            if abnormal_signal_params[1]:
                abnormal_signal_params[1] = 0
                if signal_color[1] == "绿灯" or signal_color[1] == "绿黄":
                    if signal_color[0] == "红黄" or signal_color[0] == "灭灯":
                        ans.append(LKJITEMS("信号异常", lkj_record.timestamp))
                elif signal_color[1] == "黄灯" or signal_color[1] == "双黄":
                    if signal_color[0] == "白灯" or signal_color[0] == "灭灯":
                        ans.append(LKJITEMS("信号异常", lkj_record.timestamp))
                elif signal_color[1] == "黄2" or signal_color[1] == "黄2闪":
                    if signal_color[0] == "红黄" or signal_color[0] == "红灯" or signal_color[0] == "蓝灯":
                        ans.append(LKJITEMS("信号异常", lkj_record.timestamp))
        elif lkj_record.pipe_pressure:
            if lkj_record.pipe_pressure >= standard_pressure:
                abnormal_signal_params[0] = lkj_record.timestamp
            elif lkj_record.pipe_pressure <= 20 and abnormal_signal_params[0] != 0:
                if (lkj_record.timestamp - abnormal_signal_params[0]).total_seconds() <= 5 and lkj_record.cylinder_pressure > 400:
                    abnormal_signal_params[1] = 1


def highspeed_midstop(lkj_record, signal_color, highspeed_midstop_params, ans):
    if signal_color[0] == "蓝灯" or signal_color[0] == "红黄" or signal_color[0] == "红灯":
        if lkj_record.event == "停车":
            highspeed_midstop_params[0] = 1
        elif lkj_record.event == "过信号机":
            if highspeed_midstop_params[0]:
                ans.append(LKJITEMS("高速走停走"))
                highspeed_midstop_params[0] = 0


def invalid_inspection(lkj_record, invalid_inspection_params, ans):
    if lkj_record.event == "前端巡检1":
        invalid_inspection_params[0] = lkj_record.timestamp
    elif lkj_record.event == "后端巡检":
        if (lkj_record.timestamp - invalid_inspection_params[0]).total_seconds() < 60:
            ans.append(LKJITEMS("巡检违标", lkj_record.timestamp))
            invalid_inspection_params[0] = 0
        else:
            invalid_inspection_params[1] = lkj_record.timestamp
    elif lkj_record.event == "前端巡检2":
        if invalid_inspection_params[0] != 0:
            if (lkj_record.timestamp - invalid_inspection_params[0]) < 120 or (lkj_record.timestamp - invalid_inspection_params[1]) < 60:
                ans.append(LKJITEMS("巡检违标", lkj_record.timestamp))
            invalid_inspection_params[0] = 0
            invalid_inspection_params[1] = 0


def insufficient_distance(lkj_record, setdis, in_station_flag, signal_color, ans):
    if signal_color[0] == "红黄" or signal_color[0] == "红灯" or signal_color[0] == "蓝灯":
        if lkj_record.event == "停车" and in_station_flag == 0:
            if lkj_record.distance < setdis:
                ans.append(LKJITEMS("区停距离不足", lkj_record.timestamp))


def wrong_nonworking(lkj_record, wrong_nonworking_params, ans):
    if lkj_record.event == "客货本补":
        if lkj_record.others == "货补":
            wrong_nonworking_params[0] = 1
    if wrong_nonworking_params[0]:
        if wrong_nonworking_params[1] == 0:
            if lkj_record.event == "机车信号变化":
                wrong_nonworking_params[1] = 1
                wrong_nonworking_params[2] = lkj_record.timestamp
        elif wrong_nonworking_params[1]:
            if lkj_record.event == "过信号机" or (lkj_record.event == "机车信号变化" and (lkj_record.timestamp - wrong_nonworking_params[2]).total_seconds() > 300):
                ans.append(LKJITEMS("错设为非本务状态"))
                wrong_nonworking_params[0] = 0
                wrong_nonworking_params[1] = 0
                wrong_nonworking_params[2] = 0


def speed_rank(lkj_record, speed_rank_params, ans):
    if lkj_record.event == "客货本补":
        if "客" in lkj_record.others:
            speed_rank_params[0] = 1
    elif lkj_record.event == "车速等级":
        tmp = 0
        for i in lkj_record.others:
            if ord(i) >= ord('0') and ord(i) <= ord('9'):
                tmp = tmp*10 + int(i)
            else:
                break
        speed_rank_params[1] = tmp
    elif speed_rank_params[0] and speed_rank_params[2]==0:
        if lkj_record.speed:
            if lkj_record.speed > speed_rank_params[1]:
                ans.append(LKJITEMS("客车错输速度等级", lkj_record.timestamp))
                speed_rank_params[2] = 1


def wrong_side_track(lkj_record, in_station_flag, wrong_side_track_params, ans):
    if in_station_flag:
        if lkj_record.event == "停车":
            wrong_side_track_params[0] = 1
        elif wrong_side_track_params[0]:
            if lkj_record.event == "车位对中":
                if int(lkj_record.others[3:]) > 50:
                    wrong_side_track_params[1] = 1
            elif lkj_record.event == "机车信号变化":
                if lkj_record.signal_color == "双黄":
                    if wrong_side_track_params[2] == 0:
                        wrong_side_track_params[2] = 1
                    if wrong_side_track_params[3]:
                        wrong_side_track_params[4] = 1
                else:
                    wrong_side_track_params[3] = 1

    else:
        if lkj_record.event == "出站":
            if wrong_side_track_params[4] == 0 and wrong_side_track_params[2]:
                ans.append(LKJITEMS("错误输入侧线股道号(短输长)", lkj_record.timestamp))
                wrong_side_track_params[5] = 1
        if wrong_side_track_params[1] and lkj_record.event == "车位对中" and wrong_side_track_params[5] == 0:
            if int(lkj_record.others[3:]) < -50:
                wrong_side_track_params[5] = 1
                ans.append(LKJITEMS("错误输入侧线股道号(短输长)", lkj_record.timestamp))
    if lkj_record.event == "进站":
        for i in range(len(wrong_side_track_params)):
            wrong_side_track_params[i] = 0


def unreleased_loading(lkj_record, pull_over_flag, standard_pressure, unreleased_loading_params, ans):
    if pull_over_flag[0]:
        if lkj_record.speed and lkj_record.speed > 0:
            if unreleased_loading_params[0] == 0:
                if lkj_record.pipe_pressure < standard_pressure:
                    unreleased_loading_params[0] = 1
            elif unreleased_loading_params[1] == 0:
                unreleased_loading_params[1] = 1
                unreleased_loading_params[2] = lkj_record.timestamp
            else:
                if lkj_record.event == "机车工况变化":
                    if "牵" in lkj_record.locomotive_status:
                        if (lkj_record.timestamp - unreleased_loading_params[2]).total_seconds() <= 2:
                           ans.append(LKJITEMS("未缓解加载", lkj_record.timestamp))
                    unreleased_loading_params[0] = 0
                    unreleased_loading_params[1] = 0
                    unreleased_loading_params[2] = 0

