def topic_extract(args):
    from scipy.sparse import csr_matrix
    from sklearn.decomposition import NMF, LatentDirichletAllocation
    from sklearn.feature_extraction.text import TfidfTransformer
    from collections import defaultdict
    import math
    import numpy as np
    import sqlite3
    from cc import db_name

    max_distinct_words = args.features
    n_topics = args.topics

    stop_words = set([
        'and', 'as', 'class', 'def',
        'err', 'for', 'from', 'get',
        'id', 'if', 'import', 'in', 'int', 'is',
        'let', 'my', 'name', 'nil', 'none', 'not', 'null',
        'of', 'on', 'or', 'return',
        'self', 'span', 'string', 'that',
        'the', 'this', 'to', 'true', 'type',
        'val', 'var', 'with', 'you',
    ])
    stop_words = set()

    con = sqlite3.connect(db_name)
    cur = con.cursor()

    analysis_info = {}
    for row in cur.execute("SELECT analysis.id, project.name FROM analysis JOIN project ON analysis.project_id = project.id"):
        analysis_id, project_name = row
        analysis_info[analysis_id] = {'name':project_name}

    for row in cur.execute("SELECT count(distinct analysis_id) FROM wordcount"):
        num_analyses, = row

    word_to_index = {}
    word_num_analyses = {}
    feature_names = []
    for row in cur.execute("""
SELECT word, sum(count) as count, count(distinct analysis_id) as d
FROM wordcount
GROUP BY word
HAVING d >= 2 AND d <= ?
ORDER BY count DESC, word ASC
LIMIT ?""", (int(1.95 * num_analyses), max_distinct_words)):
        word, count, num_analyses = row
        if word not in stop_words:
            word_to_index[word] = len(word_to_index)
            word_num_analyses[word] = num_analyses
            feature_names.append(word)
    n_features = len(word_to_index)
    print(f"n_features = {n_features}")

    file_indices = {}
    rows = []
    cols = []
    data = []

    if args.files or args.filenorm:
        file_counts = defaultdict(int)
        word_counts = defaultdict(int)
        item_analysis_id = []
        for row in cur.execute("SELECT analysis_id, file_number, sum(count) as c FROM wordcount GROUP BY analysis_id, file_number HAVING c >= 100"):
            analysis_id, file_number, count = row
            item = len(file_indices)
            file_indices[(analysis_id, file_number)] = item
            file_counts[analysis_id] += 1
            word_counts[analysis_id] += count
            item_analysis_id.append(analysis_id)
        n = len(file_indices)
        print(f"n = {n}")

        print("Constructing data arrays")
        for row in cur.execute("SELECT word, count, analysis_id, file_number FROM wordcount"):
            word, count, analysis_id, file_number = row
            if word in word_to_index and (analysis_id, file_number) in file_indices:
                rows.append(file_indices[(analysis_id, file_number)])
                cols.append(word_to_index[word])
                if args.filenorm:
                    #data.append(math.log(10 + count) / math.sqrt(file_counts[analysis_id]))
                    data.append(1 / math.sqrt(file_counts[analysis_id]))
                    #data.append(math.pow(file_counts[analysis_id], -0.25))
                else:
                    data.append(1)
    else:
        for row in cur.execute("SELECT analysis_id FROM wordcount GROUP BY analysis_id"):
            analysis_id, = row
            file_indices[analysis_id] = len(file_indices)
        n = len(file_indices)
        print(f"n = {n}")

        print("Constructing data arrays")
        for row in cur.execute("SELECT word, count, analysis_id FROM wordcount"):
            word, count, analysis_id = row
            if word in word_to_index and analysis_id in file_indices:
                rows.append(file_indices[analysis_id])
                cols.append(word_to_index[word])
                data.append(count)

    print("Constructing csr_matrix")
    count_matrix = csr_matrix((data, (rows,cols)), shape=(n, n_features), dtype=np.float32)

    if args.lda:
        print("Performing LDA")
        model = LatentDirichletAllocation(n_topics, verbose=2)
        transformed = model.fit_transform(count_matrix)
    else:
        if args.filenorm or args.files:
            X = count_matrix
        else:
            print("Transforming count matrix to td-idf")
            X = TfidfTransformer().fit_transform(count_matrix)

        print("Performing NMF")
        if args.kl:
            model = NMF(n_topics, solver='mu', beta_loss='kullback-leibler', verbose=2)
        else:
            model = NMF(n_topics, verbose=2)
        transformed = model.fit_transform(X)

    topic_summaries = []
    for i in range(n_topics):
        print(f"==== topic {i} ====")
        indices = list(range(n_features))
        indices.sort(key=lambda j: model.components_[i,j], reverse=True)
        for j in range(min(50, n_features)):
            word = feature_names[indices[j]]
            num_analyses = word_num_analyses.get(word)
            print(f"    {word:20}({num_analyses})   {model.components_[i,indices[j]]}")

        topic_summary = ''
        for j in range(min(3, n_features)):
            word = feature_names[indices[j]]
            topic_summary += ' ' + word
        topic_summaries.append(topic_summary)

        print()

    if args.files or args.filenorm:
        sum_vecs = defaultdict(lambda:np.zeros((n_topics,)))
        for item in range(n):
            analysis_id = item_analysis_id[item]
            sum_vecs[analysis_id] += transformed[item,:]

        for analysis_id, vec in sum_vecs.items():
            print(analysis_info[analysis_id])
            for i in sorted(range(n_topics), key=lambda i:vec[i], reverse=True)[:6]:
                print(vec[i], topic_summaries[i])

    con.close()


def topic_tsne(args):
    from scipy.sparse import csr_matrix
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize
    from sklearn.manifold import TSNE
    from collections import defaultdict
    import json
    import math
    import numpy as np
    import sqlite3
    from cc import db_name

    con = sqlite3.connect(db_name)
    cur = con.cursor()

    max_distinct_words = args.words
    word_to_index = {}
    word_names = []
    word_counts = []

    file_indices = {}
    rows = []
    cols = []
    data = []

    for row in cur.execute("SELECT word, count(distinct analysis_id) as analyses, sum(count) as count FROM wordcount GROUP BY word ORDER BY analyses DESC, count DESC, word ASC LIMIT ?", (max_distinct_words,)):
        word, _analyses, count = row
        word_to_index[word] = len(word_to_index)
        word_names.append(word)
        word_counts.append(count)
    n = len(word_to_index)
    print(f"n = {n}")

    if args.project:
        for row in cur.execute("SELECT analysis_id FROM wordcount GROUP BY analysis_id"):
            analysis_id, = row
            file_indices[analysis_id] = len(file_indices)
        n_features = len(file_indices)
        print(f"n_features = {n_features}")

        print("Constructing data arrays")
        for row in cur.execute("SELECT word, sum(count) as c, analysis_id FROM wordcount GROUP BY word, analysis_id"):
            word, count, analysis_id = row
            if word in word_to_index and analysis_id in file_indices:
                rows.append(word_to_index[word])
                cols.append(file_indices[analysis_id])
                if args.counts:
                    data.append(count)
                elif args.log:
                    data.append(math.log(1 + count, 10))
                elif args.loglog:
                    data.append(math.log(math.log(3 + count)))
                else:
                    data.append(1)
    else:
        file_counts = defaultdict(int)
        for row in cur.execute("SELECT analysis_id, file_number FROM wordcount GROUP BY analysis_id, file_number"):
            analysis_id, file_number = row
            file_indices[(analysis_id, file_number)] = len(file_indices)
            file_counts[analysis_id] += 1
        n_features = len(file_indices)
        print(f"n_features = {n_features}")

        print("Constructing data arrays")
        for row in cur.execute("SELECT word, count, analysis_id, file_number FROM wordcount"):
            word, count, analysis_id, file_number = row
            if word in word_to_index and (analysis_id, file_number) in file_indices:
                rows.append(word_to_index[word])
                cols.append(file_indices[(analysis_id, file_number)])
                if args.counts:
                    data.append(count)
                elif args.log:
                    if args.filenorm:
                        data.append(math.log(1 + count) / file_counts[analysis_id])
                    else:
                        data.append(math.log(1 + count))
                elif args.filenorm:
                    data.append(1 / file_counts[analysis_id])
                else:
                    data.append(1)

    print("Constructing csr_matrix")
    count_matrix = csr_matrix((data, (rows,cols)), shape=(n, n_features), dtype=np.float32)

    print("Normalizing")
    X = count_matrix #normalize(count_matrix, norm='l1')

    if args.intermediate < n_features:
        print("Truncated SVD")
        X_reduced = TruncatedSVD(args.intermediate).fit_transform(X)
    else:
        X_reduced = X

    print("TSNE")
    model = TSNE(n_components=2, perplexity=args.perplexity, verbose=2)
    xy = model.fit_transform(X_reduced)

    print("Writing JSON")
    with open("output.json", "w") as f:
        json.dump({
            "x": [float(x) for x in xy[:,0]],
            "y": [float(y) for y in xy[:,1]],
            "labels": word_names,
            "sizes": word_counts,
            "types": ['word' for w in word_names]
        },f)
    con.close()
