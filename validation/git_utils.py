"""
Git Utilities

This module provides utilities for interacting with git,
specifically for modifying commit messages during push operations.
"""

import subprocess
import tempfile
import os
from typing import List, Optional
from datetime import datetime


class GitUtils:
    """Utilities for git operations."""
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize with optional repository path."""
        self.repo_path = repo_path or os.getcwd()
    
    def get_last_commit_message(self) -> str:
        """Get the message of the last commit."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%B'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get last commit message: {e}")
    
    def get_last_commit_hash(self) -> str:
        """Get the hash of the last commit."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get last commit hash: {e}")
    
    def amend_commit_message(self, new_message: str) -> bool:
        """
        Amend the last commit with a new message.
        
        Args:
            new_message: The new commit message
            
        Returns:
            True if successful, False otherwise
        """
        # First check if we can amend (no uncommitted changes, etc.)
        if not self._can_amend_commit():
            print("Cannot amend commit (may have uncommitted changes or other git state issues)")
            return self._create_validation_override_commit(new_message)
        
        try:
            # Create a temporary file with the new message
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(new_message)
                temp_file = f.name
            
            try:
                # Amend the commit with the new message
                subprocess.run(
                    ['git', 'commit', '--amend', '-F', temp_file],
                    check=True,
                    capture_output=True,
                    cwd=self.repo_path
                )
                return True
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
                    
        except subprocess.CalledProcessError as e:
            print(f"Failed to amend commit message: {e}")
            print("Attempting to create validation override commit instead...")
            return self._create_validation_override_commit(new_message)
    
    def _can_amend_commit(self) -> bool:
        """Check if the current git state allows amending the last commit."""
        try:
            # Check if there are uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path
            )
            
            # If there are uncommitted changes, we can't amend safely
            if result.stdout.strip():
                return False
            
            # Check if there are any commits to amend
            subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                check=True,
                cwd=self.repo_path
            )
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _create_validation_override_commit(self, message: str) -> bool:
        """Create a separate commit with validation override information."""
        try:
            # Create a validation override file
            override_file = ".validation_override"
            with open(os.path.join(self.repo_path, override_file), 'w') as f:
                f.write(f"Validation Override Record\n")
                f.write(f"========================\n\n")
                f.write(message)
            
            # Add and commit the override file
            subprocess.run(
                ['git', 'add', override_file],
                check=True,
                capture_output=True,
                cwd=self.repo_path
            )
            
            subprocess.run(
                ['git', 'commit', '-m', 'API Validation Override Record\n\n' + message],
                check=True,
                capture_output=True,
                cwd=self.repo_path
            )
            
            print(f"✅ Created validation override commit with details in {override_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create validation override commit: {e}")
            # As last resort, just log the information
            return self._log_validation_override(message)
    
    def _log_validation_override(self, message: str) -> bool:
        """Log validation override information to a file as last resort."""
        try:
            log_file = os.path.join(self.repo_path, ".api_validation_overrides.log")
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"\n{'='*60}\n")
                f.write(f"Validation Override: {timestamp}\n")
                f.write(f"{'='*60}\n")
                f.write(message)
                f.write(f"\n{'='*60}\n\n")
            
            print(f"⚠️ Logged validation override to {log_file}")
            return True
        except Exception as e:
            print(f"Failed to log validation override: {e}")
            return False
    
    def create_validation_failure_appendix(
        self,
        justification: str, 
        errors: List[str], 
        warnings: List[str]
    ) -> str:
        """
        Create an appendix for commit message with validation failure details.
        
        Args:
            justification: User's justification for proceeding
            errors: List of validation errors
            warnings: List of validation warnings
            
        Returns:
            Formatted appendix text
        """
        appendix_parts = [
            "\n" + "="*50,
            "⚠️  VALIDATION OVERRIDE NOTICE",
            "="*50
        ]
        
        # Add justification
        appendix_parts.extend([
            "",
            "JUSTIFICATION:",
            f"  {justification}",
            ""
        ])
        
        # Add validation failures
        if errors:
            appendix_parts.extend([
                f"VALIDATION ERRORS ({len(errors)}):",
                *[f"  • {error}" for error in errors],
                ""
            ])
        
        if warnings:
            appendix_parts.extend([
                f"VALIDATION WARNINGS ({len(warnings)}):",
                *[f"  • {warning}" for warning in warnings],
                ""
            ])
        
        # Add metadata
        appendix_parts.extend([
            "This commit was pushed despite validation failures.",
            "Review and address these issues in a follow-up commit.",
            "="*50
        ])
        
        return "\n".join(appendix_parts)
    
    def append_to_commit_message(
        self,
        justification: str,
        errors: List[str],
        warnings: List[str]
    ) -> bool:
        """
        Append validation failure details to the last commit message.
        
        Args:
            justification: User's justification
            errors: List of validation errors
            warnings: List of validation warnings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current commit message
            current_message = self.get_last_commit_message()
            
            # Create appendix
            appendix = self.create_validation_failure_appendix(
                justification, errors, warnings
            )
            
            # Combine messages
            new_message = current_message + appendix
            
            # Amend the commit
            return self.amend_commit_message(new_message)
            
        except Exception as e:
            print(f"Failed to append to commit message: {e}")
            return False
    
    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                check=True,
                cwd=self.repo_path
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current git branch."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_path
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False 