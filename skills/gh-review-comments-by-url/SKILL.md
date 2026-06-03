---
name: gh-review-comments-by-url
description: 指定された GitHub PR URL のレビューコメントに対応する。ユーザーがこのスキルを明示的に呼び出し、pull request URL を提供した場合のみ使う。コメントやレビューの取得、返信投稿など GitHub への接続はすべて `gh` コマンド経由で行う。レビューコメントとスレッドを取得し、1件ずつ処理し、`reviewThreads.nodes[].id` と `addPullRequestReviewThreadReply` で各レビュー スレッドに返信する。対応した項目にはコミットログを含め、対応しない項目には理由を添えて返信する。
---

# PR レビューコメント対応（URL 入力）

## 1) 前提条件を確認する
- GitHub への接続はすべて GitHub CLI の `gh` コマンドで行う。直接 HTTP クライアント、GitHub SDK、個別トークン読み込みには切り替えない。
- `gh auth status` を実行し、GitHub CLI が認証済みであることを確認する。
- サンドボックスによりネットワークアクセスがブロックされる場合は、昇格したネットワーク権限で `gh` コマンドを実行する。
- 認証に失敗した場合は、ユーザーに `gh auth login` の実行を依頼してから再試行する。
- URL は `https://github.com/<owner>/<repo>/pull/<number>` 形式である必要がある。
- ユーザーがまだ PR URL を提供していない場合は、取得処理を始める前に URL を尋ねる。

## 2) PR URL からレビュー情報を取得する
- PR URL から `OWNER`、`REPO`、`NUMBER` を読み取る。
- `gh api graphql` を直接実行して PR 情報、conversation comments、reviews、review threads を取得する。
- 取得時も GitHub への接続経路は `gh` のみとする。
- 例:
```bash
PR_DATA=$(gh api graphql \
  -F owner="$OWNER" \
  -F repo="$REPO" \
  -F number="$NUMBER" \
  -f query='
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          number
          url
          title
          state
          comments(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              body
              createdAt
              updatedAt
              author { login }
            }
          }
          reviews(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              state
              body
              submittedAt
              author { login }
            }
          }
          reviewThreads(first: 100) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              isResolved
              isOutdated
              path
              line
              diffSide
              startLine
              startDiffSide
              originalLine
              originalStartLine
              resolvedBy { login }
              comments(first: 100) {
                nodes {
                  id
                  body
                  createdAt
                  updatedAt
                  author { login }
                }
              }
            }
          }
        }
      }
    }
  ')
```
- `pageInfo.hasNextPage` が `true` の接続がある場合は、該当する `endCursor` を `after:` 変数として追加し、同じ `gh api graphql` 形式で続きのページを取得する。
- JSON 出力の `.data.repository.pullRequest.reviewThreads.nodes`、`.data.repository.pullRequest.reviews.nodes`、`.data.repository.pullRequest.comments.nodes` から項目を列挙する。
- 各スレッド項目では、返信投稿用に `.data.repository.pullRequest.reviewThreads.nodes[].id` を `THREAD_ID` として保持する。
- 処理対象を番号付きリストにする。

## 3) 項目を仕分ける
- 各項目を `actionable`（対応する）または `skip`（対応を見送る）に分類する。
- `actionable` と判断する前に、レビュー依頼の内容を現在のコード、テスト、リポジトリの慣習に照らして確認する。
- 明確な理由がある場合のみ `skip` にする。
- よくある見送り理由: すでに解決済み、またはコード変更が不要な古い指摘。
- よくある見送り理由: PR のスコープ外。
- よくある見送り理由: コードやテストに照らすと事実と異なる指摘。
- よくある見送り理由: 既存のリポジトリ慣習と衝突する純粋な好みの指摘。
- 判断に迷う場合は、見送る前にユーザーへ確認する。

## 4) 対応が必要な項目を1件ずつ処理する
- まとめて処理せず、順番に1件ずつ処理する。
- 厳密な項目単位のループを使い、現在の項目が完了するまで次の項目へ進まない。
- Item N の分析
- Item N の実装（作業ツリーのみ）
- Item N のユーザー確認
- Item N のコミット
- その後に Item N+1 へ進む
- 各 `actionable` 項目を開始する前に、`START_SHA=$(git rev-parse HEAD)` を記録する。
- まず作業ツリー上で、項目ごとに最小限かつ戻しやすい変更を適用する（この時点ではコミットしない）。
- 変更後、影響範囲に応じた検証を実行する（テスト、lint、build など）。
- コミット前にパッチ品質を確認する（例: `git diff` と対象ファイルの確認）。
- コミット前に、現在の項目について次の3点をユーザーに明示的に確認する。
- PR レビューコメントの解釈が妥当であること。
- 提案する修正方針が妥当であること。
- 実際のコード変更が妥当であること（計画だけでなく、具体的な変更ファイルや hunk を示す）。
- 3点のいずれかが未確認の場合はコミットしない。
- ユーザーが調整を求めた場合は、コードを修正し、検証を再実行してから再確認する。
- 各 `actionable` 項目について、ユーザーの明示的な承認後に少なくとも1つのコミットを作成する。
- Item N のコミット後、`COMMIT_LOG` を収集し、Item N の返信本文を準備する。ただし、まだ投稿しない。
- 項目ごとのコミットログは `COMMIT_LOG=$(git log --reverse --pretty=format:'- %h %s' "${START_SHA}..HEAD")` で作成する。
- `COMMIT_LOG` が空の場合は、完了返信をまだ投稿しない。不足しているコミットを先に作成する。
- どの変更がどの項目番号に対応しているかを記録する。

## 5) スレッドごとの返信本文を作成する
- 返信はデフォルトで日本語で書く。
- `actionable` 項目には次のテンプレートを使う。
```text
対応しました。ありがとうございます。

変更概要:
- <変更点1>
- <変更点2>

コミットログ:
<COMMIT_LOG>
```
- `skip` 項目には次のテンプレートを使う。
```text
今回は対応を見送ります。
理由: <見送り理由>

コミット: なし（対応見送り）
```

## 6) GraphQL でスレッドごとに返信を投稿する
- 返信投稿も必ず `gh api graphql` で行う。直接 HTTP リクエストや SDK は使わない。
- `THREAD_ID` を使い、処理済みスレッド1件につき1つの返信を投稿する。
- `actionable` 項目では、ユーザー承認済みのコミットが存在する場合のみ投稿する。
- すべての関連コミットがリモートへ正常に push された後（`git push` 成功後）にのみ返信を投稿する。
- `git push` が未実行または失敗している場合、完了返信を投稿しない。
- 次のコマンド形式を使い、返ってきた返信 URL を記録する。
```bash
REPLY_URL=$(gh api graphql \
  -f query='
    mutation($threadId: ID!, $body: String!) {
      addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
        comment { url }
      }
    }
  ' \
  -F threadId="$THREAD_ID" \
  -F body="$REPLY_BODY" \
  --jq '.data.addPullRequestReviewThreadReply.comment.url')
```
- 投稿に失敗した場合は `gh auth status` を再確認し、必要に応じて再認証後に1回だけ再試行する。

## 7) 状況を報告する
- `Addressed` リストを随時更新する。項目番号、変更概要、`REPLY_URL`、`COMMIT_LOG` を含める。
- `Skipped` リストを随時更新する。項目番号、見送り理由、`REPLY_URL` を含める。
- ステータス更新も処理順（Item 1 -> Item 2 -> ...）に項目ごとに報告する。
- 最後に、すべての番号付き項目を網羅した最終サマリーを出す。

## 8) 検証チェックリスト
- ケース: 複数の `actionable` 項目。次へ進む前に、各項目で確認 -> コミットのサイクルが独立していることを確認する。
- ケース: コミット前の確認内容。指摘の解釈、修正方針、実際のコード差分概要が含まれていることを確認する。
- ケース: `git push` 前。完了返信がまだ投稿されていないことを確認する。
- ケース: `git push` 成功後。スレッドごとの完了返信が投稿されていることを確認する。
- ケース: 1コミットの `actionable` 項目。返信本文に `- <short_sha> <subject>` が含まれていることを確認する。
- ケース: 複数コミットの `actionable` 項目。返信本文にすべてのコミットが時系列順で含まれていることを確認する。
- ケース: ユーザー確認前の `actionable` 項目。コミットがまだ作成されていないことを確認する。
- ケース: コミットがない `actionable` 項目。コミットが存在するまで投稿がブロックされることを確認する。
- ケース: `skip` 項目。返信に理由と `コミット: なし（対応見送り）` が含まれていることを確認する。
- ケース: API または認証エラー。`gh auth status` の再確認案内が示されていることを確認する。
