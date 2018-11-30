function color_my_prompt {
    local __user_and_host="\[\033[01;32m\]\u@\h"
    local __cur_location="\[\033[01;34m\]\w"
    local __git_branch_color="\[\033[31m\]"
    local __git_branch='`git branch 2> /dev/null | grep -e ^* | sed -E  s/^\\\\\*\ \(.+\)$/\(\\\\\1\)\ /`'
    local __kube_prompt_color="\[\033[36m\]"
    local __kube_prompt='`kubectl config current-context 2>/dev/null | sed -E "s/^(.+)$/{\1} /"`'
    local __prompt_tail="\[\033[35m\]$"
    local __last_color="\[\033[00m\]"
    export PS1="\033]2;\w\007$__user_and_host $__cur_location $__git_branch_color$__git_branch$__kube_prompt_color$__kube_prompt$__prompt_tail$__last_color "
}
color_my_prompt
