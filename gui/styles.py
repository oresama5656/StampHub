MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #f4f5f7;
    }
    QWidget {
        font-family: 'Segoe UI', 'Meiryo', sans-serif;
    }
"""

HEADER_STYLE = """
    QWidget {
        background-color: #06C755;
        border-bottom: 1px solid #05B34C;
    }
"""

TAB_WIDGET_STYLE = """
    QTabWidget::pane {
        border-top: 1px solid #ddd;
        background-color: #f4f5f7;
    }
    QTabBar::tab {
        background-color: #e0e0e0;
        color: #555;
        padding: 10px 20px;
        min-width: 120px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 2px;
        font-weight: bold;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #f4f5f7;
        color: #06C755;
        border-bottom: 2px solid #f4f5f7;
    }
    QTabBar::tab:hover:!selected {
        background-color: #d0d0d0;
    }
"""
