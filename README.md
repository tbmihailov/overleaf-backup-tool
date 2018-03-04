# Overleaf backup tool
Tool for backing up projects from Overleaf.

## Installation
Works with Python 3.+

```bash
git clone https://github.com/tbmihailov/overleaf-backup-tool.git
pip install -r requirements
```

## Usage
```bash
python overleaf_backup.py backup_dir overleafuser@domain.com overleafpass
```

## How it works
The tool logins with your e-mail and password that you are registered in Overleaf and downloads all projects under "active" and "archived" via git.

You will find the cloned projects folders in backup_dir/git_backup/:

```text
your_backup_dir/
└── git_backup
   ├── yourproject1id
   │   ├── acl2018.bib
   │   ├── acl2018.sty
   │   ├── acl_natbib.bst
   │   ├── main.tex
   └── yourproject2id
   │   ├── acl2018.bib
   │   ├── acl2018.sty
   │   ├── acl_natbib.bst
   │   ├── main.tex
   ├── projects.json
```

projects.json contain the metadata about the projects in Overleaf.
Successfully backed up projects will not be downloaded again if they are not marked as changed in Overleaf.

## Contribute

If you want to contribute to the project, make a pull request.