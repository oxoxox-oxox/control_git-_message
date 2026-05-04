import sys
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from ui.main_window import MainWindow
from git_operations import GitOperations

class App(MainWindow):
    def __init__(self, repo_path):
        super().__init__()
        self.git_ops = GitOperations(repo_path)
        self.populate_commits()

        self.commit_table.itemSelectionChanged.connect(self.on_commit_selected)
        self.amend_button.clicked.connect(self.amend_message)
        self.revert_button.clicked.connect(self.revert_commit)

    def populate_commits(self):
        self.commit_table.setRowCount(0)
        try:
            commits = self.git_ops.get_commits()
            self.commit_table.setRowCount(len(commits))
            for row, commit in enumerate(commits):
                self.commit_table.setItem(row, 0, QTableWidgetItem(commit.hexsha[:7]))
                self.commit_table.setItem(row, 1, QTableWidgetItem(commit.author.name))
                self.commit_table.setItem(row, 2, QTableWidgetItem(commit.message.strip()))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load commits: {e}")

    def on_commit_selected(self):
        selected_items = self.commit_table.selectedItems()
        if selected_items:
            selected_row = self.commit_table.row(selected_items[0])
            commit_message = self.commit_table.item(selected_row, 2).text()
            self.commit_message_edit.setText(commit_message)

    def amend_message(self):
        selected_items = self.commit_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a commit to amend.")
            return

        selected_row = self.commit_table.row(selected_items[0])
        commit_sha = self.commit_table.item(selected_row, 0).text()
        full_sha = self.git_ops.repo.commit(commit_sha).hexsha
        
        new_message = self.commit_message_edit.toPlainText()

        if not new_message:
            QMessageBox.warning(self, "Warning", "Commit message cannot be empty.")
            return

        # Note: A simple implementation for amending the *last* commit.
        # Amending older commits is a much more complex operation.
        if self.git_ops.repo.head.commit.hexsha.startswith(commit_sha):
             success, message = self.git_ops.amend_commit_message(full_sha, new_message)
             if success:
                 QMessageBox.information(self, "Success", message)
                 self.populate_commits()
             else:
                 QMessageBox.critical(self, "Error", message)
        else:
             QMessageBox.warning(self, "Warning", "This tool currently only supports amending the most recent commit.")


    def revert_commit(self):
        selected_items = self.commit_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a commit to revert.")
            return

        selected_row = self.commit_table.row(selected_items[0])
        commit_sha = self.commit_table.item(selected_row, 0).text()
        full_sha = self.git_ops.repo.commit(commit_sha).hexsha

        reply = QMessageBox.question(self, 'Confirm Revert', 
                                     f"Are you sure you want to revert commit {commit_sha}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.git_ops.revert_commit(full_sha)
            if success:
                QMessageBox.information(self, "Success", message)
                self.populate_commits()
            else:
                QMessageBox.critical(self, "Error", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # You need to provide the path to your git repository here
    # For example: repo_path = 'path/to/your/repo'
    repo_path = '.' 
    main_app = App(repo_path)
    main_app.show()
    sys.exit(app.exec())
