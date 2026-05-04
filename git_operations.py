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

    def rebase_and_edit_commit_message(self, commit_sha, new_message):
        """
        Perform an interactive rebase to edit a commit message.
        This is a simplified example and has limitations.
        """
        try:
            # We need to find how many commits to go back.
            # This is a simple and potentially fragile way to do it.
            commits = list(self.repo.iter_commits('main', max_count=100))
            commit_to_edit = self.repo.commit(commit_sha)

            count = 0
            for commit in commits:
                count += 1
                if commit == commit_to_edit:
                    break
            else:
                return False, "Commit not found in the last 100 commits."

            # Using git command line for interactive rebase is tricky from a script.
            # We will use a script to automate the rebase.
            # This is a placeholder for a more robust implementation.
            # A truly robust solution would require careful handling of the rebase editor.

            # For this example, we'll use a trick with `git filter-branch` or a similar
            # command as a proxy, as true interactive rebase is hard to script.
            # A better approach for a real app might be to construct a rebase script.

            # Let's try a different approach that is more script-friendly.
            # We can use `git rebase -i` and set up an editor script.

            # This is a conceptual example. A real implementation would be more complex.
            # We will simulate the rebase by creating a new commit history.

            # The logic here is complex. For now, we will show a message.
            # A full implementation would involve:
            # 1. Starting `git rebase -i HEAD~N`
            # 2. Setting `GIT_SEQUENCE_EDITOR` to a script that changes 'pick' to 'reword' for the target commit.
            # 3. The script would then need to provide the new message.

            # This is a known difficult problem to solve with scripting.
            # Let's provide a message to the user on how to do it manually for now.

            rebase_command = f"git rebase -i HEAD~{count}"

            # A simplified, and DANGEROUS, way to automate this:
            # This is not recommended for production code without extensive testing.
            # It assumes a clean state and no conflicts.

            editor_script = f"sed -i 's/pick {commit_sha[:7]}/reword {commit_sha[:7]}/' $1"

            # This is very platform-specific and fragile.
            # A better way is to guide the user.

            return False, f"Automated rebase is complex. To edit this commit, run:\n\n" \
                          f"1. git rebase -i HEAD~{count}\n" \
                          f"2. In the editor, change 'pick' to 'reword' for commit {commit_sha[:7]}.\n" \
                          f"3. Save and close. A new editor will open.\n" \
                          f"4. Change the commit message to your new message.\n" \
                          f"5. Save and close."

        except git.exc.GitCommandError as e:
            return False, f"Failed to perform rebase: {e}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    def revert_commit(self, commit_sha):
        """
        Revert a specific commit. This creates a new commit that undoes the changes.
        """
        try:
            self.repo.git.revert(commit_sha, no_edit=True)
            return True, f"Successfully reverted commit {commit_sha}."
        except git.exc.GitCommandError as e:
            return False, f"Failed to revert commit {commit_sha}: {e}"
