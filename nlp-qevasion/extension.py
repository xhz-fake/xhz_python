"""QNLI 数据效率对比：官方完整训练池的 10%、30%、100%，固定官方验证集。

预先固定参数，不以验证集选择模型。分层嵌套抽样，3 个随机种子。
100% 数据下模型与随机种子无关，仅拟合一次并在汇总中注明。
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import json, time, hashlib, platform, sys
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report
from experiment import adapt, embeddings, load_glove

O=Path('extension_output');O.mkdir(exist_ok=True)
SEEDS=[42,52,62]
RATIOS=[0.1,0.3,1.0]

def subset(y, ratio, seed):
    # 每类先固定一个顺序；同一种子下 10% 是 30% 的子集。
    rng=np.random.default_rng(seed)
    chosen=[]
    for label in sorted(np.unique(y)):
        ids=np.flatnonzero(y==label)
        ids=rng.permutation(ids)
        chosen.extend(ids[:max(1,int(round(len(ids)*ratio)))].tolist())
    return np.array(sorted(chosen),dtype=int)

def evaluate(model, xtrain, ytrain, xtest, ytest):
    start=time.perf_counter()
    model.fit(xtrain,ytrain)
    p=model.predict(xtest)
    probs=model.predict_proba(xtest)
    return p,probs,{'accuracy':accuracy_score(ytest,p),
        'macro_f1':f1_score(ytest,p,average='macro'),
        'per_class':classification_report(ytest,p,output_dict=True,zero_division=0),
        'fit_predict_seconds':time.perf_counter()-start}

def main():
    tr=adapt(pd.read_parquet('data/qnli_train-00000-of-00001.parquet'),'question','sentence','label')
    va=adapt(pd.read_parquet('data/qnli_validation-00000-of-00001.parquet'),'question','sentence','label')
    y=tr.label.to_numpy();yv=va.label.to_numpy()
    print('Official QNLI sizes',len(tr),len(va),flush=True)
    vectors=load_glove('data/glove.6B.50d.txt')
    print('Building frozen GloVe pair vectors',len(vectors),flush=True)
    x=embeddings(tr,vectors);xv=embeddings(va,vectors)
    np.savez_compressed(O/'embedding_cache.npz',train=x,validation=xv)
    rows=[]; details={}; full={}
    train_text=(tr.text_a+' [SEP] '+tr.text_b).tolist()
    val_text=(va.text_a+' [SEP] '+va.text_b).tolist()
    for ratio in RATIOS:
        for seed in (SEEDS if ratio<1 else [SEEDS[0]]):
            idx=subset(y,ratio,seed)
            for kind in ['glove_lr','tfidf_lr']:
                key=f'{kind}_{int(ratio*100)}_seed{seed}'
                model=LogisticRegression(max_iter=1000,random_state=42)
                start=time.perf_counter()
                if kind=='glove_lr':
                    a,b=x[idx],xv
                else:
                    vec=TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=40000,sublinear_tf=True)
                    a=vec.fit_transform([train_text[i] for i in idx]);b=vec.transform(val_text)
                pred,prob,result=evaluate(model,a,y[idx],b,yv)
                result.update({'n_train':len(idx),'n_eval':len(va),'ratio':ratio,'seed':seed,
                    'model':kind,'subset_sha256':hashlib.sha256(idx.tobytes()).hexdigest(),
                    'end_to_end_seconds':time.perf_counter()-start})
                details[key]=result;rows.append({k:v for k,v in result.items() if k!='per_class'})
                pd.DataFrame({'id':va.source_id,'gold':yv,'prediction':pred,
                    'probability_0':prob[:,0],'probability_1':prob[:,1]}).to_csv(O/f'{key}_predictions.csv',index=False)
                np.savetxt(O/f'{key}_train_indices.txt',idx,fmt='%d')
                print(key,len(idx),round(result['macro_f1'],4),flush=True)
                (O/'details.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
    df=pd.DataFrame(rows);df.to_csv(O/'runs.csv',index=False)
    summary=[]
    for (model,ratio),g in df.groupby(['model','ratio']):
        summary.append({'model':model,'ratio':float(ratio),'n_train':int(g.n_train.iloc[0]),
            'n_eval':len(va),'independent_runs':len(g),
            'accuracy_mean':float(g.accuracy.mean()),'macro_f1_mean':float(g.macro_f1.mean()),
            'macro_f1_std':float(g.macro_f1.std(ddof=1)) if len(g)>1 else None})
    (O/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.rcParams['font.family']='Microsoft YaHei'
    fig,ax=plt.subplots(figsize=(8,4.4))
    for kind,label,color in [('glove_lr','GloVe 文本对表示 + LR','#0F766E'),('tfidf_lr','TF-IDF + LR','#284B70')]:
        s=[q for q in summary if q['model']==kind]
        ax.errorbar([q['ratio']*100 for q in s],[q['macro_f1_mean'] for q in s],
            yerr=[q['macro_f1_std'] or 0 for q in s],label=label,color=color,marker='o',capsize=4)
    ax.set(xlabel='官方 QNLI 训练数据比例（%）',ylabel='Macro-F1',xticks=[10,30,100],ylim=(0.45,0.85))
    ax.legend(frameon=False);ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(O/'data_efficiency.png',dpi=180);plt.close(fig)
    config={'python':sys.version,'sklearn':sklearn.__version__,'numpy':np.__version__,
        'platform':platform.platform(),'seeds':SEEDS,'ratios':RATIOS,
        'official_qnli_train':len(tr),'official_qnli_validation':len(va),
        'label_semantics':{'0':'entailment','1':'not_entailment'},
        'protocol':'All models/parameters fixed in advance. Nested stratified samples. Official validation used for reporting only. 100% fitted once because identical data and deterministic estimator.',
        'pretrained':'Frozen truncated GloVe 6B 50d, max 192 words each, [q,a,abs(q-a),q*a]',
        'tfidf':'word ngram 1-2, min_df 2, max_features 40000, sublinear_tf True',
        'classifier':'LogisticRegression(max_iter=1000, random_state=42, default other parameters)'}
    (O/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
