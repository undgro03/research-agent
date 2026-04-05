# Embodied AI Radar — プロジェクトメモリ

## 目的
Embodied AI / ロボティクス分野の自動リサーチ監視システム。
PI（ユーザー）が優秀なPhD学生（Claude）にリサーチタスクを委任するモデルで動作する。

X（Twitter）速報監視・arXiv / 主要ラボ論文の日次追跡・構造化レポート生成（Markdown + コンサル風HTML）・テーマ別ディープダイブに対応。

## エージェント構成
- **Coordinator**（メインセッション）: パイプライン全体を指揮、末端作業は委任のみ
- **Monitor**（サブエージェント）: データ収集専任 — arXiv・X/Twitter・RSS
- **Analyst**（サブエージェント）: スコアリング・ランキング・トレンド検出 — claude-opus-4-6 使用
- **Writer**（サブエージェント）: 6形式レポート生成 — claude-sonnet-4-6 使用
- **Archivist**（サブエージェント）: SQLite永続化 — claude-haiku-4-5 使用（軽量）

## 主要ディレクトリ
- `themes/` — テーマプロファイルYAML（`_base.yaml` を継承）
- `reports/daily/` — 日次ダイジェスト（YYYY-MM-DD/）
- `reports/weekly/` — 週次レポート（YYYY-WNN/）
- `reports/deep-dives/<theme>/` — テーマ別ディープダイブ
- `reports/articles/<theme>/` — 日次サブテーマ記事
- `data/radar.db` — SQLiteメモリストア
- `data/feeds.yaml` — ラボRSS・Xアカウント・ソース一覧（リンク付き）
- `.claude/agents/` — サブエージェント定義ファイル（Markdownフロントマター形式）
- `src/radar/` — Pythonパッケージ
- `templates/` — HTML/CSSレポートテンプレート

## レポート形式（1回の実行で6種類生成）
1. `report_ja.md` — Markdown・日本語
2. `report_en.md` — Markdown・英語
3. `report_bilingual.md` — Markdown・日英併記
4. `report_ja.html` — コンサル風HTML/CSS・Mermaid図解・日本語
5. `report_en.html` — コンサル風HTML/CSS・Mermaid図解・英語
6. `report_bilingual.html` — コンサル風HTML/CSS・日英併記

加えて日次サブテーマ記事（当日の注目度から動的に2〜4本選択）。

## テーマプロファイル
すべて `themes/_base.yaml` を継承。利用可能なテーマ：
- `embodied-ai-overview` — Embodied AI全体（メインテーマ）
- `world-action-models` — World Models × Action
- `vlm-robotics` — VLM × ロボット制御
- `action-video-generation` — Action Conditioned 動画生成

新テーマ追加: `themes/<slug>.yaml` を作成し `extends: _base` を記述。

## スケジュール（Toronto時間 / ET）
- 毎日 7:00 AM EDT（3〜11月）→ RemoteTrigger `radar-daily-digest-edt`
- 毎日 7:00 AM EST（12〜2月）→ RemoteTrigger `radar-daily-digest-est`
- 毎週月曜 7:00 AM EDT → RemoteTrigger `radar-weekly-report-edt`
- 毎週月曜 7:00 AM EST → RemoteTrigger `radar-weekly-report-est`
- 4時間ごと → RemoteTrigger `radar-alert-check`
- スケジュール管理: https://claude.ai/code/scheduled

## データベース（data/radar.db）
テーブル: `items`, `trend_snapshots`, `reports`, `alerts`, `articles`
アイテムはsha256(source+url)で重複排除。90日後に自動削除。

## APIキー
`.env` / `.env.example` 参照:
- `ANTHROPIC_API_KEY`
- `TWITTER_BEARER_TOKEN` — X API v2 読み取り専用

## 実行方法
```bash
uv sync
python scripts/init_db.py

python scripts/run_daily.py
python scripts/run_weekly.py
python scripts/run_deep_dive.py --theme world-action-models
```

スラッシュコマンド: `/daily`、`/weekly`、`/deep-dive <theme>`
