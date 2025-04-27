from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
from scheduler import fcfs, sjf_non_preemptive, priority_non_preemptive, round_robin
from process import Process
from scheduler import fcfs, sjf_non_preemptive, priority_non_preemptive, round_robin, mlfq


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

        self.theme_button = QPushButton("Toggle Dark/Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        
        button_layout.addWidget(self.theme_button)
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

        self.suggest_algorithm(process_list)

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
            scheduled_processes = mlfq(process_list)

        else:
            QMessageBox.warning(self, "Warning", "Unknown Algorithm Selected!")
            return


        print("\nScheduled Processes (after FCFS):")
        for p in scheduled_processes:
            print(f"PID: {p.pid}, Start: {p.start_time}, Finish: {p.finish_time}, Waiting: {p.waiting_time}, Turnaround: {p.turnaround_time}")
        
        self.draw_gantt_chart(scheduled_processes)
        self.show_performance_metrics(scheduled_processes)

        # For now just print to console
        print("\nProcesses Loaded:")
        for p in process_list:
            print(p)

    def draw_gantt_chart(self, process_list):
        if not process_list:
            return

        width_per_unit = 30  # Pixels per unit time
        chart_height = 100
        label_height = 30
        total_time = process_list[-1].finish_time
        width = max(600, total_time * width_per_unit)

        pixmap = QPixmap(width, chart_height + label_height)
        pixmap.fill(QColor('#f0f0f0'))  # Light background

        painter = QPainter(pixmap)
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        # Colors (improved modern colors)
        colors = [QColor('#3498db'), QColor('#2ecc71'), QColor('#e74c3c'),
                QColor('#9b59b6'), QColor('#f1c40f'), QColor('#e67e22'), QColor('#1abc9c')]

        x = 0

        for i, process in enumerate(process_list):
            process_width = (process.finish_time - process.start_time) * width_per_unit

            # Draw block with rounded rectangle
            painter.setBrush(colors[i % len(colors)])
            painter.setPen(QColor('#2c3e50'))  # Dark border
            painter.drawRoundedRect(x + 2, 2, process_width - 4, chart_height - 4, 10, 10)

            # Center the Process ID in the middle
            text = f"P{process.pid}"
            text_rect = painter.boundingRect(x, 0, process_width, chart_height, 0, text)
            painter.drawText(text_rect, Qt.AlignCenter, text)

            # Draw start time at the bottom
            start_time_text = str(process.start_time)
            painter.drawText(x, chart_height + 20, start_time_text)

            x += process_width

        # Draw final finish time
        painter.drawText(x, chart_height + 20, str(process_list[-1].finish_time))

        painter.end()

        # Set pixmap to label
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

    def show_performance_metrics(self, scheduled_processes):
        if not scheduled_processes:
            return

        total_waiting_time = sum(p.waiting_time for p in scheduled_processes)
        total_turnaround_time = sum(p.turnaround_time for p in scheduled_processes)
        total_burst_time = sum(p.burst_time for p in scheduled_processes)
        total_processes = len(scheduled_processes)
        total_time_span = scheduled_processes[-1].finish_time - min(p.arrival_time for p in scheduled_processes)

        average_waiting_time = total_waiting_time / total_processes
        average_turnaround_time = total_turnaround_time / total_processes
        cpu_utilization = (total_burst_time / total_time_span) * 100
        throughput = total_processes / total_time_span

        report = f"""

            Performance Metrics:
            ---------------------

Average Waiting Time: {average_waiting_time:.2f} units
Average Turnaround Time: {average_turnaround_time:.2f} units
CPU Utilization: {cpu_utilization:.2f} %
Throughput: {throughput:.2f} processes/unit time
Completion Order: {', '.join('P'+str(p.pid) for p in scheduled_processes)}
        """

        QMessageBox.information(self, "Performance Metrics", report)

    def toggle_theme(self):
        current_style = self.parent().styleSheet() if self.parent() else self.styleSheet()

        if "#ecf0f1" in current_style:
            # Switch to dark mode
            with open("styles_dark.qss", "r") as f:
                self.parent().setStyleSheet(f.read()) if self.parent() else self.setStyleSheet(f.read())
        else:
            # Switch to light mode
            with open("styles.qss", "r") as f:
                self.parent().setStyleSheet(f.read()) if self.parent() else self.setStyleSheet(f.read())

    def suggest_algorithm(self, process_list):
        short_tasks = sum(1 for p in process_list if p.burst_time <= 3)
        long_wait_expected = any(p.priority > 5 for p in process_list)
        mixed_tasks = any(p.burst_time >= 8 for p in process_list) and any(p.burst_time <= 3 for p in process_list)

        suggestion = "Suggestion:\n"

        if short_tasks >= len(process_list) // 2:
            suggestion += "- Many short tasks detected. Recommended: SJF (Shortest Job First)\n"

        if long_wait_expected:
            suggestion += "- Interactive tasks with long wait times detected. Recommended: Priority Scheduling\n"

        if mixed_tasks:
            suggestion += "- Mixture of I/O-bound and CPU-bound tasks detected. Recommended: Multilevel Feedback Queue (MLFQ)\n"

        if suggestion.strip() != "Suggestion:":
            QMessageBox.information(self, "Algorithm Suggestion", suggestion)
        else:
            QMessageBox.information(self, "Algorithm Suggestion", "No specific suggestion. Default algorithms can be used.")
