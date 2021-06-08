from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

class DragDropImage(QWidget):
    def __init__(self, parent):
        super(DragDropImage, self).__init__()
        self.parent=parent
        parent.setAcceptDrops(True)

        parent.dragEnterEvent = self.dragEnterEvent 
        parent.dragMoveEvent = self.dragMoveEvent 
        parent.dropEvent = self.dropEvent 
 

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.parent.set_image(file_path)

            event.accept()
        else:
            event.ignore()



