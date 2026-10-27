#!/bin/sh
# Generate the PWA's runtime API config from $PWA_API_BASE.
# nginx's built-in envsubst only fills conf.d templates, so this handles
# the static-asset template explicitly.
set -e
if [ -f /usr/share/nginx/html/config.js.template ]; then
  defined_envs=$(printf '${%s} ' $(env | cut -d= -f1))
  envsubst "$defined_envs" \
    < /usr/share/nginx/html/config.js.template \
    > /usr/share/nginx/html/config.js
fi
