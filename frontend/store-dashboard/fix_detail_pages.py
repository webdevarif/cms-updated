#!/usr/bin/env python3
"""
Script to fix async params in all detail pages in [id]/posts directory
"""

import os
import re


def fix_detail_page_async_params(file_path, page_type):
    """Fix async params for a single detail page"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update function signature to include the specific param
        if page_type == "post":
            pattern = r"export default function (\w+)\(\{ params \}: \{ params: Promise<\{ id: string; locale: string \}> \}\) \{"
            replacement = r"export default function \1({ params }: { params: Promise<{ id: string; locale: string; pid: string }> }) {"
        elif page_type == "page":
            pattern = r"export default function (\w+)\(\{ params \}: \{ params: Promise<\{ id: string; locale: string \}> \}\) \{"
            replacement = r"export default function \1({ params }: { params: Promise<{ id: string; locale: string; pageid: string }> }) {"
        elif page_type == "category":
            pattern = r"export default function (\w+)\(\{ params \}: \{ params: Promise<\{ id: string; locale: string \}> \}\) \{"
            replacement = r"export default function \1({ params }: { params: Promise<{ id: string; locale: string; catid: string }> }) {"
        elif page_type == "comment":
            pattern = r"export default function (\w+)\(\{ params \}: \{ params: Promise<\{ id: string; locale: string \}> \}\) \{"
            replacement = r"export default function \1({ params }: { params: Promise<{ id: string; locale: string; cmtid: string }> }) {"
        elif page_type == "posttype":
            pattern = r"export default function (\w+)\(\{ params \}: \{ params: Promise<\{ id: string; locale: string \}> \}\) \{"
            replacement = r"export default function \1({ params }: { params: Promise<{ id: string; locale: string; postTid: string }> }) {"
        elif page_type == "metadata":
            pattern = r"export default function (\w+)\(\{ params \}: \{ params: Promise<\{ id: string; locale: string \}> \}\) \{"
            replacement = r"export default function \1({ params }: { params: Promise<{ id: string; locale: string; metaid: string }> }) {"

        content = re.sub(pattern, replacement, content)

        # Replace the conflicting params usage
        if page_type == "post":
            content = re.sub(
                r"const params = useParams\(\);\s*const router = useRouter\(\);\s*const id = params\.pid as string;",
                "const router = useRouter();\n  const resolvedParams = React.use(params);\n  const id = resolvedParams.pid;",
                content,
            )
        elif page_type == "page":
            content = re.sub(
                r"const params = useParams\(\);\s*const router = useRouter\(\);\s*const id = params\.pageid as string;",
                "const router = useRouter();\n  const resolvedParams = React.use(params);\n  const id = resolvedParams.pageid;",
                content,
            )
        elif page_type == "category":
            content = re.sub(
                r"const params = useParams\(\);\s*const router = useRouter\(\);\s*const id = params\.catid as string;",
                "const router = useRouter();\n  const resolvedParams = React.use(params);\n  const id = resolvedParams.catid;",
                content,
            )
        elif page_type == "comment":
            content = re.sub(
                r"const params = useParams\(\);\s*const router = useRouter\(\);\s*const id = params\.cmtid as string;",
                "const router = useRouter();\n  const resolvedParams = React.use(params);\n  const id = resolvedParams.cmtid;",
                content,
            )
        elif page_type == "posttype":
            content = re.sub(
                r"const params = useParams\(\);\s*const router = useRouter\(\);\s*const id = params\.postTid as string;",
                "const router = useRouter();\n  const resolvedParams = React.use(params);\n  const id = resolvedParams.postTid;",
                content,
            )
        elif page_type == "metadata":
            content = re.sub(
                r"const params = useParams\(\);\s*const router = useRouter\(\);\s*const id = params\.metaid as string;",
                "const router = useRouter();\n  const resolvedParams = React.use(params);\n  const id = resolvedParams.metaid;",
                content,
            )

        # Add React.use import if not present
        if "React, { useState, use }" not in content:
            content = re.sub(
                r"import React, { useState } from 'react';",
                "import React, { useState, use } from 'react';",
                content,
            )

        # Remove unused useParams import
        content = re.sub(
            r"import { useParams, useRouter } from 'next/navigation';",
            "import { useRouter } from 'next/navigation';",
            content,
        )

        # Write the updated content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Fixed {file_path}")
        return True

    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to process all detail pages"""
    posts_dir = (
        "g:/Digital Farmers/cms-updated/frontend/store-dashboard/app/[locale]/stores/[id]/posts"
    )

    # Find and fix all detail pages
    fixed_count = 0
    for root, dirs, files in os.walk(posts_dir):
        for file in files:
            if file == "page.tsx":
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, posts_dir)

                # Determine page type based on directory structure
                if "[pid]" in rel_path:
                    fix_detail_page_async_params(file_path, "post")
                    fixed_count += 1
                elif "[pageid]" in rel_path:
                    fix_detail_page_async_params(file_path, "page")
                    fixed_count += 1
                elif "[catid]" in rel_path:
                    fix_detail_page_async_params(file_path, "category")
                    fixed_count += 1
                elif "[cmtid]" in rel_path:
                    fix_detail_page_async_params(file_path, "comment")
                    fixed_count += 1
                elif "[postTid]" in rel_path:
                    fix_detail_page_async_params(file_path, "posttype")
                    fixed_count += 1
                elif "[metaid]" in rel_path:
                    fix_detail_page_async_params(file_path, "metadata")
                    fixed_count += 1

    print(f"\nFixed {fixed_count} detail page files")


if __name__ == "__main__":
    main()
