import datetime
import json
import os
from collections import deque

# ------------------------------
# Task Class
# ------------------------------
class Task:
    task_counter = 1

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
# Task Manager
# ------------------------------
class TaskManager:
    FILE_NAME = "tasks.json"

    def __init__(self):
        self.tasks = []
        self.undo_stack = []   # stack for undo
        self.reminder_queue = deque()  # queue for reminders
        self.load_tasks()
        self.build_reminder_queue()

    # ---------- CRUD ----------
    def add_task(self, title, description, priority, due_date):
        try:
            due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
            task = Task(title, description, priority, due_date_obj)
            self.tasks.append(task)
            self.save_tasks()

            # Add to reminder queue if due soon
            if (due_date_obj - datetime.date.today()).days <= 3:
                self.reminder_queue.append(task)

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
                self.undo_stack.append(task)  # save for undo
                self.tasks.remove(task)
                self.save_tasks()
                print("🗑 Task deleted successfully! (Undo available)\n")
                return
        print("⚠ Task not found!\n")

    # ---------- Sorting ----------
    def sort_by_due_date(self):
        self.tasks.sort(key=lambda t: t.due_date)
        print("📅 Tasks sorted by due date!\n")
        self.view_tasks()

    def sort_by_priority(self):
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        self.tasks.sort(key=lambda t: priority_order.get(t.priority, 4))
        print("⭐ Tasks sorted by priority!\n")
        self.view_tasks()

    # ---------- Searching ----------
    def search_tasks(self, keyword):
        results = [task for task in self.tasks if keyword.lower() in task.title.lower() or keyword.lower() in task.description.lower()]
        if results:
            print(f"🔍 Search results for '{keyword}':\n")
            for task in results:
                print(task)
        else:
            print(f"⚠ No tasks found with keyword '{keyword}'.\n")

    # ---------- Undo ----------
    def undo_delete(self):
        if not self.undo_stack:
            print("⚠ Nothing to undo.\n")
            return
        last_deleted = self.undo_stack.pop()
        self.tasks.append(last_deleted)
        self.save_tasks()
        print(f"↩ Undo successful! Restored task: {last_deleted}\n")

    # ---------- Reminders (Queue) ----------
    def build_reminder_queue(self):
        """Rebuild the reminder queue from tasks due soon."""
        self.reminder_queue.clear()
        for task in sorted(self.tasks, key=lambda t: t.due_date):
            if (task.due_date - datetime.date.today()).days <= 3 and task.status == "Pending":
                self.reminder_queue.append(task)

    def show_next_reminder(self):
        if not self.reminder_queue:
            print("📭 No upcoming reminders!\n")
            return
        next_task = self.reminder_queue.popleft()
        print(f"🔔 Reminder: {next_task}\n")

    # ---------- File I/O ----------
    def save_tasks(self):
        with open(self.FILE_NAME, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def load_tasks(self):
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
        print("5. Sort by Due Date")
        print("6. Sort by Priority")
        print("7. Search Tasks")
        print("8. Undo Delete")
        print("9. Show Next Reminder")
        print("10. Exit")
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
            manager.sort_by_due_date()

        elif choice == "6":
            manager.sort_by_priority()

        elif choice == "7":
            keyword = input("Enter keyword to search: ")
            manager.search_tasks(keyword)

        elif choice == "8":
            manager.undo_delete()

        elif choice == "9":
            manager.show_next_reminder()

        elif choice == "10":
            print("👋 Exiting Task Manager. Goodbye!")
            break
        else:
            print("⚠ Invalid choice. Try again!\n")


if __name__ == "__main__":
    main()
