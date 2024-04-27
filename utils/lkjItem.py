class LkjItem(object):
    def __init__(self, item_name, time_stamp, details = {}):
        self.item_name = item_name
        self.time_stamp = time_stamp
        self.details = details
    
    def toStr(self):
        lkj_item = [self.time_stamp, self.item_name, self.details]
        str_lkj = ','.join([str(i) for i in lkj_item])
        return str_lkj
    