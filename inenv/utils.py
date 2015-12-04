activate_envvars_template = "export _OLD_{envvar}=\"${envvar}\" {envvar}={new_value}"
deactivate_envvar_template = "export {envvar}=\"$_OLD_{envvar}\"; unset _OLD_{envvar}"

template = """save_function() {
    local ORIG_FUNC="$(declare -f $1)"
    local NEWNAME_FUNC="$2${ORIG_FUNC#$1}"
    eval "$NEWNAME_FUNC"
}
%s
save_function deactivate python_deactivate
deactivate(){
     python_deactivate
     %s
}
"""


def override_envars_and_deactivate(env):
    if not env:
        return ""
    activators, deactivators = [], []
    for k, v in env.items():
        activators.append(activate_envvars_template.format(envvar=k, new_value=v))
        deactivators.append(deactivate_envvar_template.format(envvar=k))
    return template % ('\n'.join(activators), '\n'.join(deactivators))

