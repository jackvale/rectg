#!/bin/bash

# read https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -euxo pipefail

# Read .env settings if .env is present (.env will not be present in a pipeline)
# In that case, settings are read from environment
# https://stackoverflow.com/a/30969768
# https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html#:~:text=option%2Dname%3A-,allexport,-Same%20as%20%2Da
# shellcheck disable=SC1091
# shellcheck source=/dev/null
if [ -f .env ]; then
    echo Reading from .env file
    set -o allexport && source .env && set +o allexport
else
    echo No .env file present, assuming we\'re running within pipeline
fi
# shellcheck enable=all


if [ "$RUNNING_WITHIN_CI_PIPELINE" -eq 0 ]; then
    echo We\'re not RUNNING_WITHIN_CI_PIPELINE so performing checkout to WORKSPACE_DIR "$WORKSPACE_DIR"

    echo Checking for WORKSPACE_DIR
    (set +x
    if [ -z "$WORKSPACE_DIR" ]; then
        echo "Please set the WORKSPACE_DIR variable and try again."
        echo "💥 ERROR: WORKSPACE_DIR is not set but RUNNING_WITHIN_CI_PIPELINE was 0"
        echo "If RUNNING_WITHIN_CI_PIPELINE=0 we expect you're running deploy.sh locally"
        echo "and you're not running within an automated pipeline (GitHub actions/Gitlab Pipelines etc)."
        echo "When running outside of a pipeline, deploy.sh needs to do a git checkout of"
        echo "your repo, therefore you need to set WORKSPACE_DIR to a path"
        echo "you'd like to clone the repo to."
        echo "If you are trying to deploy within a pipeline, then change"
        echo "RUNNING_WITHIN_CI_PIPELINE=0 to RUNNING_WITHIN_CI_PIPELINE=1"
        exit 255
    fi
    )
    echo Creating WORKSPACE_DIR
    mkdir -p "$WORKSPACE_DIR"

    echo Checking for GIT_CLONE_URL_OR_PATH
    (set +x
    if [ -n "${GIT_CLONE_URL_OR_PATH:+notset}" ]; then
      echo "GIT_CLONE_URL_OR_PATH is set to $GIT_CLONE_URL_OR_PATH"
    else
      echo "💥 ERROR: GIT_CLONE_URL_OR_PATH is not set but RUNNING_WITHIN_CI_PIPELINE was 0"
      echo "If RUNNING_WITHIN_CI_PIPELINE=0 we expect you're running deploy.sh locally"
      echo "and you're not running within an automated pipeline (GitHub actions/Gitlab Pipelines etc)."
      echo "When running outside of a pipeline, deploy.sh needs to do a git checkout of"
      echo "your repo, therefore you need to set GIT_CLONE_URL_OR_PATH to the URL or"
      echo "path of your git repo being deployed."
      echo "If you are trying to deploy within a pipeline, then change"
      echo "RUNNING_WITHIN_CI_PIPELINE=0 to RUNNING_WITHIN_CI_PIPELINE=1"
      exit 255
    fi
    )
	# Verify that WORKSPACE_DIR is not a critical system path
	critical_paths=(
	  "/"
	  "/bin"
      "/yoloyolo"
	  "/boot"
	  "/dev"
	  "/etc"
	  "/home"
	  "/lib"
	  "/lib64"
	  "/media"
	  "/mnt"
	  "/opt"
	  "/proc"
	  "/root"
	  "/run"
	  "/sbin"
	  "/srv"
	  "/sys"
	  "/tmp"
	  "/usr"
	  "/var"
	)

	(set +x
	for path in "${critical_paths[@]}"; do
	  if [ "$WORKSPACE_DIR" == "$path" ]; then
		echo "💥 Error: WORKSPACE_DIR is set to a dangerous critical path,"
        echo "which you probably don't want to delete so we stopped before deletion."
        echo "WORKSPACE_DIR was set to: $WORKSPACE_DIR"
        echo "Please set a different path and try again. See .env.example"
		exit 1
	  fi
	done
	)

    echo Deleting current WORKSPACE_DIR "$WORKSPACE_DIR"
    rm -rf "${WORKSPACE_DIR:?}/"* || true
    rm -rf "${WORKSPACE_DIR:?}/."* || true
    echo "Checking out git repo '$GIT_CLONE_URL_OR_PATH' to $WORKSPACE_DIR"
    git clone "$GIT_CLONE_URL_OR_PATH" "$WORKSPACE_DIR"
    echo "Changing directory to root of GIT_CLONE_URL_OR_PATH"
    cd "$WORKSPACE_DIR"
fi

echo Checking if provided DOKKU_SSH_PRIVATE_KEY key requires a passphrase
if ssh-keygen -y -P "" -f /dev/stdin <<<"$DOKKU_SSH_PRIVATE_KEY"&>/dev/null; then
        echo "✅ DOKKU_SSH_PRIVATE_KEY does not require a passphrase. OK."
    else
        echo "🧐 DOKKU_SSH_PRIVATE_KEY requires a passphrase. Ask user for passphrase"
		echo Verify ssh-askpass is installed, needed for passphrase protected ssh key
		(set +e
		which ssh-askpass
		ret=$?
		if [ "$ret" -ne 0 ];
		then
			set +x
			echo '💥 ERROR: The DOKKU_SSH_PRIVATE_KEY you have given requires a passphrase'
			echo '(this is probably a mistake- if you want an automated pipeline, then'
			echo generate an ssh key *without* a passphrase\).
			echo If this wasn\'t a mistake and you want to enter a password every time,
			echo 'then you must install ssh-askpass'
			echo e.g. \'sudo apt install ssh-askpass\'
			exit 255
		fi)
fi


if [ -n "${AMBER_SECRET:+notset}" ]; then
  echo "AMBER_SECRET is set"
else
  echo "ERROR: AMBER_SECRET is not set"
  exit 255
fi

echo Installing amber secrets manager
mkdir -p ./bin
curl -L https://github.com/fpco/amber/releases/download/v0.1.3/amber-x86_64-unknown-linux-musl > ./amber
chmod +x ./amber
mv ./amber ./bin/amber
PATH=./bin:$PATH

echo Setup ssh to talk to dokku host
mkdir -p ~/.ssh
amber -v exec -- sh -c 'ssh-keyscan $DOKKU_HOST >> ~/.ssh/known_hosts'
eval "$(ssh-agent -s)"
ssh-add -D
ssh-add - <<< "$DOKKU_SSH_PRIVATE_KEY"
ssh-add -l
SSH_ARGS="-F $SSH_CONFIG_FILE"

amber exec -- sh -c ''"ssh $SSH_ARGS"' dokku@$DOKKU_HOST -C $CONTAINER_HOSTING_API_KEY dokku apps:create $APP_NAME || true'
amber exec -- sh -c ''"ssh $SSH_ARGS"' dokku@$DOKKU_HOST -C $CONTAINER_HOSTING_API_KEY dokku builder:set $APP_NAME build-dir src'
amber exec -- sh -c ''"ssh $SSH_ARGS"' dokku@$DOKKU_HOST -C $CONTAINER_HOSTING_API_KEY dokku builder-dockerfile:set $APP_NAME dockerfile-path Dockerfile'

# Set common env settings

# Note we *dont* expand the APP_NAME env setting because the APP_NAME
# is worked out from the CONTAINER_HOSTING_API_KEY server side by
# searching the containers database:
# WHERE CONTAINER_HOSTING_API_KEY = CONTAINER_HOSTING_API_KEY
# see:
# https://github.com/KarmaComputing/container-hosting/blob/91573f47cf0de5bbd3a35d7e8a7a019e184c2117/dokku-wrapper.py#L44
#  

echo Set app envrionment settings

amber exec -- sh -c ''"ssh $SSH_ARGS"' dokku@$DOKKU_HOST -C $CONTAINER_HOSTING_API_KEY \
    dokku config:set --no-restart $APP_NAME \
    DB_USER=$DB_USER\
    DB_PASSWORD=$DB_PASSWORD\
    DB_HOST=$DB_HOST\
    DB_PORT=$DB_PORT\
    DB_NAME=$DB_NAME\
    RAILS_DEVELOPMENT_HOSTS=$APP_NAME.containers.anotherwebservice.com\
    DATABASE_URL=$RAILS_DATABASE_URL\
    SECRET_KEY=$DJANGO_SECRET_KEY\
    ALLOWED_HOSTS=$ALLOWED_HOSTS\
    DEBUG=$DJANGO_DEBUG\
    DB_ENGINE=$DJANGO_ENGINE\
    DB_NAME=$DJANGO_DB_NAME\
    DB_HOST=$DJANGO_DB_HOST\
    DB_USER=$DJANGO_DB_USER\
    DB_PASSWORD=$DJANGO_DB_PASSWORD\
    DB_PORT=$DJANGO_DB_PORT'


amber exec -- sh -c ''"ssh $SSH_ARGS"' dokku@$DOKKU_HOST -C $CONTAINER_HOSTING_API_KEY dokku git:sync --build $APP_NAME https://github.com/'"$GIT_USERNAME_OR_ORG"'/'"$GIT_REPO_NAME"'.git main'

# Assign letsencrypt wildcard certificate
# Note that SSH_ARGS are not stored in amber, which is why they are expanded
# vs the rest (e.g. DOKKU_HOST and CONTAINER_HOSTING_API_KEY which are stored
# within amber.yaml secrets
amber exec -v --unmasked -- sh -c 'ssh '"$SSH_ARGS"' dokku@$DOKKU_HOST -C "$CONTAINER_HOSTING_API_KEY dokku certs:add $APP_NAME < cert-key.tar"'

