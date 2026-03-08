import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

BOARD_SIZE = 8

class ChessBoard(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Настройки доски
        self.square_size = 80
        self.light_color = QColor("#f0d9b5")
        self.dark_color = QColor("#b58863")
        self.border_color = QColor("black")
        self.border_width = 3
        self.margin = 50

        # Координаты
        self.show_coords = True
        self.coord_font = QFont("Arial", 12)

        # Фигуры
        self.pieces = []
        self.piece_scale = 0.9

        # Drag & drop
        self.drag_item = None

        # Текстуры клеток
        self.light_texture = None
        self.dark_texture = None

        self.draw_board()

    def draw_board(self):
        self.scene.clear()
        size = BOARD_SIZE * self.square_size
        offset = self.margin

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = self.light_color if (r+c)%2==0 else self.dark_color
                rect = QGraphicsRectItem(offset + c*self.square_size,
                                         offset + r*self.square_size,
                                         self.square_size,
                                         self.square_size)
                if (r+c)%2==0 and self.light_texture:
                    rect.setBrush(QBrush(self.light_texture.scaled(self.square_size,self.square_size)))
                elif (r+c)%2==1 and self.dark_texture:
                    rect.setBrush(QBrush(self.dark_texture.scaled(self.square_size,self.square_size)))
                else:
                    rect.setBrush(QBrush(color))
                rect.setPen(QPen(Qt.GlobalColor.black,0))
                self.scene.addItem(rect)

        border = QGraphicsRectItem(offset, offset, size, size)
        border.setPen(QPen(self.border_color, self.border_width))
        border.setBrush(QBrush(Qt.GlobalColor.transparent))
        self.scene.addItem(border)

        if self.show_coords:
            for i in range(BOARD_SIZE):
                text_top = QGraphicsTextItem(chr(97+i))
                text_top.setFont(self.coord_font)
                text_top.setPos(offset + i*self.square_size + self.square_size/2 - 5, offset - 30)
                self.scene.addItem(text_top)

                text_bottom = QGraphicsTextItem(chr(97+i))
                text_bottom.setFont(self.coord_font)
                text_bottom.setPos(offset + i*self.square_size + self.square_size/2 -5, offset + size + 5)
                self.scene.addItem(text_bottom)

                text_left = QGraphicsTextItem(str(BOARD_SIZE-i))
                text_left.setFont(self.coord_font)
                text_left.setPos(offset -25, offset + i*self.square_size + self.square_size/2 -10)
                self.scene.addItem(text_left)

                text_right = QGraphicsTextItem(str(BOARD_SIZE-i))
                text_right.setFont(self.coord_font)
                text_right.setPos(offset + size +5, offset + i*self.square_size + self.square_size/2 -10)
                self.scene.addItem(text_right)

        for piece in self.pieces:
            self.scene.addItem(piece)

        self.setSceneRect(0,0,size+2*self.margin,size+2*self.margin)

    # Работа с фигурами
    def add_piece(self, pixmap, row, col):
        offset = self.margin
        size = self.square_size * self.piece_scale
        scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        item = QGraphicsPixmapItem(scaled)
        x = offset + col*self.square_size + (self.square_size - scaled.width())/2
        y = offset + row*self.square_size + (self.square_size - scaled.height())/2
        item.setPos(x, y)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(item)
        self.pieces.append(item)

    def remove_piece_at(self, pos):
        items = self.scene.items(pos)
        for item in items:
            if isinstance(item, QGraphicsPixmapItem):
                self.scene.removeItem(item)
                self.pieces.remove(item)
                break

    def clear_pieces(self):
        for p in self.pieces:
            self.scene.removeItem(p)
        self.pieces.clear()

    def export_png(self, path, dpi=300):
        rect = self.scene.sceneRect()
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        meter = dpi / 0.0254
        image.setDotsPerMeterX(int(meter))
        image.setDotsPerMeterY(int(meter))
        image.save(path)

    # Текстуры клеток
    def set_light_texture(self,path):
        if path:
            self.light_texture = QPixmap(path)
            self.draw_board()
    def set_dark_texture(self,path):
        if path:
            self.dark_texture = QPixmap(path)
            self.draw_board()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Diagram Editor V3")
        self.resize(1300, 800)

        self.board = ChessBoard()
        self.piece_list = QListWidget()
        self.piece_pixmaps = []

        self.init_ui()
        self.board.viewport().installEventFilter(self)

    def init_ui(self):
        load_piece = QPushButton("Load Piece PNG/SVG")
        load_piece.clicked.connect(self.load_piece)

        clear = QPushButton("Clear Board")
        clear.clicked.connect(self.board.clear_pieces)

        start = QPushButton("Start Position")
        start.clicked.connect(self.start_position)

        export = QPushButton("Export PNG 300 DPI")
        export.clicked.connect(lambda: self.export_png(300))
        export_hd = QPushButton("Export PNG 600 DPI")
        export_hd.clicked.connect(lambda: self.export_png(600))

        square_size_spin = QSpinBox()
        square_size_spin.setRange(40,200)
        square_size_spin.setValue(self.board.square_size)
        square_size_spin.valueChanged.connect(self.change_square_size)

        piece_size_spin = QSpinBox()
        piece_size_spin.setRange(20,120)
        piece_size_spin.setValue(90)
        piece_size_spin.valueChanged.connect(self.change_piece_size)

        light_btn = QPushButton("Set Light Cell Texture")
        light_btn.clicked.connect(self.set_light_texture)
        dark_btn = QPushButton("Set Dark Cell Texture")
        dark_btn.clicked.connect(self.set_dark_texture)

        border_color_btn = QPushButton("Border Color")
        border_color_btn.clicked.connect(self.change_border_color)
        border_width_spin = QSpinBox()
        border_width_spin.setRange(1,10)
        border_width_spin.setValue(self.board.border_width)
        border_width_spin.valueChanged.connect(self.change_border_width)

        coords_font_btn = QPushButton("Coordinates Font Size")
        coords_font_btn.clicked.connect(self.change_coords_font)

        left = QVBoxLayout()
        left.addWidget(QLabel("Loaded Pieces"))
        left.addWidget(self.piece_list)
        left.addWidget(load_piece)
        left.addWidget(start)
        left.addWidget(clear)
        left.addWidget(export)
        left.addWidget(export_hd)
        left.addWidget(QLabel("Square Size"))
        left.addWidget(square_size_spin)
        left.addWidget(QLabel("Piece Size %"))
        left.addWidget(piece_size_spin)
        left.addWidget(light_btn)
        left.addWidget(dark_btn)
        left.addWidget(border_color_btn)
        left.addWidget(QLabel("Border Width"))
        left.addWidget(border_width_spin)
        left.addWidget(coords_font_btn)
        left.addStretch()

        container = QWidget()
        layout = QHBoxLayout()
        layout.addLayout(left)
        layout.addWidget(self.board)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_piece(self):
        path,_ = QFileDialog.getOpenFileName(self,"Load Piece","","Images (*.png *.svg)")
        if path:
            pix = QPixmap(path)
            self.piece_pixmaps.append(pix)
            self.piece_list.addItem(path.split("/")[-1])

    def change_square_size(self,val):
        self.board.square_size = val
        self.board.draw_board()
    def change_piece_size(self,val):
        self.board.piece_scale = val/100
        self.board.draw_board()
    def change_border_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.board.border_color=c
            self.board.draw_board()
    def change_border_width(self,val):
        self.board.border_width=val
        self.board.draw_board()
    def change_coords_font(self):
        size,ok=QInputDialog.getInt(self,"Font Size","Enter font size:",self.board.coord_font.pointSize(),5,50)
        if ok:
            self.board.coord_font.setPointSize(size)
            self.board.draw_board()
    def set_light_texture(self):
        path,_=QFileDialog.getOpenFileName(self,"Select Light Cell Texture","","Images (*.png *.jpg)")
        self.board.set_light_texture(path)
    def set_dark_texture(self):
        path,_=QFileDialog.getOpenFileName(self,"Select Dark Cell Texture","","Images (*.png *.jpg)")
        self.board.set_dark_texture(path)
    def export_png(self,dpi):
        path,_ = QFileDialog.getSaveFileName(self,"Export PNG","","PNG (*.png)")
        if path:
            self.board.export_png(path,dpi=dpi)
    def start_position(self):
        if len(self.piece_pixmaps)<6: return
        self.board.clear_pieces()
        p = self.piece_pixmaps
        for c in range(8):
            self.board.add_piece(p[0],1,c)
            self.board.add_piece(p[0],6,c)
        back=[1,2,3,4,5,3,2,1]
        for c,t in enumerate(back):
            self.board.add_piece(p[t],0,c)
            self.board.add_piece(p[t],7,c)

    def eventFilter(self,obj,event):
        if event.type()==QEvent.Type.MouseButtonPress:
            if event.button()==Qt.MouseButton.RightButton:
                pos=self.board.mapToScene(event.pos())
                self.board.remove_piece_at(pos)
        return super().eventFilter(obj,event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
