import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class GitMessageTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Message Control Tool")
        self.root.geometry("800x600")
        
        self.selected_repo = None
        self.current_commits = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # 仓库选择区域
        repo_frame = ttk.LabelFrame(self.root, text="仓库选择")
        repo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.repo_path_var = tk.StringVar()
        ttk.Entry(repo_frame, textvariable=self.repo_path_var, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(repo_frame, text="浏览", command=self.browse_repo).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(repo_frame, text="验证", command=self.validate_repo).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Commit历史区域
        commit_frame = ttk.LabelFrame(self.root, text="Commit历史")
        commit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.commit_list = tk.Listbox(commit_frame, width=80, height=20)
        self.commit_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(commit_frame, orient=tk.VERTICAL, command=self.commit_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.commit_list.config(yscrollcommand=scrollbar.set)
        self.commit_list.bind('<<ListboxSelect>>', self.on_commit_select)
        
        # Message编辑区域
        message_frame = ttk.LabelFrame(self.root, text="修改Message")
        message_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(message_frame, text="新Message:").pack(anchor=tk.W, padx=5, pady=5)
        self.new_message = tk.Text(message_frame, height=5)
        self.new_message.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 添加确认修改按钮，确保用户能看到
        ttk.Button(button_frame, text="确认修改Message", command=self.update_message).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="刷新Commit", command=self.refresh_commits).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="切换分支", command=self.switch_branch).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 确保窗口大小合适
        self.root.update()
        self.root.minsize(800, 600)
    
    def browse_repo(self):
        path = filedialog.askdirectory(title="选择Git仓库")
        if path:
            self.repo_path_var.set(path)
    
    def validate_repo(self):
        path = self.repo_path_var.get()
        if not path:
            messagebox.showwarning("警告", "请先选择仓库路径")
            return
        
        if not self.is_git_repo(path):
            messagebox.showerror("错误", "选择的目录不是Git仓库")
            return
        
        if not self.is_github_repo(path):
            messagebox.showwarning("警告", "选择的仓库未与GitHub关联")
            return
        
        self.selected_repo = path
        
        # 自动检查并切换到正确的分支
        self.auto_switch_branch()
        
        messagebox.showinfo("成功", f"仓库验证成功：{path}")
        self.refresh_commits()
    
    def auto_switch_branch(self):
        if not self.selected_repo:
            return
        
        try:
            # 检查当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.selected_repo,
                text=True,
                capture_output=True
            )
            current_branch = result.stdout.strip()
            print(f"Current branch: {current_branch}")
            
            # 检查是否有远程分支
            result = subprocess.run(
                ['git', 'branch', '-r'],
                cwd=self.selected_repo,
                text=True,
                capture_output=True
            )
            
            remote_branches = [b.strip() for b in result.stdout.strip().split('\n') if b.strip()]
            if not remote_branches:
                return
            
            # 清理远程分支名称，移除HEAD引用信息
            clean_remote_branches = []
            for branch in remote_branches:
                # 移除类似 "HEAD -> origin/main" 中的箭头部分
                if '->' in branch:
                    branch = branch.split('->')[-1].strip()
                clean_remote_branches.append(branch)
            
            print(f"Clean remote branches: {clean_remote_branches}")
            
            # 检查当前分支是否有commits
            result = subprocess.run(
                ['git', 'log', '--oneline', '-1'],
                cwd=self.selected_repo,
                text=True,
                capture_output=True
            )
            
            if result.returncode != 0:
                # 当前分支没有commits，尝试切换到远程分支
                for remote_branch in clean_remote_branches:
                    # 优先选择main或master分支
                    if 'main' in remote_branch or 'master' in remote_branch:
                        # 确保分支名格式正确（remotes/origin/branch）
                        if not remote_branch.startswith('remotes/'):
                            remote_branch = f'remotes/{remote_branch}'
                        
                        # 提取本地分支名
                        local_branch = remote_branch.replace('remotes/origin/', '')
                        print(f"Trying to switch to: {local_branch} from {remote_branch}")
                        
                        # 检查是否有未跟踪的文件
                        status_result = subprocess.run(
                            ['git', 'status', '--porcelain'],
                            cwd=self.selected_repo,
                            text=True,
                            capture_output=True
                        )
                        
                        has_untracked = '??' in status_result.stdout
                        
                        if has_untracked:
                            print("Untracked files found, trying with --force")
                            # 有未跟踪文件，使用 -f 强制切换
                            result = subprocess.run(
                                ['git', 'checkout', '-b', local_branch, remote_branch, '--force'],
                                cwd=self.selected_repo,
                                text=True,
                                capture_output=True
                            )
                        else:
                            # 没有未跟踪文件，正常切换
                            result = subprocess.run(
                                ['git', 'checkout', '-b', local_branch, remote_branch],
                                cwd=self.selected_repo,
                                text=True,
                                capture_output=True
                            )
                        
                        if result.returncode == 0:
                            print(f"Successfully switched to: {local_branch}")
                            # 验证切换是否成功
                            verify_result = subprocess.run(
                                ['git', 'branch', '--show-current'],
                                cwd=self.selected_repo,
                                text=True,
                                capture_output=True
                            )
                            print(f"Verified branch: {verify_result.stdout.strip()}")
                            break
                        else:
                            print(f"Error switching branch: {result.stderr}")
                            # 尝试另一种方法：先创建分支，再设置上游
                            print("Trying alternative method: create branch then set upstream")
                            
                            # 创建本地分支
                            create_result = subprocess.run(
                                ['git', 'branch', local_branch],
                                cwd=self.selected_repo,
                                text=True,
                                capture_output=True
                            )
                            
                            if create_result.returncode == 0:
                                # 切换到本地分支
                                checkout_result = subprocess.run(
                                    ['git', 'checkout', local_branch],
                                    cwd=self.selected_repo,
                                    text=True,
                                    capture_output=True
                                )
                                
                                if checkout_result.returncode == 0:
                                    # 设置上游分支
                                    upstream_result = subprocess.run(
                                        ['git', 'branch', '--set-upstream-to', remote_branch],
                                        cwd=self.selected_repo,
                                        text=True,
                                        capture_output=True
                                    )
                                    
                                    if upstream_result.returncode == 0:
                                        # 拉取最新代码
                                        pull_result = subprocess.run(
                                            ['git', 'pull'],
                                            cwd=self.selected_repo,
                                            text=True,
                                            capture_output=True
                                        )
                                        
                                        if pull_result.returncode == 0:
                                            print(f"Successfully set up branch: {local_branch}")
                                            break
        except Exception as e:
            print(f"Error auto-switching branch: {str(e)}")
    
    def check_branch(self, repo_path):
        try:
            # 检查当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=repo_path,
                text=True,
                capture_output=True
            )
            current_branch = result.stdout.strip()
            print(f"Current branch: {current_branch}")
            
            # 检查所有分支
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=repo_path,
                text=True,
                capture_output=True
            )
            print(f"All branches: {result.stdout}")
            
            return current_branch
        except Exception as e:
            print(f"Error checking branch: {str(e)}")
            return None
    
    def refresh_commits(self):
        if not self.selected_repo:
            messagebox.showwarning("警告", "请先选择并验证仓库")
            return
        
        # 检查分支
        self.check_branch(self.selected_repo)
        
        # 尝试获取所有分支的commits
        commits = self.get_commits(self.selected_repo)
        if commits:
            self.current_commits = commits
            self.commit_list.delete(0, tk.END)
            for commit in commits:
                if commit:
                    self.commit_list.insert(tk.END, commit)
        else:
            # 尝试检查远程分支
            try:
                result = subprocess.run(
                    ['git', 'branch', '-r'],
                    cwd=self.selected_repo,
                    text=True,
                    capture_output=True
                )
                remote_branches = result.stdout.strip().split('\n')
                if remote_branches and remote_branches[0]:
                    messagebox.showinfo("提示", f"发现远程分支：{remote_branches[0]}\n请先切换到正确的分支")
                else:
                    messagebox.showinfo("提示", "该仓库还没有任何Commit记录")
            except Exception:
                messagebox.showinfo("提示", "该仓库还没有任何Commit记录")
    
    def on_commit_select(self, event):
        # 可以在这里添加显示选中commit的详细信息
        pass
    
    def switch_branch(self):
        if not self.selected_repo:
            messagebox.showwarning("警告", "请先选择并验证仓库")
            return
        
        try:
            # 获取所有远程分支
            result = subprocess.run(
                ['git', 'branch', '-r'],
                cwd=self.selected_repo,
                text=True,
                capture_output=True
            )
            
            remote_branches = [b.strip() for b in result.stdout.strip().split('\n') if b.strip()]
            if not remote_branches:
                messagebox.showinfo("提示", "没有发现远程分支")
                return
            
            # 创建分支选择对话框
            branch_window = tk.Toplevel(self.root)
            branch_window.title("切换分支")
            branch_window.geometry("400x300")
            
            ttk.Label(branch_window, text="选择要切换的分支：").pack(padx=10, pady=10)
            
            # 分支列表
            branch_var = tk.StringVar()
            branch_listbox = tk.Listbox(branch_window, height=10, width=50)
            branch_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            for branch in remote_branches:
                branch_listbox.insert(tk.END, branch)
            
            # 切换按钮
            def do_switch():
                selected_indices = branch_listbox.curselection()
                if not selected_indices:
                    messagebox.showwarning("警告", "请选择一个分支")
                    return
                
                selected_branch = branch_listbox.get(selected_indices[0])
                # 转换远程分支为本地分支名（去掉remotes/origin/前缀）
                local_branch = selected_branch.replace('remotes/origin/', '')
                
                try:
                    # 检查本地是否存在该分支
                    result = subprocess.run(
                        ['git', 'branch'],
                        cwd=self.selected_repo,
                        text=True,
                        capture_output=True
                    )
                    
                    local_branches = [b.strip().replace('* ', '') for b in result.stdout.strip().split('\n') if b.strip()]
                    
                    if local_branch in local_branches:
                        # 本地存在该分支，直接切换
                        result = subprocess.run(
                            ['git', 'checkout', local_branch],
                            cwd=self.selected_repo,
                            text=True,
                            capture_output=True
                        )
                    else:
                        # 本地不存在该分支，创建并切换
                        result = subprocess.run(
                            ['git', 'checkout', '-b', local_branch, selected_branch],
                            cwd=self.selected_repo,
                            text=True,
                            capture_output=True
                        )
                    
                    if result.returncode == 0:
                        messagebox.showinfo("成功", f"成功切换到分支：{local_branch}")
                        branch_window.destroy()
                        self.refresh_commits()
                    else:
                        messagebox.showerror("错误", f"切换分支失败：{result.stderr}")
                except Exception as e:
                    messagebox.showerror("错误", f"切换分支失败：{str(e)}")
            
            ttk.Button(branch_window, text="切换", command=do_switch).pack(padx=10, pady=10)
            ttk.Button(branch_window, text="取消", command=branch_window.destroy).pack(padx=10, pady=5)
            
        except Exception as e:
            messagebox.showerror("错误", f"获取分支列表失败：{str(e)}")
    
    def update_message(self):
        if not self.selected_repo:
            messagebox.showwarning("警告", "请先选择并验证仓库")
            return
        
        new_message = self.new_message.get(1.0, tk.END).strip()
        if not new_message:
            messagebox.showwarning("警告", "请输入新的Message")
            return
        
        if self.amend_commit_message(self.selected_repo, new_message):
            messagebox.showinfo("成功", "Message修改成功")
            self.refresh_commits()
        else:
            messagebox.showerror("错误", "Message修改失败")
    
    def is_git_repo(self, path):
        return os.path.isdir(os.path.join(path, '.git'))
    
    def is_github_repo(self, path):
        try:
            result = subprocess.run(
                ['git', '-C', path, 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )
            return 'github.com' in result.stdout
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False
    
    def get_commits(self, repo_path, limit=50):
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', f'-{limit}'],
                cwd=repo_path,
                text=True,
                capture_output=True
            )
            if result.returncode != 0:
                print(f"Git log error: {result.stderr}")
                return None
            commits = result.stdout.strip().split('\n')
            return [commit for commit in commits if commit]
        except Exception as e:
            print(f"Error getting commits: {str(e)}")
            return None
    
    def amend_commit_message(self, repo_path, new_message):
        try:
            result = subprocess.run(
                ['git', 'commit', '--amend', '-m', new_message],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = GitMessageTool(root)
    root.mainloop()
     