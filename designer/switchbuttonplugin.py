from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from switchbutton import SwitchButton

class SwitchButtonPlugin(QPyDesignerCustomWidgetPlugin):

    # The __init__() method is only used to set up the plugin and define its
    # initialized variable.
    def __init__(self, parent=None):
    
        super(SwitchButtonPlugin, self).__init__(parent)

        self.initialized = False

    # The initialize() and isInitialized() methods allow the plugin to set up
    # any required resources, ensuring that this can only happen once for each
    # plugin.
    def initialize(self, core):

        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):

        return self.initialized

    # This factory method creates new instances of our custom widget with the
    # appropriate parent.
    def createWidget(self, parent):
        return SwitchButton(parent)

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return "SwitchButton"

    # Returns the name of the group in Qt Designer's widget box that this
    # widget belongs to.
    def group(self):
        return "PyQt Examples"

    # Return the icon used to represent the custom widget in Designer's widget
    # box.
    def icon(self):
        return QIcon(_logo_pixmap)

    # Returns a short description of the custom widget for use in a tool tip.
    def toolTip(self):
        return ""

    # Returns a short description of the custom widget for use in a "What's
    # This?" help message for the widget.
    def whatsThis(self):
        return ""

    # Returns True if the custom widget acts as a container for other widgets;
    # otherwise returns False. Note that plugins for custom containers also
    # need to provide an implementation of the QDesignerContainerExtension
    # interface if they need to add custom editing support to Qt Designer.
    def isContainer(self):
        return False
        
    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return "switchbutton"

        # Define the image used for the icon.
_logo_16x16_xpm = [
"16 16 61 1",
"6 c #5bbd7c",
"a c #7aaada",
"h c #7eaddb",
"n c #7faddb",
"E c #82afdc",
"x c #83b0dd",
"C c #84b0dd",
"z c #84b1dd",
"B c #85b1dd",
"u c #87b2de",
"U c #9ec1e4",
"Z c #9fc1e4",
"H c #a1c3e5",
"Y c #a5c5e4",
"V c #a6c6e4",
"P c #afcbe2",
"S c #afcbe3",
"O c #b1cde9",
"T c #b2cee9",
"t c #b4cee3",
"r c #b5cee3",
"q c #c2d8ee",
"0 c #c7dbef",
"f c #cedddb",
"b c #cfdddb",
"1 c #d0e1f2",
"J c #d8e2d2",
"I c #d9e2d2",
"# c #dfeaf6",
"g c #e3edf7",
"K c #ecf2f9",
"N c #ecf3f9",
"o c #eeecbb",
"i c #f2edb2",
"l c #f2edb3",
"w c #f6eea6",
"v c #f7eea6",
"W c #fcee8c",
"m c #fcfdfe",
"L c #fdec73",
"k c #fedd00",
"e c #fede06",
"p c #fede07",
"j c #fee013",
"X c #fee015",
"s c #fee223",
"d c #fee32c",
"A c #fee749",
"Q c #fee850",
"R c #fee851",
"D c #fee854",
"y c #feea65",
"M c #feec74",
"c c #feed7c",
"F c #feee85",
"G c #feee86",
"5 c #fef095",
"4 c #fef195",
"3 c #fef6bb",
"2 c #fefdf5",
". c #fefefe",
"..#abcdeedcfa#..",
".ghijkkkkkkjlhg.",
"mnopkkkkkkkkponm",
"qrskkkkkkkkkkstq",
"uvkkkkkkkkkkkkwu",
"xykkkkkkkkkkkkyx",
"zAkkkkkkkkkkkkAB",
"CDkkkkkkkkkkkkDC",
"EFkkkkkkkkkkkkGE",
"HIekkkkkkkkkkeJH",
"KBLkkkkkkkkkkMBN",
".OPQkkkkkkkkRST.",
"..UVWXkkkkXWYZ..",
"...0123453210...",
"6666666666666666",
"BBBBBBBBBBBBBBBB"]

_logo_pixmap = QPixmap(_logo_16x16_xpm)