import os

import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score
import rtdl
import torch
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, train_test_split
import zero
from sklearn.metrics import accuracy_score
import numpy as np


@torch.no_grad()
def evaluate(part, model, X, y):
    model.eval()
    prediction = []
    for batch in zero.iter_batches(X[part], 1024):
        prediction.append(model(batch, None))
    prediction = torch.cat(prediction).squeeze(1).cpu().numpy()
    target = y[part].cpu().numpy()

    score = f1_score(target, (prediction > 0.5).astype(np.float32))

    return score, prediction


def apply_model(x_num, x_cat=None):
    return model(x_num, x_cat)


csvs = sorted(os.listdir("CSVS/"))
for file in csvs:
    df = pd.read_csv("CSVS/" + file, index_col="token_address")

    target = pd.read_csv("../Labelling/labeled_list.csv", index_col="token_address")
    df = df.merge(target['label'], left_index=True, right_index=True)

    lock_features = pd.read_csv("../../data/token_lock_features.csv", index_col="token_address")
    df = df.merge(lock_features, how='left', left_index=True, right_index=True)

    ids = []
    total_probs, total_targets = [], []
    X, y = {}, {}

    skfolds = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
    for fold, (t, v) in enumerate(skfolds.split(df.reset_index()['token_address'], df['label'])):
        X['train'], X['test'] = df.iloc[t].drop(["eval_block", "label"], axis=1), \
                                df.iloc[v].drop(["eval_block", "label"], axis=1)

        y['train'], y['test'] = df['label'].iloc[t], df['label'].iloc[v]

        X['train'], X['val'], y['train'], y['val'] = train_test_split(X['train'], y['train'], train_size=0.8)

        device = torch.device('cuda')
        # not the best way to preprocess features, but enough for the demonstration
        preprocess = StandardScaler().fit(X['train'])
        X = {
            k: torch.tensor(preprocess.fit_transform(v), device=device)
            for k, v in X.items()
        }
        y = {k: torch.tensor(v, device=device) for k, v in y.items()}
        y = {k: v.float() for k, v in y.items()}

        model = rtdl.FTTransformer.make_default(
            n_num_features=X['train'].shape[1],
            cat_cardinalities=None,
            last_layer_query_idx=[-1],  # it makes the model faster and does NOT affect its output
            d_out=1,
        )

        model.to(device)
        model.double()
        optimizer = model.make_default_optimizer()
        loss_fn = F.binary_cross_entropy_with_logits

        batch_size = 100
        train_loader = zero.data.IndexLoader(len(X['train']), batch_size, device=device)
        progress = zero.ProgressTracker(patience=2)

        n_epochs = 10
        for epoch in range(1, n_epochs + 1):
            for iteration, batch_idx in enumerate(train_loader):
                model.train()
                optimizer.zero_grad()
                x_batch = X['train'][batch_idx]
                y_batch = y['train'][batch_idx]
                loss = loss_fn(model(x_batch, None).squeeze(1), y_batch)
                loss.backward()
                optimizer.step()

            val_score, prob = evaluate('val', model, X, y)
            progress.update(val_score)
            if progress.fail:
                break

        val_score, prob = evaluate('test', model, X, y)
        ids += df.iloc[v].index.tolist()
        total_probs += prob.tolist()
        total_targets += y['test'].cpu().tolist()
        prob = (prob > 0.5).astype(np.float32)

        f1 = f1_score(y['test'].cpu(), prob)
        sensibilitat = recall_score(y['test'].cpu(), prob)
        precisio = precision_score(y['test'].cpu(), prob)
        accuracy = accuracy_score(y['test'].cpu(), prob)
        hour = file.split("h")[0].split("_")[1]
        print("{},{},{},{},{},{}".format(accuracy, sensibilitat, precisio, f1, fold, hour))


