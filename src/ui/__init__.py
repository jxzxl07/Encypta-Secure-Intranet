from . import auth as _auth
from . import calls as _calls
from . import chat as _chat
from . import dashboard as _dashboard
from .auth import ChangePasswordDialog, Log_In, Log_In_Window, Sign_Up, Sign_Up_Window, Two_Factor_Dialogue
from .calls import ActiveCallWindow, Calls_Window, VideoCallWindow
from .chat import DirectMessage, Direct_Messages_Window, GroupMessage, Group_Messages_Window
from .dashboard import Admin_Dash_Window, Main_Menu_Window, User_Dash_Window


_auth.Admin_Dash_Window = Admin_Dash_Window
_auth.Main_Menu_Window = Main_Menu_Window
_dashboard.Calls_Window = Calls_Window
_dashboard.ChangePasswordDialog = ChangePasswordDialog
_dashboard.Direct_Messages_Window = Direct_Messages_Window
_dashboard.Group_Messages_Window = Group_Messages_Window
_dashboard.Log_In_Window = Log_In_Window
_chat.Main_Menu_Window = Main_Menu_Window
_calls.Main_Menu_Window = Main_Menu_Window


__all__ = [
    "ActiveCallWindow",
    "Admin_Dash_Window",
    "Calls_Window",
    "ChangePasswordDialog",
    "DirectMessage",
    "Direct_Messages_Window",
    "GroupMessage",
    "Group_Messages_Window",
    "Log_In",
    "Log_In_Window",
    "Main_Menu_Window",
    "Sign_Up",
    "Sign_Up_Window",
    "Two_Factor_Dialogue",
    "User_Dash_Window",
    "VideoCallWindow",
]
