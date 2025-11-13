"""
Git integration tools for repository management
"""
import subprocess
import os
from typing import Dict, Any
from pathlib import Path
from .base import Tool


class GitStatus(Tool):
    """Get git repository status"""

    def get_name(self) -> str:
        return "git_status"

    def get_description(self) -> str:
        return "Get the status of the current git repository"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository (default: current directory)",
                    "default": "."
                }
            }
        }

    def execute(self, repo_path: str = ".") -> Dict[str, Any]:
        """Get git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain', '-b'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {"error": result.stderr or "Not a git repository"}

            # Parse status
            lines = result.stdout.strip().split('\n')
            branch_info = lines[0] if lines else ""
            files = lines[1:] if len(lines) > 1 else []

            # Get current branch
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            current_branch = branch_result.stdout.strip()

            return {
                "branch": current_branch,
                "branch_info": branch_info,
                "files": files,
                "clean": len(files) == 0 or (len(files) == 1 and not files[0]),
                "raw_output": result.stdout
            }

        except Exception as e:
            return {"error": str(e)}


class GitDiff(Tool):
    """View git diff"""

    def get_name(self) -> str:
        return "git_diff"

    def get_description(self) -> str:
        return "View git diff for staged or unstaged changes"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository",
                    "default": "."
                },
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes (default: false shows unstaged)",
                    "default": False
                },
                "file_path": {
                    "type": "string",
                    "description": "Specific file to diff (optional)"
                }
            }
        }

    def execute(self, repo_path: str = ".", staged: bool = False, file_path: str = None) -> Dict[str, Any]:
        """Get git diff"""
        try:
            cmd = ['git', 'diff']
            if staged:
                cmd.append('--cached')
            if file_path:
                cmd.append(file_path)

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "diff": result.stdout,
                "has_changes": bool(result.stdout.strip())
            }

        except Exception as e:
            return {"error": str(e)}


class GitCommit(Tool):
    """Create a git commit"""

    def get_name(self) -> str:
        return "git_commit"

    def get_description(self) -> str:
        return "Create a git commit with the specified message"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Commit message"
                },
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository",
                    "default": "."
                },
                "add_all": {
                    "type": "boolean",
                    "description": "Add all changes before committing",
                    "default": False
                }
            },
            "required": ["message"]
        }

    def execute(self, message: str, repo_path: str = ".", add_all: bool = False) -> Dict[str, Any]:
        """Create a commit"""
        try:
            if add_all:
                # Add all changes
                add_result = subprocess.run(
                    ['git', 'add', '-A'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if add_result.returncode != 0:
                    return {"error": f"Failed to add files: {add_result.stderr}"}

            # Create commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": result.stderr or "Commit failed"}

            return {
                "success": True,
                "output": result.stdout,
                "message": message
            }

        except Exception as e:
            return {"error": str(e)}


class GitBranch(Tool):
    """Manage git branches"""

    def get_name(self) -> str:
        return "git_branch"

    def get_description(self) -> str:
        return "List, create, or switch git branches"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create", "switch", "delete"],
                    "description": "Action to perform"
                },
                "branch_name": {
                    "type": "string",
                    "description": "Branch name (required for create/switch/delete)"
                },
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository",
                    "default": "."
                }
            },
            "required": ["action"]
        }

    def execute(self, action: str, branch_name: str = None, repo_path: str = ".") -> Dict[str, Any]:
        """Manage branches"""
        try:
            if action == "list":
                result = subprocess.run(
                    ['git', 'branch', '-a'],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                branches = [line.strip().replace('* ', '') for line in result.stdout.split('\n') if line.strip()]
                return {"branches": branches, "output": result.stdout}

            elif action == "create":
                if not branch_name:
                    return {"error": "branch_name required for create action"}
                result = subprocess.run(
                    ['git', 'branch', branch_name],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return {"error": result.stderr}
                return {"success": True, "branch": branch_name, "action": "created"}

            elif action == "switch":
                if not branch_name:
                    return {"error": "branch_name required for switch action"}
                result = subprocess.run(
                    ['git', 'checkout', branch_name],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return {"error": result.stderr}
                return {"success": True, "branch": branch_name, "action": "switched"}

            elif action == "delete":
                if not branch_name:
                    return {"error": "branch_name required for delete action"}
                result = subprocess.run(
                    ['git', 'branch', '-d', branch_name],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return {"error": result.stderr}
                return {"success": True, "branch": branch_name, "action": "deleted"}

            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            return {"error": str(e)}


class GitPush(Tool):
    """Push commits to remote"""

    def get_name(self) -> str:
        return "git_push"

    def get_description(self) -> str:
        return "Push commits to remote repository"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository",
                    "default": "."
                },
                "remote": {
                    "type": "string",
                    "description": "Remote name (default: origin)",
                    "default": "origin"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch to push (optional, defaults to current)"
                },
                "force": {
                    "type": "boolean",
                    "description": "Force push (use with caution)",
                    "default": False
                }
            }
        }

    def execute(self, repo_path: str = ".", remote: str = "origin", branch: str = None, force: bool = False) -> Dict[str, Any]:
        """Push to remote"""
        try:
            cmd = ['git', 'push', remote]
            if branch:
                cmd.append(branch)
            if force:
                cmd.append('--force')

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {"error": result.stderr or "Push failed"}

            return {
                "success": True,
                "output": result.stdout + result.stderr
            }

        except Exception as e:
            return {"error": str(e)}


class GitPull(Tool):
    """Pull changes from remote"""

    def get_name(self) -> str:
        return "git_pull"

    def get_description(self) -> str:
        return "Pull changes from remote repository"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository",
                    "default": "."
                },
                "remote": {
                    "type": "string",
                    "description": "Remote name (default: origin)",
                    "default": "origin"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch to pull (optional)"
                }
            }
        }

    def execute(self, repo_path: str = ".", remote: str = "origin", branch: str = None) -> Dict[str, Any]:
        """Pull from remote"""
        try:
            cmd = ['git', 'pull', remote]
            if branch:
                cmd.append(branch)

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return {"error": result.stderr or "Pull failed"}

            return {
                "success": True,
                "output": result.stdout
            }

        except Exception as e:
            return {"error": str(e)}


class GitLog(Tool):
    """View git commit history"""

    def get_name(self) -> str:
        return "git_log"

    def get_description(self) -> str:
        return "View git commit history"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repository",
                    "default": "."
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of commits to show (default: 10)",
                    "default": 10
                },
                "oneline": {
                    "type": "boolean",
                    "description": "Show one line per commit",
                    "default": True
                }
            }
        }

    def execute(self, repo_path: str = ".", limit: int = 10, oneline: bool = True) -> Dict[str, Any]:
        """Get commit history"""
        try:
            cmd = ['git', 'log', f'-{limit}']
            if oneline:
                cmd.append('--oneline')

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": result.stderr}

            commits = [line.strip() for line in result.stdout.split('\n') if line.strip()]

            return {
                "commits": commits,
                "count": len(commits),
                "output": result.stdout
            }

        except Exception as e:
            return {"error": str(e)}
