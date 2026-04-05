# 日次ダイジェスト

Embodied AI Radar の日次ダイジェストを実行します。

Monitor → Analyst → Writer → Archivist のパイプラインを今日の日付で実行。
6形式レポート + 日次サブテーマ記事を生成します。

```bash
python scripts/run_daily.py $ARGUMENTS
```

引数にテーマスラッグを指定した場合（例: `vla-models`）はそのテーマで実行。
指定なしの場合は `embodied-ai-overview` で実行。
