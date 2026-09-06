from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QMessageBox, QStackedWidget, 
                            QSpinBox, QTextEdit, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt
import sys
import os

# Add the parent directory to sys.path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.location_alert_system import LocationAlertSystem
from gui.stylesheets import Stylesheets
from gui.gradient_button import GradientButton
from gui.contacts_manager import ContactsManager
from gui.logo import create_icon_label
from utils.validation import InputValidator, ValidationResult

class OnArrivalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnArrival")
        self.setGeometry(100, 100, 500, 700)
        
        # Initialize alert system
        try:
            self.alert_system = LocationAlertSystem()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize alert system: {str(e)}")
            sys.exit(1)
        
        # Timer for business functionality
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.timer_label = None
        self.use_timer = False
        
        # Business contact info
        self.business_phone = None
        self.business_message = None
        self.business_name = None
        
        self.init_ui()
        self.setStyleSheet(Stylesheets.get_main_style())

    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create stacked widget for different screens
        self.screens_widget = QStackedWidget()
        main_layout.addWidget(self.screens_widget)
        
        # Create screens
        self.main_screen = self.create_main_screen()
        self.business_screen = self.create_business_screen()
        self.leisure_screen = self.create_leisure_screen()
        
        # Add screens to stacked widget
        self.screens_widget.addWidget(self.main_screen)
        self.screens_widget.addWidget(self.business_screen)
        self.screens_widget.addWidget(self.leisure_screen)
        
        # Show main screen initially
        self.screens_widget.setCurrentIndex(0)

    def create_main_screen(self):
        """Create the main menu screen"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Add logo
        logo_label = create_icon_label()
        layout.addWidget(logo_label)
        
        # Add title
        title = QLabel("OnArrival")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #2C3E50;
            margin: 20px 0;
        """)
        layout.addWidget(title)
        
        # Add subtitle
        subtitle = QLabel("Automated Arrival Notification System")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7F8C8D;
            margin-bottom: 30px;
        """)
        layout.addWidget(subtitle)
        
        # Create buttons container
        buttons_container = QWidget()
        buttons_container.setMaximumWidth(300)
        buttons_layout = QVBoxLayout(buttons_container)
        
        # Business Alert button
        business_btn = GradientButton("Business Alert")
        business_btn.clicked.connect(self.show_business_screen)
        buttons_layout.addWidget(business_btn)
        
        # Leisure Alert button
        leisure_btn = GradientButton("Leisure Alert")
        leisure_btn.clicked.connect(self.show_leisure_screen)
        buttons_layout.addWidget(leisure_btn)
        
        # Contacts button
        contacts_btn = GradientButton("Manage Contacts")
        contacts_btn.clicked.connect(self.open_contacts_manager)
        buttons_layout.addWidget(contacts_btn)
        
        layout.addWidget(buttons_container)
        layout.addStretch()
        
        return screen

    def validate_business_inputs(self, business_name: str, phone: str, message: str, timer_minutes: int = None) -> tuple[bool, str]:
        """Validate business alert inputs"""
        # Validate business name
        business_validation = InputValidator.validate_business_name(business_name)
        if not business_validation.is_valid:
            return False, f"Business name error: {business_validation.error_message}"
        
        # Validate phone number
        phone_validation = InputValidator.validate_phone_number(phone)
        if not phone_validation.is_valid:
            return False, f"Phone number error: {phone_validation.error_message}"
        
        # Validate message
        message_validation = InputValidator.validate_message(message)
        if not message_validation.is_valid:
            return False, f"Message error: {message_validation.error_message}"
        
        # Validate timer if provided
        if timer_minutes is not None:
            timer_validation = InputValidator.validate_timer_minutes(timer_minutes)
            if not timer_validation.is_valid:
                return False, f"Timer error: {timer_validation.error_message}"
        
        return True, "All inputs valid"

    def validate_leisure_inputs(self, group_name: str, message: str) -> tuple[bool, str]:
        """Validate leisure alert inputs"""
        # Validate group name
        if not group_name.strip():
            return False, "Please select a group"
        
        group_validation = InputValidator.validate_group_name(group_name)
        if not group_validation.is_valid:
            return False, f"Group name error: {group_validation.error_message}"
        
        # Validate message
        message_validation = InputValidator.validate_message(message)
        if not message_validation.is_valid:
            return False, f"Message error: {message_validation.error_message}"
        
        return True, "All inputs valid"

    def sanitize_business_inputs(self, business_name: str, phone: str, message: str) -> tuple[str, str, str]:
        """Sanitize business inputs and return cleaned values"""
        business_validation = InputValidator.validate_business_name(business_name)
        phone_validation = InputValidator.validate_phone_number(phone)
        message_validation = InputValidator.validate_message(message)
        
        return (
            business_validation.sanitized_value,
            phone_validation.sanitized_value,
            message_validation.sanitized_value
        )

    def open_contacts_manager(self):
        """Open the contacts manager window"""
        try:
            self.contacts_manager = ContactsManager(self.alert_system, self)
            self.contacts_manager.show()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open contacts manager: {str(e)}")

    def handle_back_button(self):
        """Handle back button clicks"""
        # Reset timer if it was running
        if self.timer.isActive():
            self.timer.stop()
            self.remaining_time = 0
            
            # Re-enable inputs
            if hasattr(self, 'business_name_input'):
                self.business_name_input.setEnabled(True)
                self.business_phone_input.setEnabled(True)
                self.timer_input.setEnabled(True)
                self.message_input.setEnabled(True)
                if hasattr(self, 'timer_toggle'):
                    self.timer_toggle.setEnabled(True)
        
        # Go back to main screen
        self.screens_widget.setCurrentIndex(0)

    def show_business_screen(self):
        """Switch to business screen with slide animation"""
        self.screens_widget.setCurrentIndex(1)

    def show_leisure_screen(self):
        """Switch to leisure screen with slide animation"""
        self.screens_widget.setCurrentIndex(2)

    def start_business_timer(self):
        """Start the business countdown timer"""
        business_name = self.business_name_input.text().strip()
        phone = self.business_phone_input.text().strip()
        message = self.message_input.toPlainText().strip()
        timer_minutes = self.timer_input.value()
        
        # Validate inputs
        is_valid, error_msg = self.validate_business_inputs(business_name, phone, message, timer_minutes)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        # Sanitize inputs
        sanitized_business, sanitized_phone, sanitized_message = self.sanitize_business_inputs(
            business_name, phone, message
        )
        
        # Store sanitized values for later use
        self.business_phone = sanitized_phone
        self.business_message = sanitized_message
        self.business_name = sanitized_business
        
        # Convert minutes to seconds
        self.remaining_time = timer_minutes * 60
        
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
                    self.business_name
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

    def send_leisure_alert(self):
        """Send alert using the leisure functionality"""
        try:
            selected_group = self.group_combo.currentText()
            
            # Validate group selection
            if not selected_group:
                QMessageBox.warning(self, "Error", "Please select a group!")
                return

            groups = self.alert_system.contact_storage.load_groups()
            group = next((g for g in groups if g.name == selected_group), None)
            
            if not group:
                QMessageBox.warning(self, "Error", "Selected group not found!")
                return
            
            if not group.contacts:
                QMessageBox.warning(self, "Error", f"Group '{selected_group}' has no contacts!")
                return

            # Get message template or custom script
            if self.custom_script_toggle.isChecked():
                message_template = self.script_input.toPlainText().strip()
                if not message_template or '()' not in message_template:
                    QMessageBox.warning(self, "Error", "Please enter a valid custom script with () for name placement!")
                    return
            else:
                selected_script = self.script_combo.currentText()
                if not selected_script:
                    QMessageBox.warning(self, "Error", "Please select a message script!")
                    return
                message_template = self.alert_system.notification_service.get_script_templates()[selected_script]

            # Validate inputs
            is_valid, error_msg = self.validate_leisure_inputs(selected_group, message_template)
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error_msg)
                return

            # Send alerts to all contacts in group
            success_count = 0
            error_messages = []
            
            for contact in group.contacts:
                try:
                    # Sanitize message for each contact
                    message_validation = InputValidator.validate_message(message_template.replace('()', contact.name))
                    if not message_validation.is_valid:
                        error_messages.append(f"Invalid message for {contact.name}: {message_validation.error_message}")
                        continue
                    
                    sanitized_message = message_validation.sanitized_value
                    
                    result = self.alert_system.notification_service.make_call(
                        contact.phone, 
                        sanitized_message,
                        include_follow_up=True
                    )
                    
                    if result:
                        success_count += 1
                    else:
                        error_messages.append(f"Failed to send alert to {contact.name}")
                        
                except Exception as e:
                    error_messages.append(f"Error sending to {contact.name}: {str(e)}")
            
            # Show results
            if success_count > 0:
                result_msg = f"Alerts sent to {success_count} of {len(group.contacts)} contacts in group {group.name}!"
                if error_messages:
                    result_msg += f"\n\nErrors encountered:\n" + "\n".join(error_messages[:5])  # Show first 5 errors
                QMessageBox.information(self, "Alert Results", result_msg)
            else:
                error_msg = "Failed to send any alerts."
                if error_messages:
                    error_msg += f"\n\nErrors:\n" + "\n".join(error_messages[:5])
                QMessageBox.warning(self, "Alert Failed", error_msg)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to send alerts: {str(e)}")

    def refresh_groups_combo(self):
        """Refresh the groups combo box with validation"""
        try:
            groups = self.alert_system.contact_storage.load_groups()
            self.group_combo.clear()
            
            valid_groups = []
            for group in groups:
                # Validate group integrity
                validation_result = group.validate_group_integrity()
                if validation_result.is_valid:
                    valid_groups.append(group.name)
                else:
                    print(f"Warning: Group '{group.name}' has validation issues: {validation_result.error_message}")
            
            self.group_combo.addItems(valid_groups)
            
            if valid_groups:
                self.update_contact_count(valid_groups[0])
            else:
                self.contact_count.setText("No valid groups available")
                
        except Exception as e:
            print(f"Error refreshing groups: {str(e)}")
            self.contact_count.setText("Error loading groups")

    def update_contact_count(self, selected_group: str):
        """Update the contact count when group selection changes"""
        try:
            groups = self.alert_system.contact_storage.load_groups()
            group = next((g for g in groups if g.name == selected_group), None)
            if group:
                count = len(group.contacts)
                self.contact_count.setText(f"{count} contact{'s' if count != 1 else ''} will be notified")
            else:
                self.contact_count.setText("0 contacts will be notified")
        except Exception as e:
            print(f"Error updating contact count: {str(e)}")
            self.contact_count.setText("Error loading contact count")

    def create_business_screen(self):
        """Create the business screen"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a container for the form
        form_container = QWidget()
        form_container.setMaximumWidth(600)
        form_layout = QVBoxLayout(form_container)
        
        # Add input fields with placeholders that show validation requirements
        self.business_name_input = QLineEdit()
        self.business_name_input.setPlaceholderText("Business Name (letters, numbers, spaces, common punctuation)")
        
        self.business_phone_input = QLineEdit()
        self.business_phone_input.setPlaceholderText("Phone Number (e.g., +1234567890 or (123) 456-7890)")
        
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
        self.message_input.setPlaceholderText("Message (max 1600 characters)")
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
        business_name = self.business_name_input.text().strip()
        phone = self.business_phone_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        # Validate inputs
        timer_minutes = self.timer_input.value() if self.use_timer else None
        is_valid, error_msg = self.validate_business_inputs(business_name, phone, message, timer_minutes)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        # Sanitize inputs
        sanitized_business, sanitized_phone, sanitized_message = self.sanitize_business_inputs(
            business_name, phone, message
        )
        
        # Store sanitized values
        self.business_phone = sanitized_phone
        self.business_message = sanitized_message
        self.business_name = sanitized_business
        
        if self.use_timer:
            # Start timer functionality
            self.remaining_time = timer_minutes * 60
            
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
                result = self.alert_system.notification_service.make_call(
                    sanitized_phone,
                    sanitized_message,
                    business_name=sanitized_business
                )
                if result:
                    QMessageBox.information(self, "Alert Sent", 
                                          f"Alert sent successfully to {sanitized_business}!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to send alert")
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
        
        # Group selection
        self.group_combo = QComboBox()
        self.contact_count = QLabel("0 contacts will be notified")
        
        # Script selection container
        script_container = QWidget()
        script_layout = QVBoxLayout(script_container)
        
        self.script_combo = QComboBox()
        
        # Load scripts with error handling
        try:
            scripts = self.alert_system.notification_service.get_script_templates()
            self.script_combo.addItems(scripts.keys())
        except Exception as e:
            print(f"Error loading scripts: {e}")
            self.script_combo.addItems(["Basic Arrival"])
        
        # Message preview
        self.preview_label = QLabel("Message Preview:")
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(80)
        self.preview_text.setReadOnly(True)
        
        script_layout.addWidget(self.script_combo)
        script_layout.addWidget(self.preview_label)
        script_layout.addWidget(self.preview_text)
        
        # Custom script toggle
        self.custom_script_toggle = QCheckBox("Use Custom Script")
        self.custom_script_toggle.clicked.connect(self.toggle_script_input)
        
        # Custom script input (initially hidden)
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter custom message. Use () for name placement (max 1600 characters)")
        self.script_input.setMaximumHeight(100)
        self.script_input.hide()
        
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
            try:
                selected_script = self.script_combo.currentText()
                if selected_script:
                    template = self.alert_system.notification_service.get_script_templates()[selected_script]
                    self.preview_text.setText(template.replace('()', '[Contact Name]'))
                else:
                    self.preview_text.setText("No script selected")
            except Exception as e:
                self.preview_text.setText(f"Error loading script: {str(e)}")

    def toggle_script_input(self):
        """Toggle between custom and prewritten scripts"""
        is_custom = self.custom_script_toggle.isChecked()
        self.script_input.setVisible(is_custom)
        self.script_combo.setEnabled(not is_custom)
        self.preview_label.setVisible(not is_custom)
        self.preview_text.setVisible(not is_custom)

def main():
    app = QApplication(sys.argv)
    window = OnArrivalGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 