# Copy files (-a) from dirs and ignore specific ones (--exclude) from remote (-e) while preserving dir structure (--relative, my/path/.{/dir1/*,/dir2/*})

rsync -av --relative -e ssh --exclude='*.g.csv' --exclude='*.i.csv' --exclude='*.t.csv' --exclude='*.b.csv' user@host:~/kg-analysis/out/.{/dir1/*,/dir2/*} ./out/
