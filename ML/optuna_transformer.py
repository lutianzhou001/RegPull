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


X = pd.read_csv("X.csv", index_col="token_address")

labels = pd.read_csv("Labelling/labeled_list.csv", index_col="token_address")
X = X.merge(labels['label'], left_index=True, right_index=True)
X = X.reset_index()
df = X.drop_duplicates(subset=['token_address'])
X = X.set_index("token_address")

lock_features = pd.read_csv("../data/token_lock_features.csv", index_col="token_address")
X = X.merge(lock_features, how='left', left_index=True, right_index=True)

ids = []
total_probs, total_targets = [], []
X_dict, y_dict = {}, {}

skfolds = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
for fold, (t, v) in enumerate(skfolds.split(df['token_address'], df['label'])):

    ids_train = df['token_address'].iloc[t]
    df_train = X.loc[ids_train]
    ids_test = df['token_address'].iloc[v]
    df_test = X.loc[ids_test]

    X_dict['train'], y_dict['train'] = df_train.drop(["label", "eval_block"], axis=1), df_train['label']
    X_dict['test'], y_dict['test'] = df_test.drop(["label", "eval_block"], axis=1), df_test['label']
    X_dict['train'], X_dict['val'], y_dict['train'], y_dict['val'] = train_test_split(X_dict['train'], y_dict['train'],
                                                                                      train_size=0.8)
    device = torch.device('cuda')
    # not the best way to preprocess features, but enough for the demonstration
    preprocess = StandardScaler().fit(X_dict['train'])
    X_dict = {
        k: torch.tensor(preprocess.fit_transform(v), device=device)
        for k, v in X_dict.items()
    }
    y_dict = {k: torch.tensor(v, device=device) for k, v in y_dict.items()}
    y_dict = {k: v.float() for k, v in y_dict.items()}

    model = rtdl.FTTransformer.make_default(
        n_num_features=X_dict['train'].shape[1],
        cat_cardinalities=None,
        last_layer_query_idx=[-1],  # it makes the model faster and does NOT affect its output
        d_out=1,
    )

    model.to(device)
    model.double()
    optimizer = model.make_default_optimizer()
    loss_fn = F.binary_cross_entropy_with_logits

    batch_size = 100
    train_loader = zero.data.IndexLoader(len(X_dict['train']), batch_size, device=device)
    progress = zero.ProgressTracker(patience=2)

    n_epochs = 10
    for epoch in range(1, n_epochs + 1):
        for iteration, batch_idx in enumerate(train_loader):
            model.train()
            optimizer.zero_grad()
            x_batch = X_dict['train'][batch_idx]
            y_batch = y_dict['train'][batch_idx]
            loss = loss_fn(model(x_batch, None).squeeze(1), y_batch)
            loss.backward()
            optimizer.step()

        val_score, prob = evaluate('val', model, X_dict, y_dict)
        progress.update(val_score)
        if progress.fail:
            break

    val_score, prob = evaluate('test', model, X_dict, y_dict)
    ids += df.iloc[v].index.tolist()
    total_probs += prob.tolist()
    total_targets += y_dict['test'].cpu().tolist()
    prob = (prob > 0.5).astype(np.float32)

    f1 = f1_score(y_dict['test'].cpu(), prob)
    sensibilitat = recall_score(y_dict['test'].cpu(), prob)
    precisio = precision_score(y_dict['test'].cpu(), prob)
    accuracy = accuracy_score(y_dict['test'].cpu(), prob)
    print("{},{},{},{},{}".format(accuracy, sensibilitat, precisio, f1, fold))

final_df = pd.DataFrame({'ids': ids, 'Pred': total_probs, 'Label': total_targets})\
    .to_csv("scorings_1h_FTTrans.csv", index=False)

