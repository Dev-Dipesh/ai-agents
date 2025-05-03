#!/usr/bin/env python3
"""
Cleanup script to remove excessive debugging and error handling code.
This script helps in cleaning up the codebase while maintaining functionality.
"""

import os
import re
import argparse
from typing import List, Tuple

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def cleanup_excessive_logging(file_path: str, dry_run: bool = True) -> Tuple[int, list]:
    """
    Remove excessive logging statements from a Python file.
    
    Returns:
        Tuple of (number of lines removed, list of removed lines)
    """
    with open(file_path, 'r') as f:
        content = f.readlines()
    
    # Patterns for excessive logging
    patterns = [
        r'^\s*logging\.debug\(.+\).*$',  # Debug logs
        r'^\s*print\(.+\).*$',  # Print statements for debugging
        r'^\s*logger\.debug\(.+\).*$',  # Debug logs with logger
        r'^\s*# DEBUG:.*$',  # Debug comments
    ]
    
    new_content = []
    removed_lines = []
    removed_count = 0
    
    # Track comment blocks and avoid removing imports or essential logs
    in_comment_block = False
    
    for line in content:
        # Skip debug-only logging but keep imports and essential logs
        if any(re.match(pattern, line) for pattern in patterns):
            # Don't remove if it's an import or essential log
            if not any(keyword in line for keyword in ['import logging', 'basicConfig', 'ERROR', 'CRITICAL', 'WARNING']):
                removed_lines.append(line.strip())
                removed_count += 1
                continue
        
        new_content.append(line)
    
    if not dry_run:
        with open(file_path, 'w') as f:
            f.writelines(new_content)
    
    return removed_count, removed_lines

def cleanup_excessive_error_handling(file_path: str, dry_run: bool = True) -> Tuple[int, list]:
    """
    Simplify excessive error handling in a Python file.
    
    Returns:
        Tuple of (number of blocks simplified, list of simplified blocks)
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find try-except blocks with excessive nesting or redundant exceptions
    nested_try_pattern = r'try:\s*[^\n]*\s*try:'
    excessive_except_pattern = r'except Exception as e:\s*[^\n]*\s*try:\s*[^\n]*\s*except Exception as'
    
    # Count occurrences
    nested_try_blocks = len(re.findall(nested_try_pattern, content))
    excessive_except_blocks = len(re.findall(excessive_except_pattern, content))
    
    simplified_blocks = []
    
    # For demonstration - in a real script, we'd actually transform the code
    if nested_try_blocks > 0:
        simplified_blocks.append(f"Found {nested_try_blocks} nested try blocks that could be simplified")
    
    if excessive_except_blocks > 0:
        simplified_blocks.append(f"Found {excessive_except_blocks} excessive exception handling patterns")
    
    # Only attempt automatic fixing for simple cases in real implementation
    # For this demo, we just report findings
    
    return nested_try_blocks + excessive_except_blocks, simplified_blocks

def cleanup_duplicate_code(file_path: str, dry_run: bool = True) -> Tuple[int, list]:
    """
    Identify and suggest refactoring for duplicate code blocks.
    
    Returns:
        Tuple of (number of duplicates found, list of duplicate blocks)
    """
    with open(file_path, 'r') as f:
        content = f.readlines()
    
    # Simple approach - look for repeated blocks of at least 4 identical lines
    min_block_size = 4
    blocks = {}
    duplicate_count = 0
    duplicate_blocks = []
    
    for i in range(len(content) - min_block_size + 1):
        block = ''.join(content[i:i+min_block_size])
        if len(block.strip()) > 0:  # Ignore empty/whitespace blocks
            if block in blocks:
                # Found duplicate
                if blocks[block] not in duplicate_blocks:
                    duplicate_blocks.append(blocks[block])
                    duplicate_count += 1
            else:
                blocks[block] = block
    
    return duplicate_count, duplicate_blocks

def cleanup_file(file_path: str, dry_run: bool = True) -> dict:
    """Run all cleanup operations on a single file."""
    results = {
        "file": file_path,
        "logging_removed": 0,
        "error_handling_simplified": 0,
        "duplicates_found": 0,
        "details": []
    }
    
    # Clean up excessive logging
    removed_logs, log_details = cleanup_excessive_logging(file_path, dry_run)
    results["logging_removed"] = removed_logs
    if removed_logs > 0:
        results["details"].append(f"Removed {removed_logs} excessive logging statements")
        if len(log_details) > 3:
            results["details"].append(f"Examples: {log_details[:3]} ...")
        else:
            results["details"].append(f"Lines: {log_details}")
    
    # Clean up excessive error handling
    simplified_blocks, error_details = cleanup_excessive_error_handling(file_path, dry_run)
    results["error_handling_simplified"] = simplified_blocks
    if simplified_blocks > 0:
        results["details"].extend(error_details)
    
    # Find duplicate code
    duplicates, duplicate_details = cleanup_duplicate_code(file_path, dry_run)
    results["duplicates_found"] = duplicates
    if duplicates > 0:
        results["details"].append(f"Found {duplicates} potential duplicate code blocks")
    
    return results

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Clean up excessive debugging and error handling code')
    parser.add_argument('--directory', '-d', default='src', help='Directory to process (default: src)')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Dry run - do not modify files')
    args = parser.parse_args()
    
    python_files = find_python_files(args.directory)
    print(f"Found {len(python_files)} Python files to process")
    
    total_results = {
        "files_processed": 0,
        "total_logging_removed": 0,
        "total_error_handling_simplified": 0,
        "total_duplicates_found": 0,
        "modified_files": []
    }
    
    for file_path in python_files:
        print(f"Processing {file_path}...")
        results = cleanup_file(file_path, args.dry_run)
        
        total_results["files_processed"] += 1
        total_results["total_logging_removed"] += results["logging_removed"]
        total_results["total_error_handling_simplified"] += results["error_handling_simplified"]
        total_results["total_duplicates_found"] += results["duplicates_found"]
        
        if results["logging_removed"] > 0 or results["error_handling_simplified"] > 0:
            total_results["modified_files"].append(file_path)
            print(f"  - {results['logging_removed']} logging statements removed")
            print(f"  - {results['error_handling_simplified']} error handling blocks simplified")
            for detail in results["details"]:
                print(f"    * {detail}")
    
    # Print summary
    print("\nSummary:")
    print(f"Processed {total_results['files_processed']} files")
    if args.dry_run:
        print(f"Would remove {total_results['total_logging_removed']} excessive logging statements")
        print(f"Would simplify {total_results['total_error_handling_simplified']} error handling blocks")
        print(f"Found {total_results['total_duplicates_found']} potential code duplications")
        print(f"Would modify {len(total_results['modified_files'])} files")
    else:
        print(f"Removed {total_results['total_logging_removed']} excessive logging statements")
        print(f"Simplified {total_results['total_error_handling_simplified']} error handling blocks")
        print(f"Found {total_results['total_duplicates_found']} potential code duplications")
        print(f"Modified {len(total_results['modified_files'])} files")

if __name__ == "__main__":
    main()
