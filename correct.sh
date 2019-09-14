#!/bin/sh

git filter-branch -f --env-filter '
OLD_EMAIL="corentin.vigourt@hotmail.fr"
CORRECT_NAME="Corentin Vigourt"
CORRECT_EMAIL="corentin.vigourt@epita.fr"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags
