"""Download pinned public inputs. Raw datasets are not redistributed in the package."""
from pathlib import Path
from urllib.request import Request, urlopen
import time

DEST = Path('data')
DEST.mkdir(exist_ok=True)
URLS = {
 'qevasion_train.parquet': 'https://huggingface.co/datasets/ailsntua/QEvasion/resolve/3afc18f0b582b3cfdb927822cff57ddc6e871f9c/data/train-00000-of-00001.parquet',
 'qevasion_test.parquet': 'https://huggingface.co/datasets/ailsntua/QEvasion/resolve/3afc18f0b582b3cfdb927822cff57ddc6e871f9c/data/test-00000-of-00001.parquet',
 'qnli_train-00000-of-00001.parquet': 'https://huggingface.co/datasets/nyu-mll/glue/resolve/bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c/qnli/train-00000-of-00001.parquet',
 'qnli_validation-00000-of-00001.parquet': 'https://huggingface.co/datasets/nyu-mll/glue/resolve/bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c/qnli/validation-00000-of-00001.parquet',
 'glove.6B.50d.txt': 'https://huggingface.co/datasets/antokun/glove.6B.50d/resolve/ab51545236b5a21a48a8d604f05af082fded839d/glove.6B.50d.txt',
}

def fetch(name, url):
    target=DEST/name
    cap=8000000 if name.endswith('.txt') else None
    def valid(blob):
        return len(blob)==cap if cap else blob[:4]==b'PAR1' and blob[-4:]==b'PAR1'
    if target.exists() and valid(target.read_bytes()):
        print(name,target.stat().st_size,'cached')
        return
    headers={'Range':f'bytes=0-{cap-1}'} if cap else {}
    for attempt in range(5):
        try:
            with urlopen(Request(url,headers=headers),timeout=55) as response:
                # 即使服务端忽略 Range，也只读取预先声明的词向量字节数。
                data=response.read(cap) if cap else response.read()
            if not valid(data): raise RuntimeError('incomplete or invalid download')
            partial=target.with_suffix(target.suffix+'.part')
            partial.write_bytes(data)
            partial.replace(target)
            print(name,len(data))
            return
        except Exception:
            if attempt==4:raise
            time.sleep(1+attempt)

if __name__=='__main__':
    for name,url in URLS.items():fetch(name,url)
