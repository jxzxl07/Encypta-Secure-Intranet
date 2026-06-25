from .common import *
from .base import GUI_Window
from ..config import ADMIN_PASSWORD, ADMIN_USERNAME, EMAIL_ADDRESS, EMAIL_APP_PASSWORD
from ..crypto.encryption import AsymmetricEncryption, hash_password
from ..database.db_manager import generate_user_id
from ..utils.helpers import Validate_Email, Validate_Password, get_ip_address, send_status_update


class Log_In_Window(GUI_Window):
    # Constructor method initialises the window.
    def __init__(self):
        super().__init__(title="Encrypta - Log In")
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        # Create a main layout for the window.
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Create a left container for the window.
        left_container = QWidget()
        left_container.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(50, 50, 50, 50)
        # Create a label for the login image.
        login_image_container = QLabel()
        login_image_container.setMinimumSize(350, 400)
        login_image_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        login_image_container.setAlignment(Qt.AlignCenter)
        login_pixmap = QPixmap(asset_path("login.png"))
        login_image_container.setPixmap(login_pixmap)
        login_image_container.setScaledContents(True)
        left_layout.addWidget(login_image_container)
        # Create a right container for the window.
        right_container = QWidget()
        right_container.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(80, 50, 80, 50)
        # Create a container for the logo.
        logo_container = QLabel()
        logo_container.setMinimumSize(200, 100)
        logo_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        logo_container.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(asset_path("logo2.png"))
        logo_container.setPixmap(logo_pixmap)
        logo_container.setScaledContents(True)
        right_layout.addWidget(logo_container)
        # Create a container for the login form.
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(30)
        # Create a label for the login form.
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumSize(450, 60)
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.username_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px;}
            QLineEdit:focus {border: 1px solid #007BFF;} """)
        form_layout.addWidget(self.username_input)
        # Create a label for the password input.
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumSize(450, 60)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px;}
            QLineEdit:focus {border: 1px solid #007BFF;}""")
        form_layout.addWidget(self.password_input)
        # Create a container for the login button.
        form_layout.addSpacing(30)
        login_button_container = QWidget()
        login_button_layout = QHBoxLayout(login_button_container)
        login_button = QPushButton("Log In")
        login_button.setFixedSize(450, 60)
        login_button.setStyleSheet("""QPushButton {background-color: #007BFF; 
                                   color: white; border: none; 
                                   border-radius: 5px; font-size: 20px;
                                    font-weight: bold;}
            QPushButton:hover {background-color: #0056b3;}""")
        login_button.clicked.connect(self.handle_login)
        login_button_layout.addWidget(login_button)
        form_layout.addWidget(login_button_container)
        # Create a container for the sign up button.
        form_layout.addSpacing(20)
        signup_button_container = QWidget()
        signup_button_layout = QHBoxLayout(signup_button_container)
        signup_button = QPushButton("Sign Up")
        signup_button.setFixedSize(300, 40)
        signup_button.setStyleSheet("""QPushButton {background-color: transparent;
                                     color: #007BFF; border: none; font-size: 18px; 
                                    font-weight: bold; text-align: center;}
            QPushButton:hover {color: #0056b3;}""")
        signup_button.clicked.connect(self.redirect_to_signup)
        signup_button_layout.addWidget(signup_button)
        form_layout.addWidget(signup_button_container)
        # Add the form container to the right layout.
        right_layout.addWidget(form_container, alignment=Qt.AlignHCenter)
        right_layout.addStretch()
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(right_container, 1)
        self.layout.addLayout(main_layout)



    def handle_login(self):
        # Handle the login process
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        # Check if the fields are empty
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return False
        # Check if the user is an admin
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.redirect = Admin_Dash_Window()
            self.redirect.show()
            self.close()
        else:
            login_result, username = Log_In(username, password)
            if login_result:
                self.redirect = Main_Menu_Window(username)  
                self.close()
                return True
            else:
                self.username_input.clear()
                self.password_input.clear()


    def redirect_to_signup(self):
        # Redirect to the sign up window
        self.redirect = Sign_Up_Window()
        self.redirect.show()
        self.close()


class Sign_Up_Window(GUI_Window):    
    # Constructor method initialises the window.
    def __init__(self):
        super().__init__(title="Encrypta - Sign Up")
        self.init_ui()
        self.showMaximized()


    def init_ui(self):
        # Create a main layout for the window.
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Create a left container for the window.
        left_container = QWidget()
        left_container.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(50, 50, 50, 50)
        # Create a label for the sign up image.
        login_image_container = QLabel()
        login_image_container.setMinimumSize(350, 400)
        login_image_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        login_image_container.setAlignment(Qt.AlignCenter)
        login_pixmap = QPixmap(asset_path("signup.png"))
        login_image_container.setPixmap(login_pixmap)
        login_image_container.setScaledContents(True)
        left_layout.addWidget(login_image_container)
        # Create a right container for the window.
        right_container = QWidget()
        right_container.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(80, 50, 80, 50)
        # Create a container for the logo.
        logo_container = QLabel()
        logo_container.setMinimumSize(200, 100)
        logo_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        logo_container.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(asset_path("logo2.png"))
        logo_container.setPixmap(logo_pixmap)
        logo_container.setScaledContents(True)
        right_layout.addWidget(logo_container)
        # Create a container for the sign up form.
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(30)
        # Create a label for the sign up form. 
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setMinimumSize(450, 60)
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.username_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px;}
            QLineEdit:focus {border: 1px solid #007BFF;} """)
        form_layout.addWidget(self.username_input)
        # Create a label for the email input.
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Email")
        self.email_input.setMinimumSize(450, 60)
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.email_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px;}
            QLineEdit:focus {border: 1px solid #007BFF;}""")
        form_layout.addWidget(self.email_input)
        # Create a label for the password input.
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumSize(450, 60)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px;}
            QLineEdit:focus {border: 1px solid #007BFF;}""")
        form_layout.addWidget(self.password_input)
        # Create a label for the confirm password input.
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumSize(450, 60)
        self.confirm_password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.confirm_password_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 20px;}
            QLineEdit:focus {border: 1px solid #007BFF;}""")
        form_layout.addWidget(self.confirm_password_input)
        # Create a container for the sign up button.
        form_layout.addSpacing(30)
        signup_button_container = QWidget()
        signup_button_layout = QHBoxLayout(signup_button_container)
        signup_button = QPushButton("Sign Up")
        signup_button.setFixedSize(450, 60)
        signup_button.setStyleSheet("""QPushButton {background-color: #007BFF;
                                     color: white; border: none; border-radius: 5px;
                                    font-size: 20px; font-weight: bold;}
            QPushButton:hover {background-color: #0056b3;}""")
        signup_button.clicked.connect(self.handle_signup)
        signup_button_layout.addWidget(signup_button)
        form_layout.addWidget(signup_button_container)
        # Create a container for the login button.
        form_layout.addSpacing(20)
        login_button_container = QWidget()
        login_button_layout = QHBoxLayout(login_button_container)
        login_button = QPushButton("Log In")
        login_button.setFixedSize(300, 40)
        login_button.setStyleSheet("""QPushButton {background-color: transparent; 
                                   color: #007BFF; border: none; font-size: 18px;
                                    font-weight: bold; text-align: center;}
            QPushButton:hover {color: #0056b3;}""")
        login_button.clicked.connect(self.redirect_to_login)
        login_button_layout.addWidget(login_button)
        form_layout.addWidget(login_button_container)
        # Add the form container to the right layout.
        right_layout.addWidget(form_container, alignment=Qt.AlignHCenter)
        right_layout.addStretch()
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(right_container, 1)
        self.layout.addLayout(main_layout)


    def redirect_to_login(self):
        self.redirect = Log_In_Window()
        self.redirect.show()
        self.close()


    def handle_signup(self):
        # Handle the sign up process
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        # Check if the fields are empty
        if not username or not password or not confirm_password or not email:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return False
        # Check if the passwords match
        if Sign_Up(username, password, confirm_password, email):
            self.redirect = Log_In_Window()
            self.redirect.show()
            self.close()
            return True
        else:
            self.username_input.clear()
            self.password_input.clear()
            self.confirm_password_input.clear()
            self.email_input.clear()


class Two_Factor_Dialogue(QDialog):

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.code = None
        self.code_expiry = None
        self.setup_ui()
        self.send_new_code()


    def setup_ui(self):

        self.setWindowTitle("2FA Verification")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        self.message_label = QLabel("Please check your email for the 2FA code.")
        self.message_label.setStyleSheet("font-size: 14px; margin: 10px;")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter 2FA Code")
        self.code_input.setStyleSheet("""QLineEdit {border: 1px solid #ccc;border-radius: 5px;padding: 8px;font-size: 14px;margin: 10px;}
            QLineEdit:focus {border: 1px solid #007BFF;}""")
        layout.addWidget(self.code_input)

        button_layout = QVBoxLayout()
        self.verify_button = QPushButton("Verify Code")
        self.verify_button.setStyleSheet("""QPushButton {background-color: #007BFF;
                                         color: white;border: none; border-radius: 5px;
                                         padding: 8px 16px;font-size: 14px;
                                         font-weight: bold;margin: 5px;}
            QPushButton:hover {background-color: #0056b3;}""")
        self.resend_button = QPushButton("Resend Code")

        self.resend_button.setStyleSheet("""QPushButton {background-color: #6c757d;
                                         color: white;border: none; border-radius: 5px;
                                         padding: 8px 16px;font-size: 14px;
                                         font-weight: bold;margin: 5px;}
            QPushButton:hover {background-color: #5a6268;}""")
        
        button_layout.addWidget(self.verify_button)
        button_layout.addWidget(self.resend_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.verify_button.clicked.connect(self.verify_code)
        self.resend_button.clicked.connect(self.send_new_code)


    def send_new_code(self):
        self.code = str(random.randint(100000, 999999))
        self.code_expiry = datetime.now() + timedelta(minutes=10)
        success, delivery_method = self.send_2fa_code(self.username, self.code)
        if success:
            if delivery_method == "email":
                self.message_label.setText("New code sent. Please check your email.")
                QMessageBox.information(self, "Code Sent", "A new verification code has been sent to your email.")
            else:
                self.message_label.setText(f"Email is not configured. Local verification code: {self.code}")
            self.code_input.clear()
        else:
            self.message_label.setText("Failed to send code. Please try again.")
            QMessageBox.warning(self, "Error", "Failed to send verification code. Please try again.")


    def verify_code(self):
        entered_code = self.code_input.text()
        if not entered_code:
            QMessageBox.warning(self, "Error", "Please enter the code.")
            return False
        if datetime.now() > self.code_expiry:
            QMessageBox.warning(self, "Error", "Code has expired. Please request a new code.")
            return False
        if entered_code == self.code:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Incorrect code. Please try again.")


    def send_2fa_code(self, recipient_email, code):
        if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
            return True, "local"

        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = recipient_email
            msg['Subject'] = "Your Two-Factor Authentication Code"
            body = f"""
            Hello,

            Your two-factor authentication code is: {code}

            This code will expire in 10 minutes.
            If you didn't request this code, please ignore this email.

            Kind regards,
            Encrypta Secure Intranet
            """
            msg.attach(MIMEText(body, 'plain'))
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
                server.send_message(msg)
            return True, "email"
        except Exception as e:
            print(f"Failed to send 2FA code: {str(e)}")
            return False, "email"
        







def Sign_Up(username, password, confirm_password, email):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE username = ?", (username,))
        if cursor.fetchone() is not None:
            QMessageBox.warning(None, "Error", "Username already taken.")
            return False
        if len(username) < 5:
            QMessageBox.warning(None, "Error", "Username must be at least five characters long.")
            return False
        if not Validate_Password(password):
            QMessageBox.warning(None, "Error", "Invalid password format.\n Password must contain uppercase, lowercase and a number, minimum 8 characters.")
            return False
        if password != confirm_password:
            QMessageBox.warning(None, "Error", "Passwords must match.")
            return False
        if not Validate_Email(email):
            QMessageBox.warning(None, "Error", "Invalid email format.")
            return False
        cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
        if cursor.fetchone() is not None:
            QMessageBox.warning(None, "Error", "Email already exists.")
            return False
        password_hash = hash_password(password)
        user_id = generate_user_id()
        crypto = AsymmetricEncryption()
        crypto.generate_keypair()
        public_key, private_key = crypto.keys_to_string()
        cursor.execute('''
            INSERT INTO User (user_id, username, password_hash, email, role, status, private_key, public_key)
            VALUES (?, ?, ?, ?, "user", "offline", ?, ?)
        ''', (user_id, username, password_hash, email, private_key, public_key))
        conn.commit()
        QMessageBox.information(None, "Success", "Sign-up successful!")
        return True
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"An error occurred: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()





def Log_In(username, password):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, email, user_id FROM User WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result is None:
            QMessageBox.warning(None, "Error", "Username does not exist.")
            return False, None
            
        stored_password_hash, user_email, user_id = result
        hashed_password = hash_password(password)
        
        if hashed_password == stored_password_hash:
            two_fa_dialog = Two_Factor_Dialogue(user_email)
            if two_fa_dialog.exec_() == QDialog.Accepted:
                ip_address = get_ip_address()
                
                # Update database
                cursor.execute("UPDATE User SET status = 'online' WHERE username = ?", (username,))
                cursor.execute("SELECT * FROM Session WHERE user_id = ?", (user_id,))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO Session (user_id, ip_address) VALUES (?, ?)", 
                                 (user_id, ip_address))
                else:
                    cursor.execute("UPDATE Session SET ip_address = ? WHERE user_id = ?", 
                                 (ip_address, user_id))
                conn.commit()
                
                # Notify admin server
                send_status_update(username, 'login', ip_address)
                
                return True, username
            return False, username
        else:
            QMessageBox.warning(None, "Error", "Incorrect password entered.")
            return False, None
            
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Database Error", f"An error occurred: {str(e)}")
        return False, None
    finally:
        if conn:
            conn.close()















class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Change Password")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # New password input
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet("""
            QLineEdit {padding: 10px;border: 1px solid #ccc;
            border-radius: 4px;font-size: 14px;}""")
        layout.addWidget(QLabel("New Password:"))
        layout.addWidget(self.new_password)
        
        # Password requirements label
        requirements_label = QLabel(
            "Password must contain:\n"
            "- At least 8 characters\n"
            "- At least one uppercase letter\n"
            "- At least one lowercase letter\n"
            "- At least one number"
        )
        requirements_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(requirements_label)

        # Confirm password input
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet("""
            QLineEdit {padding: 10px;border: 1px solid #ccc;
            border-radius: 4px;font-size: 14px;}""")
        layout.addWidget(QLabel("Confirm Password:"))
        layout.addWidget(self.confirm_password)
        
        # Change password button
        self.change_btn = QPushButton("Change Password")
        self.change_btn.setStyleSheet("""
            QPushButton {background-color: #007bff;color: white;
            border: none;border-radius: 4px;padding: 10px;
            font-size: 14px;font-weight: bold;margin-top: 10px;}
            QPushButton:hover {background-color: #0056b3;}""")
        self.change_btn.clicked.connect(self.change_password)
        layout.addWidget(self.change_btn)
        self.setLayout(layout)

    
    def change_password(self):
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()
        # Validate input
        if not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        # Check if passwords match
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        # Hash the new password    
        password_hash = hash_password(new_pass)

        if not Validate_Password(new_pass):
             QMessageBox.warning(self,"Error", "Invalid Password")
             return
        # Check if new password is same as current password
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT password_hash 
            FROM User 
            WHERE username = ?
        ''', (self.username,))
        current_hash = cursor.fetchone()[0]
        if password_hash == current_hash:
            QMessageBox.warning(self, "Error", "New password cannot be the same as the current password")
            return
        # Update the password in database 
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE User 
                SET password_hash = ? 
                WHERE username = ?
            ''', (password_hash, self.username))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Password changed successfully!")
            self.accept()  # Close dialogue with success status
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
            self.reject()  # Close dialogue with failure status
