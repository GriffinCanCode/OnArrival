from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QLinearGradient

class GradientButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.primary_color = QColor("#3498DB")
        self.secondary_color = QColor("#27AE60")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get gradient position from parent window
        parent = self.window()
        gradient_pos = getattr(parent, 'gradient_position', 0)
            
        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt((0 + gradient_pos) % 1, self.primary_color)
        gradient.setColorAt((0.25 + gradient_pos) % 1, self.secondary_color)
        gradient.setColorAt((0.5 + gradient_pos) % 1, self.primary_color)
        gradient.setColorAt((0.75 + gradient_pos) % 1, self.secondary_color)
        gradient.setColorAt((1 + gradient_pos) % 1, self.primary_color)
        
        # Draw button background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path, gradient)
        
        # Draw text
        painter.setPen(QColor("white"))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())