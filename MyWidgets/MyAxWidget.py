from PyQt5.QAxContainer import QAxWidget


class MyAxWidget(QAxWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
