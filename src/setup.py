import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess

def check_python_portable():
    """ポータブル版Pythonかどうかを確認"""
    # sys.executableの場所を確認
    python_path = os.path.dirname(sys.executable)
    return os.path.exists(os.path.join(python_path, "python.exe")) and not "Program Files" in python_path

def install_requirements():
    """必要なパッケージをインストール"""
    try:
        print("gradioをインストールしています...")
        # インストールコマンドをより明示的に実行
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "gradio"], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
        
        # インストールの確認
        try:
            import gradio
            print(f"gradio {gradio.__version__} が正常にインストールされました。")
            return True
        except ImportError:
            print("gradioのインポートに失敗しました。手動でインストールしてください。")
            print("コマンド: pip install gradio")
            return False
    except subprocess.CalledProcessError as e:
        print(f"パッケージのインストール中にエラーが発生しました: {e}")
        print("手動でgradioをインストールしてください。")
        print("コマンド: pip install gradio")
        return False

def download_ffmpeg():
    """FFmpegをダウンロードして展開"""
    # 作業ディレクトリ
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ffmpeg_dir = os.path.join(base_dir, "ffmpeg")
    
    # すでにFFmpegがあるか確認
    if os.path.exists(os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")):
        print("FFmpegはすでにインストールされています。")
        return True
    
    try:
        # FFmpegのダウンロードURL
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(base_dir, "ffmpeg.zip")
        
        print(f"FFmpeg をダウンロード中... {ffmpeg_url}")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        print("FFmpeg を展開中...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(base_dir)
        
        # 展開したフォルダ名は ffmpeg-master-latest-win64-gpl
        extracted_dir = os.path.join(base_dir, "ffmpeg-master-latest-win64-gpl")
        
        # 必要なディレクトリだけを移動
        if os.path.exists(ffmpeg_dir):
            shutil.rmtree(ffmpeg_dir)
        
        os.makedirs(ffmpeg_dir)
        shutil.move(os.path.join(extracted_dir, "bin"), os.path.join(ffmpeg_dir, "bin"))
        
        # 不要なファイルを削除
        shutil.rmtree(extracted_dir)
        os.remove(zip_path)
        
        print("FFmpeg のセットアップが完了しました。")
        return True
    except Exception as e:
        print(f"FFmpeg のダウンロード中にエラーが発生しました: {str(e)}")
        print("FFmpeg を手動でダウンロードして、ffmpeg/bin ディレクトリに配置してください。")
        print("ダウンロードURL: https://ffmpeg.org/download.html")
        return False

def main():
    print("2webm セットアップユーティリティ")
    print("------------------------------")
    
    # ポータブル版Pythonかチェック
    if not check_python_portable():
        print("警告: これはポータブル版Pythonではないようです。")
        response = input("続行しますか？ (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # 必要なパッケージのインストール
    if not install_requirements():
        print("警告: ライブラリのインストールに問題がありましたが、続行します。")
    
    # FFmpegのダウンロードとセットアップ
    if not download_ffmpeg():
        sys.exit(1)
    
    print("\nセットアップが完了しました！")
    print("以下のコマンドでアプリケーションを起動できます:")
    print(f"python {os.path.join('src', 'main.py')}")

if __name__ == "__main__":
    main() 