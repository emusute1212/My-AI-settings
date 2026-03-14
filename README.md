# 共有エージェント設定の使い方

このリポジトリは、エージェント用の設定ファイルや `skills/` をまとめて管理し、必要なツールからシンボリックリンクで参照するための置き場所です。

この README では、以下の 2 点を説明します。

- このディレクトリ名を `My-AI-settings` 以外の好きな名前に変更する方法
- `AGENTS.md` や `skills/` などを `~/.claude` や `~/.codex` にシンボリックリンクする方法

## 想定構成

このリポジトリには、たとえば以下のようなファイルがあります。

- `AGENTS.md`
- `skills/`
- `README.md`

利用するツール側では、これらを直接コピーするのではなく、シンボリックリンクで参照すると管理が楽です。

## 1. ディレクトリ名を好きな名前に変更する

このリポジトリのディレクトリ名は `My-AI-settings` である必要はありません。たとえば `~/.my-agents` や `~/agent-config` のような好きな名前に変更できます。

### 例: `My-AI-settings` を `.my-agents` に変更する

```bash
git clone git@github.com:emusute1212/My-AI-settings.git ~/.my-agents
```

もしくはクローンしたあとで以下を実行する。

```bash
mv ~/My-AI-settings ~/.my-agents
```

変更後は、以降のリンク先も新しいパスに合わせて指定してください。

たとえば、以降の説明では次のように変数を置いておくと分かりやすくなります。

```bash
AGENT_HOME=~/.my-agents
```

もしディレクトリ名を変更しない場合は、そのまま以下を使えます。

```bash
AGENT_HOME=~/.agents
```

## 2. `~/.claude` にシンボリックリンクする

まず、`~/.claude` ディレクトリがなければ作成します。

```bash
mkdir -p ~/.claude
```

既に同名のファイルやディレクトリがある場合は、先に退避してからリンクするのが安全です。

```bash
if [ -e ~/.claude/AGENTS.md ] || [ -L ~/.claude/AGENTS.md ]; then
  mv ~/.claude/AGENTS.md ~/.claude/AGENTS.md.bak
fi

if [ -e ~/.claude/skills ] || [ -L ~/.claude/skills ]; then
  mv ~/.claude/skills ~/.claude/skills.bak
fi

ln -s "$AGENT_HOME/AGENTS.md" ~/.claude/AGENTS.md
ln -s "$AGENT_HOME/skills" ~/.claude/skills
```

### コマンドの意味

- `ln -s` : シンボリックリンクを作成します
- `mv ... .bak` : 既存のファイルやディレクトリをバックアップします

すでにリンク済みのものを手早く張り直したい場合だけ、以下のように `ln -sfn` を使っても構いません。

```bash
ln -sfn "$AGENT_HOME/AGENTS.md" ~/.claude/AGENTS.md
ln -sfn "$AGENT_HOME/skills" ~/.claude/skills
```

ただし、`~/.claude/skills` が実ディレクトリとして存在している場合は、先に退避してから実行してください。

## 3. `~/.codex` にシンボリックリンクする

同様に、`~/.codex` にもリンクできます。

```bash
mkdir -p ~/.codex

if [ -e ~/.codex/AGENTS.md ] || [ -L ~/.codex/AGENTS.md ]; then
  mv ~/.codex/AGENTS.md ~/.codex/AGENTS.md.bak
fi

if [ -e ~/.codex/skills ] || [ -L ~/.codex/skills ]; then
  mv ~/.codex/skills ~/.codex/skills.bak
fi

ln -s "$AGENT_HOME/AGENTS.md" ~/.codex/AGENTS.md
ln -s "$AGENT_HOME/skills" ~/.codex/skills
```

必要に応じて、ほかのファイルも同じ要領でリンクできます。

```bash
ln -s "$AGENT_HOME/README.md" ~/.codex/README.md
```

## 4. まとめて設定する例

`.claude` と `.codex` の両方へまとめてリンクする場合は、以下のように実行できます。

```bash
AGENT_HOME=~/.my-agents

mkdir -p ~/.claude ~/.codex

if [ -e ~/.claude/AGENTS.md ] || [ -L ~/.claude/AGENTS.md ]; then
  mv ~/.claude/AGENTS.md ~/.claude/AGENTS.md.bak
fi
if [ -e ~/.claude/skills ] || [ -L ~/.claude/skills ]; then
  mv ~/.claude/skills ~/.claude/skills.bak
fi
ln -s "$AGENT_HOME/AGENTS.md" ~/.claude/AGENTS.md
ln -s "$AGENT_HOME/skills" ~/.claude/skills

if [ -e ~/.codex/AGENTS.md ] || [ -L ~/.codex/AGENTS.md ]; then
  mv ~/.codex/AGENTS.md ~/.codex/AGENTS.md.bak
fi
if [ -e ~/.codex/skills ] || [ -L ~/.codex/skills ]; then
  mv ~/.codex/skills ~/.codex/skills.bak
fi
ln -s "$AGENT_HOME/AGENTS.md" ~/.codex/AGENTS.md
ln -s "$AGENT_HOME/skills" ~/.codex/skills
```

`.agents` のまま使う場合は、1 行目だけ以下に置き換えてください。

```bash
AGENT_HOME=~/.agents
```

## 5. 設定を確認する

リンクが正しく作成されたかは `ls -l` で確認できます。

```bash
ls -l ~/.claude
ls -l ~/.codex
```

出力例:

```text
AGENTS.md -> /Users/your-name/.my-agents/AGENTS.md
skills -> /Users/your-name/.my-agents/skills
```

リンク先が想定どおりであれば設定完了です。

## 6. 運用のポイント

- 実体ファイルはこのリポジトリ側だけを編集します
- `~/.claude` や `~/.codex` 側はリンク経由で参照させます
- 管理場所を変えたくなった場合は、元ディレクトリを移動してリンクを張り直すだけで対応できます

## 7. 最小セット

初回セットアップのように、リンク先の同名ファイルやディレクトリがまだ存在しない場合は、以下だけでも運用できます。

```bash
AGENT_HOME=~/.agents
mkdir -p ~/.claude ~/.codex
ln -s "$AGENT_HOME/AGENTS.md" ~/.claude/AGENTS.md
ln -s "$AGENT_HOME/skills" ~/.claude/skills
ln -s "$AGENT_HOME/AGENTS.md" ~/.codex/AGENTS.md
ln -s "$AGENT_HOME/skills" ~/.codex/skills
```
