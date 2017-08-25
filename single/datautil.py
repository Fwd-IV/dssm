import tensorflow as tf
import numpy as np
import operator
class SparseVector:
    def __init__(self):
        self.indices = []
        self.values = []

    def parse(self,line,fmt="libsvm"):
        if(fmt=="libsvm"):
            pars = line.split(" ")
            for part in pars:
                if ":" not in part: continue
                idx_val = part.split(":")
                idx = int(idx_val[0])
                val = float(idx_val[1])
                self.indices.append(idx)
                self.values.append(val)
    @staticmethod
    def load(inpath,fmt="libsvm"):
        vecs = []
        with open(inpath) as datfile:
            for line in datfile:
                vec = SparseVector()
                vec.parse(line,fmt)
                vecs.append(vec)
        return vecs

WORD_HASH_DIM = 7415
class TrainingData:
    def __init__(self):
        self.query_vecs = []
        self.doc_vecs = []
        self.clicks = None

    def size(self):
        return len(self.clicks)

    def toSparseTensorValue(self,sparse_vecs=[],dim=1):
        indices = []
        values = []
        #print 'shape', np.array([len(sparse_vecs),WORD_HASH_DIM], dtype=np.int64).shape
        for idx,vec in enumerate(sparse_vecs):
            for cur_idx_val in sorted(zip(vec.indices,vec.values),key=operator.itemgetter(0)):
                indices.append([idx,cur_idx_val[0]])
                values.append(cur_idx_val[1])

        tensor = tf.SparseTensorValue(
            indices=indices, #indices
            values=values, #value
            dense_shape=[len(sparse_vecs),WORD_HASH_DIM] #shape
        )
        return tensor
        #return indices,values,[len(sparse_vecs),WORD_HASH_DIM]

    def load_clicks(self,filepath):
        self.clicks = []
        for line in open(filepath):
            pars = line.split("\t")
            qid = int(pars[0])
            docid = int(pars[1])
            self.clicks.append((qid,docid))
        return self.clicks

    def load_data(self,query_vec_file, doc_vec_file, clicks_file=None):
        self.query_vecs = SparseVector.load(query_vec_file)
        self.doc_vecs = SparseVector.load(doc_vec_file)
        if clicks_file:
            self.clicks = self.load_clicks(clicks_file)
        else:
            assert len(self.query_vecs)==len(self.doc_vecs)
            self.clicks = [(x,x) for x in range(len(self.query_vecs))]

    def get_batch(self,batch_size,batch_id):
        if batch_size*(batch_id+1) > len(self.clicks):
            print "None returned"
            return None,None
        clicks_batch = self.clicks[batch_size*batch_id:batch_size*(batch_id+1)]
        query_batch = map(lambda x:self.query_vecs[x[0]],clicks_batch)
        doc_batch = map(lambda x:self.doc_vecs[x[1]],clicks_batch)
        #print len(query_batch)
        #print len(doc_batch)
        query_tensor = self.toSparseTensorValue(query_batch,dim=WORD_HASH_DIM)
        doc_tensor = self.toSparseTensorValue(doc_batch,dim=WORD_HASH_DIM)
        return query_tensor,doc_tensor

if __name__ == '__main__':
    data = TrainingData()
    data.load_data("../data/query_vec","../data/doc_vec")
