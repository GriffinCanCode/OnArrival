from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QImage, QPen

class OnArrivalLogo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Logo widget initialized")  # Debug print
        
        # Debug size and visibility
        self.setFixedSize(120, 120)
        print(f"Logo size: {self.size()}")
        
        # Make widget transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        
        # Remove debug styling
        self.setStyleSheet("")
        
        # Remove margins
        self.setContentsMargins(0, 0, 0, 0)
        
        print(f"Logo visible: {self.isVisible()}")
        print(f"Logo geometry: {self.geometry()}")
        
        # Ensure widget is visible and has proper size
        self.setVisible(True)
        self.setFixedSize(120, 120)
        
        # Force white background and remove transparency
        self.setAutoFillBackground(False)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#FFFFFF"))
        self.setPalette(palette)
        
        # State properties
        self.gradient_position = 0.0
        self.scale = 1.0
        self.target_scale = 1.0
        self.hover_opacity = 0.0
        
        # Animation timers
        self.gradient_timer = QTimer(self)
        self.gradient_timer.timeout.connect(self.update_gradient)
        self.gradient_timer.start(50)
        
        # Colors
        self.primary_color = QColor("#3498DB")
        self.secondary_color = QColor("#27AE60")
        self.accent_color = QColor("#E74C3C")
        
        # Rotation animation properties
        self.rotation_angle = 0.0
        self.target_rotation = 0.0
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.setInterval(16)
        
        # Ripple properties
        self.ripples = []
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.update_ripples)
        self.ripple_timer.setInterval(16)
        self.ripple_timer.start()
        
        # Bounce animation
        self.bounce_timer = QTimer(self)
        self.bounce_timer.timeout.connect(self.update_bounce)
        self.bounce_timer.setInterval(16)
        
        # Make widget clickable
        self.setMouseTracking(True)
        
    def sizeHint(self):
        """Override size hint to account for ripples"""
        base_size = QSize(120, 120)  # Match the fixed size
        # Add much more extra space for ripples
        return QSize(base_size.width() * 5, base_size.height() * 5)  # Increased multiplier from 3 to 5
        
    def mousePressEvent(self, event):
        """Handle mouse click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Start bounce animation
            self.target_scale = 0.9  # Compress
            self.bounce_timer.start()
            
            # Add new ripple
            self.add_ripple()
            
    def add_ripple(self):
        """Add a new ripple effect"""
        self.ripples.append((0.0, 1.0))  # Increased initial opacity from 0.8 to 1.0
        if not self.ripple_timer.isActive():
            self.ripple_timer.start()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release event"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Expand back
            self.target_scale = 1.0
            self.bounce_timer.start()
            
    def update_bounce(self):
        """Update bounce animation"""
        diff = self.target_scale - self.scale
        step = 0.1
        
        if abs(diff) < 0.01:
            self.scale = self.target_scale
            self.bounce_timer.stop()
        else:
            self.scale += diff * step
            
        self.update()
        
    def rotate_to(self, angle):
        """Start rotation animation to specified angle with ripple effect"""
        self.target_rotation = angle
        self.rotation_timer.start()
        self.add_ripple()  # Add ripple effect
        
    def update_rotation(self):
        """Update rotation animation"""
        diff = self.target_rotation - self.rotation_angle
        step = 0.2  # Adjust for faster/slower rotation
        
        if abs(diff) < step:
            self.rotation_angle = self.target_rotation
            self.rotation_timer.stop()
        else:
            # Fix: Update rotation_angle instead of scale
            self.rotation_angle += diff * step
            
        self.update()
        
    def update_ripples(self):
        """Update ripple animation state"""
        if not self.isVisible():
            return
            
        updated_ripples = []
        for size, opacity in self.ripples:
            if opacity <= 0:
                continue
            # Slower expansion speed
            new_size = min(size + 0.02, 4.0)  # Reduced from 0.04 to 0.02 for more gradual expansion
            # More gradual fade
            fade_factor = 1.0 - (new_size / 4.0) ** 1.5  # Changed from quadratic (2) to 1.5 power for more gradual fade
            new_opacity = max(opacity * fade_factor, 0)
            updated_ripples.append((new_size, new_opacity))
        
        self.ripples = updated_ripples
        if self.ripples:
            self.update()
            
    def update_gradient(self):
        """Update gradient animation"""
        self.gradient_position = (self.gradient_position + 0.01) % 1.0
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Make background transparent
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        
        # Save the current state
        painter.save()
        
        # Apply rotation around center point
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.rotation_angle)
        painter.translate(-self.width() / 2, -self.height() / 2)
        
        # Draw ripples first (behind the logo)
        for size, opacity in self.ripples:
            ripple_size = self.width() * size
            painter.setOpacity(opacity * 0.4)  # Reduced from 0.6 to 0.4 for subtler ripples
            
            # Create gradient for ripple
            ripple_gradient = QLinearGradient(
                float(self.width()/2 - ripple_size/2), float(self.height()/2 - ripple_size/2),
                float(self.width()/2 + ripple_size/2), float(self.height()/2 + ripple_size/2)
            )
            ripple_gradient.setColorAt(0, QColor("#2196F3"))  # Blue
            ripple_gradient.setColorAt(1, QColor("#4CAF50"))  # Green
            
            # Create thicker pen with gradient
            pen = QPen()
            pen.setWidth(2)  # Reduced from 3 to 2 for more subtle ripples
            pen.setBrush(ripple_gradient)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Center the ripple
            ripple_rect = QRect(
                int(self.width()/2 - ripple_size/2),
                int(self.height()/2 - ripple_size/2),
                int(ripple_size),
                int(ripple_size)
            )
            painter.drawEllipse(ripple_rect)
        
        # Reset opacity for main logo
        painter.setOpacity(1.0)
        
        # Calculate circle dimensions to fill most of the widget
        circle_size = min(self.width(), self.height()) * 0.8  # 80% of widget size
        circle_rect = QRect(
            int(self.width()/2 - circle_size/2),
            int(self.height()/2 - circle_size/2),
            int(circle_size),
            int(circle_size)
        )
        
        # Create gradient background for circle
        gradient = QLinearGradient(
            float(circle_rect.x()), float(circle_rect.y()),  # Start point
            float(circle_rect.x() + circle_rect.width()), float(circle_rect.y() + circle_rect.height())  # End point
        )
        gradient.setColorAt(0, QColor("#2196F3"))  # Blue
        gradient.setColorAt(1, QColor("#4CAF50"))  # Green
        
        # Draw the circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(circle_rect)
        
        # Save current transform
        painter.save()
        
        # Apply scaling animation
        painter.translate(self.width()/2, self.height()/2)
        painter.scale(self.scale, self.scale)
        painter.translate(-self.width()/2, -self.height()/2)
        
        # Calculate arrow dimensions
        width = int(circle_size * 0.5)  # Convert to int
        height = int(width * 1.3)       # Convert to int
        
        # Create arrow path
        path = QPainterPath()
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # Calculate points for arrow with inward bottom curve
        top_y = int(center.y() - height/2)
        bottom_y = int(center.y() + height/3)
        
        # Create arrow shape with inward curve at bottom
        path.moveTo(center.x(), top_y)  # Top point
        path.lineTo(center.x() - width//2, bottom_y)  # Bottom left
        
        # Add curved bottom (inward notch) using float coordinates
        control_x = float(center.x())
        control_y = float(bottom_y + height/6)
        end_x = float(center.x() + width//2)
        end_y = float(bottom_y)
        
        # Use quadTo with float coordinates
        path.quadTo(control_x, control_y, end_x, end_y)
        
        path.closeSubpath()
        
        # Draw arrow in white
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))  # Pure white
        painter.drawPath(path)
        
        # Restore transform
        painter.restore()
        
        painter.end()
        
    def rotate_to_without_ripple(self, angle):
        """Start rotation animation to specified angle without ripple effect"""
        self.target_rotation = angle
        self.rotation_timer.start()
        # No ripple effect added here