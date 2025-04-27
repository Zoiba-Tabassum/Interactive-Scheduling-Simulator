from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from scheduler import fcfs, sjf_non_preemptive, priority_non_preemptive, round_robin
from process import Process


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive Scheduling Simulator")
        self.setGeometry(100, 100, 1000, 600)  # x, y, width, height
        self.initUI()

    def initUI(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Process Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "Arrival Time", "Burst Time", "Priority"])

        main_layout.addWidget(self.table)

        # --- Algorithm Selection + Buttons ---
        button_layout = QHBoxLayout()

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["First-Come-First-Served (FCFS)", "Shortest Job First (SJF)", "Priority Scheduling", "Round Robin", "Multilevel Feedback Queue"])
        button_layout.addWidget(self.algorithm_combo)

        self.time_quantum_label = QLabel("Time Quantum:")
        self.time_quantum_input = QTableWidgetItem()

        self.time_quantum_box = QPushButton("Set Quantum")
        self.time_quantum_box.clicked.connect(self.get_time_quantum)

        button_layout.addWidget(self.time_quantum_label)
        self.time_quantum_label.hide()  # Hidden by default
        self.time_quantum_box.hide()


        self.add_button = QPushButton("Add Process")
        self.add_button.clicked.connect(self.add_process)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_process)

        self.start_button = QPushButton("Start Simulation")  # <-- THIS BUTTON
        self.start_button.clicked.connect(self.start_simulation) 

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.start_button)

        main_layout.addLayout(button_layout)

        # --- Gantt Chart Placeholder ---
        self.gantt_chart_label = QLabel()
        self.gantt_chart_label.setFixedHeight(150)  # Set height for Gantt chart area
        self.gantt_chart_label.setStyleSheet("background-color: white; border: 1px solid black;")
        
        main_layout.addWidget(self.gantt_chart_label)

    def add_process(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Pre-fill PID automatically
        self.table.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))

    def delete_selected_process(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)
 
    def start_simulation(self):
        process_list = []

        for row in range(self.table.rowCount()):
            try:
                pid = int(self.table.item(row, 0).text())
                arrival_time = int(self.table.item(row, 1).text())
                burst_time = int(self.table.item(row, 2).text())
                priority = int(self.table.item(row, 3).text())
            except AttributeError:
                QMessageBox.warning(self, "Warning", "Please fill all fields!")
                return
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid number format!")
                return

            process = Process(pid, arrival_time, burst_time, priority)
            process_list.append(process)

        selected_algorithm = self.algorithm_combo.currentText()

        if selected_algorithm == "First-Come-First-Served (FCFS)":
            scheduled_processes = fcfs(process_list)
        elif selected_algorithm == "Shortest Job First (SJF)":
            scheduled_processes = sjf_non_preemptive(process_list)
        elif selected_algorithm == "Priority Scheduling":
            scheduled_processes = priority_non_preemptive(process_list)
        elif selected_algorithm == "Round Robin":
            time_quantum, ok = self.get_time_quantum()
            if not ok:
                return
            scheduled_processes = round_robin(process_list, time_quantum)
        elif selected_algorithm == "Multilevel Feedback Queue":
            QMessageBox.information(self, "Info", "MLFQ not implemented yet.")
            return
        else:
            QMessageBox.warning(self, "Warning", "Unknown Algorithm Selected!")
            return


        print("\nScheduled Processes (after FCFS):")
        for p in scheduled_processes:
            print(f"PID: {p.pid}, Start: {p.start_time}, Finish: {p.finish_time}, Waiting: {p.waiting_time}, Turnaround: {p.turnaround_time}")
        
        self.draw_gantt_chart(scheduled_processes)

        # For now just print to console
        print("\nProcesses Loaded:")
        for p in process_list:
            print(p)

    def draw_gantt_chart(self, process_list):
        if not process_list:
            return

        # Create a blank image
        width_per_unit = 30  # Pixels per unit time
        height = 100
        total_time = process_list[-1].finish_time
        width = max(600, total_time * width_per_unit)

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor('white'))

        painter = QPainter(pixmap)

        colors = [QColor('skyblue'), QColor('lightgreen'), QColor('lightcoral'),
                QColor('plum'), QColor('khaki'), QColor('orange'), QColor('cyan')]

        x = 0

        for i, process in enumerate(process_list):
            process_width = (process.finish_time - process.start_time) * width_per_unit

            # Draw process block
            painter.setBrush(colors[i % len(colors)])
            painter.drawRect(x, 0, process_width, height)

            # Draw process ID
            painter.drawText(x + process_width // 2 - 10, height // 2, f"P{process.pid}")

            # Draw start time
            painter.drawText(x, height - 10, str(process.start_time))

            x += process_width

        # Draw the final finish time
        painter.drawText(x, height - 10, str(process_list[-1].finish_time))

        painter.end()

        # Set to label
        self.gantt_chart_label.setPixmap(pixmap)

    def get_time_quantum(self):
        text, ok = QInputDialog.getText(self, 'Time Quantum', 'Enter Time Quantum:')
        if ok:
            try:
                value = int(text)
                if value <= 0:
                    raise ValueError
                return value, True
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid Time Quantum!")
                return None, False
        return None, False

