class ReportingSystem:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    def generate_overview_report(self):
        stats = self.task_manager.get_task_statistics()
        report = "Task System Overview Report\n"
        report += "===========================\n"
        report += f"Total Tasks: {stats['total_tasks']}\n"
        report += f"Tasks by Status: {stats['by_status']}\n"
        report += f"Tasks by Priority: {stats['by_priority']}\n"
        report += f"Overdue Tasks: {stats['overdue_count']}\n"
        return report

    def export_report(self, report_content, filename="report.txt"):
        with open(filename, "w") as f:
            f.write(report_content)
        print(f"Report exported to {filename}")

