from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings


class MyWebWidget(QWebEngineView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
