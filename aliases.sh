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
alias wixpull='git pull --rebase'
alias wixpush='git pull --rebase && git push'
alias rgrep='grep -rnE'
alias wcl='wc -l'
alias rsagen='ssh-keygen -t rsa -b 4096 -C'
alias gitconcise="git log --pretty=oneline | sed -r 's/([0-9a-f]{7})[0-9a-f]*/\1/'"
alias c='clear'
alias plz='sudo'
alias flushdns='sudo service dnsmasq restart'
alias resetdomainpass="smbpasswd -r 192.168.30.6 -U $LOGNAME"
alias removeemptylines="sed '/^\s*$/d'"
alias gitdrop="git add -A && git stash && git stash drop"
alias keepeye="ping -f -i1"
alias copy="xclip -selection clipboard"
alias xpaste="xclip -selection clipboard -o"
alias gc="git commit -m"
alias gaa="git add -A && git diff --cached"
alias remove-leading-whitespaces="sed 's/^[ \t]*//'"
alias atomit="atom . >/dev/null &"
alias parse-knife-search-node='grep -Ev "^[\ ]" | sed "/^\s*$/d" | cut -d ":" -f1'
alias jqless="jq . -C | less -R"
alias reload_bashrc="source ~/.bashrc"
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

