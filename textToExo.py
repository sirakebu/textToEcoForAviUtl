# encoding: utf-8

import sys
import binascii
import re

#### Configuration ###

captionLifeTime = 180 # [frame]

exeditConfig = u'''[exedit]
width=1920
height=1080
rate=60
scale=1
length=280760
audio_rate=44100
audio_ch=2\n'''

captionConfig = u'''[$1]
start=$2
end=$3
layer=$5
overlay=1
camera=0
[$1.0]
_name=テキスト
サイズ=65
表示速度=0.0
文字毎に個別オブジェクト=0
移動座標上に表示する=0
自動スクロール=0
B=0
I=0
type=3
autoadjust=0
soft=1
monospace=0
align=4
spacing_x=0
spacing_y=0
precision=1
color=db7093
color2=ffffff
font=Splatfont
text=$4
[$1.1]
_name=縁取り
サイズ=5
ぼかし=0
color=db7093
file=
[$1.2]
_name=標準描画
X=2.0
Y=420.0
Z=0.0
拡大率=100.00
透明度=0.0
回転=0.00
blend=0\n''' # 変更する箇所を"$n"とし，置換していく．

### Functions ###

def encodeForExo(text):
    '''
    exoファイルようにテキストをUTF-16 リトルエンディアン（4096文字まで0パディング）に変換します．
    '''

    #文末の改行を削除する
    text = re.sub(r'\n$', '', text)

    # 一行のテキストは61文字以上の場合，60文字（文末を(ry）にする
    textLength = len(text)
    if textLength > 61:
        text = text[:57] 
        text = text + "(ry"

    # テキストをUTF-16 リトルエンディアンに変換
    textEncoded = ''
    if text != '\n':
        for char in text:
            if char == '\n': # 改行コードがうまく変換できないので，例外処理
                bytes_be = '000d000a'
            else:
                hex_be = hex(ord(char)).replace('0x','')
            bytes_be = binascii.unhexlify(hex_be)
            bytes_le = bytes_be[::-1]
            hex_le = binascii.hexlify(bytes_le).decode()

            # 英数字が2文字になるので，4文字になるように0埋めする
            hex_le = hex_le[::-1]
            hex_le = hex_le.zfill(4)
            hex_le = hex_le[::-1]

            textEncoded = textEncoded + hex_le

    # 4096文字まで0でパディング
    textEncoded = textEncoded[::-1].zfill(4096)
    textEncoded = textEncoded[::-1]

    return textEncoded

def makeCaptionDescritpion(captionNum, textEncoded):
    '''
    キャプションごとに出力するexoファイルに書き込む用の文字列を返す．
    '''
    startTiming = 1 + captionNum * captionLifeTime
    endTiming = (captionNum + 1) * captionLifeTime
    layer = 1 if captionNum % 2 == 0 else 2
    captionDescription = captionConfig
    captionDescription = captionDescription.replace("$1", str(captionNum))
    captionDescription = captionDescription.replace("$2", str(startTiming))
    captionDescription = captionDescription.replace("$3", str(endTiming))
    captionDescription = captionDescription.replace("$4", textEncoded)
    captionDescription = captionDescription.replace("$5", str(layer))
    return captionDescription

### Main ###

def main():
    '''
    テキストファイル（encoding=shift-jis）を行ごとにキャプションを表示するexoファイルを作成する．
    第一引数にテキストファイル，第ニ引数に出力ファイル名を与えて，実行する．
    キャプションの装飾，長さ等は本スクリプト上部の ### Configuration#### で設定する．
    '''
    try:
        inputFile = sys.argv[1]
        outputFile = sys.argv[2]
    except:
        print(
'''
テキストファイル（encoding=shift-jis）を行ごとにキャプションを表示するexoファイルを作成する．
第一引数にテキストファイル，第ニ引数に出力ファイル名を与えて，実行する．
キャプションの装飾，長さ等は本スクリプト上部の ### Configuration#### で設定する．
'''
        )

    captionNum = 0

    with open(outputFile, 'w', encoding='shift-jis') as w:
        w.write(exeditConfig)

        with open(inputFile, 'r', encoding='shift-jis') as r:
            while True:
                text = r.readline()
                if not text: break
                print(text)
                textEncoded = encodeForExo(text)
                captionDescription = makeCaptionDescritpion(captionNum, textEncoded)
                w.write(captionDescription)

                captionNum = captionNum + 1

if __name__ == "__main__":main()