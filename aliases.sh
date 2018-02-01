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
alias byebye='sudo poweroff'
alias gitconcise="git log --pretty=oneline | sed -r 's/([0-9a-f]{7})[0-9a-f]*/\1/'"
alias c='clear'
alias plz='sudo'
alias flushdns='sudo service dnsmasq restart'
alias resetdomainpass="smbpasswd -r 192.168.30.6 -U $LOGNAME"
alias removeemptylines="sed '/^\s*$/d'"
alias gitdrop="git add -A && git stash && git stash drop"
alias keepeye="ping -f -i1"
alias copy="xclip -selection clipboard"
alias gc="git commit -m"
alias gaa="git add -A && git diff --cached"
alias remove-leading-whitespaces="sed 's/^[ \t]*//'"
alias atomit="atom . >/dev/null &"
alias parse-knife-search-node='grep -Ev "^[\ ]" | sed "/^\s*$/d" | cut -d ":" -f1'

