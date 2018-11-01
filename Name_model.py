from utils import *
import tensorflow as tf
import functools

from keras import backend as K
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam

import matplotlib.pyplot as plt

def as_keras_metric(method):
    @functools.wraps(method)
    def wrapper(self, args, **kwargs):
        """ Wrapper for turning tensorflow metrics into keras metrics """
        value, update_op = method(self, args, **kwargs)
        K.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([update_op]):
            value = tf.identity(value)
        return value
    return wrapper

class Model:
    def __init__(self):
        return

    def load(self, path):
        self.graph = tf.Graph()
        self.sess = tf.Session(graph = self.graph)

        with self.graph.as_default():
            saver = tf.train.import_meta_graph(path + 'model.ckpt.meta')
            saver.restore(self.sess, tf.train.latest_checkpoint(path))
            self.X = self.graph.get_tensor_by_name('X2:0')
            self.y_ = self.graph.get_tensor_by_name('y2_:0')

    def pred(self, name):
        return np_softmax(self.sess.run(self.y_, feed_dict={
            self.X: np.expand_dims(name_one_hot(name, 30), axis=0)
        }))[0][0]


class keras_Model:
    def __init__(self):
        self.model = None
        self.model_path = './model/name_model.h5'

    def load(self):
        self.model = load_model(
            './model/name_model.h5', custom_objects={
                'auc': as_keras_metric(tf.metrics.auc)
            }
        )

    def pred(self, seq):
        return self.model.predict(
            name_one_hot(seq, 15).reshape(1, 15, 26)
        )[0]

    def build_model(self):
        model = Sequential()
        model.add(Bidirectional(LSTM(64, input_shape=(15, 26))))
        model.add(Dense(3, activation='softmax', kernel_initializer='normal'))
        model.compile(loss='categorical_crossentropy', optimizer=Adam(0.0005),
                      metrics=['accuracy', as_keras_metric(tf.metrics.auc)])
        self.model = model

    def show_train_graph(self, hist):
        fig, loss_ax = plt.subplots()
        acc_ax = loss_ax.twinx()

        loss_ax.plot(hist.history['loss'], 'y', label='train loss')
        loss_ax.plot(hist.history['val_loss'], 'r', label='val loss')

        acc_ax.plot(hist.history['acc'], 'b', label='train acc')
        acc_ax.plot(hist.history['val_acc'], 'g', label='val acc')

        acc_ax.plot(hist.history['auc'], 'm', label='train auc')
        acc_ax.plot(hist.history['val_auc'], 'k', label='val auc')

        loss_ax.set_xlabel('epoch')
        loss_ax.set_ylabel('loss')
        acc_ax.set_ylabel('auc_roc')

        loss_ax.legend(loc='upper left')
        acc_ax.legend(loc='lower left')

        plt.show()
        fig.savefig('./model/train_graph.png')

    def train(self):
        # ------------------------------------
        max_seq_len = 15
        np.random.seed(5)
        # ------------------------------------

        kr_list = get_file('./data/kr_first_names.txt')
        ch_list = get_file('./data/ch_first_names.txt')
        us_list = get_file('./data/us_first_names.txt')

        a = len(kr_list)
        b = len(ch_list)
        c = len(us_list)
        data_len = a + b + c

        X, Y = [], []

        for _ in range(1):
            for name in kr_list:
                X.append(name_one_hot(name, max_seq_len))
                Y.append(np.array([1, 0, 0]))
        for _ in range(1):
            for name in ch_list:
                X.append(name_one_hot(name, max_seq_len))
                Y.append(np.array([0, 1, 0]))
        for name in us_list:
            X.append(name_one_hot(name, max_seq_len))
            Y.append(np.array([0, 0, 1]))

        X, Y = np.array(X), np.array(Y)

        np.reshape(X, (data_len, max_seq_len, 26))
        np.reshape(Y, (data_len, 1, 3))

        permutation = np.random.permutation(X.shape[0])
        X = X[permutation]
        Y = Y[permutation]

        train_len = int(data_len * 0.99)

        x_train = X[:train_len]
        y_train = Y[:train_len]
        x_val = X[train_len:]
        y_val = Y[train_len:]

        loss_CP = ModelCheckpoint(
            './model/loss.h5', monitor='val_loss', mode='min',
            verbose=0, save_best_only=True
        )
        acc_CP = ModelCheckpoint(
            './model/acc.h5', monitor='val_acc', mode='max',
            verbose=0, save_best_only=True
        )
        auc_CP = ModelCheckpoint(
            './model/auc.h5', monitor='val_auc', mode='max',
            verbose=0, save_best_only=True
        )

        self.build_model()
        model = self.model
        hist = model.fit(x_train, y_train, epochs=300, batch_size=512,
                         validation_data=(x_val, y_val), verbose=2,
                         callbacks=[loss_CP, acc_CP, auc_CP])

        # score = model.evaluate(x_test, y_test)
        # print("%s: %.2f%%" %(model.metrics_names[1], score[1] * 100))

        # model.save(self.model_path)
        self.show_train_graph(hist)

if __name__=='__main__':
    km = keras_Model()
    km.train()