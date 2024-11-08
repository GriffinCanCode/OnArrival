from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit,
                            QMessageBox, QStackedWidget, QSpinBox, QTextEdit,
                            QTreeWidget, QTreeWidgetItem, QTabWidget, QComboBox,
                            QDialog)
from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen, QLinearGradient
import sys
from services.location_alert_system import LocationAlertSystem
from gui.logo import OnArrivalLogo
from PyQt6.QtCore import QTimer
import threading
import math
from models.group import Group
from models.contact import Contact
from gui.contacts_manager import ContactsManager
from gui.gradient_button import GradientButton
from gui.stylesheets import MAIN_STYLE, DELETE_BUTTON_STYLE

class OnArrivalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnArrival")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(MAIN_STYLE)
        
        # Initialize the location alert system
        self.alert_system = LocationAlertSystem()
        
        # Start the Flask server in a separate thread
        flask_thread = threading.Thread(target=self.alert_system.notification_service.run, daemon=True)
        flask_thread.start()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create and add logo with transparent background
        self.logo = OnArrivalLogo(main_widget)
        main_layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add more spacing around logo
        main_layout.addSpacing(40)  # Increased from 20
        
        # Create screens widget
        self.screens_widget = QStackedWidget()
        
        # Create choice screen
        choice_screen = QWidget()
        choice_layout = QVBoxLayout(choice_screen)
        choice_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create button container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(20)

        # Create contacts button (25% smaller)
        contacts_btn = GradientButton("Contacts")
        contacts_btn.setFixedSize(225, 75)  # 25% smaller than other buttons
        contacts_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border-radius: 12px;
            }
        """)
        
        # Create business and leisure buttons
        business_btn = GradientButton("Business")
        leisure_btn = GradientButton("Leisure")
        
        # Style the main buttons
        for btn in [business_btn, leisure_btn]:
            btn.setFixedSize(300, 100)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    border-radius: 12px;
                }
            """)
        
        # Add contacts button
        button_layout.addWidget(contacts_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.addSpacing(10)  # Add some space between contacts and other buttons
        
        # Create and add the business/leisure container
        choice_widget = QWidget()
        choice_layout_h = QHBoxLayout(choice_widget)
        choice_layout_h.setSpacing(30)
        choice_layout_h.addWidget(business_btn)
        choice_layout_h.addWidget(leisure_btn)
        button_layout.addWidget(choice_widget)
        
        # Add button container to choice screen
        choice_layout.addWidget(button_container)
        
        # Create other screens
        self.business_screen = self.create_business_screen()
        self.leisure_screen = self.create_leisure_screen()
        self.contacts_screen = QWidget()
        contacts_layout = QVBoxLayout(self.contacts_screen)
        self.contacts_manager = ContactsManager(self.alert_system, self)
        contacts_layout.addWidget(self.contacts_manager)
        
        # Add all screens to the stacked widget
        self.screens_widget.addWidget(choice_screen)
        self.screens_widget.addWidget(self.business_screen)
        self.screens_widget.addWidget(self.leisure_screen)
        self.screens_widget.addWidget(self.contacts_screen)
        
        # Connect button signals
        contacts_btn.clicked.connect(self.show_contacts_manager)
        business_btn.clicked.connect(self.handle_business_click)
        leisure_btn.clicked.connect(self.handle_leisure_click)
        
        # Add screens widget to main layout
        main_layout.addWidget(self.screens_widget)
        
        # Show initial screen
        self.screens_widget.setCurrentWidget(choice_screen)
        
        # Initialize timer and business data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.timer_label = None
        self.business_phone = None
        self.use_timer = False  # Add flag for timer usage

    def handle_business_click(self):
        """Handle business button click with animation"""
        self.logo.rotate_to(-25)
        # Wait for animation to complete before changing screen
        QTimer.singleShot(300, self.show_business_screen)
        
    def handle_leisure_click(self):
        """Handle leisure button click with animation"""
        # Check if there are any groups
        groups = self.alert_system.contact_storage.load_groups()
        
        if not groups:
            QMessageBox.warning(
                self, 
                "No Groups", 
                "Please create a contact group first before using the leisure feature.\nWould you like to create one now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if QMessageBox.StandardButton.Yes:
                # Show contacts manager to create a group
                self.show_contacts_manager()
            return
        
        # If groups exist, proceed with leisure screen
        self.logo.rotate_to(25)
        QTimer.singleShot(300, self.show_leisure_screen)
        
        # Refresh the groups combo box
        self.refresh_groups_combo()
        
    def show_choice_screen(self, from_back_button=True):
        """Switch to the choice screen"""
        self.logo.rotate_to_without_ripple(0)  # Always use without ripple when returning to choice screen
        self.screens_widget.setCurrentIndex(0)  # First screen is choice screen

    def show_business_screen(self):
        """Switch to business screen with slide animation"""
        self.screens_widget.setCurrentIndex(1)

    def show_leisure_screen(self):
        """Switch to leisure screen with slide animation"""
        self.screens_widget.setCurrentIndex(2)

    def start_business_timer(self):
        """Start the business countdown timer"""
        business_name = self.business_name_input.text()
        phone = self.business_phone_input.text()
        message = self.message_input.toPlainText()
        
        if not all([business_name, phone, message]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields!")
            return
        
        # Store phone and message for later use
        self.business_phone = phone
        self.business_message = message
        
        # Convert minutes to seconds
        self.remaining_time = self.timer_input.value() * 60
        
        # Create or update timer label
        if not self.timer_label:
            self.timer_label = QLabel()
            self.business_screen.layout().addWidget(self.timer_label)
        
        # Update label and start timer
        self.update_timer()  # Initial update
        self.timer.start(1000)  # Update every second
        
        # Disable inputs while timer is running
        self.business_name_input.setEnabled(False)
        self.business_phone_input.setEnabled(False)
        self.timer_input.setEnabled(False)
        self.message_input.setEnabled(False)

    def update_timer(self):
        """Update the countdown timer display"""
        if self.remaining_time <= 0:
            self.timer.stop()
            self.timer_label.setText("Time's up!")
            
            # Send notification
            try:
                self.alert_system.notification_service.make_call(
                    self.business_phone,
                    self.business_message,
                    self.business_name  # Pass business name here too
                )
                QMessageBox.information(self, "Alert Sent", 
                                      f"Timer finished and alert sent to {self.business_name}!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to send alert: {str(e)}")
            
            # Re-enable inputs
            self.business_name_input.setEnabled(True)
            self.business_phone_input.setEnabled(True)
            self.timer_input.setEnabled(True)
            self.message_input.setEnabled(True)
            return
            
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"Time remaining: {minutes:02d}:{seconds:02d}")
        self.remaining_time -= 1

    def send_business_alert(self):
        """Send alert when business timer expires"""
        try:
            current_location = self.alert_system.location_service.get_current_location()
            self.alert_system.notification_service.make_call(
                self.business_contact["name"],
                self.business_contact["message"]
            )
            QMessageBox.information(self, "Success", "Business alert sent successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to send alert: {str(e)}")

    def refresh_contacts_list(self):
        """Refresh the contacts list display"""
        # Clear existing widgets
        for i in reversed(range(self.contacts_list_layout.count())): 
            self.contacts_list_layout.itemAt(i).widget().setParent(None)
        
        # Add each contact
        for contact in self.alert_system.contacts:
            contact_widget = QWidget()
            contact_layout = QHBoxLayout(contact_widget)
            
            contact_info = QLabel(f"{contact.name} - {contact.phone}")
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(DELETE_BUTTON_STYLE)
            delete_btn.clicked.connect(lambda checked, c=contact: self.delete_contact(c))
            
            contact_layout.addWidget(contact_info)
            contact_layout.addWidget(delete_btn)
            
            self.contacts_list_layout.addWidget(contact_widget)
            
            # Update contact widget styling
            contact_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px 0;
                }
                QWidget:hover {
                    background-color: #F8F9FA;
                    border-color: #3498DB;
                }
            """)
            
            contact_info.setStyleSheet("""
                QLabel {
                    color: #2C3E50;
                    font-size: 16px;
                    padding: 8px;
                }
            """)
            
            delete_btn.setStyleSheet(DELETE_BUTTON_STYLE)

    def send_location_alert(self):
        """Send location alert to contacts"""
        try:
            current_location = self.alert_system.location_service.get_current_location()
            selected_group = self.group_combo.currentText()
            
            if not selected_group:
                QMessageBox.warning(self, "Error", "Please select a group!")
                return

            groups = self.alert_system.contact_storage.load_groups()
            group = next((g for g in groups if g.name == selected_group), None)
            
            if not group:
                QMessageBox.warning(self, "Error", "Selected group not found!")
                return

            alerts_sent = False
            for location_name, location_data in self.alert_system.locations.items():
                if self.alert_system.location_service.is_within_radius(
                    current_location, 
                    location_data.coords, 
                    location_data.radius
                ):
                    for contact in group.contacts:
                        self.alert_system.notification_service.make_call(
                            contact.phone, 
                            location_data.message
                        )
                    alerts_sent = True
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Alerts sent to {len(group.contacts)} contacts in group {group.name}!"
                    )
                    break
            
            if not alerts_sent:
                QMessageBox.information(self, "Notice", "Not within any monitored locations")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to send alerts: {str(e)}")

    def send_leisure_alert(self):
        """Send alert using the leisure functionality"""
        try:
            selected_group = self.group_combo.currentText()
            
            if not selected_group:
                QMessageBox.warning(self, "Error", "Please select a group!")
                return

            groups = self.alert_system.contact_storage.load_groups()
            group = next((g for g in groups if g.name == selected_group), None)
            
            if not group:
                QMessageBox.warning(self, "Error", "Selected group not found!")
                return

            # Get message template or custom script
            if self.custom_script_toggle.isChecked():
                message_template = self.script_input.toPlainText()
                if not message_template or '()' not in message_template:
                    QMessageBox.warning(self, "Error", "Please enter a valid custom script with () for name placement!")
                    return
            else:
                message_template = self.alert_system.notification_service.get_script_templates()[self.script_combo.currentText()]

            # Send alerts to all contacts in group
            for contact in group.contacts:
                message = message_template.replace('()', contact.name)
                self.alert_system.notification_service.make_call(
                    contact.phone, 
                    message,
                    include_follow_up=True  # Add this parameter to include the follow-up message
                )
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Alerts sent to {len(group.contacts)} contacts in group {group.name}!"
            )
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to send alerts: {str(e)}")

    def update_gradient(self):
        """Update gradient animation for all buttons"""
        self.gradient_position = (self.gradient_position + 0.005) % 1.0
        # Force update of all gradient buttons
        for child in self.findChildren(GradientButton):
            child.update()

    def show_contacts_manager(self):
        """Switch to contacts management screen"""
        self.logo.rotate_to(180)  # Rotate logo upside down
        self.contacts_manager.reset_to_menu()  # Show the menu screen of contacts manager
        QTimer.singleShot(200, lambda: self.screens_widget.setCurrentIndex(3))  # Assuming it's the 4th screen

    def setup_contacts_screen(self):
        """Setup the contacts management screen"""
        pass

    def refresh_groups_combo(self):
        """Refresh the groups in the combo boxes"""
        try:
            # Temporarily disconnect the signal to prevent recursive calls
            self.group_combo.currentTextChanged.disconnect()
            
            self.group_combo.clear()
            groups = self.alert_system.contact_storage.load_groups()
            
            for group in groups:
                self.group_combo.addItem(group.name)
            
            # Update contact count label
            selected_group = self.group_combo.currentText()
            if selected_group:
                group = next((g for g in groups if g.name == selected_group), None)
                if group:
                    self.contact_count.setText(f"{len(group.contacts)} contacts will be notified")
                else:
                    self.contact_count.setText("0 contacts will be notified")
                
            # Reconnect the signal
            self.group_combo.currentTextChanged.connect(self.update_contact_count)
            
        except Exception as e:
            print(f"Error refreshing groups: {str(e)}")
            self.contact_count.setText("0 contacts will be notified")

    def update_contact_count(self, selected_group: str):
        """Update the contact count when group selection changes"""
        try:
            groups = self.alert_system.contact_storage.load_groups()
            group = next((g for g in groups if g.name == selected_group), None)
            if group:
                self.contact_count.setText(f"{len(group.contacts)} contacts will be notified")
            else:
                self.contact_count.setText("0 contacts will be notified")
        except Exception as e:
            print(f"Error updating contact count: {str(e)}")
            self.contact_count.setText("0 contacts will be notified")

    def create_business_screen(self):
        """Create the business screen"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a container for the form
        form_container = QWidget()
        form_container.setMaximumWidth(600)
        form_layout = QVBoxLayout(form_container)
        
        # Add input fields
        self.business_name_input = QLineEdit()
        self.business_name_input.setPlaceholderText("Business Name")
        
        self.business_phone_input = QLineEdit()
        self.business_phone_input.setPlaceholderText("Phone Number")
        
        # Create timer container
        timer_container = QWidget()
        timer_layout = QVBoxLayout(timer_container)
        
        # Add timer toggle button
        self.timer_toggle = GradientButton("Use Timer")
        self.timer_toggle.setCheckable(True)
        self.timer_toggle.clicked.connect(self.toggle_timer_input)
        
        # Add timer input (initially hidden)
        self.timer_input = QSpinBox()
        self.timer_input.setRange(1, 120)
        self.timer_input.setValue(30)
        self.timer_input.setSuffix(" minutes")
        self.timer_input.hide()
        
        timer_layout.addWidget(self.timer_toggle)
        timer_layout.addWidget(self.timer_input)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Message")
        self.message_input.setMaximumHeight(100)
        
        action_btn = GradientButton("Send Alert")
        back_btn = GradientButton("Back")
        back_btn.clicked.connect(lambda: self.handle_back_button())
        
        # Add widgets to layout
        form_layout.addWidget(self.business_name_input)
        form_layout.addWidget(self.business_phone_input)
        form_layout.addWidget(timer_container)
        form_layout.addWidget(self.message_input)
        form_layout.addWidget(action_btn)
        form_layout.addWidget(back_btn)
        
        # Add form container to main layout
        layout.addWidget(form_container)
        
        # Connect signals
        action_btn.clicked.connect(self.handle_business_action)
        back_btn.clicked.connect(lambda: self.handle_back_button())
        
        return screen

    def toggle_timer_input(self):
        """Toggle timer input visibility and usage"""
        self.use_timer = self.timer_toggle.isChecked()
        self.timer_input.setVisible(self.use_timer)
        
    def handle_business_action(self):
        """Handle business alert with optional timer"""
        business_name = self.business_name_input.text()
        phone = self.business_phone_input.text()
        message = self.message_input.toPlainText()
        
        if not all([business_name, phone, message]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields!")
            return
        
        # Store phone and message
        self.business_phone = phone
        self.business_message = message
        self.business_name = business_name  # Store business name
        
        if self.use_timer:
            # Start timer functionality
            self.remaining_time = self.timer_input.value() * 60
            
            # Create or update timer label
            if not self.timer_label:
                self.timer_label = QLabel()
                self.business_screen.layout().addWidget(self.timer_label)
            
            # Update label and start timer
            self.update_timer()
            self.timer.start(1000)
            
            # Disable inputs
            self.business_name_input.setEnabled(False)
            self.business_phone_input.setEnabled(False)
            self.timer_input.setEnabled(False)
            self.message_input.setEnabled(False)
            self.timer_toggle.setEnabled(False)
        else:
            # Send alert immediately
            try:
                self.alert_system.notification_service.make_call(
                    self.business_phone,
                    self.business_message,
                    business_name  # Pass business name to make_call
                )
                QMessageBox.information(self, "Alert Sent", 
                                      f"Alert sent to {business_name}!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to send alert: {str(e)}")

    def create_leisure_screen(self):
        """Create the leisure screen"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a container for the form
        form_container = QWidget()
        form_container.setMaximumWidth(600)
        form_layout = QVBoxLayout(form_container)
        
        # Add group selection
        self.group_combo = QComboBox()
        self.contact_count = QLabel("0 contacts will be notified")
        
        # Add script selection
        script_container = QWidget()
        script_layout = QVBoxLayout(script_container)
        
        script_label = QLabel("Select Message Type:")
        self.script_combo = QComboBox()
        self.script_combo.addItems(self.alert_system.notification_service.get_script_templates().keys())
        
        # Add custom script toggle and input
        self.custom_script_toggle = GradientButton("Use Custom Script")
        self.custom_script_toggle.setCheckable(True)
        self.custom_script_toggle.clicked.connect(self.toggle_script_input)
        
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter your message. Use () where you want to insert contact names.\nExample: Hello (), your message here")
        self.script_input.setMaximumHeight(100)
        self.script_input.hide()  # Initially hidden
        
        # Preview label
        self.preview_label = QLabel("Message Preview:")
        self.preview_text = QLabel()
        self.preview_text.setWordWrap(True)
        self.preview_text.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }")
        
        script_layout.addWidget(script_label)
        script_layout.addWidget(self.script_combo)
        script_layout.addWidget(self.preview_label)
        script_layout.addWidget(self.preview_text)
        
        send_btn = GradientButton("Send Alert")
        back_btn = GradientButton("Back")
        back_btn.clicked.connect(lambda: self.handle_back_button())
        
        # Add widgets to layout
        form_layout.addWidget(self.group_combo)
        form_layout.addWidget(self.contact_count)
        form_layout.addWidget(script_container)
        form_layout.addWidget(self.custom_script_toggle)
        form_layout.addWidget(self.script_input)
        form_layout.addWidget(send_btn)
        form_layout.addWidget(back_btn)
        
        # Add form container to main layout
        layout.addWidget(form_container)
        
        # Connect signals
        send_btn.clicked.connect(self.send_leisure_alert)
        back_btn.clicked.connect(lambda: self.handle_back_button())
        self.group_combo.currentTextChanged.connect(self.update_contact_count)
        self.script_combo.currentTextChanged.connect(self.update_message_preview)
        
        # Initial loads
        self.refresh_groups_combo()
        self.update_message_preview()
        
        return screen

    def update_message_preview(self):
        """Update the message preview with selected template"""
        if not self.custom_script_toggle.isChecked():
            template = self.alert_system.notification_service.get_script_templates()[self.script_combo.currentText()]
            self.preview_text.setText(template.replace('()', '[Contact Name]'))

    def toggle_script_input(self):
        """Toggle between custom and prewritten scripts"""
        is_custom = self.custom_script_toggle.isChecked()
        self.script_input.setVisible(is_custom)
        self.script_combo.setEnabled(not is_custom)
        self.preview_label.setVisible(not is_custom)
        self.preview_text.setVisible(not is_custom)

    def handle_back_button(self):
        """Handle back button clicks with rotation but no ripple"""
        self.logo.rotate_to_without_ripple(0)  # Rotate back to 0 degrees without ripple
        QTimer.singleShot(300, lambda: self.show_choice_screen())

def main():
    app = QApplication(sys.argv)
    window = OnArrivalGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 