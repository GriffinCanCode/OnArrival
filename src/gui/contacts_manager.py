from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, 
                            QMessageBox, QWidget, QStackedWidget, QComboBox, QMainWindow)
from PyQt6.QtCore import Qt, QTimer
from models.group import Group
from models.contact import Contact
from .gradient_button import GradientButton
from .stylesheets import MAIN_STYLE

class ContactsManager(QWidget):
    def __init__(self, alert_system, parent=None):
        super().__init__(parent)
        self.alert_system = alert_system
        self.main_window = parent
        self.setMinimumSize(600, 400)
        
        # Use the main stylesheet
        self.setStyleSheet(MAIN_STYLE)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create stacked widget for different screens
        self.screens = QStackedWidget()
        
        # Create screens
        self.menu_screen = self.create_menu_screen()
        self.management_screen = self.create_management_screen()
        
        # Add screens to stacked widget
        self.screens.addWidget(self.menu_screen)
        self.screens.addWidget(self.management_screen)
        
        layout.addWidget(self.screens)
        
        # Show menu screen initially
        self.screens.setCurrentWidget(self.menu_screen)

    def reset_to_menu(self):
        """Reset to menu screen"""
        self.screens.setCurrentWidget(self.menu_screen)

    def create_menu_screen(self):
        """Create the initial menu screen with two buttons"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        choose_group_btn = GradientButton("Choose Existing Group")
        create_group_btn = GradientButton("Create New Group")
        back_btn = GradientButton("Back to Main Menu")
        
        layout.addStretch(1)
        layout.addWidget(choose_group_btn)
        layout.addWidget(create_group_btn)
        layout.addWidget(back_btn)
        layout.addStretch(1)
        
        choose_group_btn.clicked.connect(self.show_group_selection_dialog)
        create_group_btn.clicked.connect(self.show_group_creation_dialog)
        back_btn.clicked.connect(self.go_back_to_main)  # Use new method
        
        return screen

    def go_back_to_main(self):
        """Helper method to return to main menu"""
        if isinstance(self.main_window, QMainWindow):
            self.main_window.logo.rotate_to_without_ripple(0)  # Use without_ripple method
            QTimer.singleShot(200, lambda: self.main_window.show_choice_screen(from_back_button=True))

    def create_management_screen(self):
        """Create the group management screen"""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setSpacing(20)
        
        # Add a back button at the top
        back_to_menu_btn = GradientButton("← Back to Groups")
        back_to_menu_btn.clicked.connect(lambda: (
            self.screens.setCurrentWidget(self.menu_screen),
            self.setWindowTitle("Contacts Manager")
        ))
        layout.addWidget(back_to_menu_btn)
        
        # Group name header
        self.group_name_label = QLabel()
        self.group_name_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            padding: 10px;
        """)
        
        # Contact controls
        contact_controls = QHBoxLayout()
        self.contact_name_input = QLineEdit()
        self.contact_phone_input = QLineEdit()
        self.contact_name_input.setPlaceholderText("Contact Name")
        self.contact_phone_input.setPlaceholderText("Phone Number")
        add_contact_btn = GradientButton("Add Contact")
        
        contact_controls.addWidget(self.contact_name_input)
        contact_controls.addWidget(self.contact_phone_input)
        contact_controls.addWidget(add_contact_btn)
        
        # Contacts tree with specific styling that's not in main stylesheet
        self.contacts_tree = QTreeWidget()
        self.contacts_tree.setHeaderLabels(["Name", "Phone"])
        self.contacts_tree.setStyleSheet("""
            QTreeWidget {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                color: #2C3E50;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #F8F9FA;
                border-color: #3498DB;
            }
        """)
        
        # Button controls
        button_layout = QHBoxLayout()
        delete_contact_btn = GradientButton("Delete Contact")
        delete_group_btn = GradientButton("Delete Group")
        
        button_layout.addWidget(delete_contact_btn)
        button_layout.addWidget(delete_group_btn)
        
        # Connect buttons
        add_contact_btn.clicked.connect(self.add_contact_to_group)
        delete_contact_btn.clicked.connect(self.delete_selected_contact)
        delete_group_btn.clicked.connect(self.delete_selected_group)
        
        # Add widgets to layout
        layout.addWidget(self.group_name_label)
        layout.addLayout(contact_controls)
        layout.addWidget(self.contacts_tree)
        layout.addLayout(button_layout)
        
        return screen

    def show_group_selection_dialog(self):
        """Show popup dialog for group selection"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Group")
        layout = QVBoxLayout(dialog)
        
        combo = QComboBox()
        self.refresh_groups_combo(combo)
        select_btn = GradientButton("Select")
        
        layout.addWidget(QLabel("Choose a group:"))
        layout.addWidget(combo)
        layout.addWidget(select_btn)
        
        def handle_selection():
            group_name = combo.currentText()
            if group_name:
                self.group_name_label.setText(f"Group: {group_name}")
                self.refresh_contacts_tree(group_name)
                self.screens.setCurrentWidget(self.management_screen)
                dialog.accept()
        
        select_btn.clicked.connect(handle_selection)
        dialog.exec()

    def show_group_creation_dialog(self):
        """Show popup dialog for group creation"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Group")
        layout = QVBoxLayout(dialog)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter Group Name")
        create_btn = GradientButton("Create")
        
        layout.addWidget(QLabel("New Group Name:"))
        layout.addWidget(name_input)
        layout.addWidget(create_btn)
        
        def handle_creation():
            name = name_input.text()
            if name:
                try:
                    new_group = Group(name)
                    self.alert_system.contact_storage.add_group(new_group)
                    self.group_name_label.setText(f"Group: {name}")
                    self.refresh_contacts_tree(name)
                    self.screens.setCurrentWidget(self.management_screen)
                    dialog.accept()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to create group: {str(e)}")
        
        create_btn.clicked.connect(handle_creation)
        dialog.exec()

    def refresh_groups_combo(self, combo):
        """Refresh the groups in the combo box"""
        combo.clear()
        groups = self.alert_system.contact_storage.load_groups()
        for group in groups:
            combo.addItem(group.name)

    def refresh_contacts_tree(self, group_name):
        """Refresh the contacts tree for the selected group"""
        self.contacts_tree.clear()
        groups = self.alert_system.contact_storage.load_groups()
        group = next((g for g in groups if g.name == group_name), None)
        
        if group:
            for contact in group.contacts:
                item = QTreeWidgetItem([contact.name, contact.phone])
                self.contacts_tree.addTopLevelItem(item)

    def add_contact_to_group(self):
        """Add a contact to the current group"""
        name = self.contact_name_input.text()
        phone = self.contact_phone_input.text()
        group_name = self.group_name_label.text().replace("Group: ", "")
        
        if not all([name, phone, group_name]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields!")
            return
            
        try:
            groups = self.alert_system.contact_storage.load_groups()
            group = next((g for g in groups if g.name == group_name), None)
            
            if group:
                contact = Contact(name, phone)
                group.contacts.append(contact)
                self.alert_system.contact_storage.update_group(group)
                
                # Clear inputs
                self.contact_name_input.clear()
                self.contact_phone_input.clear()
                
                # Refresh display
                self.refresh_contacts_tree(group_name)
                QMessageBox.information(self, "Success", "Contact added successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add contact: {str(e)}")

    def delete_selected_contact(self):
        """Delete the selected contact from the current group"""
        current_item = self.contacts_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a contact to delete!")
            return
        
        group_name = self.group_name_label.text().replace("Group: ", "")
        contact_name = current_item.text(0)
        contact_phone = current_item.text(1)
        
        reply = QMessageBox.question(
            self, 
            'Delete Contact',
            f'Are you sure you want to delete {contact_name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                groups = self.alert_system.contact_storage.load_groups()
                group = next((g for g in groups if g.name == group_name), None)
                
                if group:
                    group.contacts = [c for c in group.contacts 
                                    if not (c.name == contact_name and c.phone == contact_phone)]
                    self.alert_system.contact_storage.update_group(group)
                    self.refresh_contacts_tree(group_name)
                    QMessageBox.information(self, "Success", "Contact deleted successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete contact: {str(e)}")

    def delete_selected_group(self):
        """Delete the current group and return to menu screen"""
        group_name = self.group_name_label.text().replace("Group: ", "")
        
        reply = QMessageBox.question(
            self, 
            'Delete Group',
            f'Are you sure you want to delete group "{group_name}" and all its contacts?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.alert_system.contact_storage.delete_group(group_name)
                self.contacts_tree.clear()
                self.screens.setCurrentWidget(self.menu_screen)
                QMessageBox.information(self, "Success", "Group deleted successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete group: {str(e)}")