# pyaozora

aozoraのXHTMLリンクからEPUB3に

使った外部モジュールは `ebooklib` と `bs4` だけです。
```
pip install -r requirements.txt
```

もしかして、他のサイトも変換できますが、青空文庫の本だけが試しました。

# 機能
`-t`と`-y`」が縦書きと横書きの設定です。 デフォルトは縦書き。
`-o`プログラムの出力ファイルの設定です。デフォルトは `$題名.epub` です。

```
pyaozora -y -o 吾輩は猫である.epub "https://www.aozora.gr.jp/cards/000148/files/789_14547.html"
```
