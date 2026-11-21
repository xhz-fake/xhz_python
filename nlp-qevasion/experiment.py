"""QEvasion 与 QNLI 文本对分类实验。运行：PYTHONPATH=deps python experiment.py"""
import json
import random
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
import re

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
O = Path('output')
O.mkdir(exist_ok=True)
LABELS = ['Clear Reply', 'Ambivalent', 'Clear Non-Reply']

def adapt(df, a, b, label, group=None):
    z = pd.DataFrame({'text_a': df[a].fillna('').astype(str),
                      'text_b': df[b].fillna('').astype(str),
                      'label': df[label],
                      'group': df[group].fillna('').astype(str) if group else '',
                      'source_id': df.index.astype(str)})
    return z.reset_index(drop=True)

def scores(gold, pred, labels):
    p, r, f, support = precision_recall_fscore_support(gold, pred, labels=labels, zero_division=0)
    return {'accuracy': accuracy_score(gold, pred), 'macro_p': float(p.mean()),
            'macro_r': float(r.mean()), 'macro_f1': float(f.mean()),
            'per_class': {str(k): {'precision': float(p[i]), 'recall': float(r[i]),
                                   'f1': float(f[i]), 'support': int(support[i])}
                          for i, k in enumerate(labels)},
            'confusion_matrix': confusion_matrix(gold, pred, labels=labels).tolist()}

def tfidf_fit(train, test, labels, ngram=(1, 2), balanced=False):
    vec = TfidfVectorizer(ngram_range=ngram, min_df=2, max_features=40000,
                          sublinear_tf=True, lowercase=True)
    fmt = lambda d: (d.text_a + ' [SEP] ' + d.text_b).tolist()
    x = vec.fit_transform(fmt(train))
    y = vec.transform(fmt(test))
    lr = LogisticRegression(max_iter=1000, random_state=SEED,
                            class_weight='balanced' if balanced else None)
    lr.fit(x, train.label)
    return lr.predict(y), lr.predict_proba(y), list(lr.classes_), len(vec.vocabulary_)

def load_glove(path):
    vectors = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip().split(' ')
            if len(parts) == 51:
                vectors[parts[0]] = np.asarray(parts[1:], dtype=np.float32)
    return vectors

def embeddings(df, vectors, max_words=192):
    # Pair representation retains both sides and their relation: [q, a, |q-a|, q*a].
    def mean_vec(s):
        words = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+",s.lower())[:max_words]
        found = [vectors[w] for w in words if w in vectors]
        return np.mean(found,axis=0) if found else np.zeros(50,dtype=np.float32)
    a = np.vstack([mean_vec(s) for s in df.text_a])
    b = np.vstack([mean_vec(s) for s in df.text_b])
    return np.hstack((a,b,np.abs(a-b),a*b))

def figure_bar(counts, title, path):
    plt.figure(figsize=(8.7, 3.5)); counts.plot.bar(color='#507199')
    plt.title(title); plt.ylabel('Samples'); plt.xticks(rotation=30, ha='right')
    plt.tight_layout(); plt.savefig(path, dpi=170); plt.close()

def figure_lengths(df):
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, field in zip(axs, ['question', 'interview_answer']):
        lengths = df[field].fillna('').str.len()
        ax.hist(lengths.clip(upper=lengths.quantile(.99)), bins=35, color='#507199')
        ax.set_title(field); ax.set_xlabel('Characters (clipped at 99th percentile)')
        ax.set_ylabel('Samples')
    fig.tight_layout();fig.savefig(O/'figure2_lengths.png',dpi=170);plt.close(fig)

def figure_cm(cm, labels):
    fig, ax = plt.subplots(figsize=(6.4, 4.5))
    ax.imshow(cm, cmap='Blues')
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, cm[i][j], ha='center', va='center')
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha='right')
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel('Predicted');ax.set_ylabel('Gold')
    fig.tight_layout();fig.savefig(O/'figure3_confusion.png',dpi=170);plt.close(fig)

def export_prediction(name, data, pred, prob, classes):
    z = pd.DataFrame({'id': data.source_id, 'gold': data.label, 'prediction': pred})
    for i, k in enumerate(classes): z['probability_'+str(k)] = prob[:, i]
    z.to_csv(O/f'{name}_predictions.csv',index=False)

def main():
    tr = pd.read_parquet('data/qevasion_train.parquet')
    te = pd.read_parquet('data/qevasion_test.parquet')
    qtr = adapt(tr, 'question', 'interview_answer', 'clarity_label', 'title')
    qte = adapt(te, 'question', 'interview_answer', 'clarity_label')
    raw_qnli_train = pd.read_parquet('data/qnli_train-00000-of-00001.parquet')
    raw_qnli_val = pd.read_parquet('data/qnli_validation-00000-of-00001.parquet')
    # 迁移实验使用固定随机抽样，以控制本地 CPU 耗时；抽样后不改变官方集合归属。
    ntr = adapt(raw_qnli_train.sample(n=3448,random_state=SEED), 'question','sentence','label')
    nte = adapt(raw_qnli_val.sample(n=308,random_state=SEED), 'question','sentence','label')
    nlabels = [0, 1]  # GLUE QNLI: 0 entailment; 1 not_entailment
    stats = {'qevasion': {}, 'qnli': {}, 'data_revision': '3afc18f0b582b3cfdb927822cff57ddc6e871f9c'}
    for name, dataset in [('train',tr),('test',te)]:
        stats['qevasion'][name] = {'rows':len(dataset),'dtypes':{k:str(v) for k,v in dataset.dtypes.items()},
          'missing':{k:int(dataset[k].isna().sum()) for k in ['question','interview_answer','clarity_label','title','president']},
          'empty':{k:int(dataset[k].fillna('').astype(str).str.strip().eq('').sum()) for k in ['question','interview_answer','clarity_label','evasion_label']},
          'clarity':dataset.clarity_label.value_counts().to_dict(),
          'evasion':dataset.evasion_label.value_counts(dropna=False).to_dict(),
          'question_mean_chars':float(dataset.question.str.len().mean()),
          'answer_mean_chars':float(dataset.interview_answer.str.len().mean()),
          'exact_qa_duplicates':int(dataset.duplicated(['question','interview_answer']).sum()),
          'titles':int(dataset.title.nunique()), 'presidents':int(dataset.president.nunique())}
    stats['qevasion']['train_test_title_overlap'] = len(set(tr.title.dropna())&set(te.title.dropna()))
    stats['qnli']={'full_train':len(raw_qnli_train),'full_validation':len(raw_qnli_val),
                   'sample_train':len(ntr),'sample_validation':len(nte)}
    figure_bar(tr.clarity_label.value_counts().reindex(LABELS), 'QEvasion clarity labels — train',O/'figure1_labels.png')
    figure_bar(tr.evasion_label.value_counts(), 'QEvasion fine labels — train',O/'figure1b_fine_labels.png')
    figure_lengths(tr)
    results = {}
    majority = qtr.label.mode()[0]
    results['majority']=scores(qte.label,[majority]*len(qte),LABELS)
    for name,ngram,balanced in [('tfidf_unigram',(1,1),False),('tfidf_bigram',(1,2),False),('tfidf_bigram_balanced',(1,2),True)]:
        pred,prob,classes,features=tfidf_fit(qtr,qte,LABELS,ngram,balanced)
        results[name]=scores(qte.label,pred,LABELS)
        results[name]['features']=features
        export_prediction(name,qte,pred,prob,classes)
        if name=='tfidf_bigram_balanced':
            analysis_pred=pred.copy()
        print(name,results[name]['macro_f1'],flush=True)
    vectors=load_glove('data/glove.6B.50d.txt')
    x=embeddings(qtr,vectors)
    y=embeddings(qte,vectors)
    lr=LogisticRegression(max_iter=1000,random_state=SEED)
    lr.fit(x,qtr.label)
    pred=lr.predict(y);prob=lr.predict_proba(y)
    results['glove_lr']=scores(qte.label,pred,LABELS)
    export_prediction('glove_lr',qte,pred,prob,lr.classes_)
    figure_cm(results['tfidf_bigram_balanced']['confusion_matrix'],LABELS)
    errors=qte.loc[np.array(analysis_pred)!=qte.label.to_numpy(),['source_id','text_a','text_b','label']].copy()
    errors['prediction']=np.array(analysis_pred)[np.array(analysis_pred)!=qte.label.to_numpy()]
    errors['answer_chars']=errors.text_b.str.len()
    errors.to_csv(O/'qevasion_errors.csv',index=False)
    print('glove_lr',results['glove_lr']['macro_f1'],flush=True)
    # Direct model transfer: explicit semantic bridge, original Clear Reply -> entailment.
    # Direct transfer must use the original QEvasion-trained model on QNLI vectors.
    nx=embeddings(ntr,vectors)
    ny=embeddings(nte,vectors)
    original_pred=lr.predict(ny)
    direct=np.where(original_pred=='Clear Reply',0,1)
    results['qnli_direct']=scores(nte.label,direct,nlabels)
    # 保留直接复用的逐样本决策。决策先三分类后映射；概率列为粗标签质量之和。
    source_prob=lr.predict_proba(ny)
    clear_index=list(lr.classes_).index('Clear Reply')
    bridge_prob=np.column_stack((source_prob[:,clear_index],1-source_prob[:,clear_index]))
    export_prediction('qnli_direct',nte,direct,bridge_prob,nlabels)
    npred,nprob,nclasses,nfeatures=tfidf_fit(ntr,nte,nlabels,(1,2),False)
    results['qnli_tfidf']=scores(nte.label,npred,nlabels)
    results['qnli_tfidf']['features']=nfeatures
    export_prediction('qnli_tfidf',nte,npred,nprob,nclasses)
    nlr=LogisticRegression(max_iter=1000,random_state=SEED)
    nlr.fit(nx,ntr.label)
    npred=nlr.predict(ny);nprob=nlr.predict_proba(ny)
    results['qnli_glove_lr']=scores(nte.label,npred,nlabels)
    export_prediction('qnli_glove_lr',nte,npred,nprob,nlr.classes_)
    print('qnli',results['qnli_direct']['macro_f1'],results['qnli_tfidf']['macro_f1'],results['qnli_glove_lr']['macro_f1'],flush=True)
    (O/'stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    (O/'metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    (O/'config.json').write_text(json.dumps({'seed':SEED,'tfidf':'word 1-2 grams, min_df=2, max_features=40000, sublinear_tf=True',
      'pretrained':'GloVe 6B 50d (antokun/glove.6B.50d revision ab51545236b5a21a48a8d604f05af082fded839d), first 8000000 bytes (~18712 common words), mean pooling, max 192 words per side, concat [q,a,abs(q-a),q*a]',
      'dataset_adapters':{'QEvasion':{'text_a':'question','text_b':'interview_answer','label':'clarity_label','group':'title'},
       'QNLI':{'text_a':'question','text_b':'sentence','label':'label','group':None}},
      'qnli_revision':'bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c',
      'qnli_sampling':'3448 official train and 308 official validation, independent seed 42',
      'label_bridge':{'Clear Reply':0,'Ambivalent':1,'Clear Non-Reply':1}},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
