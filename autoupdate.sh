./restart.sh
origin="origin"
branch="master"
# url of the remote repo
url=$(git remote get-url "$origin")
while [ true ]
do
    # last commit hash
    commit=$(git log -n 1 --pretty=format:%H "$origin/$branch")
    for line in "$(git ls-remote -h $url)"; do
        fields=($(echo $line | tr -s ' ' ))
        test "${fields[1]}" == "refs/heads/$branch" || continue
        if ["${fields[0]}" != "$commit"]
        then
            git pull
            ./restart.sh
        fi
    done
done