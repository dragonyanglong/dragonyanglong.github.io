#!/usr/bin/env python3
"""
Auto-add new publication to personal website.
Usage: python3 add_publication.py <DOI> [pdf_path]
python3 add_publication.py 10.1021/jacs.5c17193 ~/Downloads/paper.pdf
"""

import sys
import os
import re
import json
import shutil
import urllib.request
import urllib.error
from datetime import datetime


def get_doi_metadata(doi: str) -> dict:
    """Fetch metadata from DOI using Content Negotiation API."""
    url = f"https://doi.org/{doi}"
    headers = {
        "Accept": "application/vnd.citationstyles.csl+json",
    }
    
    request = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise ValueError(f"Failed to fetch DOI metadata: HTTP {e.code}")


def format_authors(authors: list) -> str:
    """Format author list in the required style."""
    formatted = []
    for author in authors:
        given = author.get("given", "")
        family = author.get("family", "")
        if given and family:
            formatted.append(f"{given} {family}")
        elif family:
            formatted.append(family)
    
    if len(formatted) == 0:
        return ""
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return ", ".join(formatted[:-1]) + ", and " + formatted[-1]


def format_month(month_num: int) -> str:
    """Convert month number to month name."""
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    return months.get(month_num, "")


def format_publication_entry(metadata: dict, doi: str) -> str:
    """Format the publication entry in the required style."""
    authors = format_authors(metadata.get("author", []))
    title = metadata.get("title", "").replace("\n", " ").strip()
    title = title[0].upper() + title[1:].lower() if title else ""
    
    container = metadata.get("container-title", "")
    container = re.sub(r"\s+", " ", container).strip()
    
    volume = metadata.get("volume", "")
    issue = metadata.get("issue", "")
    page = metadata.get("page", "")
    
    published = metadata.get("published-print", {}) or metadata.get("published-online", {}) or metadata.get("published", {})
    date_parts = published.get("date-parts", [[]])
    if date_parts and date_parts[0]:
        year = date_parts[0][0] if len(date_parts[0]) > 0 else ""
        month = date_parts[0][1] if len(date_parts[0]) > 1 else None
    else:
        year = ""
        month = None
    
    month_name = format_month(month) if month else ""
    
    doi_clean = doi.replace("/", ":")
    
    journal_info = ""
    if container:
        journal_info = container
    if volume:
        if issue:
            journal_info += f", {volume}({issue})"
        else:
            journal_info += f", {volume}"
    if page:
        journal_info += f":{page}"
    
    date_str = ""
    if month_name and year:
        date_str = f"{month_name} {year}"
    elif year:
        date_str = str(year)
    
    entry = f"- {authors}. {title}, {journal_info}, {date_str}. https://doi.org/{doi}. [pdf](/files/papers/{doi_clean}.pdf)"
    
    return entry


def insert_publication(entry: str, publications_file: str):
    """Insert the publication entry at the top of the publications file (after YAML front matter)."""
    with open(publications_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    front_matter_end = content.find('\n---\n', 4)
    if front_matter_end == -1:
        front_matter_end = content.find('\n---', 3)
    
    if front_matter_end != -1:
        front_matter_end += 5
        header = content[:front_matter_end]
        body = content[front_matter_end:]
    else:
        header = ""
        body = content
    
    lines = body.split('\n')
    
    insert_index = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('-'):
            insert_index = i
            break
        elif stripped and not stripped.startswith('You may also find'):
            pass
    
    lines.insert(insert_index, entry)
    lines.insert(insert_index + 1, "")
    
    new_content = header + '\n'.join(lines)
    
    with open(publications_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Publication added to {publications_file}")


def copy_pdf(pdf_path: str, doi: str, papers_dir: str):
    """Copy PDF file to the papers directory with proper naming."""
    doi_clean = doi.replace("/", ":")
    dest_path = os.path.join(papers_dir, f"{doi_clean}.pdf")
    
    if os.path.exists(pdf_path):
        shutil.copy2(pdf_path, dest_path)
        print(f"PDF copied to {dest_path}")
    else:
        print(f"PDF file not found: {pdf_path}")
        print(f"Please manually copy your PDF to: {dest_path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if len(sys.argv) < 2:
        print("Usage: python3 add_publication.py <DOI> [pdf_path]")
        print("Example: python3 add_publication.py 10.1021/jacs.5c17193 ./paper.pdf")
        sys.exit(1)
    
    doi = sys.argv[1].strip()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Fetching metadata for DOI: {doi}...")
    
    try:
        metadata = get_doi_metadata(doi)
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        sys.exit(1)
    
    entry = format_publication_entry(metadata, doi)
    
    print("\nFormatted entry:")
    print("-" * 80)
    print(entry)
    print("-" * 80)
    
    publications_file = os.path.join(script_dir, "_pages", "publications.md")
    papers_dir = os.path.join(script_dir, "files", "papers")
    
    insert_publication(entry, publications_file)
    
    doi_clean = doi.replace("/", ":")
    dest_pdf_path = os.path.join(papers_dir, f"{doi_clean}.pdf")
    
    if pdf_path:
        copy_pdf(pdf_path, doi, papers_dir)
    else:
        print(f"\nPlease manually copy your PDF file to: {dest_pdf_path}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
