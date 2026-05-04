import git

class GitOperations:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)

    def get_commits(self, n=50):
        """Get the last n commits."""
        commits = list(self.repo.iter_commits('main', max_count=n))
        return commits

    def amend_commit_message(self, commit_sha, new_message):
        """
        Amend the message of a specific commit.
        This is a complex and potentially dangerous operation, especially for older commits.
        A simple approach for the most recent commit is `git commit --amend`.
        For older commits, interactive rebase is required.
        This is a placeholder for a more complex implementation.
        """
        # For simplicity, this example only shows how to amend the *last* commit message.
        # Amending older commits requires interactive rebase, which is much more complex.
        if self.repo.head.commit.hexsha == commit_sha:
            self.repo.git.commit('--amend', '-m', new_message)
            return True, "Successfully amended the last commit message."
        else:
            # Interactive rebase logic would go here.
            # This is non-trivial to implement with GitPython.
            return False, "Amending older commits requires interactive rebase, which is not implemented in this example."

    def revert_commit(self, commit_sha):
        """
        Revert a specific commit. This creates a new commit that undoes the changes.
        """
        try:
            self.repo.git.revert(commit_sha, no_edit=True)
            return True, f"Successfully reverted commit {commit_sha}."
        except git.exc.GitCommandError as e:
            return False, f"Failed to revert commit {commit_sha}: {e}"

