import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import Qt


class TransparentImageViewer(QWidget):
    def __init__(self, image_path: str):
        super().__init__()

        # Stato
        self.mirrored = False
        self.current_scale = 1.5
        self.start_pos = None

        # Finestra: frameless + always on top (NO Qt.Tool)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Per ricevere eventi tastiera anche su finestra frameless
        self.setFocusPolicy(Qt.StrongFocus)

        # Blocca menu contestuali
        self.setContextMenuPolicy(Qt.NoContextMenu)

        # Label immagine
        self.label = QLabel(self)
        self.label.setContextMenuPolicy(Qt.NoContextMenu)

        # Fondamentale: gli eventi mouse devono arrivare al QWidget, non alla QLabel
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Carica immagine
        self.original_pixmap = QPixmap(image_path)

        # Allinea subito stato e vista (evita il bug della prima rotella)
        self.update_pixmap()

        # Centra sullo schermo (dopo update_pixmap, così usa le dimensioni reali)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_pixmap(self):
        pixmap = self.original_pixmap

        if self.mirrored:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))

        new_width = max(10, int(pixmap.width() * self.current_scale))
        new_height = max(10, int(pixmap.height() * self.current_scale))

        scaled_pixmap = pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.label.setPixmap(scaled_pixmap)
        self.label.resize(scaled_pixmap.size())
        self.resize(scaled_pixmap.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            # IMPORTANTISSIMO: non chiudere qui, chiudi al release (Windows apre menu sul release)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            self.move(event.globalPos() - self.start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = None
            event.accept()
        elif event.button() == Qt.RightButton:
            event.accept()
            self.close()

    def wheelEvent(self, event):
        # Robusto: giù = riduci, su = aumenta
        if event.angleDelta().y() < 0:
            self.current_scale *= 0.9
        else:
            self.current_scale *= 1.1

        self.update_pixmap()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right):
            self.mirrored = not self.mirrored
            self.update_pixmap()
            event.accept()
        elif event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Trascina un file PNG sull'eseguibile oppure passa un file PNG come argomento.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    viewer = TransparentImageViewer(sys.argv[1])
    viewer.show()
    viewer.setFocus()  # utile per le frecce appena aperta
    sys.exit(app.exec_())
