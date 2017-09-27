ACTIVATE_ENVVARS_TEMPLATE = "export _OLD_{envvar}=\"${envvar}\" {envvar}={new_value}"
DEACTIVATE_ENVVAR_TEMPLATE = "export {envvar}=\"$_OLD_{envvar}\"; unset _OLD_{envvar}"

TEMPLATE = """save_function() {
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
    for key, value in env.items():
        activators.append(ACTIVATE_ENVVARS_TEMPLATE.format(envvar=key, new_value=value))
        deactivators.append(DEACTIVATE_ENVVAR_TEMPLATE.format(envvar=key))
    return TEMPLATE % ('\n'.join(activators), '\n'.join(deactivators))
