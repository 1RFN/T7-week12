# Nama  : Irfan Jayadi
# NIM   : F1D02310011
# Kelas : D

import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QLabel,
    QFileDialog, QMessageBox, QFrame, QScrollArea, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# STYLESHEET
MODERN_STYLE = """
QMainWindow {
    background-color: #f0f2f5;
}
QLabel {
    color: #334155;
}
QFrame#KPICard, QFrame#ChartCard {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}
QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}
QPushButton {
    background-color: #3b82f6;
    color: white;
    border-radius: 6px;
    padding: 10px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #2563eb;
}
QPushButton#ExportBtn {
    background-color: #10b981;
}
QPushButton#ExportBtn:hover {
    background-color: #059669;
}
QComboBox {
    padding: 8px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background-color: #f8fafc;
    color: #334155;
}
QTableWidget {
    background-color: #ffffff;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    gridline-color: #f1f5f9;
    color: #334155;
}
QHeaderView::section {
    background-color: #f8fafc;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    font-weight: bold;
    color: #475569;
}
"""

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        try:
            self.df = pd.read_csv(self.file_path)
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def get_data(self):
        return self.df

    def get_filtered_data(self, branch, city):
        df_filtered = self.df.copy()
        if branch != "All":
            df_filtered = df_filtered[df_filtered['Branch'] == branch]
        if city != "All":
            df_filtered = df_filtered[df_filtered['City'] == city]
        return df_filtered

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        plt.style.use('bmh')
        self.figure.patch.set_facecolor('#ffffff')

    def update_charts(self, df):
        self.figure.clear()
        
        if df is None or df.empty:
            self.canvas.draw()
            return

        ax1 = self.figure.add_subplot(221)
        ax2 = self.figure.add_subplot(222)
        ax3 = self.figure.add_subplot(223)
        ax4 = self.figure.add_subplot(224)

        sales_trend = df.groupby('Date')['Sales'].sum().reset_index().sort_values('Date')
        ax1.plot(sales_trend['Date'], sales_trend['Sales'], marker='o', color='#3b82f6', linewidth=2)
        ax1.set_title("Sales Trend over Time", fontsize=11, fontweight='bold', color='#334155')
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        
        sales_by_product = df.groupby('Product line')['Sales'].sum().sort_values()
        sales_by_product.plot(kind='barh', ax=ax2, color='#10b981')
        ax2.set_title("Total Sales by Product Line", fontsize=11, fontweight='bold', color='#334155')
        ax2.set_ylabel("")

        cust_type = df['Customer type'].value_counts()
        ax3.pie(cust_type, labels=cust_type.index, autopct='%1.1f%%', startangle=90, 
                colors=['#8b5cf6', '#f43f5e'], wedgeprops={'width': 0.4, 'edgecolor': 'w'})
        ax3.set_title("Customer Type Distribution", fontsize=11, fontweight='bold', color='#334155')

        sales_by_city = df.groupby('City')['Sales'].sum().sort_values(ascending=False)
        sales_by_city.plot(kind='bar', ax=ax4, color='#f59e0b')
        ax4.set_title("Total Sales by City", fontsize=11, fontweight='bold', color='#334155')
        ax4.tick_params(axis='x', rotation=0)
        ax4.set_xlabel("")

        self.figure.tight_layout(pad=3.0, h_pad=5.0, w_pad=3.0)
        self.canvas.draw()

    def export_to_png(self, filename):
        self.figure.savefig(filename, dpi=300, bbox_inches='tight')

class KPICard(QFrame):
    def __init__(self, title, value="0"):
        super().__init__()
        self.setObjectName("KPICard")
        self.setMinimumSize(200, 100)
        
        layout = QVBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #64748b;")
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setFont(QFont("Arial", 18, QFont.Bold))
        self.lbl_value.setStyleSheet("color: #0f172a;")
        self.lbl_value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addStretch()
        self.setLayout(layout)

    def set_value(self, value):
        self.lbl_value.setText(value)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supermarket Analytics Dashboard")
        self.resize(1366, 768)
        self.setStyleSheet(MODERN_STYLE)

        self.data_loader = DataLoader("SuperMarket Analysis.csv")
        self.data_loaded = self.data_loader.load_data()

        self.init_ui()
        
        if self.data_loaded:
            self.populate_filters()
            self.update_dashboard()
        else:
            QMessageBox.critical(self, "Error", "Gagal memuat dataset.")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # SIDEBAR KIRI
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)

        title_lbl = QLabel("Supermarket\nAnalytics")
        title_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #0f172a; margin-bottom: 20px;")
        
        # Filters
        self.cb_branch = QComboBox()
        self.cb_city = QComboBox()
        
        self.cb_branch.currentIndexChanged.connect(self.update_dashboard)
        self.cb_city.currentIndexChanged.connect(self.update_dashboard)

        # Buttons
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.clicked.connect(self.update_dashboard)
        
        self.btn_export = QPushButton("Export Dashboard")
        self.btn_export.setObjectName("ExportBtn")
        self.btn_export.clicked.connect(self.export_chart)

        sidebar_layout.addWidget(title_lbl)
        sidebar_layout.addWidget(QLabel("Filter Branch:"))
        sidebar_layout.addWidget(self.cb_branch)
        sidebar_layout.addWidget(QLabel("Filter City:"))
        sidebar_layout.addWidget(self.cb_city)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_refresh)
        sidebar_layout.addWidget(self.btn_export)

        main_layout.addWidget(sidebar)

        content_area = QScrollArea()
        content_area.setWidgetResizable(True)
        content_area.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        kpi_layout = QHBoxLayout()
        self.kpi_sales = KPICard("Total Revenue")
        self.kpi_transactions = KPICard("Total Transactions")
        self.kpi_rating = KPICard("Average Rating")
        
        kpi_layout.addWidget(self.kpi_sales)
        kpi_layout.addWidget(self.kpi_transactions)
        kpi_layout.addWidget(self.kpi_rating)
        content_layout.addLayout(kpi_layout)

        chart_frame = QFrame()
        chart_frame.setObjectName("ChartCard")
        chart_layout = QVBoxLayout(chart_frame)
        self.chart_widget = ChartWidget()
        
        self.chart_widget.setMinimumHeight(650)
        chart_layout.addWidget(self.chart_widget)
        content_layout.addWidget(chart_frame)

        table_label = QLabel("Raw Transaction Data")
        table_label.setFont(QFont("Arial", 14, QFont.Bold))
        table_label.setStyleSheet("color: #0f172a; margin-top: 10px;")
        content_layout.addWidget(table_label)

        self.table_widget = QTableWidget()
        self.table_widget.setMinimumHeight(300)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        content_layout.addWidget(self.table_widget)

        content_area.setWidget(content_widget)
        main_layout.addWidget(content_area)

    def populate_filters(self):
        df = self.data_loader.get_data()
        if df is not None:
            branches = df['Branch'].unique().tolist()
            branches.sort()
            self.cb_branch.addItem("All")
            self.cb_branch.addItems(branches)

            cities = df['City'].unique().tolist()
            cities.sort()
            self.cb_city.addItem("All")
            self.cb_city.addItems(cities)

    def update_dashboard(self):
        if not self.data_loaded: return

        selected_branch = self.cb_branch.currentText()
        selected_city = self.cb_city.currentText()
        
        if not selected_branch or not selected_city: return

        df_filtered = self.data_loader.get_filtered_data(selected_branch, selected_city)

        if not df_filtered.empty:
            total_sales = df_filtered['Sales'].sum()
            total_trx = len(df_filtered)
            avg_rating = df_filtered['Rating'].mean()
            
            self.kpi_sales.set_value(f"${total_sales:,.2f}")
            self.kpi_transactions.set_value(f"{total_trx}")
            self.kpi_rating.set_value(f"{avg_rating:.1f} / 10")
        else:
            self.kpi_sales.set_value("$0")
            self.kpi_transactions.set_value("0")
            self.kpi_rating.set_value("0")

        self.update_table(df_filtered)
        self.chart_widget.update_charts(df_filtered)

    def update_table(self, df):
        self.table_widget.clear()
        if df is None or df.empty:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return

        display_df = df.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')

        self.table_widget.setRowCount(display_df.shape[0])
        self.table_widget.setColumnCount(display_df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(display_df.columns.astype(str))

        for row in range(display_df.shape[0]):
            for col in range(display_df.shape[1]):
                item = QTableWidgetItem(str(display_df.iat[row, col]))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table_widget.setItem(row, col, item)

    def export_chart(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Dashboard Export", "Dashboard_Export.png", "PNG Files (*.png)", options=options)
        if file_name:
            if not file_name.endswith('.png'): file_name += '.png'
            self.chart_widget.export_to_png(file_name)
            QMessageBox.information(self, "Success", f"Dashboard berhasil diexport ke {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())