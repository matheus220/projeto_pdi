class Values:
    toastquantity = 0
    speed = 0

    def __init__(self):
        super(Values, self).__init__()

    @staticmethod
    def get_toast_count():
        return Values.toastquantity

    @staticmethod
    def set_toast_count(count):
        Values.toastquantity = count

    @staticmethod
    def get_speed():
        return Values.speed

    @staticmethod
    def set_speed(spd):
        Values.speed = spd
