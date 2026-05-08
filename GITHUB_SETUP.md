# GitHub Repository Setup Guide

This guide will help you set up your protein structure/function analysis project on GitHub for your Masters in Bioinformatics.

---

## Step 1: Create a GitHub Account

If you don't have one:
1. Go to https://github.com
2. Click "Sign up"
3. Choose a username, email, and password
4. Complete email verification

---

## Step 2: Initialize Git Locally

Navigate to your project directory and initialize git:

```bash
cd protein-structure-analysis
git init
```

Configure your git identity:

```bash
git config user.name "Your Full Name"
git config user.email "your.email@example.com"

# Or set globally (for all projects)
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

---

## Step 3: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Log in to GitHub
2. Click **+** icon (top right) → **New repository**
3. Name: `protein-structure-analysis`
4. Description: `A research project for protein structure and function analysis using machine learning`
5. Choose **Public** (recommended for academic work)
6. ✓ Add .gitignore: Python
7. ✓ Add license: MIT License
8. Click **Create repository**

### Option B: Using GitHub CLI (gh)

```bash
# Install GitHub CLI from https://cli.github.com
gh repo create protein-structure-analysis --public --description "A research project for protein structure and function analysis"
```

---

## Step 4: Connect Local Repository to GitHub

Get the repository URL from GitHub, then:

```bash
# Add remote
git remote add origin https://github.com/yourusername/protein-structure-analysis.git

# Verify
git remote -v
```

---

## Step 5: Add Files and Make First Commit

```bash
# Check status
git status

# Add all files
git add .

# Or add specific files
git add README.md requirements.txt setup.py

# Verify what will be committed
git status

# Create first commit
git commit -m "Initial commit: Project structure and core modules"
```

Good commit message format:
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues if applicable: "Fix #123"

---

## Step 6: Push to GitHub

```bash
# For first push, set upstream
git branch -M main
git push -u origin main

# Subsequent pushes
git push
```

---

## Step 7: Verify on GitHub

1. Go to https://github.com/yourusername/protein-structure-analysis
2. You should see all your files
3. The README.md should display on the main page

---

## Best Practices for Academic Projects

### Directory Structure
```
protein-structure-analysis/
├── README.md                 # Project overview
├── QUICKSTART.md            # Getting started guide
├── METHODOLOGY.md           # Detailed methods
├── LICENSE                  # MIT License
├── requirements.txt         # Dependencies
├── setup.py                 # Package setup
├── config.yaml              # Configuration
├── data/                    # Data directory
├── notebooks/               # Jupyter notebooks
├── src/                     # Source code
├── tests/                   # Unit tests
├── results/                 # Results and figures
└── docs/                    # Additional documentation
```

### Commit Workflow

```bash
# Work on a feature
# Make changes to files

# Stage changes
git add .

# Commit with meaningful message
git commit -m "Add feature extraction module

- Implement k-mer analysis
- Add physicochemical property extraction
- Include unit tests"

# Push to GitHub
git push

# Repeat as needed
```

### Important Commits to Make

1. **Initial Structure**
   ```bash
   git commit -m "Initial commit: Project skeleton and documentation"
   ```

2. **Core Modules**
   ```bash
   git commit -m "Add core bioinformatics modules
   
   - structure_analyzer.py: Protein analysis
   - data_fetcher.py: PDB/UniProt integration
   - feature_extractor.py: Feature engineering
   - predictor.py: ML models"
   ```

3. **Notebooks**
   ```bash
   git commit -m "Add Jupyter notebooks for analysis workflow"
   ```

4. **Results**
   ```bash
   git commit -m "Add preliminary results and visualizations"
   ```

---

## Managing Different File Types

### Large Files
If you have large data files (>100MB), use Git LFS:

```bash
# Install Git LFS
# https://git-lfs.github.com/

# Track large files
git lfs track "data/raw/*.pdb"
git add .gitattributes
git commit -m "Setup Git LFS for large structure files"
```

### Excluded Files
The `.gitignore` file already excludes:
- Virtual environments (`venv/`)
- Cache files (`__pycache__/`)
- Raw data (`data/raw/`)
- Results (`results/`)

---

## Branching Strategy (Optional)

For more complex projects:

```bash
# Create a development branch
git branch develop
git checkout develop
# or: git switch develop

# Create feature branches
git branch feature/ml-models
git checkout feature/ml-models

# Make changes, commit, push
git commit -m "Implement ML models"
git push -u origin feature/ml-models

# Create Pull Request on GitHub
# Review, then merge to main
```

---

## Writing Good Commit Messages

### Format
```
<type>: <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code reorganization
- `perf`: Performance improvement
- `test`: Test additions/changes

### Examples

**Good:**
```
feat: add feature extraction module

Implement k-mer analysis and physicochemical property extraction.
Includes unit tests and documentation.

Fixes #42
```

**Bad:**
```
Update files
```

---

## Updating Your Repository

### Regular Updates

```bash
# Check status
git status

# See recent commits
git log --oneline -5

# Show changes
git diff

# Add and commit
git add .
git commit -m "Descriptive message"
git push
```

### Pulling Updates (if working with collaborators)

```bash
git pull
```

---

## GitHub Features for Academic Work

### 1. GitHub Pages (Host Documentation)
```bash
# Create gh-pages branch
git checkout --orphan gh-pages

# Add docs to gh-pages
# Push
git push origin gh-pages

# Enable in settings → Pages → gh-pages branch
```

### 2. Releases
```bash
# Tag a version
git tag -a v0.1.0 -m "First release"
git push origin v0.1.0

# Create release on GitHub with:
# - Changelog
# - Download links
# - Release notes
```

### 3. README Badges

Add badges to your README:

```markdown
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

---

## Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution:**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub:
# Settings → SSH and GPG keys → New SSH key
# Paste public key from ~/.ssh/id_ed25519.pub

# Test connection
ssh -T git@github.com
```

### Issue: "fatal: refusing to merge unrelated histories"

**Solution:**
```bash
git pull origin main --allow-unrelated-histories
```

### Issue: Want to change repository name

**Solution:**
1. Go to repository Settings
2. Scroll to "Danger Zone"
3. Click "Rename"
4. Update local remote: `git remote set-url origin new-url`

---

## Publishing for Assessment

### Before Final Submission

1. **Clean up:**
   ```bash
   rm -rf __pycache__
   rm -rf .pytest_cache
   # Already handled by .gitignore
   ```

2. **Update documentation:**
   - Ensure README.md is complete
   - Add methodologies in docs/
   - Include results summary

3. **Create final commit:**
   ```bash
   git commit -m "Final submission for Masters evaluation"
   git push
   ```

4. **Create a release:**
   - Go to Releases
   - Create new release
   - Tag: v1.0.0
   - Title: "Masters Thesis Submission"
   - Add summary of work

5. **Share repository URL:**
   - https://github.com/yourusername/protein-structure-analysis
   - Include in submission

---

## Recommended GitHub README Template

See the README.md included in this project. Key sections:
- Overview of research
- Installation instructions
- Usage examples
- Data sources
- Results summary
- References
- Contact information

---

## Additional Resources

- **GitHub Help**: https://docs.github.com/en
- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **License Info**: https://choosealicense.com/
- **Markdown Guide**: https://guides.github.com/features/mastering-markdown/

---

## Quick Reference

```bash
# Initialize and first push
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/protein-structure-analysis.git
git push -u origin main

# Regular workflow
git add .
git commit -m "Descriptive message"
git push

# Check status anytime
git status
git log --oneline -10

# Undo last commit (not pushed)
git reset --soft HEAD~1

# View changes
git diff
```

---

**Congratulations! Your project is now on GitHub! 🚀**

For questions about Git/GitHub, consult the resources above or your advisor.

Last Updated: May 2024
