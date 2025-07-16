"""
Git Utilities

This module provides utilities for interacting with git,
specifically for modifying commit messages during push operations.
"""

import subprocess
import tempfile
import os
from typing import List, Optional


class GitUtils:
    """Utilities for git operations."""
    
    @staticmethod
    def get_last_commit_message() -> str:
        """Get the message of the last commit."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%B'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get last commit message: {e}")
    
    @staticmethod
    def get_last_commit_hash() -> str:
        """Get the hash of the last commit."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get last commit hash: {e}")
    
    @staticmethod
    def amend_commit_message(new_message: str) -> bool:
        """
        Amend the last commit with a new message.
        
        Args:
            new_message: The new commit message
            
        Returns:
            True if successful, False otherwise
        """
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
                    capture_output=True
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
            return False
    
    @staticmethod
    def create_validation_failure_appendix(
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
    
    @staticmethod
    def append_to_commit_message(
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
            current_message = GitUtils.get_last_commit_message()
            
            # Create appendix
            appendix = GitUtils.create_validation_failure_appendix(
                justification, errors, warnings
            )
            
            # Combine messages
            new_message = current_message + appendix
            
            # Amend the commit
            return GitUtils.amend_commit_message(new_message)
            
        except Exception as e:
            print(f"Failed to append to commit message: {e}")
            return False
    
    @staticmethod
    def is_git_repository() -> bool:
        """Check if current directory is a git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def get_current_branch() -> Optional[str]:
        """Get the name of the current git branch."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def has_uncommitted_changes() -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False 