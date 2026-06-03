# コンテキスト永続化ルール

チャット履歴が失われても作業の経緯・意図・知見を復元できるようにするため、作業内容を `~/.agents/.context/` 配下にファイルとして永続化する。エージェントツール（Claude Code / Cursor / Codex など）を切り替えても同じ場所を参照することで、コンテキストを引き継げるようにする。

## 保存先

実行ディレクトリに関わらず、**常に `~/.agents/.context/`以下へ** 保存する。

### 保存先の構造

timestampのフォーマット: YYYY-MM-DD_HH_mm_ss（ローカルタイムゾーン、`date +%Y-%m-%d_%H_%M_%S` で生成）

|ファイル名|内容|
|:-:|:--|
|`context.tsv`|各種情報がどこに保存されているのかの情報を示す。tsvの構造は[context.tsv](#contexttsv)へ|
|`{timestamp}/PLAN.md`|立てたプランを保存する。詳細は[PLAN.md](#planmd)へ。|
|`{timestamp}/TODO.md`|TODOを保存する。詳細は[TODO.md](#todomd)へ。|
|`{timestamp}/CONTEXT.md`|タスクを遂行するうえでの学びや構成に引き継ぐべき内容を保存する。詳細は[CONTEXT.md](#contextmd)へ。|

なお、ディレクトリが存在しないときはディレクトリの作成から行ってください。

### 既存タスクの判定

セッション開始時、または新しいプロンプトを受けたときに**毎回必ず以下を実行する**

1. `pwd`を実行して現在のディレクトリを確認する
2. `~/.agents/.context/context.tsv` を現在のディレクトリのPathで`grep`して、現在のディレクトリの情報がどこに保存されているのかを特定する。
    - `awk -F'\t' -v p="$(pwd)" '$1 == p' ~/.agents/.context/context.tsv`  を実行する
3. 存在する場合はそのディレクトリの `PLAN.md` / `TODO.md` / `CONTEXT.md` を読み込んで続きから作業するかユーザへ確認する
    - 同じ target_path の過去 `CONTEXT.md`は読む
        - これはcontext.tsvのstatusがDONEでも同じ
4. 存在しない場合は新しい作業ディレクトリを作る

### 保存タイミング

#### `~/.agents/.context/{timestamp}`の更新タイミング

- 原則: プロンプトの解決毎に更新
    - `~/.agents/.context/{timestamp}`を作り、`PLAN.md` / `TODO.md` / `CONTEXT.md` を作成
    - プロンプトを解決するたびに`PLAN.md` / `TODO.md` / `CONTEXT.md` を更新
- 例外（スキップ可）: [除外条件](#除外条件)を参照
- Plan mode: プランを立てた時点で`~/.agents/.context/{timestamp}`を作成し `PLAN.md`/`TODO.md` を埋め、実行後に `CONTEXT.md` を追記、必要があれば `PLAN.md` / `TODO.md`も更新。

#### 除外条件

- 単なる質問・相談で、ファイルを変更していない場合
- /clear 直後のメタな会話
- CONTEXT.md に書く価値のある「学び」「決定」「変更」が無い

#### context.tsvの更新タイミング

`~/.agents/.context/{timestamp}`が新たに追加されるときだけ

## ファイル詳細

### context.tsv
どの内容がどこのディレクトリに格納されているかを紐づけるためのtsv。

#### 構造

以下の内容をリストで持つ。

|パラメータ|型|内容|
|:-:|:-:|:--|
|target_path|文字列|AIエージェントが実行しているセッションのPath。`pwd`を実行した内容を保存する。|
|context_path|文字列|Contextの情報がどこに保存されているのかを表すPath。`~/.agents/.context/{timestamp}`の形になる。|
|status|文字列(PROGRESS, DONE)|タスクの状況を保存する。実行中は `PROGRESS` (初期値)、完了は `DONE` とする。`PROGRESS` → `DONE`のステータス変更はユーザーが「完了」「ありがとう」など終了を示唆した時、または明確に別タスクに移った時に更新する。迷ったら `PROGRESS` のままにする。|
|task_summary|文字列|タスクの簡単なサマリを持つ。最大でも100文字程度で納めておきたい。|

例：

```tsv
target_path	context_path	status	task_summary
/Users/yosuke.miyanishi/AiWorkspace/my-consultation	/Users/yosuke.miyanishi/.agents/.context/2026-04-24_12_12_44	PROGRESS	ハーネスエンジニアリングのJiraTicketの追加を依頼されている。
/Users/yosuke.miyanishi/AiWorkspace/Worktime	/Users/yosuke.miyanishi/.agents/.context/2026-04-24_12_15_24	DONE	tsvをcsvへ変更する依頼あり。
```

### PLAN.md
これからやることの設計・アプローチ・判断理由。PLAN.md は単一タスクの最新スナップショット。変更時は全体を書き換える。履歴は CONTEXT.md に残す。
plan modeで出力した内容相当のものを保存する。

```markdown
# {タスク名}

## ゴール
（何を達成したいか）

## アプローチ
（どうやるか、選択した方針）

## 設計判断
（重要な選択とその理由）

## 未解決事項
（判断がついていない点）
```

### TODO.md
永続化されたチェックリスト。セッション内の細かいタスク管理は TaskCreate/TaskUpdate（Claude Code の組み込みタスク管理）を使い、**ここには作業単位で残すべき粒度のタスク**を書く。完了したタスクは削除せず `[x]` にする（完了の記録として残す）。

```markdown
# TODO

- [x] 完了したタスク
- [~] 進行中のタスク
- [ ] 未着手のタスク
```

更新の際は項目をどんどん追加していく。

例：

```markdown
# TODO

- [x] 完了したタスク
- [x] 進行中だったタスク
- [~] 未着手だったが今着手した
- [~] あたらしく追加した進行中のタスク
- [ ] あたらしく追加した未着手のタスク
```

### CONTEXT.md
時系列の作業記録。**新しいエントリを上に積む**（最新が一番上）。

```markdown
# CONTEXT

## YYYY-MM-DD HH:MM:SS - {エントリタイトル}

**ユーザーの指示**: （プロンプトの要約、または原文）
**やったこと**: （具体的なアクション）
**なぜ**: （意図・制約・選択の理由）
**結果**: （成功/失敗/保留、生成・変更したファイル）
**学び**: （ハマりどころ、非自明な知見。なければ省略可）
```

更新の際は`YYYY-MM-DD HH:MM:SS - {エントリタイトル}`を上にどんどん追加していく。

例：

```markdown
# CONTEXT

## 2026-04-24 13:10:30 - hogehoge

**ユーザーの指示**: hogeをhoge'にしたい
**やったこと**: hogeを変更する際の影響範囲について調べた
**なぜ**: hogeの呼び出し箇所にも影響が及ぶから
**結果**: hogeはhogehoge、hogehoge2に影響あり。これらのファイルについても変更する。
**学び**: hogeはhogehogeとhogehoge2との依存関係がある

## 2026-04-24 12:32:52 - fugafuga

**ユーザーの指示**: fugaを実装して
**やったこと**: fugaの詳細を調査
**なぜ**: fugaはどういうものなのか曖昧だったため
**結果**: fugaはfugafugaと同義
**学び**: 実装依頼を受けたときはヒアリングをすること。同義実装が隠れている可能性がある。
```

## 既存の仕組みとの棲み分け

- **CLAUDE.md / AGENTS.md**: プロジェクトの「ルール・指示」。静的。
- **TaskCreate/TaskUpdate（組み込みタスク管理）**: セッション内の細かい進行管理。セッション終了で消える。
- **`~/.agents/.context/`（本ルール）**: 作業単位の経緯・計画・ログ。タスク完了後も履歴として残す。不要になったらユーザーが手動で削除する。
