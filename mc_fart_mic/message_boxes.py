import traceback

from PyQt5.QtWidgets import QMessageBox


def message_box_constructor(
        message_text: str,
        *,
        title: str, informative_text: str = None,
        detailed_text: str = None, icon: QMessageBox.Icon = QMessageBox.Information
) -> QMessageBox:
    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(message_text)
    message_box.setInformativeText(informative_text)
    message_box.setDetailedText(detailed_text)
    message_box.setIcon(icon)
    return message_box


def show_simple_info_message(message_text: str):
    message_box_constructor(message_text, title="Info").exec_()


def show_simple_success_message(message_text: str):
    message_box_constructor(message_text, title="Success").exec_()


def show_simple_warning_message(message_text: str):
    message_box_constructor(message_text, title="Warning", icon=QMessageBox.Warning).exec_()


def show_simple_traceback_message(message_text: str, *, custom_traceback_msg: str = None):
    """
    Shows information on the last traceback.
    If custom_traceback_msg is passed then shows that instead of last traceback.
    """
    traceback_msg = traceback.format_exc(1) if custom_traceback_msg is None else custom_traceback_msg
    error_msg = message_box_constructor(
        message_text, title="Error", icon=QMessageBox.Warning, detailed_text=traceback_msg
    )
    error_msg.exec_()


def show_simple_confirmation_message(message_text: str = "Are you sure?") -> bool:
    confirmation_msg = message_box_constructor(message_text, title="Confirmation", icon=QMessageBox.Question)
    confirmation_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return confirmation_msg.exec_() == QMessageBox.Ok
