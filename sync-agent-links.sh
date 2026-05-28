#!/bin/sh

set -eu

HOME_DIR=${HOME:?HOME is not set}
SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

confirm_replace() {
  dest_path=$1
  src_path=$2
  reason=$3

  printf '%s\n' "$reason"
  printf 'replace "%s" with symlink to "%s"? [y/N] ' "$dest_path" "$src_path"
  read answer

  case $answer in
    y|Y|yes|YES)
      rm -rf "$dest_path"
      return 0
      ;;
    *)
      printf 'skip: %s\n' "$dest_path"
      return 1
      ;;
  esac
}

link_children() {
  src_dir=$1
  dest_dir=$2

  if [ ! -d "$src_dir" ]; then
    printf 'skip: source directory does not exist: %s\n' "$src_dir"
    return 0
  fi

  mkdir -p "$dest_dir"

  for src_path in "$src_dir"/*; do
    [ -d "$src_path" ] || continue

    name=$(basename "$src_path")
    dest_path=$dest_dir/$name

    if [ -L "$dest_path" ]; then
      current_target=$(readlink "$dest_path")
      if [ "$current_target" = "$src_path" ]; then
        printf 'ok: %s -> %s\n' "$dest_path" "$src_path"
        continue
      fi

      if ! confirm_replace "$dest_path" "$src_path" "conflict: symlink already exists with different target: $dest_path -> $current_target"; then
        continue
      fi
    elif [ -e "$dest_path" ]; then
      if ! confirm_replace "$dest_path" "$src_path" "conflict: destination already exists and is not a symlink: $dest_path"; then
        continue
      fi
    fi

    ln -s "$src_path" "$dest_path"
    printf 'linked: %s -> %s\n' "$dest_path" "$src_path"
  done
}

link_path() {
  src_path=$1
  dest_path=$2

  if [ ! -e "$src_path" ]; then
    printf 'skip: source path does not exist: %s\n' "$src_path"
    return 0
  fi

  mkdir -p "$(dirname "$dest_path")"

  if [ -L "$dest_path" ]; then
    current_target=$(readlink "$dest_path")
    if [ "$current_target" = "$src_path" ]; then
      printf 'ok: %s -> %s\n' "$dest_path" "$src_path"
      return 0
    fi

    if ! confirm_replace "$dest_path" "$src_path" "conflict: symlink already exists with different target: $dest_path -> $current_target"; then
      return 0
    fi
  elif [ -e "$dest_path" ]; then
    if ! confirm_replace "$dest_path" "$src_path" "conflict: destination already exists and is not a symlink: $dest_path"; then
      return 0
    fi
  fi

  ln -s "$src_path" "$dest_path"
  printf 'linked: %s -> %s\n' "$dest_path" "$src_path"
}

link_children "$SOURCE_ROOT/skills" "$HOME_DIR/.codex/skills"
link_children "$SOURCE_ROOT/skills" "$HOME_DIR/.claude/skills"
link_children "$SOURCE_ROOT/agents" "$HOME_DIR/.codex/agents"
link_children "$SOURCE_ROOT/agents" "$HOME_DIR/.claude/agents"
link_path "$SOURCE_ROOT/AGENTS.md" "$HOME_DIR/AGENTS.md"
link_path "$SOURCE_ROOT/AGENTS.md" "$HOME_DIR/CLAUDE.md"
