class Values:
    toastvalue = 0
    speed = 0
    toastcount = 0
    totalcount = 0
    alpha = 0

    def __init__(self):
        super(Values, self).__init__()

    @staticmethod
    def get_toast_count():
        return Values.toastcount

    @staticmethod
    def set_toast_count(count):
        Values.toastcount = count

    @staticmethod
    def get_speed():
        return Values.speed

    @staticmethod
    def set_speed(spd):
        Values.speed = spd

    @staticmethod
    def get_total_count():
        return Values.totalcount

    @staticmethod
    def set_total_count(count):
        Values.totalcount = count


    @staticmethod
    def get_alpha():
        return Values.alpha

    @staticmethod
    def set_alpha(alp):
        Values.alpha = alp


    @staticmethod
    def get_toast_value():
        return Values.toastvalue

    @staticmethod
    def set_toast_value(toast):
        Values.toastvalue = toast