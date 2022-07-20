alias dowant='sudo apt-get install'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias getfinger='ssh-keygen -l -E md5 -f'
alias getpublic='ssh-keygen -y -f'
alias grep='grep --color=auto'
alias l='ls -CF'
alias la='ls -A'
alias listinstalled='dpkg -l | grep ^ii'
alias ll='ls -lah'
alias ls='ls --color=auto'
alias nicedate='date +%F'
alias ping84='ping 8.8.4.4'
alias ping88='ping 8.8.8.8'
alias rgrep='grep -rnE --color=auto'
alias wcl='wc -l'
alias rsagen='ssh-keygen -t rsa -b 4096 -C'
alias c='clear'
alias plz='sudo'
alias flushdns='sudo service dnsmasq restart'
alias gitdrop="git reset --hard && git clean -fd"
alias keepeye="ping -f -i1"
alias copy="xclip -selection clipboard"
alias xpaste="xclip -selection clipboard -o"
alias gc="git commit -m"
alias gaa="git add -A && git diff --cached"
alias jqless="jq . -C | less -XR"
alias docker-rm-all='docker ps -aq --no-trunc -f status=exited | xargs docker rm'
alias docker-stop-all='docker ps -q | xargs docker stop'
alias lsgits='find -type d -name .git 2>/dev/null | sed -E "s|^\./(.+)/\.git$|\1|"'
alias push-with-tags='git push && git push --tags'
alias disable-touchpad-while-typing='gsettings set org.gnome.desktop.peripherals.touchpad disable-while-typing true'
alias enable-touchpad-while-typing='gsettings set org.gnome.desktop.peripherals.touchpad disable-while-typing false'
alias byebye='(cd ~/.byebye; find . -type f -name "check-*" | while read script; do $script || echo $script returned non-zero; done)'
alias gitlab-pipelines="git remote get-url origin | sed -E 's|\.git$|/pipelines|'"
alias open-gitlab-pipelines='firefox --new-tab $(git remote get-url origin | sed -E "s|\.git$|/pipelines|")'
alias drh='docker run --name $(basename `pwd`) -it -v /etc/passwd:/etc/passwd:ro --group-add root -v `pwd`:/workdir --workdir /workdir --user $(id -u):$(id -g) -e HOME=/workdir'
alias gpft='git push --follow-tags'
alias sumlist='awk "{s+=\$1} END {print s}"'
alias lexx="less -X"
alias open-in-azure-devops='firefox --new-tab $(git remote get-url origin | sed -E "s|^[a-z]+@[a-z0-9\.\-]+\.com\:[a-z0-9]+/([a-zA-Z0-9\-]+)/([a-zA-Z0-9\-]+)/([a-zA-Z0-9\-]+)|https://dev.azure.com/\1/\2/_git/\3|")'
alias tolower="awk '{print tolower(\$0)}'"
alias gupa="git pull --rebase --autostash"

