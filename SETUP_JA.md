# ArUco AR 実行環境の作り方（Ubuntu 22.04）

## 必要なもの

- Ubuntu 22.04
- USBカメラ
- マーカー1〜4（`create_marker/markers_1-4_A4.pdf`）

## 1. OSパッケージをインストール

```bash
sudo apt update
sudo apt install -y python3-venv libgl1-mesa-dri libegl-mesa0 libglx-mesa0 mesa-utils
```

## 2. Python仮想環境を作成

プロジェクトのディレクトリへ移動して実行します。Minicondaではなく、`/usr/bin/python3`を明示的に使用してください。

```bash
cd ArucoAR-Python
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. 起動

```bash
source .venv/bin/activate
python main.py
```

終了するには、AR画面を選択して `Q` キーを押します。

## 4. マーカーを印刷

`create_marker/markers_1-4_A4.pdf`をA4用紙へ印刷します。印刷設定は「実際のサイズ」または「100%」にし、用紙へ合わせる拡大縮小は無効にしてください。

## 現在のテスト内容

- マーカー1：100%のピンク色キューブ
- マーカー2：75%のピンク色キューブ
- マーカー3：50%のピンク色キューブ
- マーカー4：25%のピンク色キューブ
- テストモデル：`model/test_cube.mqo`

モデルと倍率は`settings.txt`の`mqoModel:`および`mqoPose:`で変更できます。

## トラブルシューティング

### カメラが開けない

`settings.txt`の`cameraID:`を確認します。通常は`0`です。接続されたカメラは次のコマンドで確認できます。

```bash
ls /dev/video*
```

### EGLまたはswrastのエラー

仮想環境がMiniconda由来になっていないか確認します。

```bash
cat .venv/pyvenv.cfg
```

`home = /usr/bin`またはUbuntu標準Pythonを示していれば正常です。`home = /home/.../miniconda/...`の場合は`.venv`を作り直してください。
