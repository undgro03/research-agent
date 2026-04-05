# ディープダイブ

特定のEmbodied AIテーマに絞った深掘りリサーチを実行します。

## 使い方
```
/deep-dive <テーマスラッグ>
```

## 利用可能なテーマ
- `embodied-ai-overview` — Embodied AI全体
- `world-action-models` — World Models × Action
- `vlm-robotics` — VLM × ロボット制御
- `action-video-generation` — Action Conditioned 動画生成

## 実行内容
1. `themes/<slug>.yaml` からテーマプロファイルを読み込み
2. 拡張ルックバック期間での広範囲検索
3. テーマの研究ランドスケープを全体マッピング
4. エキスパートレベルの6形式レポート + 詳細記事を生成

```bash
python scripts/run_deep_dive.py --theme $ARGUMENTS
```
