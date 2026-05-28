# 共有エージェント設定の使い方

私のホームディレクトリにおいているAI設定ファイル群です。
基本的に各種AI Agentにsymlinkして利用することを想定しています。

## 対応Agent

- Codex
- ClaudeCode

## 想定構成

`skills/`以下ディレクトリを一つずつ各種AI Agentファイル群へsymlinkします。他のディレクトリも同じです。

`AGENTS.md`は`$HOME/CLAUDE.md`や`$HOME/AGENTS.md`へsymlinkします。

## セットアップ

このディレクトリでスクリプトを実行します。

```bash
./sync-agent-links.sh
```

## 作成されるリンク

`sync-agent-links.sh` は、以下のリンクを作成します。

```text
~/.codex/skills/<skill名>  ->  ./skills/<skill名>
~/.claude/skills/<skill名> ->  ./skills/<skill名>

~/.codex/agents/<agent名>  ->  ./agents/<agent名>
~/.claude/agents/<agent名> ->  ./agents/<agent名>

~/AGENTS.md  ->  ./AGENTS.md
~/CLAUDE.md  ->  ./AGENTS.md
```

リンク元はフルパスで作成されます。

## 競合した場合

リンク先に同名のファイル、ディレクトリ、または別の symlink が既にある場合、スクリプトは勝手に上書きせず確認します。

```text
replace "/Users/you/.codex/skills/foo" with symlink to "/Users/you/My-AI-settings/skills/foo"? [y/N]
```

`y` / `Y` / `yes` / `YES` と入力すると置き換えます。それ以外はスキップします。

既に正しいリンクがある場合は、何も変更せず `ok` と表示されます。

## 確認方法

リンクが正しく作成されたかは `ls -l` や `readlink` で確認できます。

```bash
ls -l ~/.codex/skills
ls -l ~/.claude/skills
readlink ~/AGENTS.md
readlink ~/CLAUDE.md
```

## 運用のポイント

- 実体ファイルはこのリポジトリ側だけを編集します
- Codex や Claude 側には symlink 経由で同じ実体を見せます
- `skills/` や `agents/` に新しいディレクトリを追加したら、もう一度 `./sync-agent-links.sh` を実行します
- ディレクトリ名を変えた場合は、移動後の場所で再実行するとリンクを張り直せます
