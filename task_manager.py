import datetime
import json
import os

# ------------------------------
# Task Class (OOP Fundamentals)
# ------------------------------
class Task:
    task_counter = 1  # static variable for unique IDs

    def __init__(self, title, description, priority, due_date, status="Pending", task_id=None):
        if task_id:
            self.id = task_id
        else:
            self.id = Task.task_counter
            Task.task_counter += 1

        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.status = status

    def mark_complete(self):
        self.status = "Completed"

    def to_dict(self):
        """Convert task to dictionary for saving in JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        """Re-create a Task object from dictionary (when loading)."""
        due_date_obj = datetime.datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        return Task(
            data["title"],
            data["description"],
            data["priority"],
            due_date_obj,
            status=data["status"],
            task_id=data["id"]
        )

    def __str__(self):
        return f"[{self.id}] {self.title} ({self.priority}) - Due: {self.due_date} - {self.status}"


# ------------------------------
# Task Manager (Core + File I/O)
# ------------------------------
class TaskManager:
    FILE_NAME = "tasks.json"

    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def add_task(self, title, description, priority, due_date):
        try:
            due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
            task = Task(title, description, priority, due_date_obj)
            self.tasks.append(task)
            self.save_tasks()
            print("✅ Task added successfully!\n")
        except ValueError:
            print("⚠ Invalid date format! Use YYYY-MM-DD.\n")

    def view_tasks(self):
        if not self.tasks:
            print("⚠ No tasks available.\n")
            return
        for task in self.tasks:
            print(task)
        print()

    def mark_task_complete(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                task.mark_complete()
                self.save_tasks()
                print("✅ Task marked as completed!\n")
                return
        print("⚠ Task not found!\n")

    def delete_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                self.save_tasks()
                print("🗑 Task deleted successfully!\n")
                return
        print("⚠ Task not found!\n")

    def save_tasks(self):
        """Save all tasks to JSON file."""
        with open(self.FILE_NAME, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def load_tasks(self):
        """Load tasks from JSON file if exists."""
        if os.path.exists(self.FILE_NAME):
            with open(self.FILE_NAME, "r") as f:
                try:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(data) for data in tasks_data]
                    if self.tasks:
                        Task.task_counter = max(task.id for task in self.tasks) + 1
                except json.JSONDecodeError:
                    self.tasks = []


# ------------------------------
# Console Menu
# ------------------------------
def main():
    manager = TaskManager()

    while True:
        print("===== SMART TASK MANAGER =====")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Task as Completed")
        print("4. Delete Task")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            priority = input("Enter priority (High/Medium/Low): ")
            due_date = input("Enter due date (YYYY-MM-DD): ")
            manager.add_task(title, description, priority, due_date)

        elif choice == "2":
            manager.view_tasks()

        elif choice == "3":
            try:
                task_id = int(input("Enter task ID to mark complete: "))
                manager.mark_task_complete(task_id)
            except ValueError:
                print("⚠ Invalid input! Enter a number.\n")

        elif choice == "4":
            try:
                task_id = int(input("Enter task ID to delete: "))
                manager.delete_task(task_id)
            except ValueError:
                print("⚠ Invalid input! Enter a number.\n")

        elif choice == "5":
            print("👋 Exiting Task Manager. Goodbye!")
            break
        else:
            print("⚠ Invalid choice. Try again!\n")


if __name__ == "__main__":
    main()
