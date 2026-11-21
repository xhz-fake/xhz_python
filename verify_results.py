"""独立检查保存的预测、指标及嵌套抽样，不重新训练模型。"""
from pathlib import Path
import json,gzip
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score,f1_score

def main():
 out=Path('output'); ext=Path('extension_output'); evidence=[]
 metrics=json.loads((out/'metrics.json').read_text())
 for file in out.glob('*_predictions.csv'):
  name=file.name.removesuffix('_predictions.csv')
  d=pd.read_csv(file);ref=metrics[name]
  acc=accuracy_score(d.gold,d.prediction);macro=f1_score(d.gold,d.prediction,average='macro')
  assert abs(acc-ref['accuracy'])<1e-12 and abs(macro-ref['macro_f1'])<1e-12,file
  assert d.id.is_unique and not d.isna().any().any(),file
  evidence.append({'file':str(file),'rows':len(d),'accuracy':acc,'macro_f1':macro})
 detail=json.loads((ext/'details.json').read_text())
 compact=[]
 for key,ref in detail.items():
  d=pd.read_csv(ext/f'{key}_predictions.csv')
  acc=accuracy_score(d.gold,d.prediction);macro=f1_score(d.gold,d.prediction,average='macro')
  assert len(d)==5463 and d.id.is_unique
  assert abs(acc-ref['accuracy'])<1e-12 and abs(macro-ref['macro_f1'])<1e-12,key
  z=d[['id','gold','prediction']].copy();z.insert(0,'run',key);compact.append(z)
  evidence.append({'file':key,'rows':len(d),'accuracy':acc,'macro_f1':macro})
 for seed in [42,52,62]:
  a=set(np.loadtxt(ext/f'glove_lr_10_seed{seed}_train_indices.txt',dtype=int).tolist())
  b=set(np.loadtxt(ext/f'glove_lr_30_seed{seed}_train_indices.txt',dtype=int).tolist())
  assert a < b and len(a)==10475 and len(b)==31423
 all_ids=np.loadtxt(ext/'glove_lr_100_seed42_train_indices.txt',dtype=int)
 assert np.array_equal(all_ids,np.arange(104743))
 summary=json.loads((ext/'summary.json').read_text())
 for s in summary:
  vals=[v['macro_f1'] for v in detail.values() if v['model']==s['model'] and v['ratio']==s['ratio']]
  assert abs(np.mean(vals)-s['macro_f1_mean'])<1e-12
  if len(vals)>1:assert abs(np.std(vals,ddof=1)-s['macro_f1_std'])<1e-12
 dest=Path('submission_results');dest.mkdir(exist_ok=True)
 pd.concat(compact,ignore_index=True).to_csv(dest/'extension_predictions.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 for name in ['tfidf_bigram_balanced','glove_lr','qnli_direct','qnli_tfidf','qnli_glove_lr']:
  d=pd.read_csv(out/f'{name}_predictions.csv')
  d[['id','gold','prediction']].to_csv(dest/f'{name}_predictions.csv',index=False)
 record={'status':'pass','checked_prediction_files':len(evidence),'checks':evidence,
  'nested_stratified_subsets':'pass','full_training_indices':'0..104742 inclusive',
  'summary_recomputed':'pass'}
 (dest/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print('PASS',len(evidence),'prediction files; nested subsets; full training pool; summary')

if __name__=='__main__':main()
