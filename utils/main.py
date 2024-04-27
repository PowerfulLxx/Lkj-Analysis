import functions


class LKJITEMS(object):
    def __init__(self, item_name, timestamp, details={}):
        self.item_name = item_name
        self.timestamp = timestamp
        self.details = details

    def __str__(self):
        items = [self.item_name, self.timestamp, self.details]
        return ','.join([str(n) for n in items])


def lkjitems_analysis(lkj_header, lkj_records, logger):
    ans = []
    departure_flag = 0  #是否开车对标，0否1是
    in_station_flag = 0  #是否进站，0站外，1站内
    pull_over_flag = [0, 0]  #是否停车,0停车1开车;timestamp;
    delta_pull_over = 0  #停车时长
    shunt_flag = 0  #是否调车,0不调1调
    temp_limit_flag = 0  #是否临时限速,0不限1限
    exit_section_flag = 0  #是否出段(我将出段视作入库，该flag为1代表在库内)
    handle = ""  #手柄位置（工况变化）
    equalizing_reservior = [0, 0]  #均衡风缸压力;均衡风缸下降量

    signal_color = ["", ""]
    standard_pressure = 600
    last_2_stops = [[0, 0], [0, 0]]  #倒数第二次和倒数第一次停车的距离及是否超速
    changing_condition = [0, ""]  #最后一次停车到开车前的工况变化记录
    penetr_params = [0, 0, 0, 0, 0, 0]  #是否违标;初速度是否大于40;当前速度;速度下降量;当前管压;管压下降量;
    before_departure_brake_params = [0, 0, 0, 0]  #是否进行试验;timestamp;管压;管压减少量;
    first_in_params = [0, 0, 0, 0, 0, 0]  #当前管压;管压下降量;是否下降超过五十;是否试闸;第一停车站前结束符;第一临时限速点前结束符;
    long_pull_over_params = [0, 0, 0, 0, 0]  #是否简略制动试验；当前管压；管压下降量；是否下降达到100；初下降timestamp
    station_shunt_params = [0, 0, 0, 0, 0]  #参数同上
    insufficient_decompress_params = [0, 0]  #timestamp;是否初减压不足
    total_decompress_params = [0, 0]  #当前管压；累计管压
    invalid_release_EB_params = [200]  #当前管压;
    pull_over_pressure = [0, 0]  #停车时管压;停车是否超过30s
    disconnection_pressure_unreserved_params = [standard_pressure, 0, 0]  #当前管压;缓解开始timestamp;是否完成
    single_vlave_brake_params = [0, 0]  #速度最高是否大于3；是否完成
    band_brake_params = [0, 0, 0]  #timestamp;是否进入指定参数范围;是否完成
    EB_invalid_release_params = [0, 0, 0, 0, 0]  #timestamp;当前管压;降压时速度是否大于零;是否降到0;是否开始下降
    turn_off_params = [0, 0]  #是否关机；关机timestamp
    passing_neural_section_params = [0, 0, ""]  #是否过分相；过分相距离；过分相工况；
    LKJ_behavior_params = [0, 0, 0, 0, 0, 0, 0, 0]  #是否防溜；是否警惕；是否超模式限速；是否平调;是否防撞土档;是否降级;是否完成其他紧急制动;是否完成紧急制动
    misconfirm_params = [0, 0, 0, 0]  #是否确认;红黄灯:1,白灯:2；timestamp；是否更改
    invalid_direction_change_params = [0]  #前或后
    invalid_switch_handle_params = [0]  #零或非零
    double_pull_over_params = [0]  #站内多次停车
    move_forward_params = [0, 0]  #停车时的距离;是否前行
    rotate_speed_limit = 100  #可更改，暂定100
    pull_over_unbraked_params = [0, 0]  #timestamp；是否完成停车
    IW_least_pressure_params = [0, 0, 0]  #timestamp;缸压；是否有该记录
    IW_most_pressure_params = [0]  #是否有最大减压记录
    IW_over_pressure_params = [0]  #是否有过量记录
    IW_emergency_brake_params = [0, 0]  #定压的timestamp;是否有紧急制动记录
    IW_single_valve_params = [0, 0, 0]  #闸缸压力到达0；缸压达300；是否有单阀记录
    IW_over_charge_params = [0]  #是否过充
    IW_rotate_speed_adjust_params = [0]  #是否柴油机调速
    IW_locomotive_status_params = [0]  #是否工况试验
    IW_high_pressure_params = ["", 0]  #工况；是否有高压试验
    IW_speeding_params = [10, 0]  #限速；是否超速
    IW_check_release_params = [0, 0]  #timestamp；是否完成检查
    invalid_benchmark_params = [0, 0, 0]  #上个分区是否按车位；本分区是否按车位；是否违规对标
    set_off_untried_params = [0, 0, 0, 0, 0]  #减压前timestamp;是否紧集制动或管压为0停车;初始是否到达定压;是否下降50;是否试闸
    low_speed_release_params = [200]  #当前的管压（仅记录200以下）
    big_split_params = [0]
    electrical_brake_stop_params = [0, 0, 0]  #当前速度;是否有电制;是否有风制
    invalid_cancel_EB_params = [0, 0, 0]  #当前管压;是否到达电制位;是否完成该动作
    EBWB_cowork_params = [0, 0]  #电制timestamp;是否完成
    unreleased_small_brake_params = [0, 0]  #紧急制动timestamp;是否完成
    wheelset_sliding_params = [0, 0]  #timestamp；是否滑行
    wheelset_idling_params = [0, 0]  #是否满足条件；timestamp
    wrong_mode_params = [0, 0]  #分别为总重和辆数
    abnormal_signal_params = [0, 0]  #定压的timestamp;是否有紧急制动记录
    highspeed_midstop_params = [0]  #是否有停车记录
    invalid_inspection_params = [0, 0]  #前端timestamp;后端timestamp
    setdis = 50
    setspeed = 40
    wrong_nonworking_params = [0, 0, 0]  #是否非本务；是否有信号；收到信号timestamp
    speed_rank_params = [0, 0, 0]  #是否为客车；车速等级；是否完成事件
    wrong_side_track_params = [0, 0, 0, 0, 0, 0]  #是否站内停车;是否出站信号机处车位调整;是否信号开始为双黄;是否信号转到其他信号;信号是否转回双黄;是否完成事件录入
    unreleased_loading_params = [0, 0, 0]  #是否低于定压；是否完成缓解；完成缓解timestamp
    for lkj_record in lkj_records:
        if pull_over_flag[1] == 0 and lkj_record.timestamp:
            pull_over_flag[1] = lkj_record.timestamp
        if lkj_record.event == "开车对标":
            departure_flag = 1
        elif lkj_record.event == "停车":
            delta_pull_over = 0
            pull_over_flag = [0, lkj_record.timestamp]
            functions.highspeed_midstop(lkj_record=lkj_record, signal_color=signal_color, highspeed_midstop_params=highspeed_midstop_params, ans=ans)
            functions.insufficient_distance(lkj_record=lkj_record, setdis=setdis, in_station_flag=in_station_flag, signal_color=signal_color, ans=ans)
            functions.wrong_side_track(lkj_record=lkj_record, in_station_flag=in_station_flag, wrong_side_track_params=wrong_side_track_params, ans=ans)
        elif lkj_record.event == "开车":
            delta_pull_over = (lkj_record.timestamp - pull_over_flag[1]).total_seconds()
            pull_over_flag = [1, lkj_record.timestamp]
        elif lkj_record.event == "进站":
            in_station_flag = 1
            functions.wrong_side_track(lkj_record=lkj_record, in_station_flag=in_station_flag,
                             wrong_side_track_params=wrong_side_track_params, ans=ans)
        elif lkj_record.event == "出站":
            in_station_flag = 0
            functions.wrong_side_track(lkj_record=lkj_record, in_station_flag=in_station_flag,
                             wrong_side_track_params=wrong_side_track_params, ans=ans)
        elif lkj_record.event == "临时限速起点" or lkj_record.event == "临时限速开始":
            temp_limit_flag = 1
        elif lkj_record.event == "临时限速终点" or lkj_record.event == "临时限速结束":
            temp_limit_flag = 0
        elif lkj_record.event == "进入调车":
            shunt_flag = 1
        elif lkj_record.event == "退出调车":
            shunt_flag = 0
        elif lkj_record.event == "机车工况变化":
            handle = lkj_record.locomotive_status
        elif lkj_record.event == "机车信号变化":
            functions.signal_mutation(lkj_record=lkj_record, signal_color=signal_color, ans=ans)
            signal_color[1] = signal_color[0]
            signal_color[0] = lkj_record.signal_color
            functions.wrong_nonworking(lkj_record=lkj_record, wrong_nonworking_params=wrong_nonworking_params, ans=ans)
            functions.wrong_side_track(lkj_record=lkj_record, in_station_flag=in_station_flag,
                             wrong_side_track_params=wrong_side_track_params, ans=ans)
        elif lkj_record.event == "入段":
            exit_section_flag = 1
        elif lkj_record.event == "出段":
            exit_section_flag = 0
        elif lkj_record.event == "均缸压力变化":
            equalizing_reservior[1] = lkj_record.equalizing_cylinder_1 - equalizing_reservior[0]
            equalizing_reservior[0] = lkj_record.equalizing_cylinder_1
        elif lkj_record.event == "路票解锁":
            ans.append(LKJITEMS("路票解锁", lkj_record.timestamp))
        elif lkj_record.event == "临时路票解锁":
            ans.append(LKJITEMS("临时路票解锁", lkj_record.timestamp))
        elif lkj_record.event == "绿证解锁":
            ans.append(LKJITEMS("绿证解锁", lkj_record.timestamp))
        elif lkj_record.event == "临时绿证解锁":
            ans.append(LKJITEMS("临时绿证解锁", lkj_record.timestamp))
        elif lkj_record.event == "手信号引导解锁":
            ans.append(LKJITEMS("手信号引导解锁", lkj_record.timestamp))
        elif lkj_record.event == "特定引导解锁":
            ans.append(LKJITEMS("特定引导解锁", lkj_record.timestamp))
        elif lkj_record.event == "靠标解锁":
            ans.append(LKJITEMS("靠标解锁", lkj_record.timestamp))
        elif lkj_record.event == "调车点式解锁":
            ans.append(LKJITEMS("调车点式解锁", lkj_record.timestamp))
        elif lkj_record.event == "股道无码确认":
            ans.append(LKJITEMS("股道无码确认", lkj_record.timestamp))
        elif lkj_record.event == "绿/绿黄确认":
            ans.append(LKJITEMS("绿/绿黄确认", lkj_record.timestamp))
        elif lkj_record.event == "特殊发码确认":
            ans.append(LKJITEMS("特殊发码确认", lkj_record.timestamp))
        elif lkj_record.event == "触发常用":
            ans.append(LKJITEMS("触发常用", lkj_record.timestamp))
        elif lkj_record.event == "触发卸载":
            ans.append(LKJITEMS("触发卸载", lkj_record.timestamp))
        elif lkj_record.event == "进入随时停车模式":
            ans.append(LKJITEMS("20km/h限速", lkj_record.timestamp))
        elif lkj_record.event == "临时数据解除":
            ans.append(LKJITEMS("揭示解除", lkj_record.timestamp))
        elif lkj_record.event == "总重":
            functions.wrong_mode(lkj_record=lkj_record, wrong_mode_params=wrong_mode_params, ans=ans)
        elif lkj_record.event == "辆数":
            functions.wrong_mode(lkj_record=lkj_record, wrong_mode_params=wrong_mode_params, ans=ans)
        elif lkj_record.event == "模式状态":
            functions.wrong_mode(lkj_record=lkj_record, wrong_mode_params=wrong_mode_params, ans=ans)
        elif lkj_record.event == "过信号机":
            functions.highspeed_midstop(lkj_record=lkj_record, signal_color=signal_color,
                              highspeed_midstop_params=highspeed_midstop_params, ans=ans)
            functions.wrong_nonworking(lkj_record=lkj_record, wrong_nonworking_params=wrong_nonworking_params, ans=ans)
        elif lkj_record.event == "报警开始":
            ans.append(LKJITEMS("警惕报警", lkj_record.timestamp))
        elif lkj_record.event == "支线选择":
            ans.append(LKJITEMS("支线输入", lkj_record.timestamp))
        elif lkj_record.event == "前端巡检1":
            functions.invalid_inspection(lkj_record=lkj_record, invalid_inspection_params=invalid_inspection_params, ans=ans)
        elif lkj_record.event == "前端巡检2":
            functions.invalid_inspection(lkj_record=lkj_record, invalid_inspection_params=invalid_inspection_params, ans=ans)
        elif lkj_record.event == "后端巡检":
            functions.invalid_inspection(lkj_record=lkj_record, invalid_inspection_params=invalid_inspection_params, ans=ans)
        elif lkj_record.event == "工务线路信息" or lkj_record.event == "线路信息":
            if "反向" in lkj_record.others:
                ans.append(LKJITEMS("反向行车", lkj_record.timestamp))
        elif lkj_record.event == "过分相":
            if lkj_record.speed < setspeed:
                ans.append(LKJITEMS("分相未达速", lkj_record.timestamp))
        elif lkj_record.event == "客货本补":
            functions.wrong_nonworking(lkj_record=lkj_record, wrong_nonworking_params=wrong_nonworking_params, ans=ans)
        elif lkj_record.event == "车位对中":
            functions.wrong_side_track(lkj_record=lkj_record, in_station_flag=in_station_flag,
                             wrong_side_track_params=wrong_side_track_params, ans=ans)
        functions.coupling_pull_over(lkj_record=lkj_record, departure_flag=departure_flag, last_2_stops=last_2_stops, changing_condition=changing_condition, ans=ans)
        functions.penetration_trial(lkj_record=lkj_record, penetr_params=penetr_params, delta_pull_over=delta_pull_over, ans=ans)
        functions.zero_pressure(lkj_record=lkj_record, ans=ans)
        functions.before_departure_brake(lkj_record=lkj_record, before_departure_brake_params=before_departure_brake_params, departure_flag=departure_flag, ans=ans)
        functions.first_in_brake(lkj_record=lkj_record, first_in_params=first_in_params, departure_flag=departure_flag, in_station_flag=in_station_flag, temp_limit_flag=temp_limit_flag, ans=ans)
        functions.long_pull_over(lkj_record=lkj_record, long_pull_over_params=long_pull_over_params, pull_over_flag=pull_over_flag, delta_pull_over=delta_pull_over, ans=ans)
        functions.station_shunt(lkj_record=lkj_record, station_shunt_params=station_shunt_params,in_station_flag=in_station_flag, pull_over_flag=pull_over_flag, shunt_flag=shunt_flag, ans=ans)
        functions.insufficient_decompress(lkj_record=lkj_record, insufficient_decompress_params=insufficient_decompress_params, ans=ans)
        functions.total_decompress(lkj_record=lkj_record, standard_pressure=standard_pressure, total_decompress_params=total_decompress_params, pull_over_flag=pull_over_flag, ans=ans)
        functions.over_pressure(lkj_record=lkj_record, standard_pressure=standard_pressure, pull_over_flag=pull_over_flag, ans=ans)
        functions.invalid_release_EB(lkj_record=lkj_record, invalid_release_EB_params=invalid_release_EB_params, ans=ans)
        functions.pressure_unreserved_pull_over(lkj_record=lkj_record, pull_over_pressure=pull_over_pressure, pull_over_flag=pull_over_flag, ans=ans)
        functions.disconnection_pressure_unreserved(lkj_record=lkj_record, in_station_flag=in_station_flag, pull_over_flag=pull_over_flag, shunt_flag=shunt_flag, disconnection_pressure_unreserved_params=disconnection_pressure_unreserved_params, ans=ans)
        functions.single_vlave_brake(lkj_record=lkj_record, single_valve_brake_params=single_vlave_brake_params, standard_pressure=standard_pressure, ans=ans)
        functions.band_brake(lkj_record=lkj_record, band_brake_params=band_brake_params, standard_pressure=standard_pressure, ans=ans)
        functions.EB_invalid_release(lkj_record=lkj_record, EB_invalid_release_params=EB_invalid_release_params, ans=ans)
        functions.turn_off(lkj_record=lkj_record, pull_over_flag=pull_over_flag, turn_off_params=turn_off_params, ans=ans)
        functions.passing_neural_section(lkj_record=lkj_record, passing_neural_section_params=passing_neural_section_params, ans=ans)
        functions.LKJ_behavior(lkj_record=lkj_record, LKJ_behavior_params=LKJ_behavior_params,ans=ans)
        functions.degrade(lkj_record=lkj_record, ans=ans)
        functions.position_adjust(lkj_record=lkj_record, ans=ans)
        functions.misconfirm(lkj_record=lkj_record, misconfirm_params=misconfirm_params, ans=ans)
        functions.invalid_direction_change(lkj_record=lkj_record, pull_over_flag=pull_over_flag, invalid_direction_change_params=invalid_direction_change_params, ans=ans)
        functions.invalid_switch_handle(lkj_record=lkj_record, invalid_switch_handle_params=invalid_switch_handle_params, ans=ans)
        functions.double_pull_over(lkj_record=lkj_record, in_station_flag=in_station_flag, double_pull_over_params=double_pull_over_params, ans=ans)
        functions.pull_over_switch(lkj_record=lkj_record, handle=handle, pull_over_flag=pull_over_flag, ans=ans)
        functions.move_forward(lkj_record=lkj_record, pull_over_flag=pull_over_flag, move_forward_params=move_forward_params, ans=ans)
        functions.signal_unchanged(lkj_record=lkj_record, signal_color=signal_color, ans=ans)
        functions.rotate_over_speed(lkj_record=lkj_record, rotate_speed_limit=rotate_speed_limit, ans=ans)
        functions.rotate_zero_speed(lkj_record=lkj_record, ans=ans)
        functions.outside_pullover(lkj_record=lkj_record, departure_flag=departure_flag, in_station_flag=in_station_flag, ans=ans)
        functions.in_station_shunt(lkj_record=lkj_record, in_station_flag=in_station_flag, pull_over_flag=pull_over_flag, ans=ans)
        functions.calibration(lkj_record=lkj_record, ans=ans)
        functions.low_pressure_driving(lkj_record=lkj_record, pull_over_flag=pull_over_flag, standard_pressure=standard_pressure, ans=ans)
        functions.pull_over_unbraked(lkj_record=lkj_record, pull_over_unbraked_params=pull_over_unbraked_params, pull_over_flag=pull_over_flag, ans=ans)
        functions.brake_trial(lkj_record=lkj_record, ans=ans)
        functions.invalid_benchmark(lkj_record=lkj_record, invalid_benchmark_params=invalid_benchmark_params, ans=ans)
        functions.set_off_untried(lkj_record=lkj_record, pull_over_flag=pull_over_flag, standard_pressure=standard_pressure, set_off_untried_params=set_off_untried_params, ans=ans)
        functions.low_speed_release(lkj_record=lkj_record, pull_over_flag=pull_over_flag, low_speed_release_params=low_speed_release_params, ans=ans)
        functions.big_split(lkj_record=lkj_record, handle=handle, big_split_params=big_split_params, ans=ans)
        functions.electrical_brake_stop(lkj_record=lkj_record, pull_over_flag=pull_over_flag, handle=handle, equalizing_reservior=equalizing_reservior, electrical_brake_stop_params=electrical_brake_stop_params, ans=ans)
        functions.invalid_cancel_EB(lkj_record=lkj_record, standard_pressure=standard_pressure, handle=handle, invalid_cancel_EB_params=invalid_cancel_EB_params, ans=ans)
        functions.EBWB_cowork(lkj_record=lkj_record, handle=handle, EBWB_cowork_params=EBWB_cowork_params, ans=ans)
        functions.unreleased_small_brake(lkj_record=lkj_record, handle=handle, unreleased_small_brake_params=unreleased_small_brake_params, ans=ans)
        functions.abnormal_pull_over(lkj_record=lkj_record, departure_flag=departure_flag, signal_color=signal_color, in_station_flag=in_station_flag, ans=ans)
        functions.wheelset_sliding(lkj_record=lkj_record, wheelset_sliding_params=wheelset_sliding_params, ans=ans)
        functions.wheelset_idling(lkj_record=lkj_record, pull_over_flag=pull_over_flag, wheelset_idling_params=wheelset_idling_params, ans=ans)
        functions.pullover_instation(lkj_record=lkj_record, departure_flag=departure_flag, in_station_flag=in_station_flag, ans=ans)
        functions.revealing_inputs(lkj_record=lkj_record, ans=ans)
        functions.abnormal_signal(lkj_record=lkj_record, departure_flag=departure_flag, in_station_flag=in_station_flag, standard_pressure=standard_pressure, signal_color=signal_color, abnormal_signal_params=abnormal_signal_params, ans=ans)
        functions.speed_rank(lkj_record=lkj_record, speed_rank_params=speed_rank_params, ans=ans)
        functions.unreleased_loading(lkj_record=lkj_record, pull_over_flag=pull_over_flag, standard_pressure=standard_pressure, unreleased_loading_params=unreleased_loading_params, ans=ans)
        if exit_section_flag or lkj_record.event == "出段":
            functions.IW_least_pressure(lkj_record=lkj_record, exit_section_flag=exit_section_flag, standard_pressure=standard_pressure, IW_least_pressure_params=IW_least_pressure_params, ans=ans)
            functions.IW_most_pressure(lkj_record=lkj_record, exit_section_flag=exit_section_flag, standard_pressure=standard_pressure, IW_most_pressure_params=IW_most_pressure_params, ans=ans)
            functions.IW_over_pressure(lkj_record=lkj_record, exit_section_flag=exit_section_flag, standard_pressure=standard_pressure, IW_over_pressure_params=IW_over_pressure_params, ans=ans)
            functions.IW_emergency_brake(lkj_record=lkj_record, exit_section_flag=exit_section_flag, standard_pressure=standard_pressure, IW_emergency_brake_params=IW_emergency_brake_params, ans=ans)
            functions.IW_single_valve(lkj_record=lkj_record, exit_section_flag=exit_section_flag, standard_pressure=standard_pressure, pull_over_flag=pull_over_flag, IW_single_valve_params=IW_single_valve_params, ans=ans)
            functions.IW_over_charge(lkj_record=lkj_record, exit_section_flag=exit_section_flag, standard_pressure=standard_pressure, IW_over_charge_params=IW_over_charge_params, ans=ans)
            functions.IW_rotate_speed_adjust(lkj_record=lkj_record, exit_section_flag=exit_section_flag, pull_over_flag=pull_over_flag, IW_rotate_speed_params=IW_rotate_speed_adjust_params, ans=ans)
            functions.IW_locomotive_status(lkj_record=lkj_record, exit_section_flag=exit_section_flag, IW_locomotive_status_params=IW_locomotive_status_params, ans=ans)
            functions.IW_high_pressure(lkj_record=lkj_record, exit_section_flag=exit_section_flag, handle=handle, pull_over_flag=pull_over_flag, IW_high_pressure_params=IW_high_pressure_params, ans=ans)
            functions.IW_speeding(lkj_record=lkj_record, exit_section_flag=exit_section_flag, IW_speeding_params=IW_speeding_params, ans=ans)
            functions.IW_check_release(lkj_record=lkj_record, exit_section_flag=exit_section_flag, pull_over_flag=pull_over_flag, IW_check_release_params=IW_check_release_params, ans=ans)

    return ans

