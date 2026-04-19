##
# Install the management script from the project's repo
#
# Expects the following variables:
#   GAME_USER    - User account to install the game under
#   GAME_DIR     - Directory to install the game into
#   WARLOCK_GUID - Warlock GUID for this game
#
# @param $1 Application Repo Name (e.g., user/repo)
# @param $2 Application Branch Name (default: main)
# @param $3 Warlock Manager Branch to use (default: release-v2)
#
# CHANGELOG:
#   20260326 - Add support for full version strings
#   20260325 - Update to install warlock-manager from PyPI if a version number is specified instead of a branch name
#   20260319 - Add third option to specify the version of Warlock Manager to use as the base
#   20260301 - Update to install warlock-manager from github (along with its dependencies) as a pip package
#
function install_warlock_manager() {
	print_header "Performing install_management"

	# Install management console and its dependencies

	# Source URL to download the application from
	local SRC=""
	# Github repository of the source application
	local REPO="$1"
	# Branch of the source application to download from (default: main)
	local BRANCH="${2:-main}"
	# Branch of Warlock Manager to install (default: release-v2)
	local MANAGER_BRANCH="${3:-release-v2}"
	local MANAGER_SOURCE
	local MANAGER_SHA

	if [[ "$MANAGER_BRANCH" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
		# Support 1.2.3 version strings; indicates at least .3 of the revision.
		MANAGER_SOURCE="pip"
		MANAGER_BRANCH=">=${MANAGER_BRANCH},<=$(echo $MANAGER_BRANCH | sed 's:\.[0-9]*$:.9999:')"
	elif [[ "$MANAGER_BRANCH" =~ ^[0-9]+\.[0-9]+$ ]]; then
		# Support 1.2 version strings; indicates it just must be within this API version
        MANAGER_SOURCE="pip"
        MANAGER_BRANCH=">=${MANAGER_BRANCH}.0,<=${MANAGER_BRANCH}.9999"
    else
    	# Not a version string, probably a branch name instead.
        MANAGER_SOURCE="github"
    fi

	SRC="https://raw.githubusercontent.com/${REPO}/refs/heads/${BRANCH}/dist/manage.py"

	if ! download "$SRC" "$GAME_DIR/manage.py"; then
		echo "Could not download management script!" >&2
		exit 1
	fi

	chown $GAME_USER:$GAME_USER "$GAME_DIR/manage.py"
	chmod +x "$GAME_DIR/manage.py"

	# Record the hash of the install and branch name for display in the management UI and checking for updates.
	# We use the direct hash because installation scripts may not necessarily use tagged versions.
	MANAGER_SHA="$(curl -s "https://api.github.com/repos/${REPO}/commits/${BRANCH}" \
        | grep '"sha":' \
        | head -n 1 \
        | sed -E 's/.*"sha": *"([^"]+)".*/\1/')"

	# Record this hash along with the branch into a file accessible by the manager.
	# This will be read by the Python, so JSON is fine.
	cat > "$GAME_DIR/.manage.json" <<EOF
{
	"source": "github",
	"repo": "${REPO}",
	"branch": "${BRANCH}",
	"commit": "${MANAGER_SHA}",
	"game": "${WARLOCK_GUID}"
}
EOF
	chown $GAME_USER:$GAME_USER "$GAME_DIR/.manage.json"

	# Install configuration definitions
	cat > "$GAME_DIR/configs.yaml" <<EOF
# script:configs.yaml
EOF
	chown $GAME_USER:$GAME_USER "$GAME_DIR/configs.yaml"

	# Most games use .settings.ini for manager settings
	touch "$GAME_DIR/.settings.ini"
	chown $GAME_USER:$GAME_USER "$GAME_DIR/.settings.ini"

	# A python virtual environment is now required by Warlock-based managers.
	sudo -u $GAME_USER python3 -m venv "$GAME_DIR/.venv"
	sudo -u $GAME_USER "$GAME_DIR/.venv/bin/pip" install --upgrade pip
	if [ "$MANAGER_SOURCE" == "pip" ]; then
		# Install from PyPI with version specifier
		sudo -u $GAME_USER "$GAME_DIR/.venv/bin/pip" install "warlock-manager${MANAGER_BRANCH}"
	else
		# Install directly from GitHub
		sudo -u $GAME_USER "$GAME_DIR/.venv/bin/pip" install warlock-manager@git+https://github.com/BitsNBytes25/Warlock-Manager.git@$MANAGER_BRANCH
	fi

	# Ensure warlock lib directory exists for supplemental data
	[ -d "/var/lib/warlock" ] || mkdir -p "/var/lib/warlock"
	[ -e /var/lib/warlock/.auth ] || touch /var/lib/warlock/.auth
    # Ensure it's a valid 64-character hash
    if [ "$(cat /var/lib/warlock/.auth | wc -c)" != "64" ]; then
    	cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 64 | head -n 1 | tr -d '\n' > "/var/lib/warlock/.auth"
    fi
	[ -e "/var/lib/warlock/.email" ] || touch /var/lib/warlock/.email
}

